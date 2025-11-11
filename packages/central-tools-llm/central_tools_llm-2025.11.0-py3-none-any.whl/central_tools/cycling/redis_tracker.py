"""Redis-backed implementation of the global usage tracker."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable, Iterable, List, Sequence

from .api_cycler import RateLimitRule
from .usage_tracker import UsageTracker


@dataclass(slots=True)
class _RuleContext:
    rule: RateLimitRule
    window_id: int
    calls_key: str
    tokens_key: str | None


class RedisUsageTracker(UsageTracker):
    """Coordinate usage across processes using Redis as the shared store."""

    DEFAULT_STATUS_FIELDS: Sequence[str] = ("success", "rate_limit", "failure", "transient_failure")

    def __init__(
        self,
        client: Any,
        *,
        namespace: str = "central-tools",
        ttl_padding: int = 5,
        status_ttl: int = 300,
        status_fields: Sequence[str] | None = None,
        time_func: Callable[[], float] | None = None,
        use_pipeline: bool = True,
    ) -> None:
        self._client = client
        self._namespace = namespace.rstrip(":")
        self._ttl_padding = ttl_padding
        self._status_ttl = status_ttl
        self._status_fields = tuple(status_fields or self.DEFAULT_STATUS_FIELDS)
        self._time = time_func or time.time
        self._use_pipeline = use_pipeline

    # UsageTracker interface -------------------------------------------------
    def reserve(
        self,
        provider_id: str,
        model_name: str | None,
        key_identifier: str,
        rules: list[RateLimitRule],
        expected_tokens: int,
    ) -> bool:
        if not rules:
            return True

        now = self._time()
        contexts = self._build_contexts(provider_id, model_name, rules, now)
        keys: list[str] = []
        for ctx in contexts:
            keys.append(ctx.calls_key)
            if ctx.tokens_key:
                keys.append(ctx.tokens_key)

        if not keys:
            return True

        values = self._client.mget(keys)
        idx = 0
        for ctx in contexts:
            calls = self._coerce_int(values[idx])
            idx += 1
            if ctx.rule.max_calls is not None and calls + 1 > ctx.rule.max_calls:
                return False

            if ctx.tokens_key:
                tokens = self._coerce_int(values[idx])
                idx += 1
                if ctx.rule.max_tokens is not None and tokens + max(expected_tokens, 0) > ctx.rule.max_tokens:
                    return False
            elif ctx.rule.max_tokens is not None and max(expected_tokens, 0) > ctx.rule.max_tokens:
                # Cap purely on expected tokens if we are not tracking tokens in Redis
                return False

        return True

    def record(
        self,
        provider_id: str,
        model_name: str | None,
        key_identifier: str,
        status: str,
        tokens_used: int,
        *,
        rules: list[RateLimitRule] | None = None,
        reserved_tokens: int | None = None,
    ) -> None:
        rule_list = list(rules or [])
        now = self._time()
        contexts = self._build_contexts(provider_id, model_name, rule_list, now)
        token_amount = max(int(tokens_used), 0)
        if token_amount <= 0 and reserved_tokens:
            token_amount = max(int(reserved_tokens), 0)

        expiry_padding = self._ttl_padding
        ttl_candidates = [ctx.rule.period_seconds for ctx in contexts if ctx.rule.period_seconds > 0]
        status_ttl = (max(ttl_candidates) if ttl_candidates else self._status_ttl) + expiry_padding

        if self._use_pipeline and hasattr(self._client, "pipeline"):
            with self._client.pipeline() as pipe:
                self._apply_record(pipe, contexts, token_amount, expiry_padding)
                pipe.execute()
        else:
            self._apply_record(self._client, contexts, token_amount, expiry_padding)

        self._increment_status(provider_id, model_name, status, status_ttl)

    # Public helpers ---------------------------------------------------------
    def get_usage_snapshot(
        self,
        provider_id: str,
        model_name: str | None,
        rules: Iterable[RateLimitRule],
    ) -> dict[str, dict[str, int]]:
        rule_list = list(rules)
        now = self._time()
        contexts = self._build_contexts(provider_id, model_name, rule_list, now)

        keys: list[str] = []
        for ctx in contexts:
            keys.append(ctx.calls_key)
            if ctx.tokens_key:
                keys.append(ctx.tokens_key)

        values = self._client.mget(keys) if keys else []
        ttl_lookup: dict[str, int] = {}
        if keys and hasattr(self._client, "ttl"):
            for key in keys:
                ttl_value = self._safe_ttl(key)
                if ttl_value is not None:
                    ttl_lookup[key] = ttl_value
        snapshot: dict[str, dict[str, int]] = {}
        idx = 0
        for ctx in contexts:
            entry = {"calls": self._coerce_int(values[idx]) if idx < len(values) else 0}
            idx += 1
            ttl_value = ttl_lookup.get(ctx.calls_key)
            if ttl_value is not None:
                entry["calls_ttl"] = ttl_value
            if ctx.tokens_key:
                entry["tokens"] = self._coerce_int(values[idx]) if idx < len(values) else 0
                tokens_ttl = ttl_lookup.get(ctx.tokens_key)
                if tokens_ttl is not None:
                    entry["tokens_ttl"] = tokens_ttl
                idx += 1
            snapshot[ctx.rule.name] = entry

        status_keys = [self._status_key(provider_id, model_name, status) for status in self._status_fields]
        status_values = self._client.mget(status_keys) if status_keys else []
        snapshot["statuses"] = {
            status: self._coerce_int(status_values[i]) if i < len(status_values) else 0
            for i, status in enumerate(self._status_fields)
        }
        if status_keys and hasattr(self._client, "ttl"):
            status_ttls: dict[str, int] = {}
            for i, key in enumerate(status_keys):
                ttl_value = self._safe_ttl(key)
                if ttl_value is not None:
                    status_ttls[self._status_fields[i]] = ttl_value
            if status_ttls:
                snapshot["statuses_ttl"] = status_ttls
        return snapshot

    # Internal helpers -------------------------------------------------------
    def _apply_record(
        self,
        client: Any,
        contexts: List[_RuleContext],
        token_amount: int,
        expiry_padding: int,
    ) -> None:
        for ctx in contexts:
            ttl = max(ctx.rule.period_seconds, 1) + expiry_padding
            client.incrby(ctx.calls_key, 1)
            client.expire(ctx.calls_key, ttl)
            if ctx.tokens_key and token_amount:
                client.incrby(ctx.tokens_key, token_amount)
                client.expire(ctx.tokens_key, ttl)

    def _increment_status(self, provider_id: str, model_name: str | None, status: str, ttl: int) -> None:
        status_key = self._status_key(provider_id, model_name, status)
        self._client.incrby(status_key, 1)
        self._client.expire(status_key, ttl)

    def _build_contexts(
        self,
        provider_id: str,
        model_name: str | None,
        rules: Iterable[RateLimitRule],
        now: float,
    ) -> List[_RuleContext]:
        contexts: list[_RuleContext] = []
        for rule in rules:
            period = max(rule.period_seconds, 1)
            window_id = int(now // period)
            calls_key = self._calls_key(provider_id, model_name, rule.name, window_id)
            tokens_key = None
            if rule.max_tokens is not None:
                tokens_key = self._tokens_key(provider_id, model_name, rule.name, window_id)
            contexts.append(_RuleContext(rule=rule, window_id=window_id, calls_key=calls_key, tokens_key=tokens_key))
        return contexts

    def _calls_key(self, provider_id: str, model_name: str | None, rule_name: str, window_id: int) -> str:
        return self._key("calls", provider_id, model_name, rule_name, str(window_id))

    def _tokens_key(self, provider_id: str, model_name: str | None, rule_name: str, window_id: int) -> str:
        return self._key("tokens", provider_id, model_name, rule_name, str(window_id))

    def _status_key(self, provider_id: str, model_name: str | None, status: str) -> str:
        return self._key("status", provider_id, model_name, status)

    def _key(self, prefix: str, provider_id: str, model_name: str | None, *extra: str) -> str:
        model_fragment = self._sanitize(model_name) if model_name is not None else "global"
        parts = [self._namespace, prefix, self._sanitize(provider_id), model_fragment]
        parts.extend(self._sanitize(part) for part in extra)
        return ":".join(parts)

    @staticmethod
    def _sanitize(value: str) -> str:
        safe = value.replace(":", "_").replace("/", "_").replace(" ", "_")
        return safe or "default"

    @staticmethod
    def _coerce_int(value: Any) -> int:
        if value is None:
            return 0
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        return int(value)

    def _safe_ttl(self, key: str) -> int | None:
        try:
            ttl_value = self._client.ttl(key)
        except Exception:  # noqa: BLE001 - snapshot must not raise
            return None
        if ttl_value is None:
            return None
        try:
            ttl_int = int(ttl_value)
        except (TypeError, ValueError):
            return None
        if ttl_int < 0:
            return None
        return ttl_int

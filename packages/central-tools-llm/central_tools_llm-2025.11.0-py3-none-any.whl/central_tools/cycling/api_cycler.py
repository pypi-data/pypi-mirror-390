"""API key cycling utilities to distribute load across credentials."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Deque, Dict, Iterable, List, Optional, Tuple

from ..exceptions import NoAvailableAPIKey, RateLimitExceeded
from ..models import LLMResponse
from .usage_tracker import UsageTracker

UTC = timezone.utc


def _now() -> datetime:
    return datetime.now(tz=UTC)


@dataclass(slots=True)
class RateLimitRule:
    """Describes a rate limit window for an API key."""

    name: str
    period_seconds: int
    max_calls: int | None = None
    max_tokens: int | None = None
    cooldown_seconds: int | None = None

    @property
    def period(self) -> timedelta:
        return timedelta(seconds=self.period_seconds)


@dataclass(slots=True)
class _TokenBucket:
    events: Deque[tuple[datetime, int]] = field(default_factory=deque)
    total_tokens: int = 0

    def add(self, timestamp: datetime, tokens: int) -> None:
        self.events.append((timestamp, tokens))
        self.total_tokens += tokens

    def prune(self, window_start: datetime) -> None:
        while self.events and self.events[0][0] <= window_start:
            _, tokens = self.events.popleft()
            self.total_tokens -= tokens


@dataclass(slots=True)
class _CallWindow:
    timestamps: Deque[datetime] = field(default_factory=deque)

    def add(self, timestamp: datetime) -> None:
        self.timestamps.append(timestamp)

    def prune(self, window_start: datetime) -> None:
        while self.timestamps and self.timestamps[0] <= window_start:
            self.timestamps.popleft()

    def count(self) -> int:
        return len(self.timestamps)


@dataclass(slots=True)
class APIKeyState:
    """Holds runtime state for a single API key."""

    identifier: str
    secret: str
    rules: List[RateLimitRule]
    call_windows: Dict[str, _CallWindow] = field(default_factory=dict)
    token_windows: Dict[str, _TokenBucket] = field(default_factory=dict)
    last_used: Optional[datetime] = None
    cooldown_until: Optional[datetime] = None
    consecutive_failures: int = 0

    def ensure_rule_tracking(self, rule: RateLimitRule) -> None:
        self.call_windows.setdefault(rule.name, _CallWindow())
        self.token_windows.setdefault(rule.name, _TokenBucket())

    def prune_windows(self, now: datetime) -> None:
        for rule in self.rules:
            self.ensure_rule_tracking(rule)
            window_start = now - rule.period
            self.call_windows[rule.name].prune(window_start)
            self.token_windows[rule.name].prune(window_start)

    def can_use(self, now: datetime) -> bool:
        if self.cooldown_until and self.cooldown_until > now:
            return False
        self.prune_windows(now)
        for rule in self.rules:
            calls = self.call_windows[rule.name].count()
            if rule.max_calls is not None and calls >= rule.max_calls:
                return False
            tokens = self.token_windows[rule.name].total_tokens
            if rule.max_tokens is not None and tokens >= rule.max_tokens:
                return False
        return True

    def record_attempt(self, now: datetime, tokens_used: int = 0) -> None:
        self.prune_windows(now)
        for rule in self.rules:
            self.ensure_rule_tracking(rule)
            self.call_windows[rule.name].add(now)
            if tokens_used:
                self.token_windows[rule.name].add(now, tokens_used)
        self.last_used = now

    def start_cooldown(self, duration: timedelta) -> None:
        now = _now()
        desired = now + duration
        if self.cooldown_until and self.cooldown_until > desired:
            return
        self.cooldown_until = desired


@dataclass(slots=True)
class APIKeySnapshot:
    """Immutable snapshot returned to callers."""

    identifier: str
    secret: str


@dataclass(slots=True)
class _Reservation:
    rules: list[RateLimitRule]
    expected_tokens: int


class APIKeyCycler:
    """Cycles through API keys while respecting rate limits."""

    def __init__(self, *, max_keys: int = 5, usage_tracker: UsageTracker | None = None) -> None:
        self.max_keys = max_keys
        self._keys: Dict[str, List[APIKeyState]] = {}
        self._cursors: Dict[str, int] = {}
        self._tracker: UsageTracker | None = usage_tracker
        self._reservations: Dict[Tuple[str, str], Deque[_Reservation]] = defaultdict(deque)

    def set_usage_tracker(self, tracker: UsageTracker | None) -> None:
        """Replace the usage tracker at runtime."""
        self._tracker = tracker
        if tracker is None:
            self._reservations.clear()

    def register_key(
        self,
        *,
        provider_id: str,
        identifier: str,
        secret: str,
        rules: Iterable[RateLimitRule],
    ) -> None:
        rules_list = list(rules)
        if provider_id not in self._keys:
            self._keys[provider_id] = []
        if len(self._keys[provider_id]) >= self.max_keys:
            raise ValueError(f"Max keys ({self.max_keys}) already registered for provider {provider_id}")
        state = APIKeyState(identifier=identifier, secret=secret, rules=rules_list)
        for rule in rules_list:
            state.ensure_rule_tracking(rule)
        self._keys[provider_id].append(state)

    def get_next_key(self, provider_id: str) -> APIKeySnapshot:
        return self.get_next_key_for_model(provider_id, model_name=None, model_rules=None, expected_tokens=0)

    def peek_next_key(self, provider_id: str) -> APIKeySnapshot | None:
        return self.peek_next_key_for_model(provider_id, model_name=None, model_rules=None, expected_tokens=0)

    def get_next_key_for_model(
        self,
        provider_id: str,
        *,
        model_name: str | None = None,
        model_rules: list[RateLimitRule] | None = None,
        expected_tokens: int = 0,
    ) -> APIKeySnapshot:
        """Select the next API key for a provider, optionally considering model-specific rules.

        - model_name: optional identifier for the target model, used for tracker coordination
        - model_rules: list of RateLimitRule instances describing the model's limits
        - expected_tokens: integer token estimate for the upcoming call
        """

        now = _now()
        states = self._keys.get(provider_id, [])
        if not states:
            raise NoAvailableAPIKey(f"No API keys registered for provider {provider_id!r}")

        start_index = self._cursors.get(provider_id, 0)
        rules = model_rules or []
        for offset in range(len(states)):
            index = (start_index + offset) % len(states)
            state = states[index]
            if state.cooldown_until and state.cooldown_until > now:
                continue
            # ensure tracking windows exist for model rules so we can check capacities
            for r in rules:
                state.ensure_rule_tracking(r)
            state.prune_windows(now)

            if not self._state_satisfies_rules(state, rules, expected_tokens, now):
                continue

            # state also must satisfy its own registered rules
            if not state.can_use(now):
                continue

            if not self._reserve_global_usage(provider_id, model_name, state, rules, expected_tokens):
                continue

            self._cursors[provider_id] = (index + 1) % len(states)
            return APIKeySnapshot(identifier=state.identifier, secret=state.secret)

        raise NoAvailableAPIKey(f"All API keys are currently cooling down or lack capacity for provider {provider_id!r}")

    def peek_next_key_for_model(
        self,
        provider_id: str,
        *,
        model_name: str | None = None,
        model_rules: list[RateLimitRule] | None = None,
        expected_tokens: int = 0,
    ) -> APIKeySnapshot | None:
        now = _now()
        states = self._keys.get(provider_id, [])
        if not states:
            return None
        rules = model_rules or []
        for state in states:
            if state.cooldown_until and state.cooldown_until > now:
                continue
            for r in rules:
                state.ensure_rule_tracking(r)
            state.prune_windows(now)
            if self._state_satisfies_rules(state, rules, expected_tokens, now) and state.can_use(now):
                return APIKeySnapshot(identifier=state.identifier, secret=state.secret)
        return None

    def _reserve_global_usage(
        self,
        provider_id: str,
        model_name: str | None,
        state: APIKeyState,
        rules: list[RateLimitRule],
        expected_tokens: int,
    ) -> bool:
        if not self._tracker:
            return True
        allowed = self._tracker.reserve(
            provider_id,
            model_name,
            state.identifier,
            rules,
            expected_tokens,
        )
        if allowed:
            key = (provider_id, state.identifier)
            self._reservations[key].append(_Reservation(list(rules), expected_tokens))
        return allowed

    def _state_satisfies_rules(self, state: APIKeyState, rules: list[RateLimitRule], expected_tokens: int, now: datetime) -> bool:
        # Conservative aggregate checks: compare model limits against the key's
        # observed usage (aggregate across the key's tracked windows).
        # This is intentionally conservative and avoids needing identical
        # rule names across keys and models.
        total_calls = sum(window.count() for window in state.call_windows.values())
        total_tokens = sum(bucket.total_tokens for bucket in state.token_windows.values())

        for rule in rules:
            # calls
            if rule.max_calls is not None:
                if total_calls + 1 > rule.max_calls:
                    return False
            # tokens
            if rule.max_tokens is not None:
                if expected_tokens + total_tokens > rule.max_tokens:
                    return False

        return True

    def report_success(
        self,
        provider_id: str,
        identifier: str,
        model_name: str | None,
        response: LLMResponse,
    ) -> None:
        state = self._lookup_state(provider_id, identifier)
        tokens = response.tokens_used or 0
        now = _now()
        state.record_attempt(now, tokens_used=tokens)
        state.consecutive_failures = 0
        state.cooldown_until = None
        self._record_usage(provider_id, model_name, identifier, "success", tokens)

    def report_rate_limit(
        self,
        provider_id: str,
        identifier: str,
        model_name: str | None,
        exc: RateLimitExceeded,
    ) -> None:
        state = self._lookup_state(provider_id, identifier)
        now = _now()
        state.record_attempt(now)
        cooldown = self._determine_cooldown(state, exc)
        state.start_cooldown(cooldown)
        state.consecutive_failures += 1
        self._record_usage(provider_id, model_name, identifier, "rate_limit", 0)

    def mark_failure(self, provider_id: str, identifier: str, model_name: str | None) -> None:
        state = self._lookup_state(provider_id, identifier)
        now = _now()
        state.record_attempt(now)
        state.consecutive_failures += 1
        if state.consecutive_failures >= 3:
            state.start_cooldown(timedelta(seconds=5 * state.consecutive_failures))
        self._record_usage(provider_id, model_name, identifier, "failure", 0)

    def mark_transient_failure(self, provider_id: str, identifier: str, model_name: str | None) -> None:
        state = self._lookup_state(provider_id, identifier)
        now = _now()
        state.record_attempt(now)
        state.consecutive_failures += 1
        state.start_cooldown(timedelta(seconds=min(5 * state.consecutive_failures, 30)))
        self._record_usage(provider_id, model_name, identifier, "transient_failure", 0)

    def peek_next_key(self, provider_id: str) -> APIKeySnapshot | None:
        return self.peek_next_key_for_model(provider_id, model_name=None, model_rules=None, expected_tokens=0)

    def _lookup_state(self, provider_id: str, identifier: str) -> APIKeyState:
        states = self._keys.get(provider_id, [])
        for state in states:
            if state.identifier == identifier:
                return state
        raise NoAvailableAPIKey(f"Unknown API key {identifier!r} for provider {provider_id!r}")

    @staticmethod
    def _determine_cooldown(state: APIKeyState, exc: RateLimitExceeded) -> timedelta:
        if exc.retry_after_seconds is not None:
            return timedelta(seconds=exc.retry_after_seconds)
        if exc.rule_name:
            rule = next((rule for rule in state.rules if rule.name == exc.rule_name), None)
            if rule:
                duration = rule.cooldown_seconds or rule.period_seconds
                return timedelta(seconds=duration)
        longest_period = max((rule.period_seconds for rule in state.rules), default=60)
        return timedelta(seconds=longest_period)

    def _record_usage(
        self,
        provider_id: str,
        model_name: str | None,
        identifier: str,
        status: str,
        tokens_used: int,
    ) -> None:
        if not self._tracker:
            return
        reservation: _Reservation | None = None
        key = (provider_id, identifier)
        queue = self._reservations.get(key)
        if queue:
            try:
                reservation = queue.popleft()
            except IndexError:
                reservation = None
            if not queue:
                self._reservations.pop(key, None)

        self._tracker.record(
            provider_id,
            model_name,
            identifier,
            status,
            tokens_used,
            rules=reservation.rules if reservation else None,
            reserved_tokens=reservation.expected_tokens if reservation else None,
        )

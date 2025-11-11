"""Configuration helpers to build router and cycler from data sources."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Sequence

from .cycling.api_cycler import APIKeyCycler, RateLimitRule
from .models import TaskDepth
from .routing.router import LLMRouter


@dataclass(slots=True)
class RateLimitConfig:
    name: str
    period_seconds: int
    max_calls: int | None = None
    max_tokens: int | None = None
    cooldown_seconds: int | None = None

    def to_rule(self) -> RateLimitRule:
        return RateLimitRule(
            name=self.name,
            period_seconds=self.period_seconds,
            max_calls=self.max_calls,
            max_tokens=self.max_tokens,
            cooldown_seconds=self.cooldown_seconds,
        )


@dataclass(slots=True)
class ApiKeyConfig:
    provider_id: str
    identifier: str
    secret: str
    rate_limits: Iterable[RateLimitConfig] = field(default_factory=list)


@dataclass(slots=True)
class ModelConfig:
    depth: TaskDepth
    provider_id: str
    model_name: str
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    provider_kwargs: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ApiKeyPlaceholder:
    """Describes a placeholder for an API key stored in an environment variable."""

    provider_id: str
    identifier: str
    env_name: str


def build_router(router: LLMRouter, models: Iterable[ModelConfig], provider_factories: Mapping[str, Any]) -> LLMRouter:
    for model in models:
        factory = provider_factories[model.provider_id]
        router.register_model(
            depth=model.depth,
            provider_id=model.provider_id,
            model_name=model.model_name,
            priority=model.priority,
            metadata=model.metadata,
            provider_factory=lambda api_key, *, _factory=factory, _model=model: _factory(
                api_key,
                model_name=_model.model_name,
                **_model.provider_kwargs,
            ),
        )
    return router


def build_cycler(cycler: APIKeyCycler, api_keys: Iterable[ApiKeyConfig]) -> APIKeyCycler:
    for key in api_keys:
        rules = [config.to_rule() for config in key.rate_limits]
        cycler.register_key(
            provider_id=key.provider_id,
            identifier=key.identifier,
            secret=key.secret,
            rules=rules,
        )
    return cycler


def load_api_keys_from_env(
    *,
    provider_id: str,
    env_prefix: str,
    max_keys: int = 5,
    rate_limits: Sequence[RateLimitConfig] | None = None,
) -> List[ApiKeyConfig]:
    """Load sequentially numbered API keys from environment variables."""

    keys: List[ApiKeyConfig] = []
    for index in range(1, max_keys + 1):
        env_name = f"{env_prefix}{index}"
        secret = os.getenv(env_name)
        if not secret:
            continue
        keys.append(
            ApiKeyConfig(
                provider_id=provider_id,
                identifier=str(index),
                secret=secret,
                rate_limits=rate_limits or [],
            )
        )
    return keys


def load_api_keys_from_placeholders(
    placeholders: Sequence[ApiKeyPlaceholder],
    *,
    rate_limits: Sequence[RateLimitConfig] | None = None,
    env: MutableMapping[str, str] | None = None,
) -> List[ApiKeyConfig]:
    """Turn placeholders into API key configs by resolving environment variables."""

    env_mapping = env or os.environ
    keys: List[ApiKeyConfig] = []
    for placeholder in placeholders:
        secret = env_mapping.get(placeholder.env_name)
        if not secret:
            continue
        keys.append(
            ApiKeyConfig(
                provider_id=placeholder.provider_id,
                identifier=placeholder.identifier,
                secret=secret,
                rate_limits=rate_limits or [],
            )
        )
    return keys


def load_env_file(path: str | os.PathLike[str], *, override: bool = False) -> Dict[str, str]:
    """Load key/value pairs from an env file into os.environ and return them."""

    env_path = Path(path)
    if not env_path.exists():
        raise FileNotFoundError(f"Env file not found: {env_path}")

    loaded: Dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if value.startswith("\"") and value.endswith("\""):
            value = value[1:-1]
        loaded[key] = value
        if override or key not in os.environ:
            os.environ[key] = value
    return loaded

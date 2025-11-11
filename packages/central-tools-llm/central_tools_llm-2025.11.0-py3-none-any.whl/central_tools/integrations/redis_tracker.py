"""Helpers for wiring Redis-backed usage tracking."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional

from ..cycling import APIKeyCycler
from ..cycling.usage_tracker import UsageTracker


@dataclass(slots=True)
class RedisConfig:
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    username: Optional[str] = None
    password: Optional[str] = None
    ssl: bool = False
    namespace: str = "central-tools"
    ttl_padding: int = 5
    status_ttl: int = 300

    @classmethod
    def from_env(cls, env: Mapping[str, str]) -> "RedisConfig":
        return cls(
            host=env.get("REDIS_HOST", "localhost"),
            port=int(env.get("REDIS_PORT", 6379)),
            db=int(env.get("REDIS_DB", 0)),
            username=env.get("REDIS_USER"),
            password=env.get("REDIS_PASSWORD"),
            ssl=env.get("REDIS_SSL", "false").lower() in {"1", "true", "yes"},
            namespace=env.get("REDIS_NAMESPACE", "central-tools"),
            ttl_padding=int(env.get("REDIS_TTL_PADDING", 5)),
            status_ttl=int(env.get("REDIS_STATUS_TTL", 300)),
        )


def connect_sync(config: RedisConfig) -> Any:  # pragma: no cover - thin wrappers
    from redis import Redis  # type: ignore[import-not-found]

    return Redis(
        host=config.host,
        port=config.port,
        db=config.db,
        username=config.username,
        password=config.password,
        ssl=config.ssl,
        decode_responses=False,
    )


def connect_async(config: RedisConfig) -> Any:  # pragma: no cover - thin wrappers
    from redis.asyncio import Redis as AsyncRedis  # type: ignore[import-not-found]

    return AsyncRedis(
        host=config.host,
        port=config.port,
        db=config.db,
        username=config.username,
        password=config.password,
        ssl=config.ssl,
        decode_responses=False,
    )


def build_usage_tracker(config: RedisConfig, *, client: Optional[Any] = None) -> UsageTracker:
    from ..cycling import RedisUsageTracker

    redis_client = client or connect_sync(config)
    return RedisUsageTracker(
        redis_client,
        namespace=config.namespace,
        ttl_padding=config.ttl_padding,
        status_ttl=config.status_ttl,
    )


def attach_usage_tracker(cycler: APIKeyCycler, tracker: UsageTracker) -> APIKeyCycler:
    cycler.set_usage_tracker(tracker)
    return cycler

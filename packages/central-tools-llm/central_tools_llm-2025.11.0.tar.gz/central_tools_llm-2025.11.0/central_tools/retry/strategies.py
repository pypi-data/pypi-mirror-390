"""Retry strategies for provider calls."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Callable, Sequence, Type, TypeVar

from ..exceptions import TransientProviderError

T = TypeVar("T")


class RetryStrategy:
    """Protocol-like base class for retry strategies."""

    def execute(self, func: Callable[[], T]) -> T:  # pragma: no cover - interface definition
        raise NotImplementedError


@dataclass(slots=True)
class ExponentialBackoffRetry(RetryStrategy):
    """Retry with exponential backoff and jitter for transient failures."""

    max_attempts: int = 4
    initial_delay_s: float = 0.5
    max_delay_s: float = 8.0
    multiplier: float = 2.0
    jitter_s: float = 0.1
    retry_on: Sequence[Type[BaseException]] = field(default_factory=lambda: [TransientProviderError])
    sleep_fn: Callable[[float], None] = time.sleep

    def execute(self, func: Callable[[], T]) -> T:
        attempt = 0
        delay = self.initial_delay_s
        last_exc: BaseException | None = None

        while attempt < self.max_attempts:
            try:
                return func()
            except Exception as exc:  # noqa: BLE001 - controlled by retry_on
                if not self._should_retry(type(exc)):
                    raise
                last_exc = exc
                attempt += 1
                if attempt >= self.max_attempts:
                    break
                jitter = random.uniform(-self.jitter_s, self.jitter_s)
                wait_time = min(self.max_delay_s, max(0.0, delay + jitter))
                self.sleep_fn(wait_time)
                delay *= self.multiplier

        assert last_exc is not None
        raise last_exc

    def _should_retry(self, exc_type: Type[BaseException]) -> bool:
        return any(issubclass(exc_type, retry_exc) for retry_exc in self.retry_on)

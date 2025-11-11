"""Interfaces for global usage tracking backends."""

from __future__ import annotations

from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for typing only
    from .api_cycler import RateLimitRule


class UsageTracker(Protocol):
    """Optional global tracker to coordinate usage across processes."""

    def reserve(
        self,
        provider_id: str,
        model_name: str | None,
        key_identifier: str,
        rules: list["RateLimitRule"],
        expected_tokens: int,
    ) -> bool:
        """Attempt to reserve quota for an upcoming call.

        Return True if the call may proceed, False if global limits would be violated.
        """

    def record(
        self,
        provider_id: str,
        model_name: str | None,
        key_identifier: str,
        status: str,
        tokens_used: int,
        *,
        rules: list["RateLimitRule"] | None = None,
        reserved_tokens: int | None = None,
    ) -> None:
        """Record the outcome of a call (success/limit/failure)."""
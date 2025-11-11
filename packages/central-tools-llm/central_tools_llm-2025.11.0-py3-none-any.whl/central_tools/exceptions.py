"""Custom exceptions for the central LLM tools."""

from __future__ import annotations


class CentralToolsError(RuntimeError):
    """Base for custom exceptions."""


class RoutingError(CentralToolsError):
    """Raised when routing cannot find a model."""


class ProviderError(CentralToolsError):
    """Generic provider failure."""


class TransientProviderError(ProviderError):
    """Indicates a transient provider issue that may succeed on retry."""


class RateLimitExceeded(TransientProviderError):
    """Raised when a provider signals that rate limits were reached."""

    def __init__(self, message: str = "Rate limit exceeded", *, rule_name: str | None = None, retry_after_seconds: float | None = None) -> None:
        super().__init__(message)
        self.rule_name = rule_name
        self.retry_after_seconds = retry_after_seconds


class NoAvailableAPIKey(TransientProviderError):
    """Raised when no API key qualifies for use."""

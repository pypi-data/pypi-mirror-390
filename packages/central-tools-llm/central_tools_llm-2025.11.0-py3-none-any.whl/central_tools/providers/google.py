"""Google Gemini and Gemma provider integration."""

from __future__ import annotations

from typing import Any, Callable, Iterable

from ..exceptions import ProviderError, RateLimitExceeded, TransientProviderError
from ..models import LLMRequest, LLMResponse
from .base import BaseLLMProvider

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover - optional dependency
    genai = None  # type: ignore[assignment]


_TRANSIENT_EXCEPTION_NAMES = {
    "InternalServerError",
    "ServiceUnavailable",
    "DeadlineExceeded",
    "RetryError",
    "Unavailable",
}

_RATE_LIMIT_EXCEPTION_NAMES = {
    "ResourceExhausted",
    "TooManyRequests",
}


class GoogleLLMProvider(BaseLLMProvider):
    """Adapter for Google-hosted models (Gemini, Gemma)."""

    provider_id = "google"

    def __init__(self, api_key: str, model_name: str, **model_kwargs: Any) -> None:
        settings = self._build_settings(model_name, **model_kwargs)
        super().__init__(api_key=api_key, settings=settings)

    def _invoke(self, request: LLMRequest) -> LLMResponse:
        if genai is None:
            raise ProviderError("google-generativeai is not installed. Install with the 'google' extra")

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.settings.model_name)
        try:
            response = model.generate_content(
                request.prompt,
                **self.settings.additional_params,
            )
        except Exception as exc:  # noqa: BLE001 - map to domain exceptions
            raise self._map_exception(exc) from exc

        text = self._extract_text(response)
        tokens = self._extract_total_tokens(response)
        raw_payload = response.to_dict() if hasattr(response, "to_dict") else {"response": response}
        return LLMResponse(text=text, raw=raw_payload, tokens_used=tokens)

    @staticmethod
    def _extract_text(response: Any) -> str:
        if hasattr(response, "text") and response.text:
            return response.text
        candidates: Iterable[Any] = getattr(response, "candidates", []) or []
        for cand in candidates:
            parts = getattr(cand, "content", None)
            if parts and hasattr(parts, "parts"):
                text_chunks = [getattr(part, "text", "") for part in parts.parts]
                text = "".join(chunk for chunk in text_chunks if chunk)
                if text:
                    return text
        return ""

    @staticmethod
    def _extract_total_tokens(response: Any) -> int | None:
        usage = getattr(response, "usage_metadata", None)
        if usage is None:
            return None
        return getattr(usage, "total_token_count", None)

    @staticmethod
    def _map_exception(exc: Exception) -> Exception:
        exc_name = exc.__class__.__name__
        message = str(exc)
        if exc_name in _RATE_LIMIT_EXCEPTION_NAMES:
            retry_after = getattr(exc, "retry_after", None)
            retry_seconds = None
            if retry_after is not None:
                try:
                    retry_seconds = float(retry_after)
                except (TypeError, ValueError):  # pragma: no cover - defensive
                    retry_seconds = None
            return RateLimitExceeded(message, retry_after_seconds=retry_seconds)
        if exc_name in _TRANSIENT_EXCEPTION_NAMES:
            return TransientProviderError(message)
        return ProviderError(message)


def google_provider_factory(model_name: str, **model_kwargs: Any) -> Callable[[str], GoogleLLMProvider]:
    """Build a provider factory bound to a specific Google model."""

    def factory(api_key: str) -> GoogleLLMProvider:
        return GoogleLLMProvider(api_key=api_key, model_name=model_name, **model_kwargs)

    return factory

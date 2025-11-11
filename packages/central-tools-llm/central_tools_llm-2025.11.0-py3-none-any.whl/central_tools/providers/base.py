"""Base classes for provider integrations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict

from ..exceptions import ProviderError, RateLimitExceeded, TransientProviderError
from ..models import LLMRequest, LLMResponse


@dataclass(slots=True)
class ProviderSettings:
    """Common configuration for providers."""

    model_name: str
    additional_params: Dict[str, Any]


class BaseLLMProvider(ABC):
    """Base provider adapter handling request normalization and error surfacing."""

    provider_id: str

    def __init__(self, api_key: str, settings: ProviderSettings) -> None:
        self.api_key = api_key
        self.settings = settings

    def generate(self, request: LLMRequest) -> LLMResponse:
        try:
            return self._invoke(request)
        except RateLimitExceeded:
            raise
        except TransientProviderError:
            raise
        except ProviderError:
            raise
        except Exception as exc:  # noqa: BLE001 - wrap unexpected provider errors
            raise ProviderError(str(exc)) from exc

    @abstractmethod
    def _invoke(self, request: LLMRequest) -> LLMResponse:
        """Execute the provider specific API call."""

    @staticmethod
    def _build_settings(model_name: str, **additional: Any) -> ProviderSettings:
        return ProviderSettings(model_name=model_name, additional_params=additional)

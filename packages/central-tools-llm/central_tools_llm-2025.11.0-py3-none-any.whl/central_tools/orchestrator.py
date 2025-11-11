"""Coordinator that stitches routing, retries, and API key cycling."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable, Protocol

from .cycling.api_cycler import APIKeyCycler
from .exceptions import NoAvailableAPIKey, ProviderError, RateLimitExceeded, RoutingError, TransientProviderError
from .models import LLMRequest, LLMResponse
from .retry.strategies import RetryStrategy
from .routing.router import LLMRouter
from .model_limits import rules_for as model_rules_for
from .estimators import estimate_request_tokens

logger = logging.getLogger(__name__)


class ProviderFactory(Protocol):
    """Callable that produces a provider instance when given an API key."""

    def __call__(self, api_key: str, **kwargs) -> "ModelProvider":
        ...


class ModelProvider(Protocol):
    """Common interface for provider adapters."""

    provider_id: str

    def generate(self, request: LLMRequest) -> LLMResponse:
        ...


@dataclass(slots=True)
class LLMOrchestrator:
    """High-level entry point for generating responses via routed LLM calls."""

    router: LLMRouter
    retry_strategy: RetryStrategy
    api_cycler: APIKeyCycler

    def generate(self, request: LLMRequest) -> LLMResponse:
        """Route the request and execute with retries and API key cycling."""

        def operation() -> LLMResponse:
            route = self.router.select(request)
            logger.debug("Routing decision", extra={"route": route})

            expected_tokens = estimate_request_tokens(request)

            # Try to use model-specific limits when selecting a key to avoid choosing a key
            # that is already saturated for this model's constraints.
            model_rules = model_rules_for(route.model_name)
            api_state = self.api_cycler.get_next_key_for_model(
                route.provider_id,
                model_name=route.model_name,
                model_rules=model_rules,
                expected_tokens=expected_tokens,
            )
            logger.debug(
                "Selected API key",
                extra={"provider_id": route.provider_id, "key_id": api_state.identifier},
            )

            provider = route.provider_factory(api_state.secret)

            try:
                response = provider.generate(request)
            except RateLimitExceeded as exc:
                self.api_cycler.report_rate_limit(route.provider_id, api_state.identifier, route.model_name, exc)
                logger.info(
                    "Provider rate limit encountered",
                    extra={"provider_id": route.provider_id, "key_id": api_state.identifier},
                )
                raise TransientProviderError("Rate limited, retrying with a different key") from exc
            except TransientProviderError:
                self.api_cycler.mark_transient_failure(route.provider_id, api_state.identifier, route.model_name)
                raise
            except ProviderError:
                self.api_cycler.mark_failure(route.provider_id, api_state.identifier, route.model_name)
                raise
            else:
                self.api_cycler.report_success(route.provider_id, api_state.identifier, route.model_name, response)
                return response

        try:
            return self.retry_strategy.execute(operation)
        except NoAvailableAPIKey as exc:
            logger.error("No API keys available for request", extra={"request": request})
            raise
        except RoutingError as exc:
            logger.error("Routing failed", extra={"request": request})
            raise

    def warm_up(self, factory_loader: Callable[[str], ProviderFactory]) -> None:
        """Allow pre-loading provider clients for all registered routes."""
        for route in self.router.iter_routes():
            key_state = self.api_cycler.peek_next_key(route.provider_id)
            if not key_state:
                continue
            provider_factory = factory_loader(route.provider_id)
            try:
                provider_factory(key_state.secret)
            except Exception as exc:  # noqa: BLE001 - warm-up failures should not break runtime
                logger.warning(
                    "Warm-up failed",
                    extra={"provider_id": route.provider_id, "key_id": key_state.identifier, "error": str(exc)},
                )

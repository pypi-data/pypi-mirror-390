"""Routing utilities for matching requests to LLM providers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List

from ..exceptions import RoutingError
from ..models import LLMRequest, ModelRoute, TaskDepth


ProviderFactoryType = Callable[[str], object]


@dataclass(slots=True, frozen=True)
class RegisteredModel:
    """Metadata about a routed model."""

    provider_id: str
    model_name: str
    depth: TaskDepth
    priority: int
    provider_factory: ProviderFactoryType
    metadata: Dict[str, object] = field(default_factory=dict)


class LLMRouter:
    """Routes requests to providers based on depth and optional metadata."""

    def __init__(self) -> None:
        self._routes: Dict[TaskDepth, List[RegisteredModel]] = {}

    def register_model(
        self,
        *,
        depth: TaskDepth,
        provider_id: str,
        model_name: str,
        provider_factory: ProviderFactoryType,
        priority: int = 0,
        metadata: Dict[str, object] | None = None,
    ) -> None:
        """Register a model for routing."""

        model = RegisteredModel(
            provider_id=provider_id,
            model_name=model_name,
            depth=depth,
            priority=priority,
            provider_factory=provider_factory,
            metadata=metadata or {},
        )
        self._routes.setdefault(depth, []).append(model)
        self._routes[depth].sort(key=lambda item: item.priority, reverse=True)

    def select(self, request: LLMRequest) -> ModelRoute:
        """Choose a model route given the request's depth."""

        depth_order = self._depth_preference_order(request.depth)
        for depth in depth_order:
            if depth not in self._routes:
                continue
            model = self._pick_model(self._routes[depth], request)
            if model:
                return ModelRoute(
                    provider_id=model.provider_id,
                    model_name=model.model_name,
                    depth=model.depth,
                    provider_factory=model.provider_factory,
                    metadata=model.metadata,
                )
        raise RoutingError(f"No model registered for depth {request.depth!r}")

    def iter_routes(self) -> Iterable[ModelRoute]:
        """Yield all registered routes in priority order."""

        for registered in self._sorted_models():
            yield ModelRoute(
                provider_id=registered.provider_id,
                model_name=registered.model_name,
                depth=registered.depth,
                provider_factory=registered.provider_factory,
                metadata=registered.metadata,
            )

    def _sorted_models(self) -> List[RegisteredModel]:
        models: List[RegisteredModel] = []
        for depth_models in self._routes.values():
            models.extend(depth_models)
        return sorted(models, key=lambda item: (item.depth.value, -item.priority))

    @staticmethod
    def _depth_preference_order(request_depth: TaskDepth) -> Iterable[TaskDepth]:
        ordered = sorted(TaskDepth, key=lambda depth: depth.value)
        target_index = ordered.index(request_depth)
        yield ordered[target_index]
        # Explore deeper models first if available, then lighter ones.
        for depth in ordered[target_index + 1 :]:
            yield depth
        for depth in reversed(ordered[:target_index]):
            yield depth

    def _pick_model(self, models: List[RegisteredModel], request: LLMRequest) -> RegisteredModel | None:
        for model in models:
            if self._metadata_matches(model, request):
                return model
        return None

    @staticmethod
    def _metadata_matches(model: RegisteredModel, request: LLMRequest) -> bool:
        for key, value in model.metadata.items():
            if request.metadata.get(key) != value:
                return False
        return True

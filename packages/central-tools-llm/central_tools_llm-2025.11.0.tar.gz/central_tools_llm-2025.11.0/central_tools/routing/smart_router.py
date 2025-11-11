"""Smart router that prefers models matching token needs and lower cost.

This router composes the basic `LLMRouter` and augments selection by:
- honoring task depth preference
- filtering models that cannot satisfy the request's token estimate
- ranking by a simple `cost_score` (lower is cheaper)

The router returns the same `ModelRoute` objects as `LLMRouter` for compatibility.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

from ..model_limits import meta_for
from ..models import LLMRequest, ModelRoute, TaskDepth
from .router import LLMRouter, RegisteredModel


@dataclass(slots=True)
class SmartRouter:
    base: LLMRouter

    def select(self, request: LLMRequest) -> ModelRoute:
        # collect candidates in depth preference order
        depth_order = self.base._depth_preference_order(request.depth)
        token_est = int(request.metadata.get("tokens_estimate", 32))

        for depth in depth_order:
            models = self.base._routes.get(depth, [])
            # filter candidates by token limits
            candidates: List[RegisteredModel] = []
            for m in models:
                meta = meta_for(m.model_name)
                out_limit = meta.get("output_tokens")
                in_limit = meta.get("input_tokens")
                if out_limit is not None and token_est > out_limit:
                    # can't satisfy output token requirement
                    continue
                if in_limit is not None and token_est > in_limit:
                    # request too large for input window
                    continue
                candidates.append(m)

            if not candidates:
                continue

            # rank by cost_score if present, then priority
            def score(m: RegisteredModel) -> float:
                meta = meta_for(m.model_name)
                cost = meta.get("cost_score") or 100.0
                return float(cost) - (m.priority * 0.01)

            best = sorted(candidates, key=score)[0]
            return ModelRoute(
                provider_id=best.provider_id,
                model_name=best.model_name,
                depth=best.depth,
                provider_factory=best.provider_factory,
                metadata=best.metadata,
            )

        raise RuntimeError(f"No model available for depth {request.depth}")

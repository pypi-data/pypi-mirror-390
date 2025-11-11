"""Shared data contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Mapping, MutableMapping, Optional


class TaskDepth(Enum):
    """Represents how deep an answer needs to go."""

    LITE = 1
    STANDARD = 2
    DEEP = 3
    EXPANSIVE = 4


@dataclass(slots=True)
class LLMRequest:
    """Normalized request shared across providers."""

    prompt: str
    depth: TaskDepth = TaskDepth.STANDARD
    metadata: MutableMapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class LLMResponse:
    """Normalized response from providers."""

    text: str
    raw: Mapping[str, Any]
    tokens_used: Optional[int] = None
    latency_ms: Optional[int] = None


@dataclass(slots=True)
class ModelRoute:
    """Mapping between routing decision and provider resolution."""

    provider_id: str
    model_name: str
    depth: TaskDepth
    provider_factory: Callable[[str], Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

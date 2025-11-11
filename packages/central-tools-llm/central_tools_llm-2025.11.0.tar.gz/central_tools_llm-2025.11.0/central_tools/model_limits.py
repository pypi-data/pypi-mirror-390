"""Model-specific rate limit definitions.

This module encodes the published RPM/TPM/RPD limits per model and exposes a
helper to convert them into `RateLimitRule` objects used by the cycler.
"""

from __future__ import annotations

from typing import Dict, List, Optional, TypedDict

from .cycling.api_cycler import RateLimitRule


# Table: Model -> (RPM, TPM, RPD)
class ModelMeta(TypedDict, total=False):
    rpm: Optional[int]
    tpm: Optional[int]
    rpd: Optional[int]
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    cost_score: Optional[float]


_RAW: Dict[str, ModelMeta] = {
    # Text-out models
    "gemini-2.5-pro": {"rpm": 2, "tpm": 125_000, "rpd": 50, "input_tokens": 1_048_576, "output_tokens": 65_536, "cost_score": 5.0},
    "gemini-2.5-flash": {"rpm": 10, "tpm": 250_000, "rpd": 250, "input_tokens": 1_048_576, "output_tokens": 65_536, "cost_score": 2.0},
    "gemini-2.5-flash-preview": {"rpm": 10, "tpm": 250_000, "rpd": 250, "input_tokens": 1_048_576, "output_tokens": 65_536, "cost_score": 2.5},
    "gemini-2.5-flash-lite": {"rpm": 15, "tpm": 250_000, "rpd": 1_000, "input_tokens": 1_048_576, "output_tokens": 65_536, "cost_score": 1.0},
    "gemini-2.5-flash-lite-preview": {"rpm": 15, "tpm": 250_000, "rpd": 1_000, "input_tokens": 1_048_576, "output_tokens": 65_536, "cost_score": 1.2},
    "gemini-2.0-flash": {"rpm": 15, "tpm": 1_000_000, "rpd": 200, "input_tokens": 1_048_576, "output_tokens": 8_192, "cost_score": 3.0},
    "gemini-2.0-flash-lite": {"rpm": 30, "tpm": 1_000_000, "rpd": 200, "input_tokens": 1_048_576, "output_tokens": 8_192, "cost_score": 1.5},
    # Live API (use None for unbounded or provider-controlled values)
    "gemini-2.5-flash-live": {"rpm": None, "tpm": 1_000_000, "rpd": None, "input_tokens": 128_000, "output_tokens": 8_000, "cost_score": 4.0},
    "gemini-2.5-flash-preview-native-audio": {"rpm": None, "tpm": 500_000, "rpd": None, "input_tokens": 128_000, "output_tokens": 8_000, "cost_score": 6.0},
    "gemini-2.0-flash-live": {"rpm": None, "tpm": 1_000_000, "rpd": None, "input_tokens": 1_048_576, "output_tokens": 8_192, "cost_score": 3.5},
    # Multi-modal generation
    "gemini-2.5-flash-preview-tts": {"rpm": 3, "tpm": 10_000, "rpd": 15, "input_tokens": 8_000, "output_tokens": 16_000, "cost_score": 4.5},
    "gemini-2.0-flash-preview-image-generation": {"rpm": 10, "tpm": 200_000, "rpd": 100, "input_tokens": 32_000, "output_tokens": 32_000, "cost_score": 5.0},
    # Other
    "gemma-3": {"rpm": 30, "tpm": 15_000, "rpd": 14_400, "input_tokens": 32_000, "output_tokens": 32_000, "cost_score": 2.5},
    "gemma-3n": {"rpm": 30, "tpm": 15_000, "rpd": 14_400, "input_tokens": 32_000, "output_tokens": 32_000, "cost_score": 2.7},
    "gemini-embedding": {"rpm": 100, "tpm": 30_000, "rpd": 1_000, "input_tokens": 1_000_000, "output_tokens": 1_000, "cost_score": 0.5},
    "gemini-robotics-er-1.5-preview": {"rpm": 10, "tpm": 250_000, "rpd": 250, "input_tokens": 1_048_576, "output_tokens": 65_536, "cost_score": 6.0},
}


def rules_for(model_name: str) -> List[RateLimitRule]:
    """Return a list of RateLimitRule objects for the given model.

    The rule names match what the cycler uses for keys: `per_minute`,
    `tokens_per_minute`, and `per_day`.
    """

    meta = _RAW.get(model_name, {})
    rules: List[RateLimitRule] = []
    rpm = meta.get("rpm")
    tpm = meta.get("tpm")
    rpd = meta.get("rpd")
    if rpm is not None:
        rules.append(RateLimitRule(name="per_minute", period_seconds=60, max_calls=rpm))
    if tpm is not None:
        rules.append(RateLimitRule(name="tokens_per_minute", period_seconds=60, max_tokens=tpm))
    if rpd is not None:
        rules.append(RateLimitRule(name="per_day", period_seconds=24 * 3600, max_calls=rpd))
    return rules


def all_models() -> List[str]:
    return list(_RAW.keys())


def meta_for(model_name: str) -> ModelMeta:
    """Return the metadata dict for a model (rpm/tpm/rpd and token limits)."""

    return _RAW.get(model_name, {})

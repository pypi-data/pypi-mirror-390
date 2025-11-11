"""Lightweight token estimation helpers."""

from __future__ import annotations

from .models import LLMRequest


def estimate_text_tokens(text: str) -> int:
    """Rough heuristic: assume 4 characters per token, at least len(words)."""

    if not text:
        return 0
    char_based = len(text) // 4
    word_based = len(text.split())
    return max(char_based, word_based, 1)


def estimate_request_tokens(request: LLMRequest, default: int = 32) -> int:
    """Estimate tokens for a request if not provided in metadata."""

    metadata = request.metadata
    if metadata and "tokens_estimate" in metadata:
        try:
            return max(int(metadata["tokens_estimate"]), 1)
        except (TypeError, ValueError):
            pass
    prompt_tokens = estimate_text_tokens(request.prompt)
    estimate = max(prompt_tokens, default)
    if metadata is not None:
        metadata.setdefault("tokens_estimate", estimate)
    return estimate

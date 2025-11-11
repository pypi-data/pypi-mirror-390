"""Standardized placeholders for environment-based API key configuration."""

from __future__ import annotations

from typing import List

from .config import ApiKeyPlaceholder

GOOGLE_API_KEY_PLACEHOLDERS: List[ApiKeyPlaceholder] = [
    ApiKeyPlaceholder(provider_id="google", identifier="1", env_name="GOOGLE_API_KEY_1"),
    ApiKeyPlaceholder(provider_id="google", identifier="2", env_name="GOOGLE_API_KEY_2"),
    ApiKeyPlaceholder(provider_id="google", identifier="3", env_name="GOOGLE_API_KEY_3"),
    ApiKeyPlaceholder(provider_id="google", identifier="4", env_name="GOOGLE_API_KEY_4"),
    ApiKeyPlaceholder(provider_id="google", identifier="5", env_name="GOOGLE_API_KEY_5"),
]

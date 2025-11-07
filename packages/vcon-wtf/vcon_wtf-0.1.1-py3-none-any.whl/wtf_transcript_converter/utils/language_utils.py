"""
Language utility functions for WTF transcript converter.

This module provides utilities for language code validation and normalization.
"""

import re


def is_valid_bcp47(language_code: str) -> bool:
    """
    Validate BCP-47 language code format.

    Args:
        language_code: Language code to validate

    Returns:
        True if valid BCP-47 format
    """
    # Basic BCP-47 validation pattern
    # This is a simplified version - full BCP-47 is more complex
    pattern = r"^[a-z]{2,3}(-[A-Z]{2})?(-[a-z0-9]{5,8})?(-[a-z0-9]{1,8})*(-[a-z0-9]{1,8})*(-[a-z0-9]{1,8})*$"
    return bool(re.match(pattern, language_code.lower()))


def normalize_language_code(language_code: str) -> str:
    """
    Normalize language code to standard format.

    Args:
        language_code: Language code to normalize

    Returns:
        Normalized language code
    """
    # Convert to lowercase and handle common variations
    normalized = language_code.lower()

    # Handle underscore format (en_us -> en-US)
    normalized = normalized.replace("_", "-")

    # Handle full language names
    full_names = {
        "english": "en-US",
        "spanish": "es-ES",
        "french": "fr-FR",
        "german": "de-DE",
        "italian": "it-IT",
        "portuguese": "pt-BR",
        "chinese": "zh-CN",
        "japanese": "ja-JP",
        "korean": "ko-KR",
        "russian": "ru-RU",
    }
    if normalized in full_names:
        return full_names[normalized]

    # Handle common variations
    variations = {
        "en": "en-US",
        "es": "es-ES",
        "fr": "fr-FR",
        "de": "de-DE",
        "it": "it-IT",
        "pt": "pt-BR",
        "zh": "zh-CN",
        "ja": "ja-JP",
        "ko": "ko-KR",
        "ru": "ru-RU",
    }

    return variations.get(normalized, normalized)

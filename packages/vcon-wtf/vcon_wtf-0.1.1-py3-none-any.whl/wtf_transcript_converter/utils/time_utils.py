"""
Time utility functions for WTF transcript converter.

This module provides utilities for timestamp conversion and validation.
"""

from typing import Union


def convert_timestamp(timestamp: Union[float, int, str]) -> float:
    """
    Convert various timestamp formats to floating-point seconds.

    Args:
        timestamp: Timestamp in various formats

    Returns:
        Timestamp as floating-point seconds
    """
    if isinstance(timestamp, (int, float)):
        return float(timestamp)
    elif isinstance(timestamp, str):
        # TODO: Implement string timestamp parsing
        return 0.0
    else:
        raise ValueError(f"Unsupported timestamp type: {type(timestamp)}")


def validate_timing(start: float, end: float) -> bool:
    """
    Validate that timing is consistent (end > start).

    Args:
        start: Start time in seconds
        end: End time in seconds

    Returns:
        True if timing is valid
    """
    return end > start and start >= 0


from datetime import datetime, timezone


def get_current_iso_timestamp() -> str:
    """
    Get current UTC timestamp in ISO 8601 format.

    Returns:
        ISO 8601 timestamp string
    """
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

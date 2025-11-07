"""
Confidence score utility functions for WTF transcript converter.

This module provides utilities for confidence score normalization and quality metrics.
"""

from typing import Any, Dict, List


def normalize_confidence(confidence: float, provider: str) -> float:
    """
    Normalize confidence scores to [0.0, 1.0] range based on provider.

    Args:
        confidence: Raw confidence score
        provider: Provider name

    Returns:
        Normalized confidence score [0.0, 1.0]
    """
    # TODO: Implement provider-specific normalization
    # For now, assume input is already in [0.0, 1.0] range
    return max(0.0, min(1.0, confidence))


def calculate_quality_metrics(confidences: List[float]) -> Dict[str, Any]:
    """
    Calculate quality metrics from confidence scores.

    Args:
        confidences: List of confidence scores

    Returns:
        Dictionary of quality metrics
    """
    if not confidences:
        return {}

    avg_confidence = sum(confidences) / len(confidences)
    low_confidence_count = sum(1 for c in confidences if c < 0.5)

    return {
        "average_confidence": avg_confidence,
        "low_confidence_words": low_confidence_count,
        "total_words": len(confidences),
    }

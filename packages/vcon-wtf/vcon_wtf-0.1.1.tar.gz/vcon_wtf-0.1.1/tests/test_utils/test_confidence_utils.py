"""Tests for confidence utilities."""

from wtf_transcript_converter.utils.confidence_utils import (
    calculate_quality_metrics,
    normalize_confidence,
)


class TestConfidenceUtils:
    """Test confidence utility functions."""

    def test_normalize_confidence_standard_range(self):
        """Test normalizing confidence in standard 0-1 range."""
        assert normalize_confidence(0.5, "whisper") == 0.5
        assert normalize_confidence(0.0, "whisper") == 0.0
        assert normalize_confidence(1.0, "whisper") == 1.0

    def test_normalize_confidence_negative_range(self):
        """Test normalizing confidence in negative range."""
        assert normalize_confidence(-1.0, "whisper") == 0.0
        assert normalize_confidence(-0.5, "whisper") == 0.0
        assert normalize_confidence(-0.1, "whisper") == 0.0

    def test_normalize_confidence_above_one(self):
        """Test normalizing confidence above 1.0."""
        assert normalize_confidence(1.5, "whisper") == 1.0
        assert normalize_confidence(2.0, "whisper") == 1.0

    def test_normalize_confidence_different_providers(self):
        """Test normalizing confidence with different providers."""
        assert normalize_confidence(0.5, "whisper") == 0.5
        assert normalize_confidence(0.5, "deepgram") == 0.5
        assert normalize_confidence(0.5, "assemblyai") == 0.5

    def test_calculate_quality_metrics_empty_list(self):
        """Test calculating quality metrics with empty list."""
        result = calculate_quality_metrics([])
        assert result == {}

    def test_calculate_quality_metrics_single_value(self):
        """Test calculating quality metrics with single value."""
        result = calculate_quality_metrics([0.8])
        assert result["average_confidence"] == 0.8
        assert result["low_confidence_words"] == 0
        assert result["total_words"] == 1

    def test_calculate_quality_metrics_multiple_values(self):
        """Test calculating quality metrics with multiple values."""
        confidences = [0.8, 0.9, 0.3, 0.6]  # One low confidence (< 0.5)
        result = calculate_quality_metrics(confidences)

        expected_avg = sum(confidences) / len(confidences)
        assert result["average_confidence"] == expected_avg
        assert result["low_confidence_words"] == 1  # 0.3 < 0.5
        assert result["total_words"] == 4

    def test_calculate_quality_metrics_all_low_confidence(self):
        """Test calculating quality metrics with all low confidence."""
        confidences = [0.3, 0.4, 0.2]
        result = calculate_quality_metrics(confidences)

        assert result["low_confidence_words"] == 3
        assert result["total_words"] == 3

    def test_calculate_quality_metrics_all_high_confidence(self):
        """Test calculating quality metrics with all high confidence."""
        confidences = [0.8, 0.9, 0.7]
        result = calculate_quality_metrics(confidences)

        assert result["low_confidence_words"] == 0
        assert result["total_words"] == 3

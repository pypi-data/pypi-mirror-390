"""Integration tests for cross-provider quality testing."""

import json
from pathlib import Path

import pytest

from wtf_transcript_converter.cross_provider.quality import QualityComparator


class TestQualityComparatorIntegration:
    """Integration tests for quality comparison."""

    def setup_method(self):
        """Set up test fixtures."""
        self.comparator = QualityComparator()

    def test_quality_comparator_initialization(self):
        """Test quality comparator initialization."""
        assert self.comparator is not None
        assert hasattr(self.comparator, "analyze_quality")
        assert hasattr(self.comparator, "compare_quality_across_providers")
        assert hasattr(self.comparator, "analyze_quality_comparison")
        assert hasattr(self.comparator, "generate_quality_report")

    def test_analyze_quality_with_whisper_data(self):
        """Test quality analysis with Whisper data."""
        # Load sample Whisper data
        sample_file = Path(__file__).parent.parent / "fixtures" / "whisper_sample.json"
        if not sample_file.exists():
            pytest.skip("Sample Whisper file not found")

        with open(sample_file) as f:
            sample_data = json.load(f)

        # Analyze quality
        result = self.comparator.analyze_quality("whisper", sample_data)

        assert hasattr(result, "provider")
        assert result.provider == "whisper"
        assert hasattr(result, "overall_confidence")
        assert hasattr(result, "text_completeness")
        assert hasattr(result, "punctuation_accuracy")
        assert isinstance(result.overall_confidence, (int, float))
        assert isinstance(result.text_completeness, (int, float))
        assert isinstance(result.punctuation_accuracy, (int, float))

    def test_analyze_quality_with_empty_data(self):
        """Test quality analysis with empty data."""
        empty_data = {}

        result = self.comparator.analyze_quality("whisper", empty_data)

        assert hasattr(result, "provider")
        assert result.provider == "whisper"
        # Should have quality metrics even with empty data
        assert hasattr(result, "overall_confidence")
        assert hasattr(result, "text_completeness")
        assert hasattr(result, "punctuation_accuracy")

    def test_analyze_quality_with_minimal_data(self):
        """Test quality analysis with minimal data."""
        minimal_data = {
            "text": "Hello world",
            "segments": [{"start": 0.0, "end": 1.0, "text": "Hello world"}],
        }

        result = self.comparator.analyze_quality("whisper", minimal_data)

        assert hasattr(result, "provider")
        assert hasattr(result, "overall_confidence")
        assert hasattr(result, "text_completeness")
        assert hasattr(result, "punctuation_accuracy")

    def test_compare_quality_across_providers(self):
        """Test quality comparison across providers."""
        # Load sample data
        sample_file = Path(__file__).parent.parent / "fixtures" / "whisper_sample.json"
        if not sample_file.exists():
            pytest.skip("Sample Whisper file not found")

        with open(sample_file) as f:
            sample_data = json.load(f)

        # Compare quality across providers
        results = self.comparator.compare_quality_across_providers(sample_data)

        assert isinstance(results, list)
        assert len(results) > 0

        # Check that we have results for multiple providers
        expected_providers = ["whisper", "deepgram", "assemblyai", "rev_ai"]
        providers_found = [r.provider for r in results]
        for provider in expected_providers:
            if provider in providers_found:
                result = next(r for r in results if r.provider == provider)
                assert hasattr(result, "overall_confidence")
                assert hasattr(result, "text_completeness")
                assert hasattr(result, "punctuation_accuracy")

    def test_analyze_quality_comparison(self):
        """Test quality comparison analysis."""
        # Create mock quality results as QualityMetrics objects
        from wtf_transcript_converter.cross_provider.quality import QualityMetrics

        quality_results = [
            QualityMetrics(
                provider="whisper",
                overall_confidence=0.9,
                word_count=10,
                segment_count=1,
                duration=1.0,
                avg_word_confidence=0.9,
                min_word_confidence=0.8,
                max_word_confidence=1.0,
                low_confidence_words=0,
                punctuation_accuracy=0.85,
                text_completeness=1.0,
                timing_accuracy=0.9,
                success=True,
                error_message="",
            ),
            QualityMetrics(
                provider="deepgram",
                overall_confidence=0.88,
                word_count=10,
                segment_count=1,
                duration=1.0,
                avg_word_confidence=0.88,
                min_word_confidence=0.7,
                max_word_confidence=1.0,
                low_confidence_words=1,
                punctuation_accuracy=0.82,
                text_completeness=0.98,
                timing_accuracy=0.85,
                success=True,
                error_message="",
            ),
        ]

        analysis = self.comparator.analyze_quality_comparison(quality_results)

        assert isinstance(analysis, dict)
        assert "status" in analysis
        assert "averages" in analysis
        assert "best_performers" in analysis
        assert "provider_details" in analysis

        # Check that analysis makes sense
        assert analysis["status"] == "success"
        assert "whisper" in analysis["provider_details"]
        assert "deepgram" in analysis["provider_details"]

        # Check averages structure
        averages = analysis["averages"]
        assert "overall_confidence" in averages
        assert "punctuation_accuracy" in averages
        assert "text_completeness" in averages

    def test_generate_quality_report(self):
        """Test quality report generation."""
        # Create mock quality results as QualityMetrics objects
        from wtf_transcript_converter.cross_provider.quality import QualityMetrics

        quality_results = [
            QualityMetrics(
                provider="whisper",
                overall_confidence=0.9,
                word_count=10,
                segment_count=1,
                duration=1.0,
                avg_word_confidence=0.9,
                min_word_confidence=0.8,
                max_word_confidence=1.0,
                low_confidence_words=0,
                punctuation_accuracy=0.85,
                text_completeness=1.0,
                timing_accuracy=0.9,
                success=True,
                error_message="",
            ),
            QualityMetrics(
                provider="deepgram",
                overall_confidence=0.88,
                word_count=10,
                segment_count=1,
                duration=1.0,
                avg_word_confidence=0.88,
                min_word_confidence=0.7,
                max_word_confidence=1.0,
                low_confidence_words=1,
                punctuation_accuracy=0.82,
                text_completeness=0.98,
                timing_accuracy=0.85,
                success=True,
                error_message="",
            ),
        ]

        report = self.comparator.generate_quality_report(quality_results)

        assert isinstance(report, str)
        assert len(report) > 0
        assert "Quality Report" in report or "quality" in report.lower()

    def test_quality_metrics_accuracy(self):
        """Test that quality metrics are reasonable."""
        sample_data = {
            "text": "Hello world!",
            "segments": [
                {
                    "start": 0.0,
                    "end": 1.0,
                    "text": "Hello world!",
                    "words": [
                        {"start": 0.0, "end": 0.5, "text": "Hello"},
                        {"start": 0.5, "end": 1.0, "text": "world!"},
                    ],
                }
            ],
        }

        result = self.comparator.analyze_quality("whisper", sample_data)

        # Check that metrics are reasonable (0-1 range)
        assert 0.0 <= result.overall_confidence <= 1.0
        assert 0.0 <= result.text_completeness <= 1.0
        assert 0.0 <= result.punctuation_accuracy <= 1.0

    def test_quality_analysis_with_punctuation(self):
        """Test quality analysis with punctuation."""
        data_with_punctuation = {
            "text": "Hello, world! How are you?",
            "segments": [
                {
                    "start": 0.0,
                    "end": 2.0,
                    "text": "Hello, world! How are you?",
                    "words": [
                        {"start": 0.0, "end": 0.5, "text": "Hello,"},
                        {"start": 0.5, "end": 1.0, "text": "world!"},
                        {"start": 1.0, "end": 1.5, "text": "How"},
                        {"start": 1.5, "end": 2.0, "text": "are"},
                        {"start": 2.0, "end": 2.5, "text": "you?"},
                    ],
                }
            ],
        }

        result = self.comparator.analyze_quality("whisper", data_with_punctuation)

        assert hasattr(result, "punctuation_accuracy")
        assert isinstance(result.punctuation_accuracy, (int, float))
        assert 0.0 <= result.punctuation_accuracy <= 1.0

    def test_quality_analysis_with_confidence_scores(self):
        """Test quality analysis with confidence scores."""
        data_with_confidence = {
            "text": "Hello world",
            "segments": [
                {
                    "start": 0.0,
                    "end": 1.0,
                    "text": "Hello world",
                    "words": [
                        {"start": 0.0, "end": 0.5, "text": "Hello", "confidence": 0.9},
                        {"start": 0.5, "end": 1.0, "text": "world", "confidence": 0.8},
                    ],
                }
            ],
        }

        result = self.comparator.analyze_quality("whisper", data_with_confidence)

        assert hasattr(result, "overall_confidence")
        assert isinstance(result.overall_confidence, (int, float))
        assert 0.0 <= result.overall_confidence <= 1.0

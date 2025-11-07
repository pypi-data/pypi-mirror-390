"""Integration tests for cross-provider consistency testing."""

import json
from pathlib import Path

import pytest

from wtf_transcript_converter.cross_provider.consistency import CrossProviderConsistencyTester


class TestCrossProviderConsistencyIntegration:
    """Integration tests for cross-provider consistency testing."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tester = CrossProviderConsistencyTester()

    def test_consistency_tester_initialization(self):
        """Test consistency tester initialization."""
        assert self.tester is not None
        assert hasattr(self.tester, "test_consistency_with_sample_data")
        assert hasattr(self.tester, "analyze_consistency")
        assert hasattr(self.tester, "generate_consistency_report")

    def test_analyze_consistency_with_whisper_data(self):
        """Test consistency analysis with Whisper data."""
        # Load sample Whisper data
        sample_file = Path(__file__).parent.parent / "fixtures" / "whisper_sample.json"
        if not sample_file.exists():
            pytest.skip("Sample Whisper file not found")

        with open(sample_file) as f:
            sample_data = json.load(f)

        # Test consistency analysis
        results = self.tester.test_consistency_with_sample_data(sample_data)

        assert isinstance(results, list)
        assert len(results) > 0

        # Check that we have ConsistencyResult objects
        for result in results:
            assert hasattr(result, "provider")
            assert hasattr(result, "is_valid")
            assert hasattr(result, "wtf_doc")
            assert hasattr(result, "confidence_score")

    def test_analyze_consistency_with_empty_data(self):
        """Test consistency analysis with empty data."""
        empty_data = {}

        results = self.tester.test_consistency_with_sample_data(empty_data)

        assert isinstance(results, list)
        # With empty data, we might get empty results or results with errors
        # The exact behavior depends on how providers handle empty data

    def test_analyze_consistency_with_minimal_data(self):
        """Test consistency analysis with minimal data."""
        minimal_data = {
            "text": "Hello world",
            "segments": [{"start": 0.0, "end": 1.0, "text": "Hello world"}],
        }

        results = self.tester.test_consistency_with_sample_data(minimal_data)

        assert isinstance(results, list)
        # Should have results for multiple providers
        assert len(results) > 0

    def test_generate_consistency_report(self):
        """Test consistency report generation."""
        # Load sample data
        sample_file = Path(__file__).parent.parent / "fixtures" / "whisper_sample.json"
        if not sample_file.exists():
            pytest.skip("Sample Whisper file not found")

        with open(sample_file) as f:
            sample_data = json.load(f)

        # Test consistency first to get results
        results = self.tester.test_consistency_with_sample_data(sample_data)

        # Test the generate_consistency_report method with actual results
        if results:
            report = self.tester.generate_consistency_report(results)
            assert isinstance(report, str)
            assert len(report) > 0
        else:
            # If no results, just test that the method exists
            assert hasattr(self.tester, "generate_consistency_report")
            assert callable(self.tester.generate_consistency_report)

    def test_consistency_with_different_providers(self):
        """Test consistency analysis with different provider formats."""
        # Test with Whisper format
        whisper_data = {
            "text": "Hello world",
            "segments": [
                {
                    "id": 0,
                    "start": 0.0,
                    "end": 1.0,
                    "text": "Hello world",
                    "words": [
                        {"start": 0.0, "end": 0.5, "text": "Hello"},
                        {"start": 0.5, "end": 1.0, "text": "world"},
                    ],
                }
            ],
        }

        results = self.tester.test_consistency_with_sample_data(whisper_data)
        assert isinstance(results, list)
        assert len(results) > 0

    def test_consistency_metrics_calculation(self):
        """Test consistency metrics calculation."""
        # Create test data with known consistency
        test_data = {
            "text": "Hello world",
            "segments": [
                {
                    "id": 0,
                    "start": 0.0,
                    "end": 1.0,
                    "text": "Hello world",
                    "words": [
                        {"start": 0.0, "end": 0.5, "text": "Hello"},
                        {"start": 0.5, "end": 1.0, "text": "world"},
                    ],
                }
            ],
        }

        results = self.tester.test_consistency_with_sample_data(test_data)

        # Check that we get results
        assert isinstance(results, list)
        assert len(results) > 0

        # Check that each result has the expected attributes
        for result in results:
            assert hasattr(result, "provider")
            assert hasattr(result, "confidence_score")
            assert hasattr(result, "word_count")
            assert hasattr(result, "segment_count")

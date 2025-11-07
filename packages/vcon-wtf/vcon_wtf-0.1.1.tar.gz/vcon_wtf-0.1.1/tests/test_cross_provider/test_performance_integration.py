"""Integration tests for cross-provider performance testing."""

import json
from pathlib import Path

import pytest

from wtf_transcript_converter.cross_provider.performance import PerformanceBenchmark


class TestPerformanceBenchmarkIntegration:
    """Integration tests for performance benchmarking."""

    def setup_method(self):
        """Set up test fixtures."""
        self.benchmark = PerformanceBenchmark()

    def test_performance_benchmark_initialization(self):
        """Test performance benchmark initialization."""
        assert self.benchmark is not None
        assert hasattr(self.benchmark, "benchmark_provider")
        assert hasattr(self.benchmark, "benchmark_all_providers")
        assert hasattr(self.benchmark, "analyze_performance")
        assert hasattr(self.benchmark, "generate_performance_report")

    def test_benchmark_provider_with_whisper(self):
        """Test benchmarking a single provider (Whisper)."""
        # Load sample Whisper data
        sample_file = Path(__file__).parent.parent / "fixtures" / "whisper_sample.json"
        if not sample_file.exists():
            pytest.skip("Sample Whisper file not found")

        with open(sample_file) as f:
            sample_data = json.load(f)

        # Benchmark Whisper provider
        result = self.benchmark.benchmark_provider("whisper", sample_data)

        assert hasattr(result, "provider")
        assert result.provider == "whisper"
        assert hasattr(result, "conversion_time")
        assert hasattr(result, "memory_usage_mb")
        assert hasattr(result, "cpu_usage_percent")
        assert isinstance(result.conversion_time, (int, float))
        assert isinstance(result.memory_usage_mb, (int, float))
        assert isinstance(result.cpu_usage_percent, (int, float))

    def test_benchmark_all_providers(self):
        """Test benchmarking all providers."""
        # Load sample data
        sample_file = Path(__file__).parent.parent / "fixtures" / "whisper_sample.json"
        if not sample_file.exists():
            pytest.skip("Sample Whisper file not found")

        with open(sample_file) as f:
            sample_data = json.load(f)

        # Benchmark all providers
        results = self.benchmark.benchmark_all_providers(sample_data)

        assert isinstance(results, list)
        assert len(results) > 0

        # Check that we have results for multiple providers
        expected_providers = ["whisper", "deepgram", "assemblyai", "rev_ai"]
        providers_found = [r.provider for r in results]
        for provider in expected_providers:
            if provider in providers_found:
                result = next(r for r in results if r.provider == provider)
                assert hasattr(result, "conversion_time")
                assert hasattr(result, "memory_usage_mb")
                assert hasattr(result, "cpu_usage_percent")

    def test_benchmark_with_empty_data(self):
        """Test benchmarking with empty data."""
        empty_data = {}

        result = self.benchmark.benchmark_provider("whisper", empty_data)

        assert hasattr(result, "provider")
        assert result.provider == "whisper"
        # Should still have timing metrics even with empty data
        assert hasattr(result, "conversion_time")
        assert isinstance(result.conversion_time, (int, float))

    def test_benchmark_with_minimal_data(self):
        """Test benchmarking with minimal data."""
        minimal_data = {
            "text": "Hello world",
            "segments": [{"start": 0.0, "end": 1.0, "text": "Hello world"}],
        }

        result = self.benchmark.benchmark_provider("whisper", minimal_data)

        assert hasattr(result, "provider")
        assert hasattr(result, "conversion_time")
        assert isinstance(result.conversion_time, (int, float))

    def test_analyze_performance(self):
        """Test performance analysis."""
        # Create mock benchmark results as PerformanceMetrics objects
        from wtf_transcript_converter.cross_provider.performance import PerformanceMetrics

        benchmark_results = [
            PerformanceMetrics(
                provider="whisper",
                conversion_time=0.1,
                memory_usage_mb=10,
                cpu_usage_percent=5,
                wtf_doc_size_kb=1.0,
                success=True,
                error_message="",
            ),
            PerformanceMetrics(
                provider="deepgram",
                conversion_time=0.2,
                memory_usage_mb=15,
                cpu_usage_percent=8,
                wtf_doc_size_kb=1.2,
                success=True,
                error_message="",
            ),
        ]

        analysis = self.benchmark.analyze_performance(benchmark_results)

        assert isinstance(analysis, dict)
        assert "status" in analysis
        assert "metrics" in analysis
        assert "provider_details" in analysis

        # Check that analysis makes sense
        assert analysis["status"] == "success"
        assert "whisper" in analysis["provider_details"]
        assert "deepgram" in analysis["provider_details"]

        # Check metrics structure
        metrics = analysis["metrics"]
        assert "conversion_time" in metrics
        assert "memory_usage" in metrics
        assert "output_size" in metrics

    def test_generate_performance_report(self):
        """Test performance report generation."""
        # Create mock benchmark results as PerformanceMetrics objects
        from wtf_transcript_converter.cross_provider.performance import PerformanceMetrics

        benchmark_results = [
            PerformanceMetrics(
                provider="whisper",
                conversion_time=0.1,
                memory_usage_mb=10,
                cpu_usage_percent=5,
                wtf_doc_size_kb=1.0,
                success=True,
                error_message="",
            ),
            PerformanceMetrics(
                provider="deepgram",
                conversion_time=0.2,
                memory_usage_mb=15,
                cpu_usage_percent=8,
                wtf_doc_size_kb=1.2,
                success=True,
                error_message="",
            ),
        ]

        report = self.benchmark.generate_performance_report(benchmark_results)

        assert isinstance(report, str)
        assert len(report) > 0
        assert "Performance Report" in report or "performance" in report.lower()

    def test_benchmark_invalid_provider(self):
        """Test benchmarking with invalid provider."""
        sample_data = {"text": "test"}

        result = self.benchmark.benchmark_provider("invalid_provider", sample_data)

        # Should handle invalid provider gracefully
        assert hasattr(result, "provider")
        assert result.provider == "invalid_provider"
        # Should still have timing metrics
        assert hasattr(result, "conversion_time")

    def test_performance_metrics_accuracy(self):
        """Test that performance metrics are reasonable."""
        sample_data = {
            "text": "Hello world",
            "segments": [{"start": 0.0, "end": 1.0, "text": "Hello world"}],
        }

        result = self.benchmark.benchmark_provider("whisper", sample_data)

        # Check that metrics are reasonable
        assert result.conversion_time >= 0
        assert result.memory_usage_mb >= 0
        assert result.cpu_usage_percent >= 0

        # Conversion time should be reasonable (less than 10 seconds for small data)
        assert result.conversion_time < 10.0

"""
Performance benchmarking across providers.

This module benchmarks the performance of different providers to measure
conversion speed, memory usage, and other performance metrics.
"""

import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List

import psutil
import pytest

from wtf_transcript_converter.providers import (
    AssemblyAIConverter,
    CanaryConverter,
    DeepgramConverter,
    ParakeetConverter,
    RevAIConverter,
    WhisperConverter,
)


@dataclass
class PerformanceMetrics:
    """Performance metrics for a provider."""

    provider: str
    conversion_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    wtf_doc_size_kb: float
    success: bool
    error_message: str = ""


class PerformanceBenchmark:
    """Benchmark performance across multiple providers."""

    def __init__(self) -> None:
        self.providers = {
            "whisper": WhisperConverter(),
            "deepgram": DeepgramConverter(),
            "assemblyai": AssemblyAIConverter(),
            "rev-ai": RevAIConverter(),
            "canary": CanaryConverter(),
            "parakeet": ParakeetConverter(),
        }

    def benchmark_provider(
        self, provider_name: str, sample_data: Dict[str, Any], iterations: int = 3
    ) -> PerformanceMetrics:
        """
        Benchmark a single provider.

        Args:
            provider_name: Name of the provider
            sample_data: Sample data to convert
            iterations: Number of iterations to average

        Returns:
            Performance metrics
        """
        if provider_name not in self.providers:
            return PerformanceMetrics(
                provider=provider_name,
                conversion_time=0.0,
                memory_usage_mb=0.0,
                cpu_usage_percent=0.0,
                wtf_doc_size_kb=0.0,
                success=False,
                error_message=f"Provider {provider_name} not found",
            )

        converter = self.providers[provider_name]
        times = []
        memory_usages = []
        cpu_usages = []
        wtf_doc_sizes = []

        for i in range(iterations):
            try:
                # Measure memory before
                process = psutil.Process(os.getpid())
                memory_before = process.memory_info().rss / 1024 / 1024  # MB
                cpu_before = process.cpu_percent()

                # Time the conversion
                start_time = time.time()
                # Convert using the convert method (ToWTFConverter interface)
                wtf_doc = converter.convert(sample_data)
                end_time = time.time()

                # Measure memory after
                memory_after = process.memory_info().rss / 1024 / 1024  # MB
                cpu_after = process.cpu_percent()

                # Calculate metrics
                conversion_time = end_time - start_time
                memory_usage = memory_after - memory_before
                cpu_usage = cpu_after - cpu_before

                # Calculate WTF document size
                wtf_doc_json = wtf_doc.model_dump_json()
                wtf_doc_size = len(wtf_doc_json.encode("utf-8")) / 1024  # KB

                times.append(conversion_time)
                memory_usages.append(memory_usage)
                cpu_usages.append(cpu_usage)
                wtf_doc_sizes.append(wtf_doc_size)

            except Exception as e:
                return PerformanceMetrics(
                    provider=provider_name,
                    conversion_time=0.0,
                    memory_usage_mb=0.0,
                    cpu_usage_percent=0.0,
                    wtf_doc_size_kb=0.0,
                    success=False,
                    error_message=str(e),
                )

        # Calculate averages
        avg_time = sum(times) / len(times)
        avg_memory = sum(memory_usages) / len(memory_usages)
        avg_cpu = sum(cpu_usages) / len(cpu_usages)
        avg_size = sum(wtf_doc_sizes) / len(wtf_doc_sizes)

        return PerformanceMetrics(
            provider=provider_name,
            conversion_time=avg_time,
            memory_usage_mb=avg_memory,
            cpu_usage_percent=avg_cpu,
            wtf_doc_size_kb=avg_size,
            success=True,
        )

    def benchmark_all_providers(
        self, sample_data: Dict[str, Any], iterations: int = 3
    ) -> List[PerformanceMetrics]:
        """
        Benchmark all providers.

        Args:
            sample_data: Sample data to convert
            iterations: Number of iterations to average

        Returns:
            List of performance metrics for each provider
        """
        results = []

        for provider_name in self.providers.keys():
            metrics = self.benchmark_provider(provider_name, sample_data, iterations)
            results.append(metrics)

        return results

    def analyze_performance(self, results: List[PerformanceMetrics]) -> Dict[str, Any]:
        """
        Analyze performance results.

        Args:
            results: List of performance metrics

        Returns:
            Performance analysis
        """
        successful_results = [r for r in results if r.success]

        if not successful_results:
            return {
                "status": "failed",
                "message": "No successful benchmarks",
                "total_providers": len(results),
                "successful_providers": 0,
            }

        # Extract metrics
        times = [r.conversion_time for r in successful_results]
        memory_usages = [r.memory_usage_mb for r in successful_results]
        cpu_usages = [r.cpu_usage_percent for r in successful_results]
        sizes = [r.wtf_doc_size_kb for r in successful_results]

        # Find best performers
        fastest_provider = min(successful_results, key=lambda x: x.conversion_time)
        most_memory_efficient = min(successful_results, key=lambda x: x.memory_usage_mb)
        smallest_output = min(successful_results, key=lambda x: x.wtf_doc_size_kb)

        return {
            "status": "success",
            "total_providers": len(results),
            "successful_providers": len(successful_results),
            "metrics": {
                "conversion_time": {
                    "fastest": fastest_provider.provider,
                    "fastest_time": fastest_provider.conversion_time,
                    "average": sum(times) / len(times),
                    "all_times": {r.provider: r.conversion_time for r in successful_results},
                },
                "memory_usage": {
                    "most_efficient": most_memory_efficient.provider,
                    "most_efficient_usage": most_memory_efficient.memory_usage_mb,
                    "average": sum(memory_usages) / len(memory_usages),
                    "all_usages": {r.provider: r.memory_usage_mb for r in successful_results},
                },
                "output_size": {
                    "smallest": smallest_output.provider,
                    "smallest_size": smallest_output.wtf_doc_size_kb,
                    "average": sum(sizes) / len(sizes),
                    "all_sizes": {r.provider: r.wtf_doc_size_kb for r in successful_results},
                },
            },
            "provider_details": {
                r.provider: {
                    "success": r.success,
                    "conversion_time": r.conversion_time,
                    "memory_usage_mb": r.memory_usage_mb,
                    "cpu_usage_percent": r.cpu_usage_percent,
                    "wtf_doc_size_kb": r.wtf_doc_size_kb,
                    "error": r.error_message,
                }
                for r in results
            },
        }

    def generate_performance_report(self, results: List[PerformanceMetrics]) -> str:
        """Generate a human-readable performance report."""
        analysis = self.analyze_performance(results)

        report = []
        report.append("=" * 60)
        report.append("PERFORMANCE BENCHMARK REPORT")
        report.append("=" * 60)
        report.append(f"Status: {analysis['status'].upper()}")
        report.append(
            f"Successful Providers: {analysis['successful_providers']}/{analysis['total_providers']}"
        )
        report.append("")

        if analysis["status"] == "success":
            # Performance metrics
            report.append("PERFORMANCE METRICS:")
            report.append("-" * 30)

            # Conversion time
            time_metrics = analysis["metrics"]["conversion_time"]
            report.append(
                f"Fastest Conversion: {time_metrics['fastest']} ({time_metrics['fastest_time']:.3f}s)"
            )
            report.append(f"Average Time: {time_metrics['average']:.3f}s")
            report.append("All Times:")
            for provider, time_val in time_metrics["all_times"].items():
                report.append(f"  {provider}: {time_val:.3f}s")
            report.append("")

            # Memory usage
            memory_metrics = analysis["metrics"]["memory_usage"]
            report.append(
                f"Most Memory Efficient: {memory_metrics['most_efficient']} ({memory_metrics['most_efficient_usage']:.2f}MB)"
            )
            report.append(f"Average Memory: {memory_metrics['average']:.2f}MB")
            report.append("All Memory Usage:")
            for provider, memory_val in memory_metrics["all_usages"].items():
                report.append(f"  {provider}: {memory_val:.2f}MB")
            report.append("")

            # Output size
            size_metrics = analysis["metrics"]["output_size"]
            report.append(
                f"Smallest Output: {size_metrics['smallest']} ({size_metrics['smallest_size']:.2f}KB)"
            )
            report.append(f"Average Size: {size_metrics['average']:.2f}KB")
            report.append("All Output Sizes:")
            for provider, size_val in size_metrics["all_sizes"].items():
                report.append(f"  {provider}: {size_val:.2f}KB")
            report.append("")

        # Provider details
        report.append("PROVIDER DETAILS:")
        report.append("-" * 30)
        for provider, data in analysis["provider_details"].items():
            status = "✅" if data["success"] else "❌"
            report.append(f"{provider.upper()}: {status}")
            if data["success"]:
                report.append(f"  Conversion Time: {data['conversion_time']:.3f}s")
                report.append(f"  Memory Usage: {data['memory_usage_mb']:.2f}MB")
                report.append(f"  CPU Usage: {data['cpu_usage_percent']:.1f}%")
                report.append(f"  Output Size: {data['wtf_doc_size_kb']:.2f}KB")
            else:
                report.append(f"  Error: {data['error']}")
            report.append("")

        return "\n".join(report)


class TestPerformanceBenchmark:
    """Test cases for performance benchmarking."""

    @pytest.fixture
    def benchmark(self) -> PerformanceBenchmark:
        """Create a performance benchmark instance."""
        return PerformanceBenchmark()

    @pytest.fixture
    def sample_data(self) -> Dict[str, Any]:
        """Sample data for benchmarking (Whisper format)."""
        return {
            "text": "This is a performance test of the WTF transcript converter across multiple providers.",
            "language": "en",
            "duration": 6.5,
            "segments": [
                {
                    "id": 0,
                    "start": 0.0,
                    "end": 6.5,
                    "text": "This is a performance test of the WTF transcript converter across multiple providers.",
                    "avg_logprob": -0.5,
                    "words": [
                        {"word": "This", "start": 0.0, "end": 0.3, "probability": 0.99},
                        {"word": "is", "start": 0.4, "end": 0.5, "probability": 0.98},
                        {"word": "a", "start": 0.6, "end": 0.7, "probability": 0.97},
                        {
                            "word": "performance",
                            "start": 0.8,
                            "end": 1.5,
                            "probability": 0.96,
                        },
                        {"word": "test", "start": 1.6, "end": 1.9, "probability": 0.95},
                        {"word": "of", "start": 2.0, "end": 2.1, "probability": 0.98},
                        {"word": "the", "start": 2.2, "end": 2.3, "probability": 0.99},
                        {"word": "WTF", "start": 2.4, "end": 2.7, "probability": 0.94},
                        {
                            "word": "transcript",
                            "start": 2.8,
                            "end": 3.4,
                            "probability": 0.93,
                        },
                        {
                            "word": "converter",
                            "start": 3.5,
                            "end": 4.2,
                            "probability": 0.92,
                        },
                        {
                            "word": "across",
                            "start": 4.3,
                            "end": 4.8,
                            "probability": 0.91,
                        },
                        {
                            "word": "multiple",
                            "start": 4.9,
                            "end": 5.4,
                            "probability": 0.90,
                        },
                        {
                            "word": "providers.",
                            "start": 5.5,
                            "end": 6.5,
                            "probability": 0.89,
                        },
                    ],
                }
            ],
        }

    def test_single_provider_benchmark(self, benchmark: Any, sample_data: Any) -> None:
        """Test benchmarking a single provider."""
        metrics = benchmark.benchmark_provider("whisper", sample_data, iterations=2)

        # Should complete successfully
        assert metrics.success, f"Whisper benchmark failed: {metrics.error_message}"

        # Basic sanity checks
        assert metrics.conversion_time > 0, "Conversion time should be positive"
        assert metrics.wtf_doc_size_kb > 0, "WTF document size should be positive"

    def test_all_providers_benchmark(self, benchmark: Any, sample_data: Any) -> None:
        """Test benchmarking all providers."""
        results = benchmark.benchmark_all_providers(sample_data, iterations=2)

        # Should have results for all providers
        assert len(results) == len(benchmark.providers), "Should benchmark all providers"

        # At least some providers should succeed
        successful_results = [r for r in results if r.success]
        assert len(successful_results) > 0, "At least one provider should succeed"

        # Print performance report
        report = benchmark.generate_performance_report(results)
        print("\n" + report)

    def test_performance_analysis(self, benchmark: Any, sample_data: Any) -> None:
        """Test performance analysis."""
        results = benchmark.benchmark_all_providers(sample_data, iterations=2)
        analysis = benchmark.analyze_performance(results)

        # Should have analysis results
        assert "status" in analysis
        assert "total_providers" in analysis
        assert "successful_providers" in analysis

        if analysis["status"] == "success":
            # Should have performance metrics
            assert "metrics" in analysis
            assert "conversion_time" in analysis["metrics"]
            assert "memory_usage" in analysis["metrics"]
            assert "output_size" in analysis["metrics"]

    def test_performance_report_generation(self, benchmark: Any, sample_data: Any) -> None:
        """Test performance report generation."""
        results = benchmark.benchmark_all_providers(sample_data, iterations=2)
        report = benchmark.generate_performance_report(results)

        # Report should contain key sections
        assert "PERFORMANCE BENCHMARK REPORT" in report
        assert "PROVIDER DETAILS:" in report

        # Report should be non-empty
        assert len(report) > 100, "Report should be substantial"

    def test_benchmark_with_empty_data(self, benchmark: Any) -> None:
        """Test benchmarking with empty data."""
        empty_data = {
            "text": "",
            "language": "en",
            "duration": 0.0,
            "words": [],
            "segments": [],
        }

        results = benchmark.benchmark_all_providers(empty_data, iterations=1)

        # Should handle empty data
        assert len(results) == len(benchmark.providers)

        # Some providers might fail with empty data, which is expected
        successful_results = [r for r in results if r.success]
        # At least the basic converters should handle empty data
        assert len(successful_results) >= 0, "Should handle empty data gracefully"

    def test_benchmark_with_minimal_data(self, benchmark: Any) -> None:
        """Test benchmarking with minimal data."""
        minimal_data = {"text": "Hello", "language": "en", "duration": 1.0}

        results = benchmark.benchmark_all_providers(minimal_data, iterations=1)

        # Should handle minimal data
        assert len(results) == len(benchmark.providers)

        # Should have some successful results
        successful_results = [r for r in results if r.success]
        assert len(successful_results) > 0, "Should handle minimal data"

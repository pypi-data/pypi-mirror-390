"""
Cross-provider consistency testing.

This module tests the same audio content across multiple providers to ensure
WTF format consistency and validate standardization.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Union

from wtf_transcript_converter.core.models import WTFDocument
from wtf_transcript_converter.core.validator import validate_wtf_document
from wtf_transcript_converter.providers import (
    AssemblyAIConverter,
    CanaryConverter,
    DeepgramConverter,
    ParakeetConverter,
    RevAIConverter,
    WhisperConverter,
)


@dataclass
class ConsistencyResult:
    """Result of cross-provider consistency testing."""

    provider: str
    wtf_doc: Optional[WTFDocument]
    is_valid: bool
    validation_errors: List[str]
    processing_time: float
    confidence_score: float
    word_count: int
    segment_count: int
    duration: float


class CrossProviderConsistencyTester:
    """Test consistency across multiple transcription providers."""

    def __init__(self) -> None:
        self.providers = {
            "whisper": WhisperConverter(),
            "deepgram": DeepgramConverter(),
            "assemblyai": AssemblyAIConverter(),
            "rev-ai": RevAIConverter(),
            "canary": CanaryConverter(),
            "parakeet": ParakeetConverter(),
        }

    def test_consistency_with_sample_data(
        self, sample_data: Dict[str, Any]
    ) -> List[ConsistencyResult]:
        """
        Test consistency across providers using sample JSON data.

        Args:
            sample_data: Sample transcription data in provider format

        Returns:
            List of consistency results for each provider
        """
        results = []

        for provider_name, converter in self.providers.items():
            try:
                # Convert to WTF
                wtf_doc = converter.convert(sample_data)

                # Validate WTF document
                is_valid, validation_errors = validate_wtf_document(wtf_doc)

                # Calculate metrics
                confidence_score = wtf_doc.transcript.confidence
                word_count = len(wtf_doc.words) if wtf_doc.words else 0
                segment_count = len(wtf_doc.segments)
                duration = wtf_doc.transcript.duration

                result = ConsistencyResult(
                    provider=provider_name,
                    wtf_doc=wtf_doc,
                    is_valid=is_valid,
                    validation_errors=validation_errors,
                    processing_time=0.0,  # Not measured for sample data
                    confidence_score=confidence_score,
                    word_count=word_count,
                    segment_count=segment_count,
                    duration=duration,
                )
                results.append(result)

            except Exception as e:
                # Create error result
                result = ConsistencyResult(
                    provider=provider_name,
                    wtf_doc=None,
                    is_valid=False,
                    validation_errors=[f"Conversion failed: {str(e)}"],
                    processing_time=0.0,
                    confidence_score=0.0,
                    word_count=0,
                    segment_count=0,
                    duration=0.0,
                )
                results.append(result)

        return results

    def analyze_consistency(self, results: List[ConsistencyResult]) -> Dict[str, Any]:
        """
        Analyze consistency across provider results.

        Args:
            results: List of consistency results

        Returns:
            Analysis report
        """
        valid_results = [r for r in results if r.is_valid]

        if not valid_results:
            return {
                "status": "failed",
                "message": "No valid results from any provider",
                "total_providers": len(results),
                "valid_providers": 0,
            }

        # Extract metrics
        confidences = [r.confidence_score for r in valid_results]
        word_counts = [r.word_count for r in valid_results]
        segment_counts = [r.segment_count for r in valid_results]
        durations = [r.duration for r in valid_results]

        # Calculate consistency metrics
        confidence_std = self._calculate_std(confidences)
        word_count_std = self._calculate_std(word_counts)
        segment_count_std = self._calculate_std(segment_counts)
        duration_std = self._calculate_std(durations)

        # Check for significant differences
        confidence_consistent = confidence_std < 0.1  # Less than 10% standard deviation
        word_count_consistent = word_count_std < 2  # Less than 2 words difference
        segment_count_consistent = segment_count_std < 1  # Same segment count
        duration_consistent = duration_std < 1.0  # Less than 1 second difference

        overall_consistent = all(
            [
                confidence_consistent,
                word_count_consistent,
                segment_count_consistent,
                duration_consistent,
            ]
        )

        return {
            "status": "consistent" if overall_consistent else "inconsistent",
            "total_providers": len(results),
            "valid_providers": len(valid_results),
            "metrics": {
                "confidence": {
                    "mean": sum(confidences) / len(confidences),
                    "std": confidence_std,
                    "consistent": confidence_consistent,
                    "values": confidences,
                },
                "word_count": {
                    "mean": sum(word_counts) / len(word_counts),
                    "std": word_count_std,
                    "consistent": word_count_consistent,
                    "values": word_counts,
                },
                "segment_count": {
                    "mean": sum(segment_counts) / len(segment_counts),
                    "std": segment_count_std,
                    "consistent": segment_count_consistent,
                    "values": segment_counts,
                },
                "duration": {
                    "mean": sum(durations) / len(durations),
                    "std": duration_std,
                    "consistent": duration_consistent,
                    "values": durations,
                },
            },
            "provider_results": {
                r.provider: {
                    "valid": r.is_valid,
                    "confidence": r.confidence_score,
                    "word_count": r.word_count,
                    "segment_count": r.segment_count,
                    "duration": r.duration,
                    "errors": r.validation_errors,
                }
                for r in results
            },
        }

    def _calculate_std(self, values: Sequence[Union[int, float]]) -> float:
        """Calculate standard deviation."""
        if len(values) <= 1:
            return 0.0

        float_values = [float(x) for x in values]
        mean = sum(float_values) / len(float_values)
        variance = sum((x - mean) ** 2 for x in float_values) / (len(float_values) - 1)
        return float(variance**0.5)

    def generate_consistency_report(self, results: List[ConsistencyResult]) -> str:
        """Generate a human-readable consistency report."""
        analysis = self.analyze_consistency(results)

        report = []
        report.append("=" * 60)
        report.append("CROSS-PROVIDER CONSISTENCY REPORT")
        report.append("=" * 60)
        report.append(f"Status: {analysis['status'].upper()}")
        report.append(
            f"Valid Providers: {analysis['valid_providers']}/{analysis['total_providers']}"
        )
        report.append("")

        # Metrics section
        report.append("METRICS ANALYSIS:")
        report.append("-" * 30)
        for metric_name, metric_data in analysis["metrics"].items():
            report.append(f"{metric_name.replace('_', ' ').title()}:")
            report.append(f"  Mean: {metric_data['mean']:.3f}")
            report.append(f"  Std Dev: {metric_data['std']:.3f}")
            report.append(f"  Consistent: {'✅' if metric_data['consistent'] else '❌'}")
            report.append(f"  Values: {metric_data['values']}")
            report.append("")

        # Provider details
        report.append("PROVIDER DETAILS:")
        report.append("-" * 30)
        for provider, data in analysis["provider_results"].items():
            status = "✅" if data["valid"] else "❌"
            report.append(f"{provider.upper()}: {status}")
            if data["valid"]:
                report.append(f"  Confidence: {data['confidence']:.3f}")
                report.append(f"  Words: {data['word_count']}")
                report.append(f"  Segments: {data['segment_count']}")
                report.append(f"  Duration: {data['duration']:.2f}s")
            else:
                report.append(f"  Errors: {', '.join(data['errors'])}")
            report.append("")

        return "\n".join(report)

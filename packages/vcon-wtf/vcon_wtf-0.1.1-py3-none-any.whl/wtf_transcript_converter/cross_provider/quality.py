"""
Quality comparison across providers.

This module compares the quality of transcriptions across different providers
to assess accuracy, completeness, and other quality metrics.
"""

import re
from dataclasses import dataclass
from typing import Any, Dict, List

import pytest

from wtf_transcript_converter.core.models import WTFDocument
from wtf_transcript_converter.providers import (
    AssemblyAIConverter,
    CanaryConverter,
    DeepgramConverter,
    ParakeetConverter,
    RevAIConverter,
    WhisperConverter,
)


@dataclass
class QualityMetrics:
    """Quality metrics for a provider."""

    provider: str
    overall_confidence: float
    word_count: int
    segment_count: int
    duration: float
    avg_word_confidence: float
    min_word_confidence: float
    max_word_confidence: float
    low_confidence_words: int
    punctuation_accuracy: float
    text_completeness: float
    timing_accuracy: float
    success: bool
    error_message: str = ""


class QualityComparator:
    """Compare quality across multiple providers."""

    def __init__(self) -> None:
        self.providers = {
            "whisper": WhisperConverter(),
            "deepgram": DeepgramConverter(),
            "assemblyai": AssemblyAIConverter(),
            "rev-ai": RevAIConverter(),
            "canary": CanaryConverter(),
            "parakeet": ParakeetConverter(),
        }

    def analyze_quality(self, provider_name: str, sample_data: Dict[str, Any]) -> QualityMetrics:
        """
        Analyze quality metrics for a single provider.

        Args:
            provider_name: Name of the provider
            sample_data: Sample data to analyze

        Returns:
            Quality metrics
        """
        if provider_name not in self.providers:
            return QualityMetrics(
                provider=provider_name,
                overall_confidence=0.0,
                word_count=0,
                segment_count=0,
                duration=0.0,
                avg_word_confidence=0.0,
                min_word_confidence=0.0,
                max_word_confidence=0.0,
                low_confidence_words=0,
                punctuation_accuracy=0.0,
                text_completeness=0.0,
                timing_accuracy=0.0,
                success=False,
                error_message=f"Provider {provider_name} not found",
            )

        try:
            converter = self.providers[provider_name]
            wtf_doc = converter.convert(sample_data)

            # Basic metrics
            overall_confidence = wtf_doc.transcript.confidence
            word_count = len(wtf_doc.words) if wtf_doc.words else 0
            segment_count = len(wtf_doc.segments)
            duration = wtf_doc.transcript.duration

            # Word-level confidence analysis
            if wtf_doc.words:
                word_confidences = [word.confidence for word in wtf_doc.words]
                avg_word_confidence = sum(word_confidences) / len(word_confidences)
                min_word_confidence = min(word_confidences)
                max_word_confidence = max(word_confidences)
                low_confidence_words = sum(1 for c in word_confidences if c < 0.5)
            else:
                avg_word_confidence = 0.0
                min_word_confidence = 0.0
                max_word_confidence = 0.0
                low_confidence_words = 0

            # Quality assessments
            punctuation_accuracy = self._assess_punctuation_accuracy(wtf_doc)
            text_completeness = self._assess_text_completeness(wtf_doc, sample_data)
            timing_accuracy = self._assess_timing_accuracy(wtf_doc)

            return QualityMetrics(
                provider=provider_name,
                overall_confidence=overall_confidence,
                word_count=word_count,
                segment_count=segment_count,
                duration=duration,
                avg_word_confidence=avg_word_confidence,
                min_word_confidence=min_word_confidence,
                max_word_confidence=max_word_confidence,
                low_confidence_words=low_confidence_words,
                punctuation_accuracy=punctuation_accuracy,
                text_completeness=text_completeness,
                timing_accuracy=timing_accuracy,
                success=True,
            )

        except Exception as e:
            return QualityMetrics(
                provider=provider_name,
                overall_confidence=0.0,
                word_count=0,
                segment_count=0,
                duration=0.0,
                avg_word_confidence=0.0,
                min_word_confidence=0.0,
                max_word_confidence=0.0,
                low_confidence_words=0,
                punctuation_accuracy=0.0,
                text_completeness=0.0,
                timing_accuracy=0.0,
                success=False,
                error_message=str(e),
            )

    def compare_quality_across_providers(
        self, sample_data: Dict[str, Any]
    ) -> List[QualityMetrics]:
        """
        Compare quality across all providers.

        Args:
            sample_data: Sample data to analyze

        Returns:
            List of quality metrics for each provider
        """
        results = []

        for provider_name in self.providers.keys():
            metrics = self.analyze_quality(provider_name, sample_data)
            results.append(metrics)

        return results

    def _assess_punctuation_accuracy(self, wtf_doc: WTFDocument) -> float:
        """Assess punctuation accuracy in the transcription."""
        if not wtf_doc.words:
            return 0.0

        # Count words that should have punctuation
        expected_punctuation = 0
        actual_punctuation = 0

        for word in wtf_doc.words:
            # Check if word ends with punctuation
            if re.search(r"[.!?,:;]$", word.text):
                expected_punctuation += 1
                if word.is_punctuation:
                    actual_punctuation += 1

        if expected_punctuation == 0:
            return 1.0  # No punctuation expected, so 100% accurate

        return actual_punctuation / expected_punctuation

    def _assess_text_completeness(
        self, wtf_doc: WTFDocument, original_data: Dict[str, Any]
    ) -> float:
        """Assess how complete the transcription is compared to original."""
        original_text = original_data.get("text", "").strip()
        wtf_text = wtf_doc.transcript.text.strip()

        if not original_text:
            return 1.0 if not wtf_text else 0.0

        # Simple word-based comparison
        original_words = set(original_text.lower().split())
        wtf_words = set(wtf_text.lower().split())

        if not original_words:
            return 1.0

        # Calculate overlap
        common_words = original_words.intersection(wtf_words)
        return len(common_words) / len(original_words)

    def _assess_timing_accuracy(self, wtf_doc: WTFDocument) -> float:
        """Assess timing accuracy of words and segments."""
        if not wtf_doc.words or not wtf_doc.segments:
            return 0.0

        # Check that words are properly ordered by time
        word_times = [(word.start, word.end) for word in wtf_doc.words]
        segment_times = [(seg.start, seg.end) for seg in wtf_doc.segments]

        # Check word ordering
        word_ordered = all(
            word_times[i][0] <= word_times[i + 1][0] for i in range(len(word_times) - 1)
        )

        # Check segment ordering
        segment_ordered = all(
            segment_times[i][0] <= segment_times[i + 1][0] for i in range(len(segment_times) - 1)
        )

        # Check that words fit within segments
        words_in_segments = True
        for word in wtf_doc.words:
            word_fits = any(
                seg.start <= word.start and word.end <= seg.end for seg in wtf_doc.segments
            )
            if not word_fits:
                words_in_segments = False
                break

        # Calculate accuracy score
        accuracy_score = 0.0
        if word_ordered:
            accuracy_score += 0.4
        if segment_ordered:
            accuracy_score += 0.3
        if words_in_segments:
            accuracy_score += 0.3

        return accuracy_score

    def analyze_quality_comparison(self, results: List[QualityMetrics]) -> Dict[str, Any]:
        """
        Analyze quality comparison results.

        Args:
            results: List of quality metrics

        Returns:
            Quality analysis
        """
        successful_results = [r for r in results if r.success]

        if not successful_results:
            return {
                "status": "failed",
                "message": "No successful quality analyses",
                "total_providers": len(results),
                "successful_providers": 0,
            }

        # Find best performers
        best_confidence = max(successful_results, key=lambda x: x.overall_confidence)
        best_word_confidence = max(successful_results, key=lambda x: x.avg_word_confidence)
        best_punctuation = max(successful_results, key=lambda x: x.punctuation_accuracy)
        best_completeness = max(successful_results, key=lambda x: x.text_completeness)
        best_timing = max(successful_results, key=lambda x: x.timing_accuracy)
        most_words = max(successful_results, key=lambda x: x.word_count)

        # Calculate averages
        avg_confidence = sum(r.overall_confidence for r in successful_results) / len(
            successful_results
        )
        avg_word_confidence = sum(r.avg_word_confidence for r in successful_results) / len(
            successful_results
        )
        avg_punctuation = sum(r.punctuation_accuracy for r in successful_results) / len(
            successful_results
        )
        avg_completeness = sum(r.text_completeness for r in successful_results) / len(
            successful_results
        )
        avg_timing = sum(r.timing_accuracy for r in successful_results) / len(successful_results)

        return {
            "status": "success",
            "total_providers": len(results),
            "successful_providers": len(successful_results),
            "averages": {
                "overall_confidence": avg_confidence,
                "word_confidence": avg_word_confidence,
                "punctuation_accuracy": avg_punctuation,
                "text_completeness": avg_completeness,
                "timing_accuracy": avg_timing,
            },
            "best_performers": {
                "overall_confidence": best_confidence.provider,
                "word_confidence": best_word_confidence.provider,
                "punctuation_accuracy": best_punctuation.provider,
                "text_completeness": best_completeness.provider,
                "timing_accuracy": best_timing.provider,
                "most_words": most_words.provider,
            },
            "provider_details": {
                r.provider: {
                    "success": r.success,
                    "overall_confidence": r.overall_confidence,
                    "word_count": r.word_count,
                    "avg_word_confidence": r.avg_word_confidence,
                    "low_confidence_words": r.low_confidence_words,
                    "punctuation_accuracy": r.punctuation_accuracy,
                    "text_completeness": r.text_completeness,
                    "timing_accuracy": r.timing_accuracy,
                    "error": r.error_message,
                }
                for r in results
            },
        }

    def generate_quality_report(self, results: List[QualityMetrics]) -> str:
        """Generate a human-readable quality report."""
        analysis = self.analyze_quality_comparison(results)

        report = []
        report.append("=" * 60)
        report.append("QUALITY COMPARISON REPORT")
        report.append("=" * 60)
        report.append(f"Status: {analysis['status'].upper()}")
        report.append(
            f"Successful Providers: {analysis['successful_providers']}/{analysis['total_providers']}"
        )
        report.append("")

        if analysis["status"] == "success":
            # Averages
            report.append("AVERAGE QUALITY METRICS:")
            report.append("-" * 30)
            report.append(f"Overall Confidence: {analysis['averages']['overall_confidence']:.3f}")
            report.append(f"Word Confidence: {analysis['averages']['word_confidence']:.3f}")
            report.append(
                f"Punctuation Accuracy: {analysis['averages']['punctuation_accuracy']:.3f}"
            )
            report.append(f"Text Completeness: {analysis['averages']['text_completeness']:.3f}")
            report.append(f"Timing Accuracy: {analysis['averages']['timing_accuracy']:.3f}")
            report.append("")

            # Best performers
            report.append("BEST PERFORMERS:")
            report.append("-" * 30)
            for metric, provider in analysis["best_performers"].items():
                report.append(f"{metric.replace('_', ' ').title()}: {provider}")
            report.append("")

        # Provider details
        report.append("PROVIDER DETAILS:")
        report.append("-" * 30)
        for provider, data in analysis["provider_details"].items():
            status = "✅" if data["success"] else "❌"
            report.append(f"{provider.upper()}: {status}")
            if data["success"]:
                report.append(f"  Overall Confidence: {data['overall_confidence']:.3f}")
                report.append(f"  Word Count: {data['word_count']}")
                report.append(f"  Avg Word Confidence: {data['avg_word_confidence']:.3f}")
                report.append(f"  Low Confidence Words: {data['low_confidence_words']}")
                report.append(f"  Punctuation Accuracy: {data['punctuation_accuracy']:.3f}")
                report.append(f"  Text Completeness: {data['text_completeness']:.3f}")
                report.append(f"  Timing Accuracy: {data['timing_accuracy']:.3f}")
            else:
                report.append(f"  Error: {data['error']}")
            report.append("")

        return "\n".join(report)


class TestQualityComparison:
    """Test cases for quality comparison."""

    @pytest.fixture
    def quality_comparator(self) -> QualityComparator:
        """Create a quality comparator instance."""
        return QualityComparator()

    @pytest.fixture
    def sample_data(self) -> Dict[str, Any]:
        """Sample data for quality testing (Whisper format)."""
        return {
            "text": "Hello, this is a quality test! How are you doing today?",
            "language": "en",
            "duration": 5.0,
            "segments": [
                {
                    "id": 0,
                    "start": 0.0,
                    "end": 2.3,
                    "text": "Hello, this is a quality test!",
                    "avg_logprob": -0.4,
                    "words": [
                        {
                            "word": "Hello,",
                            "start": 0.0,
                            "end": 0.5,
                            "probability": 0.99,
                        },
                        {"word": "this", "start": 0.6, "end": 0.8, "probability": 0.98},
                        {"word": "is", "start": 0.9, "end": 1.0, "probability": 0.99},
                        {"word": "a", "start": 1.1, "end": 1.2, "probability": 0.97},
                        {
                            "word": "quality",
                            "start": 1.3,
                            "end": 1.8,
                            "probability": 0.96,
                        },
                        {
                            "word": "test!",
                            "start": 1.9,
                            "end": 2.3,
                            "probability": 0.95,
                        },
                    ],
                },
                {
                    "id": 1,
                    "start": 2.4,
                    "end": 5.0,
                    "text": "How are you doing today?",
                    "avg_logprob": -0.3,
                    "words": [
                        {"word": "How", "start": 2.4, "end": 2.6, "probability": 0.94},
                        {"word": "are", "start": 2.7, "end": 2.9, "probability": 0.93},
                        {"word": "you", "start": 3.0, "end": 3.2, "probability": 0.92},
                        {
                            "word": "doing",
                            "start": 3.3,
                            "end": 3.7,
                            "probability": 0.91,
                        },
                        {
                            "word": "today?",
                            "start": 3.8,
                            "end": 5.0,
                            "probability": 0.90,
                        },
                    ],
                },
            ],
        }

    def test_single_provider_quality(self, quality_comparator: Any, sample_data: Any) -> None:
        """Test quality analysis for a single provider."""
        metrics = quality_comparator.analyze_quality("whisper", sample_data)

        # Should complete successfully
        assert metrics.success, f"Whisper quality analysis failed: {metrics.error_message}"

        # Basic sanity checks
        assert 0.0 <= metrics.overall_confidence <= 1.0, "Invalid overall confidence"
        assert metrics.word_count > 0, "Should have words"
        assert metrics.segment_count > 0, "Should have segments"
        assert 0.0 <= metrics.avg_word_confidence <= 1.0, "Invalid word confidence"

    def test_all_providers_quality(self, quality_comparator: Any, sample_data: Any) -> None:
        """Test quality comparison across all providers."""
        results = quality_comparator.compare_quality_across_providers(sample_data)

        # Should have results for all providers
        assert len(results) == len(quality_comparator.providers), "Should analyze all providers"

        # At least some providers should succeed
        successful_results = [r for r in results if r.success]
        assert len(successful_results) > 0, "At least one provider should succeed"

        # Print quality report
        report = quality_comparator.generate_quality_report(results)
        print("\n" + report)

    def test_quality_analysis(self, quality_comparator: Any, sample_data: Any) -> None:
        """Test quality analysis."""
        results = quality_comparator.compare_quality_across_providers(sample_data)
        analysis = quality_comparator.analyze_quality_comparison(results)

        # Should have analysis results
        assert "status" in analysis
        assert "total_providers" in analysis
        assert "successful_providers" in analysis

        if analysis["status"] == "success":
            # Should have quality metrics
            assert "averages" in analysis
            assert "best_performers" in analysis
            assert "provider_details" in analysis

    def test_quality_report_generation(self, quality_comparator: Any, sample_data: Any) -> None:
        """Test quality report generation."""
        results = quality_comparator.compare_quality_across_providers(sample_data)
        report = quality_comparator.generate_quality_report(results)

        # Report should contain key sections
        assert "QUALITY COMPARISON REPORT" in report
        assert "PROVIDER DETAILS:" in report

        # Report should be non-empty
        assert len(report) > 100, "Report should be substantial"

    def test_punctuation_accuracy_assessment(self, quality_comparator: Any) -> None:
        """Test punctuation accuracy assessment."""
        # Create a mock WTF document with punctuation
        from wtf_transcript_converter.core.models import (
            WTFAudio,
            WTFMetadata,
            WTFSegment,
            WTFTranscript,
            WTFWord,
        )

        words = [
            WTFWord(
                id=0,
                start=0.0,
                end=0.5,
                text="Hello,",
                confidence=0.99,
                speaker=None,
                is_punctuation=True,
            ),
            WTFWord(
                id=1,
                start=0.6,
                end=1.0,
                text="world!",
                confidence=0.98,
                speaker=None,
                is_punctuation=True,
            ),
        ]

        segments = [
            WTFSegment(
                id=0,
                start=0.0,
                end=1.0,
                text="Hello, world!",
                confidence=0.99,
                speaker=None,
                words=[0, 1],
            )
        ]

        transcript = WTFTranscript(
            text="Hello, world!", language="en", duration=1.0, confidence=0.99
        )
        audio = WTFAudio(
            duration=1.0,
            sample_rate=None,
            channels=None,
            format=None,
            bitrate=None,
        )
        metadata = WTFMetadata(
            created_at="2024-01-01T00:00:00Z",
            processed_at="2024-01-01T00:00:00Z",
            provider="test",
            model="test",
            processing_time=None,
            audio=audio,
            options={},
        )

        wtf_doc = WTFDocument(
            transcript=transcript,
            segments=segments,
            metadata=metadata,
            words=words,
            speakers=None,
            alternatives=None,
            enrichments=None,
            extensions=None,
            quality=None,
            streaming=None,
        )

        accuracy = quality_comparator._assess_punctuation_accuracy(wtf_doc)
        assert 0.0 <= accuracy <= 1.0, "Punctuation accuracy should be between 0 and 1"

    def test_text_completeness_assessment(self, quality_comparator: Any) -> None:
        """Test text completeness assessment."""
        from wtf_transcript_converter.core.models import (
            WTFAudio,
            WTFMetadata,
            WTFSegment,
            WTFTranscript,
        )

        transcript = WTFTranscript(
            text="Hello world", language="en", duration=1.0, confidence=0.99
        )
        segments = [
            WTFSegment(
                id=0,
                start=0.0,
                end=1.0,
                text="Hello world",
                confidence=0.99,
                speaker=None,
                words=None,
            )
        ]
        audio = WTFAudio(
            duration=1.0,
            sample_rate=None,
            channels=None,
            format=None,
            bitrate=None,
        )
        metadata = WTFMetadata(
            created_at="2024-01-01T00:00:00Z",
            processed_at="2024-01-01T00:00:00Z",
            provider="test",
            model="test",
            processing_time=None,
            audio=audio,
            options={},
        )

        wtf_doc = WTFDocument(
            transcript=transcript,
            segments=segments,
            metadata=metadata,
            words=None,
            speakers=None,
            alternatives=None,
            enrichments=None,
            extensions=None,
            quality=None,
            streaming=None,
        )
        original_data = {"text": "Hello world test"}

        completeness = quality_comparator._assess_text_completeness(wtf_doc, original_data)
        assert 0.0 <= completeness <= 1.0, "Text completeness should be between 0 and 1"
        assert completeness > 0.5, "Should have some overlap with original text"

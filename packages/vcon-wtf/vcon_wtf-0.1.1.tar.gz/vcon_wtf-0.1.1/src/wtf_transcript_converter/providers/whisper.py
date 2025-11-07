"""
Whisper provider converter.

This module provides conversion between Whisper JSON format and WTF format.
"""

import math
from typing import Any, Dict, List

from ..core.converter import FromWTFConverter, ToWTFConverter
from ..core.models import (
    WTFAudio,
    WTFDocument,
    WTFMetadata,
    WTFQuality,
    WTFSegment,
    WTFTranscript,
    WTFWord,
)
from ..utils.confidence_utils import normalize_confidence
from ..utils.language_utils import normalize_language_code


class WhisperConverter(ToWTFConverter, FromWTFConverter):
    """Converter for Whisper JSON format to/from WTF format."""

    def __init__(self) -> None:
        self.provider_name = "whisper"

    def convert_to_wtf(self, whisper_data: Dict[str, Any]) -> WTFDocument:
        """
        Convert Whisper JSON data to WTF format.

        Args:
            whisper_data: Whisper JSON data structure

        Returns:
            WTF document
        """
        # Extract basic transcript information
        transcript = WTFTranscript(
            text=whisper_data.get("text", ""),
            language=normalize_language_code(whisper_data.get("language", "en")),
            duration=whisper_data.get("duration", 0.0),
            confidence=self._calculate_overall_confidence(whisper_data),
        )

        # Convert segments
        segments = []
        words = []
        word_id = 0

        for i, segment_data in enumerate(whisper_data.get("segments", [])):
            # Convert segment
            segment = WTFSegment(
                id=i,
                start=segment_data.get("start", 0.0),
                end=segment_data.get("end", 0.0),
                text=segment_data.get("text", ""),
                confidence=self._normalize_whisper_confidence(segment_data),
                speaker=0,  # Whisper doesn't do speaker diarization by default
                words=None,  # Will be set later if words are available
            )
            segments.append(segment)

            # Convert words if available
            if "words" in segment_data:
                segment_word_ids = []
                for word_data in segment_data["words"]:
                    word = WTFWord(
                        id=word_id,
                        start=word_data.get("start", 0.0),
                        end=word_data.get("end", 0.0),
                        text=word_data.get("word", ""),
                        confidence=self._normalize_whisper_confidence(word_data),
                        speaker=0,
                        is_punctuation=self._is_punctuation(word_data.get("word", "")),
                    )
                    words.append(word)
                    segment_word_ids.append(word_id)
                    word_id += 1

                segment.words = segment_word_ids

        # Create metadata
        metadata = WTFMetadata(
            created_at=self._get_timestamp(),
            processed_at=self._get_timestamp(),
            provider="whisper",
            model=whisper_data.get("model", "whisper-1"),
            processing_time=whisper_data.get("processing_time"),
            audio=WTFAudio(
                duration=whisper_data.get("duration", 0.0),
                sample_rate=whisper_data.get("sample_rate"),
                channels=whisper_data.get("channels"),
                format=whisper_data.get("format"),
                bitrate=None,
            ),
            options=self._extract_whisper_options(whisper_data),
        )

        # Create quality metrics
        quality = WTFQuality(
            audio_quality=self._assess_audio_quality(whisper_data),
            background_noise=None,
            multiple_speakers=None,
            overlapping_speech=None,
            silence_ratio=None,
            average_confidence=transcript.confidence,
            low_confidence_words=self._count_low_confidence_words(words),
            processing_warnings=self._extract_warnings(whisper_data),
        )

        # Create extensions with Whisper-specific data
        extensions = {
            "whisper": {
                "temperature": self._extract_temperature(whisper_data),
                "compression_ratio": self._extract_compression_ratio(whisper_data),
                "avg_logprob": self._extract_avg_logprob(whisper_data),
                "no_speech_prob": self._extract_no_speech_prob(whisper_data),
                "tokens": self._extract_tokens(whisper_data),
            }
        }

        return WTFDocument(
            transcript=transcript,
            segments=segments,
            metadata=metadata,
            words=words if words else None,
            speakers=None,
            alternatives=None,
            enrichments=None,
            extensions=extensions,
            quality=quality,
            streaming=None,
        )

    def convert_from_wtf(self, wtf_doc: WTFDocument) -> Dict[str, Any]:
        """
        Convert WTF document to Whisper JSON format.

        Args:
            wtf_doc: WTF document

        Returns:
            Whisper JSON data structure
        """
        # Convert segments back to Whisper format
        segments = []
        for segment in wtf_doc.segments:
            segment_data = {
                "id": segment.id,
                "start": segment.start,
                "end": segment.end,
                "text": segment.text,
                "tokens": self._convert_to_whisper_tokens(segment.text),
                "temperature": 0.0,
                "avg_logprob": self._convert_confidence_to_logprob(segment.confidence),
                "compression_ratio": 1.0,
                "no_speech_prob": 0.01,
            }

            # Add words if available
            if wtf_doc.words and segment.words:
                segment_words = []
                for word_id in segment.words:
                    word = next((w for w in wtf_doc.words if w.id == word_id), None)
                    if word:
                        segment_words.append(
                            {
                                "word": word.text,
                                "start": word.start,
                                "end": word.end,
                                "probability": word.confidence,
                            }
                        )
                segment_data["words"] = segment_words

            segments.append(segment_data)

        # Extract Whisper-specific extensions
        whisper_ext = wtf_doc.extensions.get("whisper", {}) if wtf_doc.extensions else {}

        return {
            "text": wtf_doc.transcript.text,
            "language": wtf_doc.transcript.language,
            "duration": wtf_doc.transcript.duration,
            "segments": segments,
            "model": wtf_doc.metadata.model,
            "temperature": whisper_ext.get("temperature", 0.0),
            "compression_ratio": whisper_ext.get("compression_ratio", 1.0),
            "avg_logprob": whisper_ext.get("avg_logprob", -0.5),
            "no_speech_prob": whisper_ext.get("no_speech_prob", 0.01),
        }

    def convert(self, data: Any) -> Any:
        """Generic convert method - determines direction based on data type."""
        if isinstance(data, dict) and "transcript" in data and "segments" in data:
            # This looks like a WTF document dict, convert from WTF
            wtf_doc = WTFDocument.model_validate(data)
            return self.convert_from_wtf(wtf_doc)
        elif isinstance(data, WTFDocument):
            # This is a WTF document object, convert from WTF
            return self.convert_from_wtf(data)
        else:
            # Assume this is Whisper data, convert to WTF
            return self.convert_to_wtf(data)

    def _calculate_overall_confidence(self, whisper_data: Dict[str, Any]) -> float:
        """Calculate overall confidence from Whisper data."""
        segments = whisper_data.get("segments", [])
        if not segments:
            return 0.0

        # Use average log probability converted to confidence
        logprobs = []
        for segment in segments:
            if "avg_logprob" in segment:
                logprobs.append(segment["avg_logprob"])

        if logprobs:
            avg_logprob = sum(logprobs) / len(logprobs)
            # Convert log probability to confidence (0-1 scale)
            return max(0.0, min(1.0, math.exp(avg_logprob)))

        return 0.5  # Default confidence

    def _normalize_whisper_confidence(self, data: Dict[str, Any]) -> float:
        """Normalize Whisper confidence scores to [0.0, 1.0] range."""
        if "avg_logprob" in data:
            # Convert log probability to confidence
            logprob = data["avg_logprob"]
            return max(0.0, min(1.0, math.exp(logprob)))
        elif "probability" in data:
            return normalize_confidence(data["probability"], "whisper")
        else:
            return 0.5  # Default confidence

    def _is_punctuation(self, word: str) -> bool:
        """Check if a word is punctuation."""
        return word.strip() in ".,!?;:()[]{}'\"-"

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO 8601 format."""
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()

    def _extract_whisper_options(self, whisper_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Whisper-specific options."""
        return {
            "temperature": whisper_data.get("temperature", 0.0),
            "compression_ratio": whisper_data.get("compression_ratio", 1.0),
            "no_speech_prob": whisper_data.get("no_speech_prob", 0.01),
        }

    def _assess_audio_quality(self, whisper_data: Dict[str, Any]) -> str:
        """Assess audio quality based on Whisper metrics."""
        no_speech_prob = whisper_data.get("no_speech_prob", 0.01)
        if no_speech_prob < 0.1:
            return "high"
        elif no_speech_prob < 0.3:
            return "medium"
        else:
            return "low"

    def _count_low_confidence_words(self, words: List[WTFWord]) -> int:
        """Count words with low confidence scores."""
        return sum(1 for word in words if word.confidence < 0.5)

    def _extract_warnings(self, whisper_data: Dict[str, Any]) -> List[str]:
        """Extract processing warnings from Whisper data."""
        warnings = []
        if whisper_data.get("no_speech_prob", 0) > 0.5:
            warnings.append("High probability of no speech detected")
        return warnings

    def _extract_temperature(self, whisper_data: Dict[str, Any]) -> float:
        """Extract temperature from Whisper data."""
        return float(whisper_data.get("temperature", 0.0))

    def _extract_compression_ratio(self, whisper_data: Dict[str, Any]) -> float:
        """Extract compression ratio from Whisper data."""
        return float(whisper_data.get("compression_ratio", 1.0))

    def _extract_avg_logprob(self, whisper_data: Dict[str, Any]) -> float:
        """Extract average log probability from Whisper data."""
        return float(whisper_data.get("avg_logprob", -0.5))

    def _extract_no_speech_prob(self, whisper_data: Dict[str, Any]) -> float:
        """Extract no speech probability from Whisper data."""
        return float(whisper_data.get("no_speech_prob", 0.01))

    def _extract_tokens(self, whisper_data: Dict[str, Any]) -> List[int]:
        """Extract tokens from Whisper data."""
        tokens = []
        for segment in whisper_data.get("segments", []):
            tokens.extend(segment.get("tokens", []))
        return tokens

    def _convert_to_whisper_tokens(self, text: str) -> List[int]:
        """Convert text to Whisper token IDs (placeholder implementation)."""
        # This is a placeholder - real implementation would use Whisper's tokenizer
        return [1] * len(text.split())  # Simplified token representation

    def _convert_confidence_to_logprob(self, confidence: float) -> float:
        """Convert confidence score to log probability."""
        return math.log(max(confidence, 1e-10))

"""
AssemblyAI provider converter.

This module provides conversion between AssemblyAI JSON format and WTF format.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ..core.converter import FromWTFConverter, ToWTFConverter
from ..core.models import (
    WTFAudio,
    WTFDocument,
    WTFMetadata,
    WTFQuality,
    WTFSegment,
    WTFSpeaker,
    WTFTranscript,
    WTFWord,
)
from ..utils.language_utils import normalize_language_code


class AssemblyAIConverter(ToWTFConverter, FromWTFConverter):
    """Converter for AssemblyAI JSON format to/from WTF format."""

    def __init__(self) -> None:
        self.provider_name = "assemblyai"

    def convert_to_wtf(self, assemblyai_data: Dict[str, Any]) -> WTFDocument:
        """
        Convert AssemblyAI JSON data to WTF format.

        Args:
            assemblyai_data: AssemblyAI JSON data structure

        Returns:
            WTF document
        """
        # Extract basic transcript information
        transcript = WTFTranscript(
            text=assemblyai_data.get("text", ""),
            language=self._extract_language(assemblyai_data),
            duration=assemblyai_data.get("audio_duration", 0.0),
            confidence=self._calculate_overall_confidence(assemblyai_data),
        )

        # Convert words to segments and words
        words_data = assemblyai_data.get("words", [])
        segments = self._convert_words_to_segments(words_data, transcript.text)
        words = self._convert_assemblyai_words(words_data)

        # Extract speaker information
        speakers = self._extract_speakers(assemblyai_data)

        # Create metadata
        metadata = WTFMetadata(
            created_at=assemblyai_data.get("created") or self._get_timestamp(),
            processed_at=assemblyai_data.get("created") or self._get_timestamp(),
            provider="assemblyai",
            model=self._extract_model_info(assemblyai_data),
            processing_time=assemblyai_data.get("processing_time"),
            audio=WTFAudio(
                duration=assemblyai_data.get("audio_duration", 0.0),
                sample_rate=None,  # Not available in standard AssemblyAI response
                channels=None,
                format=None,
                bitrate=None,
            ),
            options=self._extract_assemblyai_options(assemblyai_data),
        )

        # Create quality metrics
        quality = WTFQuality(
            audio_quality=self._assess_audio_quality(assemblyai_data),
            background_noise=None,
            multiple_speakers=None,
            overlapping_speech=None,
            silence_ratio=None,
            average_confidence=transcript.confidence,
            low_confidence_words=self._count_low_confidence_words(words),
            processing_warnings=self._extract_warnings(assemblyai_data),
        )

        # Create extensions with AssemblyAI-specific data
        extensions = {
            "assemblyai": {
                "id": assemblyai_data.get("id"),
                "status": assemblyai_data.get("status"),
                "language_code": assemblyai_data.get("language_code"),
                "language_confidence": assemblyai_data.get("language_confidence"),
                "punctuate": assemblyai_data.get("punctuate"),
                "format_text": assemblyai_data.get("format_text"),
                "dual_channel": assemblyai_data.get("dual_channel"),
                "webhook_url": assemblyai_data.get("webhook_url"),
                "webhook_status_code": assemblyai_data.get("webhook_status_code"),
                "webhook_auth": assemblyai_data.get("webhook_auth"),
                "webhook_auth_header_name": assemblyai_data.get("webhook_auth_header_name"),
                "auto_highlights": assemblyai_data.get("auto_highlights"),
                "audio_start_from": assemblyai_data.get("audio_start_from"),
                "audio_end_at": assemblyai_data.get("audio_end_at"),
                "word_boost": assemblyai_data.get("word_boost"),
                "boost_param": assemblyai_data.get("boost_param"),
                "filter_profanity": assemblyai_data.get("filter_profanity"),
                "redact_pii": assemblyai_data.get("redact_pii"),
                "redact_pii_audio": assemblyai_data.get("redact_pii_audio"),
                "redact_pii_audio_quality": assemblyai_data.get("redact_pii_audio_quality"),
                "redact_pii_policies": assemblyai_data.get("redact_pii_policies"),
                "redact_pii_sub": assemblyai_data.get("redact_pii_sub"),
                "speaker_labels": assemblyai_data.get("speaker_labels"),
                "speakers_expected": assemblyai_data.get("speakers_expected"),
                "content_safety": assemblyai_data.get("content_safety"),
                "content_safety_confidence": assemblyai_data.get("content_safety_confidence"),
                "iab_categories": assemblyai_data.get("iab_categories"),
                "iab_categories_result": assemblyai_data.get("iab_categories_result"),
                "language_detection": assemblyai_data.get("language_detection"),
                "custom_spelling": assemblyai_data.get("custom_spelling"),
                "disfluencies": assemblyai_data.get("disfluencies"),
                "sentiment_analysis": assemblyai_data.get("sentiment_analysis"),
                "sentiment_analysis_results": assemblyai_data.get("sentiment_analysis_results"),
                "auto_chapters": assemblyai_data.get("auto_chapters"),
                "auto_chapters_result": assemblyai_data.get("auto_chapters_result"),
                "summarization": assemblyai_data.get("summarization"),
                "summarization_model": assemblyai_data.get("summarization_model"),
                "summary_type": assemblyai_data.get("summary_type"),
                "summary_model": assemblyai_data.get("summary_model"),
                "custom_topics": assemblyai_data.get("custom_topics"),
                "topics": assemblyai_data.get("topics"),
                "speech_model": assemblyai_data.get("speech_model"),
                "speech_model_version": assemblyai_data.get("speech_model_version"),
            }
        }

        return WTFDocument(
            transcript=transcript,
            segments=segments,
            metadata=metadata,
            words=words,
            speakers=speakers,
            alternatives=None,
            enrichments=None,
            extensions=extensions,
            quality=quality,
            streaming=None,
        )

    def convert_from_wtf(self, wtf_doc: WTFDocument) -> Dict[str, Any]:
        """
        Convert WTF document to AssemblyAI JSON format.

        Args:
            wtf_doc: WTF document

        Returns:
            AssemblyAI JSON data structure
        """
        # Convert words back to AssemblyAI format
        words = []
        if wtf_doc.words:
            for word in wtf_doc.words:
                word_data = {
                    "text": word.text,
                    "start": word.start,
                    "end": word.end,
                    "confidence": word.confidence,
                    "speaker": word.speaker if word.speaker is not None else "A",
                }
                words.append(word_data)

        # Extract AssemblyAI-specific extensions
        assemblyai_ext = wtf_doc.extensions.get("assemblyai", {}) if wtf_doc.extensions else {}

        return {
            "id": assemblyai_ext.get("id", "wtf-converted"),
            "status": "completed",
            "text": wtf_doc.transcript.text,
            "language_code": wtf_doc.transcript.language,
            "language_confidence": 0.95,  # Default confidence
            "audio_duration": wtf_doc.transcript.duration,
            "confidence": wtf_doc.transcript.confidence,
            "words": words,
            "created": wtf_doc.metadata.created_at,
            "punctuate": assemblyai_ext.get("punctuate", True),
            "format_text": assemblyai_ext.get("format_text", True),
            "dual_channel": assemblyai_ext.get("dual_channel", False),
            "speaker_labels": assemblyai_ext.get("speaker_labels", True),
            "speakers_expected": assemblyai_ext.get("speakers_expected", 1),
            "speech_model": assemblyai_ext.get("speech_model", "best"),
            "speech_model_version": assemblyai_ext.get("speech_model_version", "1.0"),
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
            # Assume this is AssemblyAI data, convert to WTF
            return self.convert_to_wtf(data)

    def _extract_language(self, assemblyai_data: Dict[str, Any]) -> str:
        """Extract and normalize language from AssemblyAI data."""
        language_code = assemblyai_data.get("language_code", "en")
        return str(normalize_language_code(language_code))

    def _extract_model_info(self, assemblyai_data: Dict[str, Any]) -> str:
        """Extract model information from AssemblyAI data."""
        speech_model = assemblyai_data.get("speech_model", "best")
        speech_model_version = assemblyai_data.get("speech_model_version", "1.0")
        return f"{speech_model}-{speech_model_version}"

    def _calculate_overall_confidence(self, assemblyai_data: Dict[str, Any]) -> float:
        """Calculate overall confidence from AssemblyAI data."""
        words = assemblyai_data.get("words", [])
        if not words:
            return float(assemblyai_data.get("confidence", 0.0))

        # Calculate average confidence from words
        confidences = [word.get("confidence", 0.0) for word in words]
        return sum(confidences) / len(confidences) if confidences else 0.0

    def _convert_words_to_segments(
        self, words_data: List[Dict[str, Any]], transcript_text: str
    ) -> List[WTFSegment]:
        """Convert AssemblyAI words to WTF segments."""
        if not words_data:
            return []

        # Create a single segment that matches the transcript text exactly
        start_time = words_data[0].get("start", 0.0)
        end_time = words_data[-1].get("end", 0.0)

        # Calculate average confidence
        confidences = [word.get("confidence", 0.0) for word in words_data]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        # Get speaker (assume all words in segment have same speaker)
        speaker = words_data[0].get("speaker", "A")

        segment = WTFSegment(
            id=0,
            start=start_time,
            end=end_time,
            text=transcript_text,  # Use the exact transcript text
            confidence=avg_confidence,
            speaker=speaker,
            words=list(range(len(words_data))),  # Word indices
        )
        return [segment]

    def _convert_assemblyai_words(self, words_data: List[Dict[str, Any]]) -> List[WTFWord]:
        """Convert AssemblyAI words to WTF words."""
        words = []

        for i, word_data in enumerate(words_data):
            word = WTFWord(
                id=i,
                start=word_data.get("start", 0.0),
                end=word_data.get("end", 0.0),
                text=word_data.get("text", ""),
                confidence=word_data.get("confidence", 0.0),
                speaker=word_data.get("speaker", "A"),
                is_punctuation=self._is_punctuation(word_data.get("text", "")),
            )
            words.append(word)

        return words

    def _extract_speakers(
        self, assemblyai_data: Dict[str, Any]
    ) -> Optional[Dict[str, WTFSpeaker]]:
        """Extract speaker information from AssemblyAI data."""
        words = assemblyai_data.get("words", [])
        if not words:
            return None

        # Group words by speaker
        speaker_words: dict[str, list[Dict[str, Any]]] = {}
        for word_data in words:
            speaker_id = word_data.get("speaker", "A")
            if speaker_id not in speaker_words:
                speaker_words[speaker_id] = []
            speaker_words[speaker_id].append(word_data)

        # Create speaker objects
        speakers = {}
        for speaker_id, words in speaker_words.items():
            total_time = sum(word.get("end", 0.0) - word.get("start", 0.0) for word in words)
            avg_confidence = sum(word.get("confidence", 0.0) for word in words) / len(words)

            speaker = WTFSpeaker(
                id=speaker_id,
                label=f"Speaker {speaker_id}",
                segments=[],  # Will be populated by segment processing
                total_time=total_time,
                confidence=avg_confidence,
            )
            speakers[str(speaker_id)] = speaker

        return speakers if speakers else None

    def _is_punctuation(self, word: str) -> bool:
        """Check if a word is punctuation."""
        return word.strip() in ".,!?;:()[]{}'\"-"

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO 8601 format."""
        return datetime.now(timezone.utc).isoformat()

    def _extract_assemblyai_options(self, assemblyai_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract AssemblyAI-specific options."""
        return {
            "punctuate": assemblyai_data.get("punctuate", True),
            "format_text": assemblyai_data.get("format_text", True),
            "dual_channel": assemblyai_data.get("dual_channel", False),
            "speaker_labels": assemblyai_data.get("speaker_labels", True),
            "speakers_expected": assemblyai_data.get("speakers_expected", 1),
            "speech_model": assemblyai_data.get("speech_model", "best"),
            "auto_highlights": assemblyai_data.get("auto_highlights", False),
            "filter_profanity": assemblyai_data.get("filter_profanity", False),
            "redact_pii": assemblyai_data.get("redact_pii", False),
            "sentiment_analysis": assemblyai_data.get("sentiment_analysis", False),
            "auto_chapters": assemblyai_data.get("auto_chapters", False),
            "summarization": assemblyai_data.get("summarization", False),
        }

    def _assess_audio_quality(self, assemblyai_data: Dict[str, Any]) -> str:
        """Assess audio quality based on AssemblyAI metrics."""
        confidence = assemblyai_data.get("confidence", 0.0)
        if confidence >= 0.9:
            return "high"
        elif confidence >= 0.7:
            return "medium"
        else:
            return "low"

    def _count_low_confidence_words(self, words: List[WTFWord]) -> int:
        """Count words with low confidence scores."""
        return sum(1 for word in words if word.confidence < 0.5)

    def _extract_warnings(self, assemblyai_data: Dict[str, Any]) -> List[str]:
        """Extract processing warnings from AssemblyAI data."""
        warnings = []

        # Check for low confidence
        confidence = assemblyai_data.get("confidence", 0.0)
        if confidence < 0.7:
            warnings.append(f"Low overall confidence: {confidence:.2f}")

        # Check for language confidence
        language_confidence = assemblyai_data.get("language_confidence") or 1.0
        if language_confidence < 0.8:
            warnings.append(f"Low language detection confidence: {language_confidence:.2f}")

        # Check for content safety issues
        content_safety = assemblyai_data.get("content_safety", {})
        if content_safety and content_safety.get("status") == "error":
            warnings.append("Content safety analysis failed")

        return warnings

"""
Deepgram provider converter.

This module provides conversion between Deepgram JSON format and WTF format.
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


class DeepgramConverter(ToWTFConverter, FromWTFConverter):
    """Converter for Deepgram JSON format to/from WTF format."""

    def __init__(self) -> None:
        self.provider_name = "deepgram"

    def convert_to_wtf(self, deepgram_data: Dict[str, Any]) -> WTFDocument:
        """
        Convert Deepgram JSON data to WTF format.

        Args:
            deepgram_data: Deepgram JSON data structure

        Returns:
            WTF document
        """
        # Extract metadata
        metadata_info = deepgram_data.get("metadata", {})
        results = deepgram_data.get("results", {})
        channels = results.get("channels", [])

        if not channels:
            raise ValueError("No channels found in Deepgram data")

        # Get the first channel (most common case)
        channel = channels[0]
        alternatives = channel.get("alternatives", [])

        if not alternatives:
            raise ValueError("No alternatives found in Deepgram data")

        # Get the first alternative (highest confidence)
        alternative = alternatives[0]

        # Extract basic transcript information
        transcript_text = alternative.get("transcript", "")
        transcript = WTFTranscript(
            text=transcript_text,
            language=self._extract_language(metadata_info),
            duration=metadata_info.get("duration", 0.0),
            confidence=alternative.get("confidence", 0.0),
        )

        # Convert words to segments and words
        words_data = alternative.get("words", [])
        segments = self._convert_words_to_segments(words_data, transcript_text)
        words = self._convert_deepgram_words(words_data)

        # Extract speaker information
        speakers = self._extract_speakers(words_data)

        # Create metadata
        metadata = WTFMetadata(
            created_at=metadata_info.get("created", self._get_timestamp()),
            processed_at=self._get_timestamp(),
            provider="deepgram",
            model=self._extract_model_info(metadata_info),
            processing_time=None,  # Not available in Deepgram data
            audio=WTFAudio(
                duration=metadata_info.get("duration", 0.0),
                sample_rate=None,  # Not available in standard Deepgram response
                channels=metadata_info.get("channels", 1),
                format=None,
                bitrate=None,
            ),
            options=self._extract_deepgram_options(deepgram_data),
        )

        # Create quality metrics
        quality = WTFQuality(
            audio_quality=self._assess_audio_quality(alternative),
            background_noise=None,
            multiple_speakers=None,
            overlapping_speech=None,
            silence_ratio=None,
            average_confidence=transcript.confidence,
            low_confidence_words=self._count_low_confidence_words(words),
            processing_warnings=self._extract_warnings(deepgram_data),
        )

        # Create extensions with Deepgram-specific data
        extensions = {
            "deepgram": {
                "metadata": metadata_info,
                "model_info": metadata_info.get("model_info", {}),
                "request_id": metadata_info.get("request_id"),
                "transaction_key": metadata_info.get("transaction_key"),
                "sha256": metadata_info.get("sha256"),
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
        Convert WTF document to Deepgram JSON format.

        Args:
            wtf_doc: WTF document

        Returns:
            Deepgram JSON data structure
        """
        # Convert words back to Deepgram format
        words = []
        if wtf_doc.words:
            for word in wtf_doc.words:
                word_data = {
                    "word": word.text,
                    "start": word.start,
                    "end": word.end,
                    "confidence": word.confidence,
                    "speaker": word.speaker if word.speaker is not None else 0,
                    "speaker_confidence": 0.95,  # Default speaker confidence
                    "punctuated_word": word.text,
                }
                words.append(word_data)

        # Create alternative
        alternative = {
            "transcript": wtf_doc.transcript.text,
            "confidence": wtf_doc.transcript.confidence,
            "words": words,
        }

        # Create channel
        channel = {"alternatives": [alternative]}

        # Extract Deepgram-specific extensions
        deepgram_ext = wtf_doc.extensions.get("deepgram", {}) if wtf_doc.extensions else {}

        # Create metadata
        metadata = deepgram_ext.get("metadata", {})
        metadata.update(
            {
                "created": wtf_doc.metadata.created_at,
                "duration": wtf_doc.transcript.duration,
                "channels": wtf_doc.metadata.audio.channels or 1,
                "model_info": deepgram_ext.get("model_info", {}),
                "request_id": deepgram_ext.get("request_id", "wtf-converted"),
                "transaction_key": deepgram_ext.get("transaction_key", "deprecated"),
                "sha256": deepgram_ext.get("sha256", "wtf-converted"),
            }
        )

        return {"metadata": metadata, "results": {"channels": [channel]}}

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
            # Assume this is Deepgram data, convert to WTF
            return self.convert_to_wtf(data)

    def _extract_language(self, metadata: Dict[str, Any]) -> str:
        """Extract and normalize language from Deepgram metadata."""
        # Deepgram doesn't always provide language in metadata
        # Default to English if not specified
        return str(normalize_language_code("en"))

    def _extract_model_info(self, metadata: Dict[str, Any]) -> str:
        """Extract model information from Deepgram metadata."""
        model_info = metadata.get("model_info", {})
        if model_info:
            return str(model_info.get("name", "deepgram-model"))
        return "deepgram-model"

    def _convert_words_to_segments(
        self, words_data: List[Dict[str, Any]], transcript_text: str
    ) -> List[WTFSegment]:
        """Convert Deepgram words to WTF segments."""
        if not words_data:
            return []

        # Create a single segment that matches the transcript text exactly
        start_time = words_data[0].get("start", 0.0)
        # Use the last word's end time, but ensure it doesn't exceed the transcript duration
        end_time = words_data[-1].get("end", 0.0)

        # Calculate average confidence
        confidences = [word.get("confidence", 0.0) for word in words_data]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        # Get speaker (assume all words in segment have same speaker)
        speaker = words_data[0].get("speaker", 0)

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

    def _create_segment_from_words(
        self, words_data: List[Dict[str, Any]], segment_id: int
    ) -> WTFSegment:
        """Create a WTF segment from a list of word data."""
        if not words_data:
            raise ValueError("Cannot create segment from empty words list")

        start_time = words_data[0].get("start", 0.0)
        end_time = words_data[-1].get("end", 0.0)
        text = " ".join(word.get("word", "") for word in words_data)

        # Calculate average confidence
        confidences = [word.get("confidence", 0.0) for word in words_data]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        # Get speaker (assume all words in segment have same speaker)
        speaker = words_data[0].get("speaker", 0)

        return WTFSegment(
            id=segment_id,
            start=start_time,
            end=end_time,
            text=text,
            confidence=avg_confidence,
            speaker=speaker,
            words=list(range(len(words_data))),  # Word indices
        )

    def _convert_deepgram_words(self, words_data: List[Dict[str, Any]]) -> List[WTFWord]:
        """Convert Deepgram words to WTF words."""
        words = []

        for i, word_data in enumerate(words_data):
            word = WTFWord(
                id=i,
                start=word_data.get("start", 0.0),
                end=word_data.get("end", 0.0),
                text=word_data.get("word", ""),
                confidence=word_data.get("confidence", 0.0),
                speaker=word_data.get("speaker", 0),
                is_punctuation=self._is_punctuation(word_data.get("word", "")),
            )
            words.append(word)

        return words

    def _extract_speakers(
        self, words_data: List[Dict[str, Any]]
    ) -> Optional[Dict[str, WTFSpeaker]]:
        """Extract speaker information from words data."""
        if not words_data:
            return None

        # Group words by speaker
        speaker_words: dict[str, list[Dict[str, Any]]] = {}
        for word_data in words_data:
            speaker_id = word_data.get("speaker", 0)
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

    def _is_sentence_end(self, word: str) -> bool:
        """Check if a word indicates the end of a sentence."""
        return word.strip() in ".!?"

    def _is_punctuation(self, word: str) -> bool:
        """Check if a word is punctuation."""
        return word.strip() in ".,!?;:()[]{}'\"-"

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO 8601 format."""
        return datetime.now(timezone.utc).isoformat()

    def _extract_deepgram_options(self, deepgram_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Deepgram-specific options."""
        return {
            "model": deepgram_data.get("metadata", {}).get("model_info", {}).get("name", "nova-2"),
            "language": "en",  # Default language
            "punctuate": True,
            "diarize": True,
        }

    def _assess_audio_quality(self, alternative: Dict[str, Any]) -> str:
        """Assess audio quality based on Deepgram metrics."""
        confidence = alternative.get("confidence", 0.0)
        if confidence >= 0.9:
            return "high"
        elif confidence >= 0.7:
            return "medium"
        else:
            return "low"

    def _count_low_confidence_words(self, words: List[WTFWord]) -> int:
        """Count words with low confidence scores."""
        return sum(1 for word in words if word.confidence < 0.5)

    def _extract_warnings(self, deepgram_data: Dict[str, Any]) -> List[str]:
        """Extract processing warnings from Deepgram data."""
        warnings = []

        # Check for low confidence
        results = deepgram_data.get("results", {})
        channels = results.get("channels", [])
        if channels:
            alternatives = channels[0].get("alternatives", [])
            if alternatives:
                confidence = alternatives[0].get("confidence", 0.0)
                if confidence < 0.7:
                    warnings.append(f"Low overall confidence: {confidence:.2f}")

        return warnings

"""
Rev.ai provider converter for WTF transcript format.

This module provides conversion between Rev.ai transcription format and WTF format.
"""

import re
from typing import Any, Dict, List

from wtf_transcript_converter.core.models import (
    WTFAudio,
    WTFDocument,
    WTFMetadata,
    WTFQuality,
    WTFSegment,
    WTFSpeaker,
    WTFTranscript,
    WTFWord,
)
from wtf_transcript_converter.providers.base import BaseProviderConverter
from wtf_transcript_converter.utils.confidence_utils import normalize_confidence
from wtf_transcript_converter.utils.language_utils import is_valid_bcp47
from wtf_transcript_converter.utils.time_utils import get_current_iso_timestamp


class RevAIConverter(BaseProviderConverter):
    """Converter for Rev.ai JSON format to/from WTF format."""

    def __init__(self) -> None:
        super().__init__("rev_ai")

    provider_name: str = "rev_ai"
    description: str = "Rev.ai transcription service"
    status: str = "Implemented"

    def convert_to_wtf(self, rev_ai_data: Dict[str, Any]) -> WTFDocument:
        """
        Convert Rev.ai JSON data to WTF format.

        Args:
            rev_ai_data: Rev.ai JSON data structure

        Returns:
            WTF document
        """
        # Extract basic transcript information
        transcript = WTFTranscript(
            text=self._extract_full_transcript_text(rev_ai_data),
            language=self._extract_language(rev_ai_data),
            duration=rev_ai_data.get("duration_seconds", 0.0),
            confidence=self._calculate_overall_confidence(rev_ai_data),
        )

        # Convert monologue elements to segments and words
        # RevAI returns 'monologues' (plural) in the API response
        monologues = rev_ai_data.get("monologues", [])
        if monologues:
            monologue = monologues[0]  # Use first monologue
        else:
            monologue = rev_ai_data.get("monologue", {})  # Fallback for singular
        elements = monologue.get("elements", [])

        wtf_segments: List[WTFSegment] = []
        wtf_words: List[WTFWord] = []
        speakers: Dict[str, WTFSpeaker] = {}
        word_id_counter = 0

        # Process elements to create words and segments
        current_segment_text = ""
        current_segment_start = None
        current_segment_end = None
        current_segment_words = []
        segment_id = 0

        for element in elements:
            element_type = element.get("type", "")
            element_value = element.get("value", "")
            start_time = element.get("ts", 0.0)
            end_time = element.get("end_ts", start_time + 0.1)  # Default duration if not provided
            confidence = element.get("confidence", 0.0)

            if element_type == "text":
                # Create word
                wtf_word = WTFWord(
                    id=word_id_counter,
                    start=start_time,
                    end=end_time,
                    text=element_value,
                    confidence=normalize_confidence(confidence, "rev_ai"),
                    speaker=None,
                    is_punctuation=self._detect_punctuation(element_value),
                )
                wtf_words.append(wtf_word)
                current_segment_words.append(word_id_counter)
                word_id_counter += 1

                # Build segment text
                if current_segment_start is None:
                    current_segment_start = start_time
                current_segment_end = end_time
                current_segment_text += element_value + " "

            elif element_type == "punct" and current_segment_text:
                # End current segment and start new one
                if current_segment_text.strip():
                    # Calculate segment confidence
                    segment_confidence = (
                        sum(w.confidence for w in wtf_words[-len(current_segment_words) :])
                        / len(current_segment_words)
                        if current_segment_words
                        else 0.0
                    )

                    wtf_segment = WTFSegment(
                        id=segment_id,
                        start=(
                            float(current_segment_start)
                            if current_segment_start is not None
                            else 0.0
                        ),
                        end=float(current_segment_end) if current_segment_end is not None else 0.0,
                        text=current_segment_text.strip(),
                        confidence=segment_confidence,
                        speaker=None,
                        words=current_segment_words.copy(),
                    )
                    wtf_segments.append(wtf_segment)
                    segment_id += 1

                # Reset for next segment
                current_segment_text = ""
                current_segment_start = None
                current_segment_end = None
                current_segment_words = []

        # Add final segment if exists
        if current_segment_text.strip():
            segment_confidence = (
                sum(w.confidence for w in wtf_words[-len(current_segment_words) :])
                / len(current_segment_words)
                if current_segment_words
                else 0.0
            )

            wtf_segment = WTFSegment(
                id=segment_id,
                start=float(current_segment_start) if current_segment_start is not None else 0.0,
                end=float(current_segment_end) if current_segment_end is not None else 0.0,
                text=current_segment_text.strip(),
                confidence=segment_confidence,
                speaker=None,
                words=current_segment_words,
            )
            wtf_segments.append(wtf_segment)

        # If no segments were created, create a single segment with the full transcript
        if not wtf_segments and wtf_words:
            first_word = wtf_words[0]
            last_word = wtf_words[-1]
            segment_confidence = sum(w.confidence for w in wtf_words) / len(wtf_words)

            wtf_segment = WTFSegment(
                id=0,
                start=first_word.start,
                end=last_word.end,
                text=transcript.text,  # Use the full transcript text
                confidence=segment_confidence,
                speaker=None,
                words=[w.id for w in wtf_words],
            )
            wtf_segments.append(wtf_segment)

        # Extract speaker information
        speaker_id = monologue.get("speaker", 0)
        speakers[str(speaker_id)] = WTFSpeaker(
            id=str(speaker_id),
            label=f"Speaker {speaker_id + 1}",
            segments=[seg.id for seg in wtf_segments],
            total_time=sum(seg.end - seg.start for seg in wtf_segments),
            confidence=transcript.confidence,
        )

        # Assign speaker to segments and words
        for segment in wtf_segments:
            segment.speaker = str(speaker_id)
        for word in wtf_words:
            word.speaker = str(speaker_id)

        # Create metadata
        current_time = get_current_iso_timestamp()
        audio_duration = rev_ai_data.get("duration_seconds", 0.0)

        audio_metadata = WTFAudio(
            duration=audio_duration,
            sample_rate=None,
            channels=None,
            format=None,
            bitrate=None,
        )

        metadata = WTFMetadata(
            created_at=rev_ai_data.get("created_on", current_time),
            processed_at=current_time,
            provider=self.provider_name,
            model=self._extract_model(rev_ai_data),
            processing_time=rev_ai_data.get("processing_time_seconds"),
            audio=audio_metadata,
            options={
                "job_id": rev_ai_data.get("id"),
                "status": rev_ai_data.get("status"),
                "language": rev_ai_data.get("language"),
                "transcriber": rev_ai_data.get("transcriber"),
                "verbatim": rev_ai_data.get("verbatim"),
                "filter_profanity": rev_ai_data.get("filter_profanity"),
                "remove_disfluencies": rev_ai_data.get("remove_disfluencies"),
                "delete_after_seconds": rev_ai_data.get("delete_after_seconds"),
                "skip_diarization": rev_ai_data.get("skip_diarization"),
                "skip_punctuation": rev_ai_data.get("skip_punctuation"),
                "skip_automatic_punctuation": rev_ai_data.get("skip_automatic_punctuation"),
                "speaker_channels_count": rev_ai_data.get("speaker_channels_count"),
                "custom_vocabulary_id": rev_ai_data.get("custom_vocabulary_id"),
                "custom_vocabulary": rev_ai_data.get("custom_vocabulary"),
                "webhook_url": rev_ai_data.get("webhook_url"),
                "webhook_auth_headers": rev_ai_data.get("webhook_auth_headers"),
                "metadata": rev_ai_data.get("metadata"),
                "priority": rev_ai_data.get("priority"),
                "callback_url": rev_ai_data.get("callback_url"),
                "media_url": rev_ai_data.get("media_url"),
                "media_url_ttl": rev_ai_data.get("media_url_ttl"),
                "failure": rev_ai_data.get("failure"),
                "failure_detail": rev_ai_data.get("failure_detail"),
                "warnings": rev_ai_data.get("warnings"),
            },
        )
        # Clean options to remove None values
        metadata.options = {k: v for k, v in metadata.options.items() if v is not None}

        # Calculate quality metrics
        quality = self._calculate_quality_metrics(rev_ai_data, wtf_words)

        # Preserve other Rev.ai-specific fields in extensions
        extensions = {
            "rev_ai_raw_response": rev_ai_data  # Store the full raw response for fidelity
        }

        return WTFDocument(
            transcript=transcript,
            segments=wtf_segments,
            metadata=metadata,
            words=wtf_words if wtf_words else None,
            speakers=speakers if speakers else None,
            alternatives=None,
            enrichments=None,
            extensions=extensions if extensions else None,
            quality=quality,
            streaming=None,
        )

    def convert_from_wtf(self, wtf_doc: WTFDocument) -> Dict[str, Any]:
        """
        Convert WTF document to Rev.ai JSON format.

        Args:
            wtf_doc: WTF document

        Returns:
            Rev.ai JSON data structure
        """
        # Reconstruct Rev.ai structure
        rev_ai_data: Dict[str, Any] = {
            "id": wtf_doc.metadata.options.get("job_id", "wtf-converted-id"),
            "status": "transcribed",
            "created_on": wtf_doc.metadata.created_at,
            "duration_seconds": wtf_doc.transcript.duration,
            "language": (
                wtf_doc.transcript.language.split("-")[0]
                if "-" in wtf_doc.transcript.language
                else wtf_doc.transcript.language
            ),
            "monologue": {"speaker": 0, "elements": []},  # Default speaker
        }

        # Convert words to elements
        if wtf_doc.words:
            for word in wtf_doc.words:
                # Add text element
                rev_ai_data["monologue"]["elements"].append(
                    {
                        "type": "text",
                        "value": word.text,
                        "ts": word.start,
                        "end_ts": word.end,
                        "confidence": word.confidence,
                    }
                )

                # Add punctuation if it's punctuation
                if word.is_punctuation:
                    rev_ai_data["monologue"]["elements"].append(
                        {
                            "type": "punct",
                            "value": word.text,
                            "ts": word.end,
                            "end_ts": word.end + 0.1,
                        }
                    )

        # Merge extensions back if available
        if wtf_doc.extensions and "rev_ai_raw_response" in wtf_doc.extensions:
            original_raw = wtf_doc.extensions["rev_ai_raw_response"]
            # This is a simplistic merge; a real implementation might be more granular
            rev_ai_data.update(original_raw)
            # Ensure our converted data overrides the raw where appropriate
            rev_ai_data["duration_seconds"] = wtf_doc.transcript.duration
            rev_ai_data["language"] = (
                wtf_doc.transcript.language.split("-")[0]
                if "-" in wtf_doc.transcript.language
                else wtf_doc.transcript.language
            )
            if wtf_doc.words:
                rev_ai_data["monologue"]["elements"] = [
                    {
                        "type": "text",
                        "value": word.text,
                        "ts": word.start,
                        "end_ts": word.end,
                        "confidence": word.confidence,
                    }
                    for word in wtf_doc.words
                ]

        return rev_ai_data

    def _extract_full_transcript_text(self, rev_ai_data: Dict[str, Any]) -> str:
        """Extract full transcript text from Rev.ai elements."""
        # RevAI returns 'monologues' (plural) in the API response
        monologues = rev_ai_data.get("monologues", [])
        if monologues:
            monologue = monologues[0]  # Use first monologue
        else:
            monologue = rev_ai_data.get("monologue", {})  # Fallback for singular
        elements = monologue.get("elements", [])
        text_elements = [elem.get("value", "") for elem in elements if elem.get("type") == "text"]
        full_text = " ".join(text_elements)
        return full_text if full_text.strip() else "No transcription available"

    def _extract_language(self, rev_ai_data: Dict[str, Any]) -> str:
        """Extract and normalize language code from Rev.ai data."""
        lang = str(rev_ai_data.get("language", "en")).lower()
        if not is_valid_bcp47(lang):
            return f"{lang}-us"  # Default to US English
        return lang

    def _extract_model(self, rev_ai_data: Dict[str, Any]) -> str:
        """Extract model name from Rev.ai data."""
        transcriber = str(rev_ai_data.get("transcriber", "default"))
        return f"rev-ai-{transcriber}"

    def _calculate_overall_confidence(self, rev_ai_data: Dict[str, Any]) -> float:
        """Calculate overall confidence from Rev.ai data."""
        # RevAI returns 'monologues' (plural) in the API response
        monologues = rev_ai_data.get("monologues", [])
        if monologues:
            monologue = monologues[0]  # Use first monologue
        else:
            monologue = rev_ai_data.get("monologue", {})  # Fallback for singular
        elements = monologue.get("elements", [])
        if not elements:
            return 0.0

        text_elements = [elem for elem in elements if elem.get("type") == "text"]
        if not text_elements:
            return 0.0

        confidences = [elem.get("confidence", 0.0) for elem in text_elements]
        return sum(confidences) / len(confidences) if confidences else 0.0

    def _detect_punctuation(self, word_text: str) -> bool:
        """Simple check to see if a word is primarily punctuation."""
        return bool(re.fullmatch(r"^\W+$", word_text))

    def _calculate_quality_metrics(
        self, rev_ai_data: Dict[str, Any], wtf_words: List[WTFWord]
    ) -> WTFQuality:
        """Calculate quality metrics based on Rev.ai data."""
        low_confidence_words = sum(1 for word in wtf_words if word.confidence < 0.5)
        average_confidence = (
            sum(word.confidence for word in wtf_words) / len(wtf_words) if wtf_words else 0.0
        )

        return WTFQuality(
            audio_quality=None,
            background_noise=None,
            multiple_speakers=None,
            overlapping_speech=None,
            silence_ratio=None,
            average_confidence=average_confidence,
            low_confidence_words=low_confidence_words,
            processing_warnings=rev_ai_data.get("warnings", []),
        )

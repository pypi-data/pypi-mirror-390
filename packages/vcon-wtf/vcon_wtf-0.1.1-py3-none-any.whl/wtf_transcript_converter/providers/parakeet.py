"""
Parakeet provider converter implementation.

This module provides conversion between Parakeet (NVIDIA NeMo) transcription format and WTF.
"""

import os
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
from wtf_transcript_converter.utils.language_utils import normalize_language_code
from wtf_transcript_converter.utils.time_utils import get_current_iso_timestamp

try:
    import librosa
    import torch
    from transformers import pipeline

    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False


class ParakeetConverter(BaseProviderConverter):
    """
    Converter for Parakeet (NVIDIA NeMo) transcription format to/from WTF.
    """

    provider_name: str = "parakeet"
    description: str = "NVIDIA Parakeet speech recognition via Hugging Face"
    status: str = "Implemented"

    def __init__(
        self,
        provider_name: str = "parakeet",
        model_name: str = "nvidia/parakeet-tdt-0.6b-v3",
    ) -> None:
        super().__init__(provider_name)
        self.model_name = model_name
        self._pipeline = None
        self._tokenizer = None
        self._model = None

    def _load_model(self) -> None:
        """Load the Parakeet model and tokenizer."""
        if not HF_AVAILABLE:
            raise ImportError(
                "Hugging Face transformers, torch, librosa, and soundfile are required for Parakeet support"
            )

        if self._pipeline is None:
            # Set Hugging Face token if available
            hf_token = os.getenv("HF_TOKEN")
            if hf_token:
                os.environ["HUGGINGFACE_HUB_TOKEN"] = hf_token

            try:
                # Load the ASR pipeline
                self._pipeline = pipeline(
                    "automatic-speech-recognition",
                    model=self.model_name,
                    token=hf_token,
                    device=0 if torch.cuda.is_available() else -1,
                )
            except Exception as e:
                raise RuntimeError(f"Failed to load Parakeet model {self.model_name}: {e}")

    def transcribe_audio(self, audio_path: str, language: str = "en") -> Dict[str, Any]:
        """
        Transcribe audio file using Parakeet model.

        Args:
            audio_path: Path to audio file
            language: Language code (e.g., 'en', 'es', 'fr')

        Returns:
            Parakeet transcription result
        """
        self._load_model()

        try:
            # Load and preprocess audio
            audio, sample_rate = librosa.load(audio_path, sr=16000)

            # Transcribe using the pipeline
            if self._pipeline is None:
                raise RuntimeError("Pipeline not loaded")
            result = self._pipeline(
                audio,
                return_timestamps=True,
                chunk_length_s=30,
                stride_length_s=5,
                language=language,
            )

            # Convert to our expected format
            return self._format_parakeet_result(result, audio_path, sample_rate)

        except Exception as e:
            raise RuntimeError(f"Parakeet transcription failed: {e}")

    def _format_parakeet_result(
        self, result: Dict[str, Any], audio_path: str, sample_rate: int
    ) -> Dict[str, Any]:
        """Format Parakeet pipeline result to our expected structure."""
        text = result.get("text", "")
        chunks = result.get("chunks", [])

        # Calculate duration
        duration = len(result.get("raw", [])) / sample_rate if "raw" in result else 0.0

        # Extract words and segments
        words = []
        segments = []
        word_id = 0
        segment_id = 0

        for chunk in chunks:
            chunk_text = chunk.get("text", "").strip()
            chunk_start = chunk.get("timestamp", [0.0, 0.0])[0]
            chunk_end = chunk.get("timestamp", [0.0, 0.0])[1]

            if chunk_text:
                # Create segment
                segment = {
                    "id": segment_id,
                    "start": chunk_start,
                    "end": chunk_end,
                    "text": chunk_text,
                    "confidence": 0.9,  # Default confidence
                }
                segments.append(segment)

                # Split into words
                chunk_words = chunk_text.split()
                segment_word_ids = []

                for word_text in chunk_words:
                    if word_text.strip():
                        word = {
                            "id": word_id,
                            "start": chunk_start
                            + (word_id * (chunk_end - chunk_start) / len(chunk_words)),
                            "end": chunk_start
                            + ((word_id + 1) * (chunk_end - chunk_start) / len(chunk_words)),
                            "text": word_text.strip(),
                            "confidence": 0.9,
                        }
                        words.append(word)
                        segment_word_ids.append(word_id)
                        word_id += 1

                segment["words"] = segment_word_ids
                segment_id += 1

        return {
            "text": text,
            "language": "en",  # Default, could be extracted from model
            "duration": duration,
            "words": words,
            "segments": segments,
            "model": self.model_name,
            "audio_path": audio_path,
            "sample_rate": sample_rate,
        }

    def convert_to_wtf(self, parakeet_data: Dict[str, Any]) -> WTFDocument:
        """
        Convert Parakeet JSON data to WTF format.

        Args:
            parakeet_data: Parakeet JSON data structure

        Returns:
            WTF document
        """
        # Extract basic transcript information
        text = parakeet_data.get("text", "").strip()
        if not text:
            text = "[Empty transcript]"  # Use a meaningful placeholder for empty transcripts

        transcript = WTFTranscript(
            text=text,
            language=normalize_language_code(parakeet_data.get("language", "en")),
            duration=parakeet_data.get("duration", 0.0),
            confidence=self._calculate_overall_confidence(parakeet_data),
        )

        # Convert words
        words_data = parakeet_data.get("words", [])
        wtf_words = self._convert_parakeet_words(words_data)

        # Convert segments
        segments_data = parakeet_data.get("segments", [])
        wtf_segments = self._convert_parakeet_segments(segments_data, wtf_words)

        # Extract speaker information (Parakeet doesn't do diarization by default)
        speakers = self._extract_speakers(words_data)

        # Create metadata
        current_time = get_current_iso_timestamp()
        audio_duration = parakeet_data.get("duration", 0.0)

        audio_metadata = WTFAudio(
            duration=audio_duration,
            sample_rate=parakeet_data.get("sample_rate", 16000),
            channels=None,
            format=None,
            bitrate=None,
        )

        metadata = WTFMetadata(
            created_at=current_time,
            processed_at=current_time,
            provider=self.provider_name,
            model=parakeet_data.get("model", self.model_name),
            processing_time=None,
            audio=audio_metadata,
            options={
                "audio_path": parakeet_data.get("audio_path"),
                "model_name": self.model_name,
                "chunk_length_s": 30,
                "stride_length_s": 5,
            },
        )
        # Clean options to remove None values
        metadata.options = {k: v for k, v in metadata.options.items() if v is not None}

        # Calculate quality metrics
        quality = self._calculate_quality_metrics(parakeet_data, wtf_words)

        # Preserve other Parakeet-specific fields in extensions
        extensions = {"parakeet_raw_response": parakeet_data}

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
        Convert WTF document to Parakeet JSON format.

        Args:
            wtf_doc: WTF document

        Returns:
            Parakeet JSON data structure
        """
        parakeet_data: Dict[str, Any] = {
            "text": wtf_doc.transcript.text,
            "language": (
                wtf_doc.transcript.language.split("-")[0]
                if "-" in wtf_doc.transcript.language
                else wtf_doc.transcript.language
            ),
            "duration": wtf_doc.transcript.duration,
            "model": wtf_doc.metadata.model,
            "words": [],
            "segments": [],
        }

        # Convert words
        if wtf_doc.words:
            for word in wtf_doc.words:
                parakeet_data["words"].append(
                    {
                        "id": word.id,
                        "start": word.start,
                        "end": word.end,
                        "text": word.text,
                        "confidence": word.confidence,
                    }
                )

        # Convert segments
        if wtf_doc.segments:
            for segment in wtf_doc.segments:
                parakeet_data["segments"].append(
                    {
                        "id": segment.id,
                        "start": segment.start,
                        "end": segment.end,
                        "text": segment.text,
                        "confidence": segment.confidence,
                        "words": segment.words or [],
                    }
                )

        # Merge extensions back if available
        if wtf_doc.extensions and "parakeet_raw_response" in wtf_doc.extensions:
            original_raw = wtf_doc.extensions["parakeet_raw_response"]
            parakeet_data.update(original_raw)
            # Ensure our converted data overrides the raw where appropriate
            parakeet_data["text"] = wtf_doc.transcript.text
            parakeet_data["duration"] = wtf_doc.transcript.duration
            parakeet_data["language"] = wtf_doc.transcript.language.split("-")[0]

        return parakeet_data

    def _calculate_overall_confidence(self, parakeet_data: Dict[str, Any]) -> float:
        """Calculate overall confidence from Parakeet data."""
        words = parakeet_data.get("words", [])
        if not words:
            return 0.0

        confidences = [float(word.get("confidence", 0.0)) for word in words]
        return float(sum(confidences) / len(confidences))

    def _extract_speakers(self, words_data: List[Dict[str, Any]]) -> Dict[str, WTFSpeaker]:
        """Extract speaker information from Parakeet words data."""
        # Parakeet doesn't do speaker diarization by default
        # Return a single default speaker
        if not words_data:
            return {}

        # Calculate total speaking time
        total_time = sum(word.get("end", 0.0) - word.get("start", 0.0) for word in words_data)

        return {
            "0": WTFSpeaker(
                id="0",
                label="Speaker 1",
                segments=[0],  # Default segment
                total_time=total_time,
                confidence=0.9,  # Default confidence
            )
        }

    def _convert_parakeet_words(self, words_data: List[Dict[str, Any]]) -> List[WTFWord]:
        """Convert Parakeet words to WTF words."""
        words = []
        for word_data in words_data:
            word_text = word_data.get("text", "").strip()
            if not word_text:
                continue

            wtf_word = WTFWord(
                id=word_data.get("id", 0),
                start=word_data.get("start", 0.0),
                end=word_data.get("end", 0.0),
                text=word_text,
                confidence=normalize_confidence(
                    word_data.get("confidence", 0.0), self.provider_name
                ),
                speaker="0",  # Default speaker
                is_punctuation=self._detect_punctuation(word_text),
            )
            words.append(wtf_word)
        return words

    def _convert_parakeet_segments(
        self, segments_data: List[Dict[str, Any]], wtf_words: List[WTFWord]
    ) -> List[WTFSegment]:
        """Convert Parakeet segments to WTF segments."""
        segments = []
        for segment_data in segments_data:
            segment = WTFSegment(
                id=segment_data.get("id", 0),
                start=segment_data.get("start", 0.0),
                end=segment_data.get("end", 0.0),
                text=segment_data.get("text", ""),
                confidence=normalize_confidence(
                    segment_data.get("confidence", 0.0), self.provider_name
                ),
                speaker="0",  # Default speaker
                words=segment_data.get("words", []),
            )
            segments.append(segment)
        return segments

    def _detect_punctuation(self, word_text: str) -> bool:
        """Simple check to see if a word is primarily punctuation."""
        return bool(re.fullmatch(r"^\W+$", word_text))

    def _calculate_quality_metrics(
        self, parakeet_data: Dict[str, Any], wtf_words: List[WTFWord]
    ) -> WTFQuality:
        """Calculate quality metrics based on Parakeet data."""
        low_confidence_words = sum(1 for word in wtf_words if word.confidence < 0.5)
        average_confidence = (
            sum(word.confidence for word in wtf_words) / len(wtf_words) if wtf_words else 0.0
        )

        return WTFQuality(
            audio_quality=(
                "high"
                if average_confidence > 0.8
                else "medium" if average_confidence > 0.6 else "low"
            ),
            background_noise=None,
            multiple_speakers=None,
            overlapping_speech=None,
            silence_ratio=None,
            average_confidence=average_confidence,
            low_confidence_words=low_confidence_words,
            processing_warnings=[],
        )

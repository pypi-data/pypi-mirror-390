"""
Core WTF data models.

This module contains Pydantic models for the World Transcription Format (WTF).
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator


class WTFTranscript(BaseModel):
    """Core transcript information following WTF specification."""

    text: str = Field(..., description="Complete transcription text")
    language: str = Field(..., description="BCP-47 language code (e.g., 'en-US')")
    duration: float = Field(..., ge=0, description="Total audio duration in seconds")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Overall confidence score [0.0-1.0]"
    )

    @field_validator("language")
    @classmethod
    def validate_language_code(cls, v: str) -> str:
        """Validate BCP-47 language code format."""
        # Basic BCP-47 validation pattern
        pattern = r"^[a-z]{2,3}(-[A-Z]{2})?(-[a-z0-9]{5,8})?(-[a-z0-9]{1,8})*(-[a-z0-9]{1,8})*$"
        if not re.match(pattern, v.lower()):
            raise ValueError(f"Invalid BCP-47 language code: {v}")
        return v.lower()

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Validate and clean transcript text."""
        if not v or not v.strip():
            raise ValueError("Transcript text cannot be empty")
        return v.strip()


class WTFSegment(BaseModel):
    """Individual transcript segment with timing information."""

    id: int = Field(..., description="Sequential segment identifier")
    start: float = Field(..., ge=0, description="Start time in seconds")
    end: float = Field(..., ge=0, description="End time in seconds")
    text: str = Field(..., description="Segment text content")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Segment-level confidence [0.0-1.0]"
    )
    speaker: Optional[Union[int, str]] = Field(None, description="Speaker identifier")
    words: Optional[List[int]] = Field(None, description="Array of word indices")

    @model_validator(mode="after")
    def validate_timing(self) -> "WTFSegment":
        """Validate that end time is after start time."""
        if self.end <= self.start:
            raise ValueError(
                f"Segment {self.id}: end time ({self.end}) must be after start time ({self.start})"
            )
        return self

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Validate and clean segment text."""
        if not v or not v.strip():
            raise ValueError("Segment text cannot be empty")
        return v.strip()


class WTFWord(BaseModel):
    """Word-level transcription data."""

    id: int = Field(..., description="Sequential word identifier")
    start: float = Field(..., ge=0, description="Word start time in seconds")
    end: float = Field(..., ge=0, description="Word end time in seconds")
    text: str = Field(..., description="Word text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Word-level confidence [0.0-1.0]")
    speaker: Optional[Union[int, str]] = Field(None, description="Speaker identifier")
    is_punctuation: Optional[bool] = Field(None, description="Punctuation marker")

    @model_validator(mode="after")
    def validate_timing(self) -> "WTFWord":
        """Validate that end time is after start time."""
        if self.end <= self.start:
            raise ValueError(
                f"Word {self.id}: end time ({self.end}) must be after start time ({self.start})"
            )
        return self

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Validate and clean word text."""
        if not v or not v.strip():
            raise ValueError("Word text cannot be empty")
        return v.strip()


class WTFSpeaker(BaseModel):
    """Speaker information for diarization."""

    id: Union[int, str] = Field(..., description="Speaker identifier")
    label: str = Field(..., description="Human-readable speaker name")
    segments: List[int] = Field(..., description="Array of segment IDs for this speaker")
    total_time: float = Field(..., ge=0, description="Total speaking time in seconds")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Diarization confidence [0.0-1.0]")


class WTFAudio(BaseModel):
    """Audio metadata information."""

    duration: float = Field(..., ge=0, description="Source audio duration in seconds")
    sample_rate: Optional[int] = Field(None, description="Sample rate in Hz")
    channels: Optional[int] = Field(None, description="Number of channels")
    format: Optional[str] = Field(None, description="Audio format")
    bitrate: Optional[int] = Field(None, description="Bitrate in kbps")


class WTFMetadata(BaseModel):
    """Processing metadata information."""

    created_at: str = Field(..., description="ISO 8601 timestamp")
    processed_at: str = Field(..., description="ISO 8601 timestamp")
    provider: str = Field(..., description="Provider name (lowercase)")
    model: str = Field(..., description="Model/version identifier")
    processing_time: Optional[float] = Field(
        None, ge=0, description="Processing duration in seconds"
    )
    audio: WTFAudio = Field(..., description="Audio metadata")
    options: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific options")

    @field_validator("created_at", "processed_at")
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        """Validate ISO 8601 timestamp format."""
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError(f"Invalid ISO 8601 timestamp: {v}")
        return v

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """Validate and normalize provider name."""
        if not v or not v.strip():
            raise ValueError("Provider name cannot be empty")
        return v.strip().lower()

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: str) -> str:
        """Validate model identifier."""
        if not v or not v.strip():
            raise ValueError("Model identifier cannot be empty")
        return v.strip()


class WTFQuality(BaseModel):
    """Quality metrics for the transcription."""

    audio_quality: Optional[str] = Field(None, description="high, medium, low")
    background_noise: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Noise level [0.0-1.0]"
    )
    multiple_speakers: Optional[bool] = Field(None, description="Multiple speakers indicator")
    overlapping_speech: Optional[bool] = Field(None, description="Overlapping speech indicator")
    silence_ratio: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Percentage of silence"
    )
    average_confidence: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Mean confidence"
    )
    low_confidence_words: Optional[int] = Field(
        None, ge=0, description="Count of low confidence words"
    )
    processing_warnings: List[str] = Field(default_factory=list, description="Processing warnings")


class WTFExtensions(BaseModel):
    """Provider-specific extensions."""

    # This will be populated dynamically based on provider
    pass


class WTFDocument(BaseModel):
    """Complete WTF document structure."""

    transcript: WTFTranscript = Field(..., description="Core transcript information")
    segments: List[WTFSegment] = Field(..., description="Time-aligned text segments")
    metadata: WTFMetadata = Field(..., description="Processing metadata")
    words: Optional[List[WTFWord]] = Field(None, description="Word-level details")
    speakers: Optional[Dict[str, WTFSpeaker]] = Field(None, description="Speaker diarization")
    alternatives: Optional[List[Dict[str, Any]]] = Field(
        None, description="Alternative transcriptions"
    )
    enrichments: Optional[Dict[str, Any]] = Field(None, description="Analysis features")
    extensions: Optional[Dict[str, Any]] = Field(None, description="Provider-specific data")
    quality: Optional[WTFQuality] = Field(None, description="Quality metrics")
    streaming: Optional[Dict[str, Any]] = Field(None, description="Streaming information")

    @model_validator(mode="after")
    def validate_document_consistency(self) -> "WTFDocument":
        """Validate document-level consistency."""
        # Check that segments are properly ordered
        if len(self.segments) > 1:
            for i in range(1, len(self.segments)):
                if self.segments[i].start < self.segments[i - 1].end:
                    raise ValueError(f"Segments {i-1} and {i} have overlapping times")

        # Check that words reference valid segments if provided
        if self.words and self.segments:
            segment_ids = {seg.id for seg in self.segments}
            for word in self.words:
                if hasattr(word, "segment_id") and word.segment_id not in segment_ids:
                    raise ValueError(
                        f"Word {word.id} references invalid segment {word.segment_id}"
                    )

        # Check that speaker references are valid
        if self.speakers and self.segments:
            speaker_ids = set(self.speakers.keys())
            for segment in self.segments:
                if segment.speaker is not None:
                    speaker_key = str(segment.speaker)
                    if speaker_key not in speaker_ids:
                        raise ValueError(
                            f"Segment {segment.id} references invalid speaker {segment.speaker}"
                        )

        return self


# Placeholder for vcon-lib integration
class VConWTFAttachment(BaseModel):
    """Wrapper for WTF transcription as vCon attachment."""

    # TODO: Implement when vcon-lib is available
    pass

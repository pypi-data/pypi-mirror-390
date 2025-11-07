"""
WTF document validation functions.

This module provides validation functions for WTF documents and their components.
"""

import re
from typing import List, Tuple

from .models import WTFDocument


def validate_wtf_document(doc: WTFDocument) -> Tuple[bool, List[str]]:
    """
    Validate a WTF document for compliance with the specification.

    Args:
        doc: WTF document to validate

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Basic validation - Pydantic already handles most of this
    try:
        # Check if document can be serialized
        doc.model_dump()
    except Exception as e:
        errors.append(f"Document serialization error: {str(e)}")

    # Additional custom validations
    errors.extend(_validate_transcript_consistency(doc))
    errors.extend(_validate_timing_consistency(doc))
    errors.extend(_validate_speaker_consistency(doc))
    errors.extend(_validate_word_segment_consistency(doc))
    errors.extend(_validate_confidence_scores(doc))

    return len(errors) == 0, errors


def _validate_transcript_consistency(doc: WTFDocument) -> List[str]:
    """Validate transcript text consistency with segments."""
    errors = []

    # Check that transcript text matches concatenated segment text
    segment_text = " ".join(seg.text for seg in doc.segments)
    if doc.transcript.text.strip() != segment_text.strip():
        errors.append("Transcript text does not match concatenated segment text")

    # Check that transcript duration matches segment timing (with more tolerance for Deepgram)
    if doc.segments:
        max_end_time = max(seg.end for seg in doc.segments)
        # Allow up to 5 seconds tolerance for providers like Deepgram that may have silence at the end
        if abs(doc.transcript.duration - max_end_time) > 5.0:
            errors.append(
                f"Transcript duration ({doc.transcript.duration}) does not match segment timing ({max_end_time})"
            )

    return errors


def _validate_timing_consistency(doc: WTFDocument) -> List[str]:
    """Validate timing consistency across the document."""
    errors = []

    # Check segment timing
    for i, segment in enumerate(doc.segments):
        if segment.start >= segment.end:
            errors.append(
                f"Segment {i}: start time ({segment.start}) must be before end time ({segment.end})"
            )

    # Check for overlapping segments
    for i in range(len(doc.segments) - 1):
        if doc.segments[i].end > doc.segments[i + 1].start:
            errors.append(f"Segments {i} and {i + 1} have overlapping times")

    # Check word timing if available
    if doc.words:
        for word in doc.words:
            if word.start >= word.end:
                errors.append(
                    f"Word {word.id}: start time ({word.start}) must be before end time ({word.end})"
                )

    return errors


def _validate_speaker_consistency(doc: WTFDocument) -> List[str]:
    """Validate speaker consistency across the document."""
    errors: List[str] = []

    if not doc.speakers or not doc.segments:
        return errors

    # Get all speaker IDs from speakers dict
    speaker_ids = set(doc.speakers.keys())

    # Check that all segment speakers are valid
    for segment in doc.segments:
        if segment.speaker is not None:
            speaker_key = str(segment.speaker)
            if speaker_key not in speaker_ids:
                errors.append(f"Segment {segment.id} references invalid speaker {segment.speaker}")

    # Check that all word speakers are valid
    if doc.words:
        for word in doc.words:
            if word.speaker is not None:
                speaker_key = str(word.speaker)
                if speaker_key not in speaker_ids:
                    errors.append(f"Word {word.id} references invalid speaker {word.speaker}")

    return errors


def _validate_word_segment_consistency(doc: WTFDocument) -> List[str]:
    """Validate word-segment consistency."""
    errors: List[str] = []

    if not doc.words or not doc.segments:
        return errors

    # Create mapping of segment IDs to segments
    segment_map = {seg.id: seg for seg in doc.segments}

    # Check that all word references in segments are valid
    for segment in doc.segments:
        if segment.words:
            for word_id in segment.words:
                word = next((w for w in doc.words if w.id == word_id), None)
                if word is None:
                    errors.append(f"Segment {segment.id} references invalid word {word_id}")
                else:
                    # Check that word timing is within segment timing
                    if word.start < segment.start or word.end > segment.end:
                        errors.append(
                            f"Word {word_id} timing is outside segment {segment.id} timing"
                        )

    return errors


def _validate_confidence_scores(doc: WTFDocument) -> List[str]:
    """Validate confidence scores are in valid range."""
    errors = []

    # Check transcript confidence
    if not (0.0 <= doc.transcript.confidence <= 1.0):
        errors.append(
            f"Transcript confidence ({doc.transcript.confidence}) must be between 0.0 and 1.0"
        )

    # Check segment confidence scores
    for segment in doc.segments:
        if not (0.0 <= segment.confidence <= 1.0):
            errors.append(
                f"Segment {segment.id} confidence ({segment.confidence}) must be between 0.0 and 1.0"
            )

    # Check word confidence scores
    if doc.words:
        for word in doc.words:
            if not (0.0 <= word.confidence <= 1.0):
                errors.append(
                    f"Word {word.id} confidence ({word.confidence}) must be between 0.0 and 1.0"
                )

    # Check speaker confidence scores
    if doc.speakers:
        for speaker in doc.speakers.values():
            if not (0.0 <= speaker.confidence <= 1.0):
                errors.append(
                    f"Speaker {speaker.id} confidence ({speaker.confidence}) must be between 0.0 and 1.0"
                )

    return errors


def validate_confidence_score(confidence: float, context: str = "") -> bool:
    """
    Validate that a confidence score is in the valid range [0.0, 1.0].

    Args:
        confidence: Confidence score to validate
        context: Optional context for error messages

    Returns:
        True if valid, False otherwise
    """
    return 0.0 <= confidence <= 1.0


def validate_timestamp(timestamp: str) -> bool:
    """
    Validate ISO 8601 timestamp format.

    Args:
        timestamp: Timestamp string to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        from datetime import datetime

        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def validate_language_code(language_code: str) -> bool:
    """
    Validate BCP-47 language code format.

    Args:
        language_code: Language code to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r"^[a-z]{2,3}(-[A-Z]{2})?(-[a-z0-9]{5,8})?(-[a-z0-9]{1,8})*(-[a-z0-9]{1,8})*$"
    return bool(re.match(pattern, language_code.lower()))

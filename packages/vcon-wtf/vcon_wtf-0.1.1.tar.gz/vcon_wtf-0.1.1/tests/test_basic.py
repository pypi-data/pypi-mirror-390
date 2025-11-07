"""
Basic tests to verify the project setup works correctly.
"""

from wtf_transcript_converter.core.models import (
    WTFAudio,
    WTFDocument,
    WTFMetadata,
    WTFTranscript,
)
from wtf_transcript_converter.core.validator import validate_wtf_document


def test_wtf_transcript_creation():
    """Test creating a valid WTF transcript."""
    transcript = WTFTranscript(text="Hello world", language="en-US", duration=2.5, confidence=0.95)
    assert transcript.text == "Hello world"
    assert transcript.language == "en-us"  # Normalized to lowercase
    assert transcript.duration == 2.5
    assert transcript.confidence == 0.95


def test_wtf_transcript_validation():
    """Test WTF transcript validation."""
    # Valid transcript
    transcript = WTFTranscript(text="Hello world", language="en-US", duration=2.5, confidence=0.95)
    assert transcript.confidence >= 0.0
    assert transcript.confidence <= 1.0
    assert transcript.duration >= 0


def test_wtf_document_creation():
    """Test creating a valid WTF document."""
    transcript = WTFTranscript(text="Hello world", language="en-US", duration=2.5, confidence=0.95)

    audio = WTFAudio(duration=2.5)
    metadata = WTFMetadata(
        created_at="2025-01-02T12:00:00Z",
        processed_at="2025-01-02T12:00:15Z",
        provider="test",
        model="test-model",
        audio=audio,
    )

    doc = WTFDocument(transcript=transcript, segments=[], metadata=metadata)

    assert doc.transcript.text == "Hello world"
    assert doc.metadata.provider == "test"


def test_wtf_document_validation():
    """Test WTF document validation."""
    transcript = WTFTranscript(text="Hello world", language="en-US", duration=2.5, confidence=0.95)

    audio = WTFAudio(duration=2.5)
    metadata = WTFMetadata(
        created_at="2025-01-02T12:00:00Z",
        processed_at="2025-01-02T12:00:15Z",
        provider="test",
        model="test-model",
        audio=audio,
    )

    # Create a simple segment that matches the transcript
    from wtf_transcript_converter.core.models import WTFSegment

    segment = WTFSegment(id=0, start=0.0, end=2.5, text="Hello world", confidence=0.95)

    doc = WTFDocument(transcript=transcript, segments=[segment], metadata=metadata)

    is_valid, errors = validate_wtf_document(doc)
    if not is_valid:
        print(f"Validation errors: {errors}")
    assert is_valid
    assert len(errors) == 0

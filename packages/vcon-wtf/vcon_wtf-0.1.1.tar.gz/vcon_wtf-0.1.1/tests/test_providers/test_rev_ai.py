"""
Tests for Rev.ai provider converter.
"""

import json
from pathlib import Path

import pytest

from wtf_transcript_converter.core.validator import validate_wtf_document
from wtf_transcript_converter.providers.rev_ai import RevAIConverter


class TestRevAIConverter:
    """Test cases for RevAI converter."""

    @pytest.fixture
    def converter(self):
        """RevAI converter instance."""
        return RevAIConverter()

    @pytest.fixture
    def sample_rev_ai_data(self):
        """Sample Rev.ai JSON data for testing."""
        with open(Path(__file__).parent.parent / "fixtures" / "rev_ai_sample.json", "r") as f:
            return json.load(f)

    def test_convert_to_wtf_basic(self, converter, sample_rev_ai_data):
        """Test basic conversion from Rev.ai to WTF."""
        wtf_doc = converter.convert_to_wtf(sample_rev_ai_data)

        # Check basic structure
        assert wtf_doc.transcript is not None
        assert wtf_doc.segments is not None
        assert wtf_doc.metadata is not None

        # Check transcript content
        assert "Hello this is a sample transcription from Rev AI" in wtf_doc.transcript.text
        assert wtf_doc.transcript.language == "en"
        assert wtf_doc.transcript.duration == 8.5
        assert 0.0 <= wtf_doc.transcript.confidence <= 1.0

    def test_convert_to_wtf_segments(self, converter, sample_rev_ai_data):
        """Test segment conversion."""
        wtf_doc = converter.convert_to_wtf(sample_rev_ai_data)

        assert len(wtf_doc.segments) > 0

        # Check first segment
        first_segment = wtf_doc.segments[0]
        assert first_segment.id == 0
        assert first_segment.start >= 0.0
        assert first_segment.end > first_segment.start
        assert first_segment.text is not None
        assert 0.0 <= first_segment.confidence <= 1.0
        assert first_segment.speaker == "0"

    def test_convert_to_wtf_words(self, converter, sample_rev_ai_data):
        """Test word conversion."""
        wtf_doc = converter.convert_to_wtf(sample_rev_ai_data)

        assert wtf_doc.words is not None
        assert len(wtf_doc.words) > 0

        # Check first word
        first_word = wtf_doc.words[0]
        assert first_word.id == 0
        assert first_word.start >= 0.0
        assert first_word.end > first_word.start
        assert first_word.text == "Hello"
        assert 0.0 <= first_word.confidence <= 1.0
        assert first_word.speaker == "0"

    def test_convert_to_wtf_speakers(self, converter, sample_rev_ai_data):
        """Test speaker conversion."""
        wtf_doc = converter.convert_to_wtf(sample_rev_ai_data)

        assert wtf_doc.speakers is not None
        assert "0" in wtf_doc.speakers

        speaker = wtf_doc.speakers["0"]
        assert speaker.id == "0"
        assert speaker.label == "Speaker 1"
        assert speaker.segments is not None
        assert speaker.total_time > 0.0

    def test_convert_to_wtf_metadata(self, converter, sample_rev_ai_data):
        """Test metadata conversion."""
        wtf_doc = converter.convert_to_wtf(sample_rev_ai_data)

        metadata = wtf_doc.metadata
        assert metadata.provider == "rev_ai"
        assert metadata.model.startswith("rev-ai-")
        assert metadata.audio.duration == 8.5

        # Check options
        assert "job_id" in metadata.options
        assert "status" in metadata.options
        assert "language" in metadata.options

    def test_convert_to_wtf_quality(self, converter, sample_rev_ai_data):
        """Test quality metrics."""
        wtf_doc = converter.convert_to_wtf(sample_rev_ai_data)

        assert wtf_doc.quality is not None
        assert 0.0 <= wtf_doc.quality.average_confidence <= 1.0
        assert wtf_doc.quality.low_confidence_words >= 0

    def test_convert_to_wtf_validation(self, converter, sample_rev_ai_data):
        """Test that converted WTF document is valid."""
        wtf_doc = converter.convert_to_wtf(sample_rev_ai_data)

        is_valid, errors = validate_wtf_document(wtf_doc)
        assert is_valid, f"Validation failed: {errors}"

    def test_convert_from_wtf_basic(self, converter, sample_rev_ai_data):
        """Test basic conversion from WTF to Rev.ai."""
        # First convert to WTF
        wtf_doc = converter.convert_to_wtf(sample_rev_ai_data)

        # Then convert back to Rev.ai
        rev_ai_data = converter.convert_from_wtf(wtf_doc)

        # Check basic structure
        assert "id" in rev_ai_data
        assert "status" in rev_ai_data
        assert "duration_seconds" in rev_ai_data
        assert "language" in rev_ai_data
        assert "monologue" in rev_ai_data

    def test_convert_from_wtf_monologue(self, converter, sample_rev_ai_data):
        """Test monologue conversion."""
        wtf_doc = converter.convert_to_wtf(sample_rev_ai_data)
        rev_ai_data = converter.convert_from_wtf(wtf_doc)

        monologue = rev_ai_data["monologue"]
        assert "speaker" in monologue
        assert "elements" in monologue
        assert len(monologue["elements"]) > 0

        # Check first element
        first_element = monologue["elements"][0]
        assert "type" in first_element
        assert "value" in first_element
        assert "ts" in first_element
        assert "end_ts" in first_element

    def test_round_trip_conversion(self, converter, sample_rev_ai_data):
        """Test round-trip conversion (Rev.ai -> WTF -> Rev.ai)."""
        # Convert to WTF
        wtf_doc = converter.convert_to_wtf(sample_rev_ai_data)

        # Convert back to Rev.ai
        rev_ai_data_back = converter.convert_from_wtf(wtf_doc)

        # Check that key fields are preserved
        assert rev_ai_data_back["duration_seconds"] == sample_rev_ai_data["duration_seconds"]
        assert rev_ai_data_back["language"] == sample_rev_ai_data["language"]
        assert (
            rev_ai_data_back["monologue"]["speaker"] == sample_rev_ai_data["monologue"]["speaker"]
        )

    def test_empty_data_handling(self, converter):
        """Test handling of empty or minimal data."""
        empty_data = {
            "id": "test",
            "status": "transcribed",
            "duration_seconds": 0.0,
            "language": "en",
            "monologue": {"speaker": 0, "elements": []},
        }

        wtf_doc = converter.convert_to_wtf(empty_data)

        assert wtf_doc.transcript.text == "No transcription available"
        assert wtf_doc.transcript.duration == 0.0
        assert len(wtf_doc.segments) == 0
        assert wtf_doc.words is None or len(wtf_doc.words) == 0

    def test_punctuation_handling(self, converter):
        """Test punctuation detection and handling."""
        data_with_punctuation = {
            "id": "test",
            "status": "transcribed",
            "duration_seconds": 1.0,
            "language": "en",
            "monologue": {
                "speaker": 0,
                "elements": [
                    {
                        "type": "text",
                        "value": "Hello",
                        "ts": 0.0,
                        "end_ts": 0.5,
                        "confidence": 0.99,
                    },
                    {"type": "punct", "value": "!", "ts": 0.5, "end_ts": 0.6},
                ],
            },
        }

        wtf_doc = converter.convert_to_wtf(data_with_punctuation)

        # Should have one word
        assert len(wtf_doc.words) == 1
        assert wtf_doc.words[0].text == "Hello"
        assert not wtf_doc.words[0].is_punctuation

    def test_confidence_normalization(self, converter):
        """Test confidence score normalization."""
        data_with_confidence = {
            "id": "test",
            "status": "transcribed",
            "duration_seconds": 1.0,
            "language": "en",
            "monologue": {
                "speaker": 0,
                "elements": [
                    {
                        "type": "text",
                        "value": "test",
                        "ts": 0.0,
                        "end_ts": 0.5,
                        "confidence": 0.95,
                    }
                ],
            },
        }

        wtf_doc = converter.convert_to_wtf(data_with_confidence)

        assert wtf_doc.words[0].confidence == 0.95
        assert wtf_doc.transcript.confidence == 0.95

    def test_language_normalization(self, converter):
        """Test language code normalization."""
        data_with_language = {
            "id": "test",
            "status": "transcribed",
            "duration_seconds": 1.0,
            "language": "en",
            "monologue": {"speaker": 0, "elements": []},
        }

        wtf_doc = converter.convert_to_wtf(data_with_language)

        assert wtf_doc.transcript.language == "en"

    def test_extensions_preservation(self, converter, sample_rev_ai_data):
        """Test that Rev.ai-specific data is preserved in extensions."""
        wtf_doc = converter.convert_to_wtf(sample_rev_ai_data)

        assert wtf_doc.extensions is not None
        assert "rev_ai_raw_response" in wtf_doc.extensions
        assert wtf_doc.extensions["rev_ai_raw_response"]["id"] == sample_rev_ai_data["id"]

"""
Tests for Canary provider converter.
"""

import json
from pathlib import Path

import pytest

from wtf_transcript_converter.core.models import WTFDocument
from wtf_transcript_converter.providers.canary import CanaryConverter


class TestCanaryConverter:
    """Test cases for Canary converter."""

    @pytest.fixture
    def converter(self):
        """Create a Canary converter instance."""
        return CanaryConverter()

    @pytest.fixture
    def sample_canary_data(self) -> dict:
        """Sample Canary JSON data for testing."""
        with open(Path(__file__).parent.parent / "fixtures" / "canary_sample.json", "r") as f:
            return json.load(f)

    def test_converter_initialization(self, converter):
        """Test converter initialization."""
        assert converter.provider_name == "canary"
        assert converter.model_name == "nvidia/canary-1b-v2"

    def test_convert_to_wtf(self, converter, sample_canary_data):
        """Test conversion from Canary to WTF format."""
        wtf_doc = converter.convert_to_wtf(sample_canary_data)

        # Check basic structure
        assert isinstance(wtf_doc, WTFDocument)
        assert wtf_doc.transcript.text == sample_canary_data["text"]
        assert wtf_doc.transcript.language == "en-us"  # Normalized from "en"
        assert wtf_doc.transcript.duration == sample_canary_data["duration"]

        # Check segments
        assert len(wtf_doc.segments) == len(sample_canary_data["segments"])
        for i, segment in enumerate(wtf_doc.segments):
            assert segment.id == sample_canary_data["segments"][i]["id"]
            assert segment.start == sample_canary_data["segments"][i]["start"]
            assert segment.end == sample_canary_data["segments"][i]["end"]
            assert segment.text == sample_canary_data["segments"][i]["text"]

        # Check words
        assert len(wtf_doc.words) == len(sample_canary_data["words"])
        for i, word in enumerate(wtf_doc.words):
            assert word.id == sample_canary_data["words"][i]["id"]
            assert word.start == sample_canary_data["words"][i]["start"]
            assert word.end == sample_canary_data["words"][i]["end"]
            assert word.text == sample_canary_data["words"][i]["text"]

        # Check metadata
        assert wtf_doc.metadata.provider == "canary"
        assert wtf_doc.metadata.model == sample_canary_data["model"]
        assert wtf_doc.metadata.audio.duration == sample_canary_data["duration"]
        assert wtf_doc.metadata.audio.sample_rate == sample_canary_data["sample_rate"]

    def test_convert_from_wtf(self, converter, sample_canary_data):
        """Test conversion from WTF to Canary format."""
        # First convert to WTF
        wtf_doc = converter.convert_to_wtf(sample_canary_data)

        # Then convert back to Canary
        canary_data = converter.convert_from_wtf(wtf_doc)

        # Check basic structure
        assert canary_data["text"] == sample_canary_data["text"]
        assert canary_data["language"] == sample_canary_data["language"]
        assert canary_data["duration"] == sample_canary_data["duration"]
        assert canary_data["model"] == sample_canary_data["model"]

        # Check segments
        assert len(canary_data["segments"]) == len(sample_canary_data["segments"])
        for i, segment in enumerate(canary_data["segments"]):
            assert segment["id"] == sample_canary_data["segments"][i]["id"]
            assert segment["start"] == sample_canary_data["segments"][i]["start"]
            assert segment["end"] == sample_canary_data["segments"][i]["end"]
            assert segment["text"] == sample_canary_data["segments"][i]["text"]

        # Check words
        assert len(canary_data["words"]) == len(sample_canary_data["words"])
        for i, word in enumerate(canary_data["words"]):
            assert word["id"] == sample_canary_data["words"][i]["id"]
            assert word["start"] == sample_canary_data["words"][i]["start"]
            assert word["end"] == sample_canary_data["words"][i]["end"]
            assert word["text"] == sample_canary_data["words"][i]["text"]

    def test_calculate_overall_confidence(self, converter, sample_canary_data):
        """Test overall confidence calculation."""
        confidence = converter._calculate_overall_confidence(sample_canary_data)
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0

    def test_extract_speakers(self, converter, sample_canary_data):
        """Test speaker extraction."""
        speakers = converter._extract_speakers(sample_canary_data["words"])
        assert len(speakers) == 1
        assert "0" in speakers
        assert speakers["0"].id == "0"
        assert speakers["0"].label == "Speaker 1"

    def test_detect_punctuation(self, converter):
        """Test punctuation detection."""
        assert converter._detect_punctuation("Hello") == False
        assert converter._detect_punctuation(".") == True
        assert converter._detect_punctuation("!") == True
        assert converter._detect_punctuation("?") == True
        assert converter._detect_punctuation("...") == True

    def test_calculate_quality_metrics(self, converter, sample_canary_data):
        """Test quality metrics calculation."""
        wtf_doc = converter.convert_to_wtf(sample_canary_data)
        quality = converter._calculate_quality_metrics(sample_canary_data, wtf_doc.words)

        assert quality.average_confidence is not None
        assert quality.low_confidence_words is not None
        assert quality.audio_quality in ["high", "medium", "low"]

    def test_empty_data_handling(self, converter):
        """Test handling of empty or minimal data."""
        empty_data = {
            "text": "",
            "language": "en",
            "duration": 0.0,
            "words": [],
            "segments": [],
            "model": "nvidia/canary-1b-v2",
        }

        wtf_doc = converter.convert_to_wtf(empty_data)
        assert wtf_doc.transcript.text == "[Empty transcript]"  # Empty text becomes placeholder
        assert len(wtf_doc.segments) == 0
        assert wtf_doc.words is None or len(wtf_doc.words) == 0

    def test_missing_fields_handling(self, converter):
        """Test handling of missing fields."""
        minimal_data = {"text": "Hello world", "language": "en"}

        # Should not raise an exception
        wtf_doc = converter.convert_to_wtf(minimal_data)
        assert wtf_doc.transcript.text == "Hello world"
        assert wtf_doc.transcript.language == "en-us"  # Normalized from "en"
        assert wtf_doc.transcript.duration == 0.0  # Default value

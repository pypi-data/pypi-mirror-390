"""
Tests for Whisper provider converter.
"""

from pathlib import Path

import pytest

from wtf_transcript_converter.core.models import WTFDocument
from wtf_transcript_converter.core.validator import validate_wtf_document
from wtf_transcript_converter.providers.whisper import WhisperConverter


class TestWhisperConverter:
    """Test Whisper converter functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = WhisperConverter()
        self.fixtures_dir = Path(__file__).parent.parent / "fixtures"

    def test_whisper_to_wtf_conversion(self, sample_whisper_data):
        """Test converting Whisper data to WTF format."""
        wtf_doc = self.converter.convert_to_wtf(sample_whisper_data)

        # Validate basic structure
        assert isinstance(wtf_doc, WTFDocument)
        assert wtf_doc.transcript.text == sample_whisper_data["text"]
        assert wtf_doc.transcript.language == "en-us"  # Normalized by language utils
        assert wtf_doc.transcript.duration == sample_whisper_data["duration"]
        assert len(wtf_doc.segments) == len(sample_whisper_data["segments"])

        # Validate segments
        for i, segment in enumerate(wtf_doc.segments):
            original_segment = sample_whisper_data["segments"][i]
            assert segment.id == i
            assert segment.start == original_segment["start"]
            assert segment.end == original_segment["end"]
            assert segment.text == original_segment["text"]
            assert 0.0 <= segment.confidence <= 1.0

        # Validate metadata
        assert wtf_doc.metadata.provider == "whisper"
        assert wtf_doc.metadata.model == "whisper-1"
        assert wtf_doc.metadata.audio.duration == sample_whisper_data["duration"]

        # Validate extensions
        assert "whisper" in wtf_doc.extensions
        whisper_ext = wtf_doc.extensions["whisper"]
        assert "temperature" in whisper_ext
        assert "compression_ratio" in whisper_ext
        assert "avg_logprob" in whisper_ext
        assert "no_speech_prob" in whisper_ext

    def test_whisper_to_wtf_with_words(self):
        """Test converting Whisper data with word-level information."""
        whisper_data = {
            "text": "Hello world",
            "language": "en",
            "duration": 2.0,
            "segments": [
                {
                    "id": 0,
                    "start": 0.0,
                    "end": 2.0,
                    "text": "Hello world",
                    "words": [
                        {
                            "word": "Hello",
                            "start": 0.0,
                            "end": 1.0,
                            "probability": 0.95,
                        },
                        {
                            "word": "world",
                            "start": 1.0,
                            "end": 2.0,
                            "probability": 0.90,
                        },
                    ],
                }
            ],
        }

        wtf_doc = self.converter.convert_to_wtf(whisper_data)

        # Validate words
        assert wtf_doc.words is not None
        assert len(wtf_doc.words) == 2

        word1 = wtf_doc.words[0]
        assert word1.text == "Hello"
        assert word1.start == 0.0
        assert word1.end == 1.0
        assert word1.confidence == 0.95

        word2 = wtf_doc.words[1]
        assert word2.text == "world"
        assert word2.start == 1.0
        assert word2.end == 2.0
        assert word2.confidence == 0.90

        # Validate segment word references
        assert wtf_doc.segments[0].words == [0, 1]

    def test_wtf_to_whisper_conversion(self, sample_wtf_document):
        """Test converting WTF document to Whisper format."""
        # Convert dict to WTFDocument object
        from wtf_transcript_converter.core.models import WTFDocument

        wtf_doc = WTFDocument.model_validate(sample_wtf_document)
        whisper_data = self.converter.convert_from_wtf(wtf_doc)

        # Validate basic structure
        assert "text" in whisper_data
        assert "language" in whisper_data
        assert "duration" in whisper_data
        assert "segments" in whisper_data

        # Validate transcript
        assert whisper_data["text"] == wtf_doc.transcript.text
        assert whisper_data["language"] == wtf_doc.transcript.language
        assert whisper_data["duration"] == wtf_doc.transcript.duration

        # Validate segments
        assert len(whisper_data["segments"]) == len(wtf_doc.segments)
        for i, segment in enumerate(whisper_data["segments"]):
            original_segment = wtf_doc.segments[i]
            assert segment["id"] == original_segment.id
            assert segment["start"] == original_segment.start
            assert segment["end"] == original_segment.end
            assert segment["text"] == original_segment.text
            assert "tokens" in segment
            assert "temperature" in segment
            assert "avg_logprob" in segment

    def test_confidence_normalization(self):
        """Test confidence score normalization from log probabilities."""
        whisper_data = {
            "text": "Test",
            "language": "en",
            "duration": 1.0,
            "segments": [
                {
                    "id": 0,
                    "start": 0.0,
                    "end": 1.0,
                    "text": "Test",
                    "avg_logprob": -0.5,  # Should convert to ~0.61 confidence
                    "temperature": 0.0,
                    "compression_ratio": 1.0,
                    "no_speech_prob": 0.01,
                }
            ],
        }

        wtf_doc = self.converter.convert_to_wtf(whisper_data)

        # Check that log probability was converted to confidence
        assert 0.0 <= wtf_doc.segments[0].confidence <= 1.0
        assert wtf_doc.segments[0].confidence > 0.5  # -0.5 logprob should be > 0.5 confidence

    def test_punctuation_detection(self):
        """Test punctuation detection in words."""
        whisper_data = {
            "text": "Hello, world!",
            "language": "en",
            "duration": 2.0,
            "segments": [
                {
                    "id": 0,
                    "start": 0.0,
                    "end": 2.0,
                    "text": "Hello, world!",
                    "words": [
                        {
                            "word": "Hello",
                            "start": 0.0,
                            "end": 0.8,
                            "probability": 0.95,
                        },
                        {"word": ",", "start": 0.8, "end": 0.9, "probability": 0.98},
                        {
                            "word": "world",
                            "start": 0.9,
                            "end": 1.7,
                            "probability": 0.90,
                        },
                        {"word": "!", "start": 1.7, "end": 1.8, "probability": 0.99},
                    ],
                }
            ],
        }

        wtf_doc = self.converter.convert_to_wtf(whisper_data)

        # Check punctuation detection
        assert wtf_doc.words[0].is_punctuation is False  # "Hello"
        assert wtf_doc.words[1].is_punctuation is True  # ","
        assert wtf_doc.words[2].is_punctuation is False  # "world"
        assert wtf_doc.words[3].is_punctuation is True  # "!"

    def test_quality_metrics_calculation(self):
        """Test quality metrics calculation."""
        whisper_data = {
            "text": "Test with some low confidence words",
            "language": "en",
            "duration": 3.0,
            "no_speech_prob": 0.05,  # Low noise
            "segments": [
                {
                    "id": 0,
                    "start": 0.0,
                    "end": 3.0,
                    "text": "Test with some low confidence words",
                    "words": [
                        {"word": "Test", "start": 0.0, "end": 0.5, "probability": 0.95},
                        {"word": "with", "start": 0.5, "end": 0.8, "probability": 0.90},
                        {
                            "word": "some",
                            "start": 0.8,
                            "end": 1.1,
                            "probability": 0.30,
                        },  # Low confidence
                        {
                            "word": "low",
                            "start": 1.1,
                            "end": 1.4,
                            "probability": 0.25,
                        },  # Low confidence
                        {
                            "word": "confidence",
                            "start": 1.4,
                            "end": 2.2,
                            "probability": 0.85,
                        },
                        {
                            "word": "words",
                            "start": 2.2,
                            "end": 2.8,
                            "probability": 0.88,
                        },
                    ],
                }
            ],
        }

        wtf_doc = self.converter.convert_to_wtf(whisper_data)

        # Check quality metrics
        assert wtf_doc.quality is not None
        assert wtf_doc.quality.audio_quality == "high"  # Low no_speech_prob
        assert wtf_doc.quality.low_confidence_words == 2  # "some" and "low"
        assert wtf_doc.quality.average_confidence > 0.0

    def test_round_trip_conversion(self, sample_whisper_data):
        """Test round-trip conversion: Whisper -> WTF -> Whisper."""
        # Convert to WTF
        wtf_doc = self.converter.convert_to_wtf(sample_whisper_data)

        # Convert back to Whisper
        whisper_data_back = self.converter.convert_from_wtf(wtf_doc)

        # Validate that key fields are preserved
        assert whisper_data_back["text"] == sample_whisper_data["text"]
        assert whisper_data_back["language"] == "en-us"  # Normalized language code
        assert whisper_data_back["duration"] == sample_whisper_data["duration"]
        assert len(whisper_data_back["segments"]) == len(sample_whisper_data["segments"])

        # Validate segments
        for i, segment in enumerate(whisper_data_back["segments"]):
            original_segment = sample_whisper_data["segments"][i]
            assert segment["start"] == original_segment["start"]
            assert segment["end"] == original_segment["end"]
            assert segment["text"] == original_segment["text"]

    def test_validation_after_conversion(self, sample_whisper_data):
        """Test that converted WTF document passes validation."""
        wtf_doc = self.converter.convert_to_wtf(sample_whisper_data)

        is_valid, errors = validate_wtf_document(wtf_doc)
        assert is_valid, f"Validation failed with errors: {errors}"

    def test_error_handling_invalid_data(self):
        """Test error handling with invalid Whisper data."""
        invalid_data = {
            "text": "",  # Empty text should cause validation error
            "language": "invalid-language-code",  # Invalid language code
            "duration": -1.0,  # Negative duration
            "segments": [],
        }

        with pytest.raises(ValueError):
            self.converter.convert_to_wtf(invalid_data)

    def test_generic_convert_method(self, sample_whisper_data):
        """Test the generic convert method that auto-detects format."""
        # Test with Whisper data
        wtf_doc = self.converter.convert(sample_whisper_data)
        assert isinstance(wtf_doc, WTFDocument)

        # Test with WTF document
        whisper_data = self.converter.convert(wtf_doc)
        assert isinstance(whisper_data, dict)
        assert "text" in whisper_data

    def test_whisper_specific_extensions_preservation(self, sample_whisper_data):
        """Test that Whisper-specific data is preserved in extensions."""
        # Add some Whisper-specific data
        sample_whisper_data["temperature"] = 0.2
        sample_whisper_data["compression_ratio"] = 1.5
        sample_whisper_data["avg_logprob"] = -0.3
        sample_whisper_data["no_speech_prob"] = 0.02

        wtf_doc = self.converter.convert_to_wtf(sample_whisper_data)

        # Check that extensions contain Whisper-specific data
        assert "whisper" in wtf_doc.extensions
        whisper_ext = wtf_doc.extensions["whisper"]
        assert whisper_ext["temperature"] == 0.2
        assert whisper_ext["compression_ratio"] == 1.5
        assert whisper_ext["avg_logprob"] == -0.3
        assert whisper_ext["no_speech_prob"] == 0.02

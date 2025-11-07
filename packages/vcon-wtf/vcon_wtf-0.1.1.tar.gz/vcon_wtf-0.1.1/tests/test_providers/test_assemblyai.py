"""
Tests for AssemblyAI provider converter.
"""

from pathlib import Path

import pytest

from wtf_transcript_converter.core.models import WTFDocument
from wtf_transcript_converter.core.validator import validate_wtf_document
from wtf_transcript_converter.providers.assemblyai import AssemblyAIConverter


class TestAssemblyAIConverter:
    """Test AssemblyAI converter functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = AssemblyAIConverter()
        self.fixtures_dir = Path(__file__).parent.parent / "fixtures"

    def test_assemblyai_to_wtf_conversion(self, sample_assemblyai_data):
        """Test converting AssemblyAI data to WTF format."""
        wtf_doc = self.converter.convert_to_wtf(sample_assemblyai_data)

        # Validate basic structure
        assert isinstance(wtf_doc, WTFDocument)
        assert wtf_doc.transcript.text == sample_assemblyai_data["text"]
        assert wtf_doc.transcript.language == "en-us"  # Normalized
        assert wtf_doc.transcript.duration == sample_assemblyai_data["audio_duration"]

        # Validate segments
        assert len(wtf_doc.segments) > 0

        # Validate words
        assert wtf_doc.words is not None
        assert len(wtf_doc.words) > 0

        # Validate metadata
        assert wtf_doc.metadata.provider == "assemblyai"
        assert wtf_doc.metadata.audio.duration == sample_assemblyai_data["audio_duration"]

        # Validate extensions
        assert "assemblyai" in wtf_doc.extensions
        assemblyai_ext = wtf_doc.extensions["assemblyai"]
        assert "id" in assemblyai_ext
        assert "status" in assemblyai_ext
        assert "speech_model" in assemblyai_ext

    def test_assemblyai_to_wtf_with_speakers(self):
        """Test converting AssemblyAI data with speaker diarization."""
        assemblyai_data = {
            "id": "test-transcript-id",
            "status": "completed",
            "text": "Hello world from speaker A and speaker B",
            "language_code": "en",
            "audio_duration": 5.0,
            "confidence": 0.95,
            "words": [
                {
                    "text": "Hello",
                    "start": 0.0,
                    "end": 0.5,
                    "confidence": 0.98,
                    "speaker": "A",
                },
                {
                    "text": "world",
                    "start": 0.5,
                    "end": 1.0,
                    "confidence": 0.96,
                    "speaker": "A",
                },
                {
                    "text": "from",
                    "start": 1.0,
                    "end": 1.3,
                    "confidence": 0.94,
                    "speaker": "A",
                },
                {
                    "text": "speaker",
                    "start": 1.3,
                    "end": 1.8,
                    "confidence": 0.92,
                    "speaker": "B",
                },
                {
                    "text": "A",
                    "start": 1.8,
                    "end": 2.1,
                    "confidence": 0.90,
                    "speaker": "B",
                },
                {
                    "text": "and",
                    "start": 2.1,
                    "end": 2.4,
                    "confidence": 0.88,
                    "speaker": "B",
                },
                {
                    "text": "speaker",
                    "start": 2.4,
                    "end": 2.9,
                    "confidence": 0.86,
                    "speaker": "C",
                },
                {
                    "text": "B",
                    "start": 2.9,
                    "end": 3.2,
                    "confidence": 0.84,
                    "speaker": "C",
                },
            ],
            "speaker_labels": True,
            "speakers_expected": 3,
        }

        wtf_doc = self.converter.convert_to_wtf(assemblyai_data)

        # Validate speakers
        assert wtf_doc.speakers is not None
        assert len(wtf_doc.speakers) == 3  # Three speakers

        # Check speaker details
        assert "A" in wtf_doc.speakers
        assert "B" in wtf_doc.speakers
        assert "C" in wtf_doc.speakers

        speaker_a = wtf_doc.speakers["A"]
        assert speaker_a.label == "Speaker A"
        assert speaker_a.total_time > 0
        assert speaker_a.confidence > 0

    def test_wtf_to_assemblyai_conversion(self, sample_wtf_document):
        """Test converting WTF document to AssemblyAI format."""
        # Convert dict to WTFDocument object
        from wtf_transcript_converter.core.models import WTFDocument

        wtf_doc = WTFDocument.model_validate(sample_wtf_document)
        assemblyai_data = self.converter.convert_from_wtf(wtf_doc)

        # Validate basic structure
        assert "id" in assemblyai_data
        assert "status" in assemblyai_data
        assert "text" in assemblyai_data
        assert "language_code" in assemblyai_data
        assert "audio_duration" in assemblyai_data
        assert "words" in assemblyai_data

        # Validate transcript
        assert assemblyai_data["text"] == wtf_doc.transcript.text
        assert assemblyai_data["audio_duration"] == wtf_doc.transcript.duration
        assert assemblyai_data["confidence"] == wtf_doc.transcript.confidence

        # Validate words - the sample WTF document doesn't have words, so this should be 0
        assert len(assemblyai_data["words"]) == 0

    def test_word_level_conversion(self):
        """Test word-level conversion accuracy."""
        assemblyai_data = {
            "id": "test-transcript-id",
            "status": "completed",
            "text": "Hello world test",
            "language_code": "en",
            "audio_duration": 3.0,
            "confidence": 0.95,
            "words": [
                {
                    "text": "Hello",
                    "start": 0.0,
                    "end": 0.5,
                    "confidence": 0.98,
                    "speaker": "A",
                },
                {
                    "text": "world",
                    "start": 0.5,
                    "end": 1.0,
                    "confidence": 0.96,
                    "speaker": "A",
                },
                {
                    "text": "test",
                    "start": 1.0,
                    "end": 1.5,
                    "confidence": 0.94,
                    "speaker": "A",
                },
            ],
        }

        wtf_doc = self.converter.convert_to_wtf(assemblyai_data)

        # Validate words
        assert len(wtf_doc.words) == 3

        word1 = wtf_doc.words[0]
        assert word1.text == "Hello"
        assert word1.start == 0.0
        assert word1.end == 0.5
        assert word1.confidence == 0.98
        assert word1.speaker == "A"

        word2 = wtf_doc.words[1]
        assert word2.text == "world"
        assert word2.start == 0.5
        assert word2.end == 1.0
        assert word2.confidence == 0.96

        word3 = wtf_doc.words[2]
        assert word3.text == "test"
        assert word3.start == 1.0
        assert word3.end == 1.5
        assert word3.confidence == 0.94

    def test_punctuation_detection(self):
        """Test punctuation detection in words."""
        assemblyai_data = {
            "id": "test-transcript-id",
            "status": "completed",
            "text": "Hello, world!",
            "language_code": "en",
            "audio_duration": 2.0,
            "confidence": 0.95,
            "words": [
                {
                    "text": "Hello",
                    "start": 0.0,
                    "end": 0.5,
                    "confidence": 0.98,
                    "speaker": "A",
                },
                {
                    "text": ",",
                    "start": 0.5,
                    "end": 0.6,
                    "confidence": 0.99,
                    "speaker": "A",
                },
                {
                    "text": "world",
                    "start": 0.6,
                    "end": 1.0,
                    "confidence": 0.96,
                    "speaker": "A",
                },
                {
                    "text": "!",
                    "start": 1.0,
                    "end": 1.1,
                    "confidence": 0.99,
                    "speaker": "A",
                },
            ],
        }

        wtf_doc = self.converter.convert_to_wtf(assemblyai_data)

        # Check punctuation detection
        assert wtf_doc.words[0].is_punctuation is False  # "Hello"
        assert wtf_doc.words[1].is_punctuation is True  # ","
        assert wtf_doc.words[2].is_punctuation is False  # "world"
        assert wtf_doc.words[3].is_punctuation is True  # "!"

    def test_quality_metrics_calculation(self):
        """Test quality metrics calculation."""
        assemblyai_data = {
            "id": "test-transcript-id",
            "status": "completed",
            "text": "Test with some low confidence words",
            "language_code": "en",
            "audio_duration": 3.0,
            "confidence": 0.85,  # Medium confidence
            "words": [
                {
                    "text": "Test",
                    "start": 0.0,
                    "end": 0.5,
                    "confidence": 0.95,
                    "speaker": "A",
                },
                {
                    "text": "with",
                    "start": 0.5,
                    "end": 0.8,
                    "confidence": 0.90,
                    "speaker": "A",
                },
                {
                    "text": "some",
                    "start": 0.8,
                    "end": 1.1,
                    "confidence": 0.30,
                    "speaker": "A",
                },  # Low confidence
                {
                    "text": "low",
                    "start": 1.1,
                    "end": 1.4,
                    "confidence": 0.25,
                    "speaker": "A",
                },  # Low confidence
                {
                    "text": "confidence",
                    "start": 1.4,
                    "end": 2.2,
                    "confidence": 0.85,
                    "speaker": "A",
                },
                {
                    "text": "words",
                    "start": 2.2,
                    "end": 2.8,
                    "confidence": 0.88,
                    "speaker": "A",
                },
            ],
        }

        wtf_doc = self.converter.convert_to_wtf(assemblyai_data)

        # Check quality metrics
        assert wtf_doc.quality is not None
        assert wtf_doc.quality.audio_quality == "medium"  # 0.85 confidence
        assert wtf_doc.quality.low_confidence_words == 2  # "some" and "low"
        assert wtf_doc.quality.average_confidence > 0.0

    def test_round_trip_conversion(self, sample_assemblyai_data):
        """Test round-trip conversion: AssemblyAI -> WTF -> AssemblyAI."""
        # Convert to WTF
        wtf_doc = self.converter.convert_to_wtf(sample_assemblyai_data)

        # Convert back to AssemblyAI
        assemblyai_data_back = self.converter.convert_from_wtf(wtf_doc)

        # Validate that key fields are preserved
        assert assemblyai_data_back["text"] == sample_assemblyai_data["text"]
        assert assemblyai_data_back["audio_duration"] == sample_assemblyai_data["audio_duration"]
        assert assemblyai_data_back["language_code"] == "en-us"  # Normalized

    def test_validation_after_conversion(self, sample_assemblyai_data):
        """Test that converted WTF document passes validation."""
        wtf_doc = self.converter.convert_to_wtf(sample_assemblyai_data)

        is_valid, errors = validate_wtf_document(wtf_doc)
        assert is_valid, f"Validation failed with errors: {errors}"

    def test_error_handling_invalid_data(self):
        """Test error handling with invalid AssemblyAI data."""
        invalid_data = {
            "id": "test-transcript-id",
            "status": "completed",
            "text": "",  # Empty text should cause validation error
            "language_code": "invalid-language-code",  # Invalid language code
            "audio_duration": -1.0,  # Negative duration
            "words": [],
        }

        # Should raise validation error during conversion
        with pytest.raises(ValueError):
            self.converter.convert_to_wtf(invalid_data)

    def test_generic_convert_method(self, sample_assemblyai_data):
        """Test the generic convert method that auto-detects format."""
        # Test with AssemblyAI data
        wtf_doc = self.converter.convert(sample_assemblyai_data)
        assert isinstance(wtf_doc, WTFDocument)

        # Test with WTF document
        assemblyai_data = self.converter.convert(wtf_doc)
        assert isinstance(assemblyai_data, dict)
        assert "id" in assemblyai_data
        assert "text" in assemblyai_data

    def test_assemblyai_specific_extensions_preservation(self, sample_assemblyai_data):
        """Test that AssemblyAI-specific data is preserved in extensions."""
        wtf_doc = self.converter.convert_to_wtf(sample_assemblyai_data)

        # Check that extensions contain AssemblyAI-specific data
        assert "assemblyai" in wtf_doc.extensions
        assemblyai_ext = wtf_doc.extensions["assemblyai"]
        assert "id" in assemblyai_ext
        assert "status" in assemblyai_ext
        assert "speech_model" in assemblyai_ext
        assert "speaker_labels" in assemblyai_ext
        assert "punctuate" in assemblyai_ext
        assert "format_text" in assemblyai_ext

        # Check that original data is preserved
        assert assemblyai_ext["id"] == sample_assemblyai_data["id"]
        assert assemblyai_ext["status"] == sample_assemblyai_data["status"]
        assert assemblyai_ext["speech_model"] == sample_assemblyai_data["speech_model"]

    def test_empty_words_handling(self):
        """Test handling of empty words list."""
        assemblyai_data = {
            "id": "test-transcript-id",
            "status": "completed",
            "text": "Test",
            "language_code": "en",
            "audio_duration": 1.0,
            "confidence": 0.95,
            "words": [],  # Empty words list
        }

        wtf_doc = self.converter.convert_to_wtf(assemblyai_data)

        # Should handle empty words gracefully
        assert wtf_doc.words is None or len(wtf_doc.words) == 0
        assert len(wtf_doc.segments) == 0  # No words means no segments
        assert wtf_doc.transcript.text == "Test"

    def test_model_info_extraction(self):
        """Test model information extraction."""
        assemblyai_data = {
            "id": "test-transcript-id",
            "status": "completed",
            "text": "Test",
            "language_code": "en",
            "audio_duration": 1.0,
            "confidence": 0.95,
            "speech_model": "best",
            "speech_model_version": "2.0",
            "words": [],
        }

        wtf_doc = self.converter.convert_to_wtf(assemblyai_data)

        # Check model info
        assert wtf_doc.metadata.model == "best-2.0"

    def test_warnings_extraction(self):
        """Test warnings extraction from AssemblyAI data."""
        assemblyai_data = {
            "id": "test-transcript-id",
            "status": "completed",
            "text": "Test",
            "language_code": "en",
            "audio_duration": 1.0,
            "confidence": 0.6,  # Low confidence
            "language_confidence": 0.7,  # Low language confidence
            "content_safety": {"status": "error"},  # Content safety error
            "words": [],
        }

        wtf_doc = self.converter.convert_to_wtf(assemblyai_data)

        # Check warnings
        assert wtf_doc.quality is not None
        assert len(wtf_doc.quality.processing_warnings) > 0
        warnings = wtf_doc.quality.processing_warnings
        assert any("Low overall confidence" in warning for warning in warnings)
        assert any("Low language detection confidence" in warning for warning in warnings)
        assert any("Content safety analysis failed" in warning for warning in warnings)

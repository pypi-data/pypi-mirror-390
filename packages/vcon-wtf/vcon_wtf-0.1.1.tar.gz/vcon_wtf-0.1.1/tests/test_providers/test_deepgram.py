"""
Tests for Deepgram provider converter.
"""

from pathlib import Path

import pytest

from wtf_transcript_converter.core.models import WTFDocument
from wtf_transcript_converter.core.validator import validate_wtf_document
from wtf_transcript_converter.providers.deepgram import DeepgramConverter


class TestDeepgramConverter:
    """Test Deepgram converter functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = DeepgramConverter()
        self.fixtures_dir = Path(__file__).parent.parent / "fixtures"

    def test_deepgram_to_wtf_conversion(self, sample_deepgram_data):
        """Test converting Deepgram data to WTF format."""
        wtf_doc = self.converter.convert_to_wtf(sample_deepgram_data)

        # Validate basic structure
        assert isinstance(wtf_doc, WTFDocument)
        assert (
            wtf_doc.transcript.text
            == sample_deepgram_data["results"]["channels"][0]["alternatives"][0]["transcript"]
        )
        assert wtf_doc.transcript.language == "en-us"  # Normalized
        assert wtf_doc.transcript.duration == sample_deepgram_data["metadata"]["duration"]

        # Validate segments
        assert len(wtf_doc.segments) > 0

        # Validate words
        assert wtf_doc.words is not None
        assert len(wtf_doc.words) > 0

        # Validate metadata
        assert wtf_doc.metadata.provider == "deepgram"
        assert wtf_doc.metadata.audio.duration == sample_deepgram_data["metadata"]["duration"]

        # Validate extensions
        assert "deepgram" in wtf_doc.extensions
        deepgram_ext = wtf_doc.extensions["deepgram"]
        assert "metadata" in deepgram_ext
        assert "model_info" in deepgram_ext

    def test_deepgram_to_wtf_with_speakers(self):
        """Test converting Deepgram data with speaker diarization."""
        deepgram_data = {
            "metadata": {
                "duration": 5.0,
                "channels": 1,
                "model_info": {"name": "nova-2", "version": "2024-01-09"},
            },
            "results": {
                "channels": [
                    {
                        "alternatives": [
                            {
                                "transcript": "Hello world from speaker one and speaker two",
                                "confidence": 0.95,
                                "words": [
                                    {
                                        "word": "Hello",
                                        "start": 0.0,
                                        "end": 0.5,
                                        "confidence": 0.98,
                                        "speaker": 0,
                                    },
                                    {
                                        "word": "world",
                                        "start": 0.5,
                                        "end": 1.0,
                                        "confidence": 0.96,
                                        "speaker": 0,
                                    },
                                    {
                                        "word": "from",
                                        "start": 1.0,
                                        "end": 1.3,
                                        "confidence": 0.94,
                                        "speaker": 0,
                                    },
                                    {
                                        "word": "speaker",
                                        "start": 1.3,
                                        "end": 1.8,
                                        "confidence": 0.92,
                                        "speaker": 1,
                                    },
                                    {
                                        "word": "one",
                                        "start": 1.8,
                                        "end": 2.1,
                                        "confidence": 0.90,
                                        "speaker": 1,
                                    },
                                    {
                                        "word": "and",
                                        "start": 2.1,
                                        "end": 2.4,
                                        "confidence": 0.88,
                                        "speaker": 1,
                                    },
                                    {
                                        "word": "speaker",
                                        "start": 2.4,
                                        "end": 2.9,
                                        "confidence": 0.86,
                                        "speaker": 2,
                                    },
                                    {
                                        "word": "two",
                                        "start": 2.9,
                                        "end": 3.2,
                                        "confidence": 0.84,
                                        "speaker": 2,
                                    },
                                ],
                            }
                        ]
                    }
                ]
            },
        }

        wtf_doc = self.converter.convert_to_wtf(deepgram_data)

        # Validate speakers
        assert wtf_doc.speakers is not None
        assert len(wtf_doc.speakers) == 3  # Three speakers

        # Check speaker details
        assert "0" in wtf_doc.speakers
        assert "1" in wtf_doc.speakers
        assert "2" in wtf_doc.speakers

        speaker_0 = wtf_doc.speakers["0"]
        assert speaker_0.label == "Speaker 0"
        assert speaker_0.total_time > 0
        assert speaker_0.confidence > 0

    def test_wtf_to_deepgram_conversion(self, sample_wtf_document):
        """Test converting WTF document to Deepgram format."""
        # Convert dict to WTFDocument object
        from wtf_transcript_converter.core.models import WTFDocument

        wtf_doc = WTFDocument.model_validate(sample_wtf_document)
        deepgram_data = self.converter.convert_from_wtf(wtf_doc)

        # Validate basic structure
        assert "metadata" in deepgram_data
        assert "results" in deepgram_data
        assert "channels" in deepgram_data["results"]
        assert len(deepgram_data["results"]["channels"]) > 0

        # Validate transcript
        channel = deepgram_data["results"]["channels"][0]
        alternative = channel["alternatives"][0]
        assert alternative["transcript"] == wtf_doc.transcript.text
        assert alternative["confidence"] == wtf_doc.transcript.confidence

        # Validate metadata
        metadata = deepgram_data["metadata"]
        assert metadata["duration"] == wtf_doc.transcript.duration
        assert metadata["channels"] == wtf_doc.metadata.audio.channels

    def test_word_level_conversion(self):
        """Test word-level conversion accuracy."""
        deepgram_data = {
            "metadata": {"duration": 3.0, "channels": 1},
            "results": {
                "channels": [
                    {
                        "alternatives": [
                            {
                                "transcript": "Hello world test",
                                "confidence": 0.95,
                                "words": [
                                    {
                                        "word": "Hello",
                                        "start": 0.0,
                                        "end": 0.5,
                                        "confidence": 0.98,
                                        "speaker": 0,
                                    },
                                    {
                                        "word": "world",
                                        "start": 0.5,
                                        "end": 1.0,
                                        "confidence": 0.96,
                                        "speaker": 0,
                                    },
                                    {
                                        "word": "test",
                                        "start": 1.0,
                                        "end": 1.5,
                                        "confidence": 0.94,
                                        "speaker": 0,
                                    },
                                ],
                            }
                        ]
                    }
                ]
            },
        }

        wtf_doc = self.converter.convert_to_wtf(deepgram_data)

        # Validate words
        assert len(wtf_doc.words) == 3

        word1 = wtf_doc.words[0]
        assert word1.text == "Hello"
        assert word1.start == 0.0
        assert word1.end == 0.5
        assert word1.confidence == 0.98
        assert word1.speaker == 0

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

    def test_segment_creation_from_words(self):
        """Test that segments are properly created from words."""
        deepgram_data = {
            "metadata": {"duration": 5.0, "channels": 1},
            "results": {
                "channels": [
                    {
                        "alternatives": [
                            {
                                "transcript": "Hello world. This is a test.",
                                "confidence": 0.95,
                                "words": [
                                    {
                                        "word": "Hello",
                                        "start": 0.0,
                                        "end": 0.5,
                                        "confidence": 0.98,
                                        "speaker": 0,
                                    },
                                    {
                                        "word": "world",
                                        "start": 0.5,
                                        "end": 1.0,
                                        "confidence": 0.96,
                                        "speaker": 0,
                                    },
                                    {
                                        "word": ".",
                                        "start": 1.0,
                                        "end": 1.1,
                                        "confidence": 0.99,
                                        "speaker": 0,
                                    },
                                    {
                                        "word": "This",
                                        "start": 1.5,
                                        "end": 1.8,
                                        "confidence": 0.94,
                                        "speaker": 0,
                                    },
                                    {
                                        "word": "is",
                                        "start": 1.8,
                                        "end": 2.0,
                                        "confidence": 0.92,
                                        "speaker": 0,
                                    },
                                    {
                                        "word": "a",
                                        "start": 2.0,
                                        "end": 2.1,
                                        "confidence": 0.90,
                                        "speaker": 0,
                                    },
                                    {
                                        "word": "test",
                                        "start": 2.1,
                                        "end": 2.5,
                                        "confidence": 0.88,
                                        "speaker": 0,
                                    },
                                    {
                                        "word": ".",
                                        "start": 2.5,
                                        "end": 2.6,
                                        "confidence": 0.99,
                                        "speaker": 0,
                                    },
                                ],
                            }
                        ]
                    }
                ]
            },
        }

        wtf_doc = self.converter.convert_to_wtf(deepgram_data)

        # Should create segments at sentence boundaries
        assert len(wtf_doc.segments) >= 1

        # Check that segments have proper timing
        for segment in wtf_doc.segments:
            assert segment.start < segment.end
            assert segment.confidence > 0
            assert segment.text.strip() != ""

    def test_punctuation_detection(self):
        """Test punctuation detection in words."""
        deepgram_data = {
            "metadata": {"duration": 2.0, "channels": 1},
            "results": {
                "channels": [
                    {
                        "alternatives": [
                            {
                                "transcript": "Hello, world!",
                                "confidence": 0.95,
                                "words": [
                                    {
                                        "word": "Hello",
                                        "start": 0.0,
                                        "end": 0.5,
                                        "confidence": 0.98,
                                        "speaker": 0,
                                    },
                                    {
                                        "word": ",",
                                        "start": 0.5,
                                        "end": 0.6,
                                        "confidence": 0.99,
                                        "speaker": 0,
                                    },
                                    {
                                        "word": "world",
                                        "start": 0.6,
                                        "end": 1.0,
                                        "confidence": 0.96,
                                        "speaker": 0,
                                    },
                                    {
                                        "word": "!",
                                        "start": 1.0,
                                        "end": 1.1,
                                        "confidence": 0.99,
                                        "speaker": 0,
                                    },
                                ],
                            }
                        ]
                    }
                ]
            },
        }

        wtf_doc = self.converter.convert_to_wtf(deepgram_data)

        # Check punctuation detection
        assert wtf_doc.words[0].is_punctuation is False  # "Hello"
        assert wtf_doc.words[1].is_punctuation is True  # ","
        assert wtf_doc.words[2].is_punctuation is False  # "world"
        assert wtf_doc.words[3].is_punctuation is True  # "!"

    def test_quality_metrics_calculation(self):
        """Test quality metrics calculation."""
        deepgram_data = {
            "metadata": {"duration": 3.0, "channels": 1},
            "results": {
                "channels": [
                    {
                        "alternatives": [
                            {
                                "transcript": "Test with some low confidence words",
                                "confidence": 0.85,  # Medium confidence
                                "words": [
                                    {
                                        "word": "Test",
                                        "start": 0.0,
                                        "end": 0.5,
                                        "confidence": 0.95,
                                        "speaker": 0,
                                    },
                                    {
                                        "word": "with",
                                        "start": 0.5,
                                        "end": 0.8,
                                        "confidence": 0.90,
                                        "speaker": 0,
                                    },
                                    {
                                        "word": "some",
                                        "start": 0.8,
                                        "end": 1.1,
                                        "confidence": 0.30,
                                        "speaker": 0,
                                    },  # Low confidence
                                    {
                                        "word": "low",
                                        "start": 1.1,
                                        "end": 1.4,
                                        "confidence": 0.25,
                                        "speaker": 0,
                                    },  # Low confidence
                                    {
                                        "word": "confidence",
                                        "start": 1.4,
                                        "end": 2.2,
                                        "confidence": 0.85,
                                        "speaker": 0,
                                    },
                                    {
                                        "word": "words",
                                        "start": 2.2,
                                        "end": 2.8,
                                        "confidence": 0.88,
                                        "speaker": 0,
                                    },
                                ],
                            }
                        ]
                    }
                ]
            },
        }

        wtf_doc = self.converter.convert_to_wtf(deepgram_data)

        # Check quality metrics
        assert wtf_doc.quality is not None
        assert wtf_doc.quality.audio_quality == "medium"  # 0.85 confidence
        assert wtf_doc.quality.low_confidence_words == 2  # "some" and "low"
        assert wtf_doc.quality.average_confidence > 0.0

    def test_round_trip_conversion(self, sample_deepgram_data):
        """Test round-trip conversion: Deepgram -> WTF -> Deepgram."""
        # Convert to WTF
        wtf_doc = self.converter.convert_to_wtf(sample_deepgram_data)

        # Convert back to Deepgram
        deepgram_data_back = self.converter.convert_from_wtf(wtf_doc)

        # Validate that key fields are preserved
        original_transcript = sample_deepgram_data["results"]["channels"][0]["alternatives"][0][
            "transcript"
        ]
        back_transcript = deepgram_data_back["results"]["channels"][0]["alternatives"][0][
            "transcript"
        ]
        assert back_transcript == original_transcript

        assert (
            deepgram_data_back["metadata"]["duration"]
            == sample_deepgram_data["metadata"]["duration"]
        )
        assert (
            deepgram_data_back["metadata"]["channels"]
            == sample_deepgram_data["metadata"]["channels"]
        )

    def test_validation_after_conversion(self, sample_deepgram_data):
        """Test that converted WTF document passes validation."""
        wtf_doc = self.converter.convert_to_wtf(sample_deepgram_data)

        is_valid, errors = validate_wtf_document(wtf_doc)
        assert is_valid, f"Validation failed with errors: {errors}"

    def test_error_handling_invalid_data(self):
        """Test error handling with invalid Deepgram data."""
        invalid_data = {
            "metadata": {
                "duration": -1.0,  # Invalid duration
            },
            "results": {"channels": []},  # No channels
        }

        with pytest.raises(ValueError, match="No channels found"):
            self.converter.convert_to_wtf(invalid_data)

    def test_error_handling_no_alternatives(self):
        """Test error handling with no alternatives."""
        invalid_data = {
            "metadata": {
                "duration": 1.0,
            },
            "results": {"channels": [{"alternatives": []}]},  # No alternatives
        }

        with pytest.raises(ValueError, match="No alternatives found"):
            self.converter.convert_to_wtf(invalid_data)

    def test_generic_convert_method(self, sample_deepgram_data):
        """Test the generic convert method that auto-detects format."""
        # Test with Deepgram data
        wtf_doc = self.converter.convert(sample_deepgram_data)
        assert isinstance(wtf_doc, WTFDocument)

        # Test with WTF document
        deepgram_data = self.converter.convert(wtf_doc)
        assert isinstance(deepgram_data, dict)
        assert "metadata" in deepgram_data
        assert "results" in deepgram_data

    def test_deepgram_specific_extensions_preservation(self, sample_deepgram_data):
        """Test that Deepgram-specific data is preserved in extensions."""
        wtf_doc = self.converter.convert_to_wtf(sample_deepgram_data)

        # Check that extensions contain Deepgram-specific data
        assert "deepgram" in wtf_doc.extensions
        deepgram_ext = wtf_doc.extensions["deepgram"]
        assert "metadata" in deepgram_ext
        assert "model_info" in deepgram_ext
        assert "request_id" in deepgram_ext

        # Check that original metadata is preserved
        original_metadata = sample_deepgram_data["metadata"]
        preserved_metadata = deepgram_ext["metadata"]
        assert preserved_metadata["duration"] == original_metadata["duration"]
        assert preserved_metadata["channels"] == original_metadata["channels"]

    def test_empty_words_handling(self):
        """Test handling of empty words list."""
        deepgram_data = {
            "metadata": {"duration": 1.0, "channels": 1},
            "results": {
                "channels": [
                    {
                        "alternatives": [
                            {
                                "transcript": "Test",
                                "confidence": 0.95,
                                "words": [],  # Empty words list
                            }
                        ]
                    }
                ]
            },
        }

        wtf_doc = self.converter.convert_to_wtf(deepgram_data)

        # Should handle empty words gracefully
        assert wtf_doc.words is None or len(wtf_doc.words) == 0
        assert len(wtf_doc.segments) == 0  # No words means no segments
        assert wtf_doc.transcript.text == "Test"

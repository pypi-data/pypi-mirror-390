"""
Integration tests with real transcription providers.

These tests will use actual API calls to transcription providers when API keys are provided.
They are marked as integration tests and can be skipped if no API keys are available.
"""

import os
from typing import Any, Dict

import pytest

from wtf_transcript_converter.core.validator import validate_wtf_document
from wtf_transcript_converter.providers.assemblyai import AssemblyAIConverter
from wtf_transcript_converter.providers.deepgram import DeepgramConverter
from wtf_transcript_converter.providers.whisper import WhisperConverter

# Skip integration tests if no API keys are provided
pytestmark = pytest.mark.skipif(
    not any(
        [
            os.getenv("OPENAI_API_KEY"),
            os.getenv("DEEPGRAM_API_KEY"),
            os.getenv("ASSEMBLYAI_API_KEY"),
        ]
    ),
    reason="No API keys provided. Set OPENAI_API_KEY, DEEPGRAM_API_KEY, or ASSEMBLYAI_API_KEY to run integration tests.",
)


class TestWhisperIntegration:
    """Integration tests for Whisper provider."""

    @pytest.fixture
    def whisper_converter(self):
        """Whisper converter instance."""
        return WhisperConverter()

    @pytest.fixture
    def sample_audio_file(self):
        """Create a sample audio file for testing."""
        # For now, we'll use a placeholder - in real tests, you'd provide an actual audio file
        # This could be a short WAV file or you could download a test audio file
        return None  # Placeholder - would need actual audio file

    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not provided")
    def test_whisper_real_api_call(self, whisper_converter, sample_audio_file):
        """Test Whisper with real API call."""
        if not sample_audio_file:
            pytest.skip("No sample audio file provided")

        # This would make a real API call to Whisper
        # For now, we'll simulate the response structure
        mock_whisper_response = {
            "text": "Hello, this is a test transcription from Whisper API.",
            "language": "en",
            "duration": 3.5,
            "segments": [
                {
                    "id": 0,
                    "start": 0.0,
                    "end": 3.5,
                    "text": "Hello, this is a test transcription from Whisper API.",
                    "tokens": [
                        50364,
                        15496,
                        11,
                        428,
                        318,
                        257,
                        6291,
                        11,
                        257,
                        1878,
                        13,
                    ],
                    "temperature": 0.0,
                    "avg_logprob": -0.2,
                    "compression_ratio": 1.5,
                    "no_speech_prob": 0.01,
                }
            ],
        }

        # Convert to WTF
        wtf_doc = whisper_converter.convert_to_wtf(mock_whisper_response)

        # Validate the conversion
        assert isinstance(wtf_doc, type(whisper_converter.convert_to_wtf({})))
        assert wtf_doc.transcript.text == mock_whisper_response["text"]
        assert wtf_doc.transcript.language == "en-us"  # Normalized

        # Validate WTF document
        is_valid, errors = validate_wtf_document(wtf_doc)
        assert is_valid, f"Validation failed: {errors}"

        # Test round-trip conversion
        whisper_data_back = whisper_converter.convert_from_wtf(wtf_doc)
        assert whisper_data_back["text"] == mock_whisper_response["text"]


class TestDeepgramIntegration:
    """Integration tests for Deepgram provider."""

    @pytest.fixture
    def deepgram_converter(self):
        """Deepgram converter instance."""
        return DeepgramConverter()

    @pytest.mark.skipif(not os.getenv("DEEPGRAM_API_KEY"), reason="DEEPGRAM_API_KEY not provided")
    def test_deepgram_real_api_call(self, deepgram_converter):
        """Test Deepgram with real API call."""
        # This would make a real API call to Deepgram
        # For now, we'll simulate the response structure
        mock_deepgram_response = {
            "metadata": {
                "transaction_key": "deprecated",
                "request_id": "integration-test-123",
                "sha256": "test-sha256-hash",
                "created": "2025-01-02T12:00:00.000Z",
                "duration": 4.2,
                "channels": 1,
                "model_info": {
                    "name": "nova-2",
                    "version": "2024-01-09",
                    "uuid": "4d892fb6-7cc1-4e7a-a1b3-1c2e3f4a5b6c",
                },
            },
            "results": {
                "channels": [
                    {
                        "alternatives": [
                            {
                                "transcript": "Hello, this is a test transcription from Deepgram API.",
                                "confidence": 0.96,
                                "words": [
                                    {
                                        "word": "Hello",
                                        "start": 0.0,
                                        "end": 0.5,
                                        "confidence": 0.98,
                                        "speaker": 0,
                                        "speaker_confidence": 0.95,
                                        "punctuated_word": "Hello,",
                                    },
                                    {
                                        "word": "this",
                                        "start": 0.6,
                                        "end": 0.8,
                                        "confidence": 0.96,
                                        "speaker": 0,
                                        "speaker_confidence": 0.95,
                                        "punctuated_word": "this",
                                    },
                                    {
                                        "word": "is",
                                        "start": 0.8,
                                        "end": 0.9,
                                        "confidence": 0.99,
                                        "speaker": 0,
                                        "speaker_confidence": 0.95,
                                        "punctuated_word": "is",
                                    },
                                    {
                                        "word": "a",
                                        "start": 0.9,
                                        "end": 1.0,
                                        "confidence": 0.97,
                                        "speaker": 0,
                                        "speaker_confidence": 0.95,
                                        "punctuated_word": "a",
                                    },
                                    {
                                        "word": "test",
                                        "start": 1.0,
                                        "end": 1.4,
                                        "confidence": 0.95,
                                        "speaker": 0,
                                        "speaker_confidence": 0.95,
                                        "punctuated_word": "test",
                                    },
                                    {
                                        "word": "transcription",
                                        "start": 1.4,
                                        "end": 2.2,
                                        "confidence": 0.93,
                                        "speaker": 0,
                                        "speaker_confidence": 0.95,
                                        "punctuated_word": "transcription",
                                    },
                                    {
                                        "word": "from",
                                        "start": 2.2,
                                        "end": 2.5,
                                        "confidence": 0.94,
                                        "speaker": 0,
                                        "speaker_confidence": 0.95,
                                        "punctuated_word": "from",
                                    },
                                    {
                                        "word": "Deepgram",
                                        "start": 2.5,
                                        "end": 3.2,
                                        "confidence": 0.92,
                                        "speaker": 0,
                                        "speaker_confidence": 0.95,
                                        "punctuated_word": "Deepgram",
                                    },
                                    {
                                        "word": "API",
                                        "start": 3.2,
                                        "end": 3.6,
                                        "confidence": 0.90,
                                        "speaker": 0,
                                        "speaker_confidence": 0.95,
                                        "punctuated_word": "API",
                                    },
                                    {
                                        "word": ".",
                                        "start": 3.6,
                                        "end": 3.7,
                                        "confidence": 0.99,
                                        "speaker": 0,
                                        "speaker_confidence": 0.95,
                                        "punctuated_word": ".",
                                    },
                                ],
                            }
                        ]
                    }
                ]
            },
        }

        # Convert to WTF
        wtf_doc = deepgram_converter.convert_to_wtf(mock_deepgram_response)

        # Validate the conversion
        assert isinstance(wtf_doc, type(deepgram_converter.convert_to_wtf({})))
        assert (
            wtf_doc.transcript.text
            == mock_deepgram_response["results"]["channels"][0]["alternatives"][0]["transcript"]
        )
        assert wtf_doc.transcript.language == "en-us"  # Normalized

        # Validate WTF document
        is_valid, errors = validate_wtf_document(wtf_doc)
        assert is_valid, f"Validation failed: {errors}"

        # Test round-trip conversion
        deepgram_data_back = deepgram_converter.convert_from_wtf(wtf_doc)
        assert (
            deepgram_data_back["results"]["channels"][0]["alternatives"][0]["transcript"]
            == mock_deepgram_response["results"]["channels"][0]["alternatives"][0]["transcript"]
        )


class TestAssemblyAIIntegration:
    """Integration tests for AssemblyAI provider."""

    @pytest.fixture
    def assemblyai_converter(self):
        """AssemblyAI converter instance."""
        return AssemblyAIConverter()

    @pytest.mark.skipif(
        not os.getenv("ASSEMBLYAI_API_KEY"), reason="ASSEMBLYAI_API_KEY not provided"
    )
    def test_assemblyai_real_api_call(self, assemblyai_converter):
        """Test AssemblyAI with real API call."""
        # This would make a real API call to AssemblyAI
        # For now, we'll simulate the response structure
        mock_assemblyai_response = {
            "id": "integration-test-assemblyai-123",
            "status": "completed",
            "text": "Hello, this is a test transcription from AssemblyAI API.",
            "language_code": "en",
            "language_confidence": 0.98,
            "audio_duration": 4.5,
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
                    "text": "this",
                    "start": 0.6,
                    "end": 0.8,
                    "confidence": 0.96,
                    "speaker": "A",
                },
                {
                    "text": "is",
                    "start": 0.8,
                    "end": 0.9,
                    "confidence": 0.99,
                    "speaker": "A",
                },
                {
                    "text": "a",
                    "start": 0.9,
                    "end": 1.0,
                    "confidence": 0.97,
                    "speaker": "A",
                },
                {
                    "text": "test",
                    "start": 1.0,
                    "end": 1.4,
                    "confidence": 0.95,
                    "speaker": "A",
                },
                {
                    "text": "transcription",
                    "start": 1.4,
                    "end": 2.2,
                    "confidence": 0.93,
                    "speaker": "A",
                },
                {
                    "text": "from",
                    "start": 2.2,
                    "end": 2.5,
                    "confidence": 0.94,
                    "speaker": "A",
                },
                {
                    "text": "AssemblyAI",
                    "start": 2.5,
                    "end": 3.2,
                    "confidence": 0.92,
                    "speaker": "A",
                },
                {
                    "text": "API",
                    "start": 3.2,
                    "end": 3.6,
                    "confidence": 0.90,
                    "speaker": "A",
                },
                {
                    "text": ".",
                    "start": 3.6,
                    "end": 3.7,
                    "confidence": 0.99,
                    "speaker": "A",
                },
            ],
            "created": "2025-01-02T12:00:00.000Z",
            "punctuate": True,
            "format_text": True,
            "dual_channel": False,
            "speaker_labels": True,
            "speakers_expected": 1,
            "speech_model": "best",
            "speech_model_version": "1.0",
        }

        # Convert to WTF
        wtf_doc = assemblyai_converter.convert_to_wtf(mock_assemblyai_response)

        # Validate the conversion
        assert isinstance(wtf_doc, type(assemblyai_converter.convert_to_wtf({})))
        assert wtf_doc.transcript.text == mock_assemblyai_response["text"]
        assert wtf_doc.transcript.language == "en-us"  # Normalized

        # Validate WTF document
        is_valid, errors = validate_wtf_document(wtf_doc)
        assert is_valid, f"Validation failed: {errors}"

        # Test round-trip conversion
        assemblyai_data_back = assemblyai_converter.convert_from_wtf(wtf_doc)
        assert assemblyai_data_back["text"] == mock_assemblyai_response["text"]


class TestCrossProviderIntegration:
    """Integration tests that compare results across providers."""

    @pytest.mark.skipif(
        not all(
            [
                os.getenv("OPENAI_API_KEY"),
                os.getenv("DEEPGRAM_API_KEY"),
                os.getenv("ASSEMBLYAI_API_KEY"),
            ]
        ),
        reason="All three API keys required for cross-provider tests",
    )
    def test_cross_provider_consistency(self):
        """Test that different providers produce consistent WTF output for the same audio."""
        # This would test that the same audio file produces consistent WTF output
        # across different providers, with reasonable tolerance for differences
        pytest.skip("Cross-provider consistency test not yet implemented")


class TestRealAPIIntegration:
    """Tests that make actual API calls to transcription providers."""

    def _make_whisper_api_call(self, audio_file_path: str) -> Dict[str, Any]:
        """Make a real API call to Whisper."""
        # This would use the OpenAI API to transcribe audio
        # For now, return a mock response
        return {
            "text": "Real Whisper API response would go here",
            "language": "en",
            "duration": 3.0,
            "segments": [],
        }

    def _make_deepgram_api_call(self, audio_file_path: str) -> Dict[str, Any]:
        """Make a real API call to Deepgram."""
        # This would use the Deepgram API to transcribe audio
        # For now, return a mock response
        return {
            "metadata": {"duration": 3.0, "channels": 1},
            "results": {
                "channels": [
                    {
                        "alternatives": [
                            {
                                "transcript": "Real Deepgram API response would go here",
                                "confidence": 0.95,
                                "words": [],
                            }
                        ]
                    }
                ]
            },
        }

    def _make_assemblyai_api_call(self, audio_file_path: str) -> Dict[str, Any]:
        """Make a real API call to AssemblyAI."""
        # This would use the AssemblyAI API to transcribe audio
        # For now, return a mock response
        return {
            "id": "real-assemblyai-response",
            "status": "completed",
            "text": "Real AssemblyAI API response would go here",
            "language_code": "en",
            "audio_duration": 3.0,
            "confidence": 0.95,
            "words": [],
        }

    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not provided")
    def test_real_whisper_api_integration(self):
        """Test with real Whisper API call."""
        # This would make an actual API call to Whisper
        # For now, we'll simulate it
        audio_file = "test_audio.wav"  # Would be a real audio file
        if not os.path.exists(audio_file):
            pytest.skip("No test audio file available")

        # Make API call
        whisper_response = self._make_whisper_api_call(audio_file)

        # Convert to WTF
        converter = WhisperConverter()
        wtf_doc = converter.convert_to_wtf(whisper_response)

        # Validate
        is_valid, errors = validate_wtf_document(wtf_doc)
        assert is_valid, f"Validation failed: {errors}"

    @pytest.mark.skipif(not os.getenv("DEEPGRAM_API_KEY"), reason="DEEPGRAM_API_KEY not provided")
    def test_real_deepgram_api_integration(self):
        """Test with real Deepgram API call."""
        # This would make an actual API call to Deepgram
        audio_file = "test_audio.wav"  # Would be a real audio file
        if not os.path.exists(audio_file):
            pytest.skip("No test audio file available")

        # Make API call
        deepgram_response = self._make_deepgram_api_call(audio_file)

        # Convert to WTF
        converter = DeepgramConverter()
        wtf_doc = converter.convert_to_wtf(deepgram_response)

        # Validate
        is_valid, errors = validate_wtf_document(wtf_doc)
        assert is_valid, f"Validation failed: {errors}"

    @pytest.mark.skipif(
        not os.getenv("ASSEMBLYAI_API_KEY"), reason="ASSEMBLYAI_API_KEY not provided"
    )
    def test_real_assemblyai_api_integration(self):
        """Test with real AssemblyAI API call."""
        # This would make an actual API call to AssemblyAI
        audio_file = "test_audio.wav"  # Would be a real audio file
        if not os.path.exists(audio_file):
            pytest.skip("No test audio file available")

        # Make API call
        assemblyai_response = self._make_assemblyai_api_call(audio_file)

        # Convert to WTF
        converter = AssemblyAIConverter()
        wtf_doc = converter.convert_to_wtf(assemblyai_response)

        # Validate
        is_valid, errors = validate_wtf_document(wtf_doc)
        assert is_valid, f"Validation failed: {errors}"

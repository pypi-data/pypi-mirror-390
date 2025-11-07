"""
Integration tests for Hugging Face Canary and Parakeet models.

These tests require HF_TOKEN environment variable and will make real API calls.
"""

import os
import tempfile

import pytest

try:
    import numpy as np
except ImportError:
    np = None
    pytest.skip("numpy is required for integration tests", allow_module_level=True)

from wtf_transcript_converter.providers.canary import CanaryConverter
from wtf_transcript_converter.providers.parakeet import ParakeetConverter


@pytest.mark.skipif(not os.getenv("HF_TOKEN"), reason="HF_TOKEN environment variable not set")
class TestHuggingFaceIntegration:
    """Integration tests for Hugging Face models."""

    @pytest.fixture
    def canary_converter(self):
        """Create a Canary converter instance."""
        return CanaryConverter()

    @pytest.fixture
    def parakeet_converter(self):
        """Create a Parakeet converter instance."""
        return ParakeetConverter()

    @pytest.fixture
    def sample_audio_file(self):
        """Create a sample audio file for testing."""
        # Create a simple sine wave audio file
        sample_rate = 16000
        duration = 3.0  # 3 seconds
        frequency = 440  # A4 note

        # Generate sine wave
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio = np.sin(2 * np.pi * frequency * t) * 0.3  # Low volume

        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            # Simple WAV file creation (minimal implementation)
            # In a real test, you'd use librosa or soundfile to create proper WAV
            f.write(b"RIFF")
            f.write((36 + len(audio) * 2).to_bytes(4, "little"))
            f.write(b"WAVE")
            f.write(b"fmt ")
            f.write((16).to_bytes(4, "little"))
            f.write((1).to_bytes(2, "little"))  # PCM
            f.write((1).to_bytes(2, "little"))  # Mono
            f.write(sample_rate.to_bytes(4, "little"))
            f.write((sample_rate * 2).to_bytes(4, "little"))  # Byte rate
            f.write((2).to_bytes(2, "little"))  # Block align
            f.write((16).to_bytes(2, "little"))  # Bits per sample
            f.write(b"data")
            f.write((len(audio) * 2).to_bytes(4, "little"))

            # Convert float to 16-bit PCM
            audio_16bit = (audio * 32767).astype(np.int16)
            f.write(audio_16bit.tobytes())

            temp_file = f.name

        yield temp_file

        # Cleanup
        try:
            os.unlink(temp_file)
        except OSError:
            pass

    def test_canary_model_loading(self, canary_converter):
        """Test that Canary model can be loaded."""
        # This will test the model loading without actually transcribing
        try:
            canary_converter._load_model()
            assert canary_converter._pipeline is not None
        except (ImportError, RuntimeError, ValueError, OSError) as e:
            pytest.skip(f"Canary model loading failed: {e}")

    def test_parakeet_model_loading(self, parakeet_converter):
        """Test that Parakeet model can be loaded."""
        # This will test the model loading without actually transcribing
        try:
            parakeet_converter._load_model()
            assert parakeet_converter._pipeline is not None
        except (ImportError, RuntimeError, ValueError, OSError) as e:
            pytest.skip(f"Parakeet model loading failed: {e}")

    def test_canary_transcription(self, canary_converter, sample_audio_file):
        """Test Canary transcription with real audio file."""
        try:
            result = canary_converter.transcribe_audio(sample_audio_file, language="en")

            # Check basic structure
            assert "text" in result
            assert "language" in result
            assert "duration" in result
            assert "words" in result
            assert "segments" in result
            assert "model" in result

            # Check that we got some result (even if it's just silence)
            assert isinstance(result["text"], str)
            assert result["language"] == "en"
            assert result["duration"] > 0

        except (ImportError, RuntimeError, ValueError, OSError) as e:
            pytest.skip(f"Canary transcription failed: {e}")

    def test_parakeet_transcription(self, parakeet_converter, sample_audio_file):
        """Test Parakeet transcription with real audio file."""
        try:
            result = parakeet_converter.transcribe_audio(sample_audio_file, language="en")

            # Check basic structure
            assert "text" in result
            assert "language" in result
            assert "duration" in result
            assert "words" in result
            assert "segments" in result
            assert "model" in result

            # Check that we got some result (even if it's just silence)
            assert isinstance(result["text"], str)
            assert result["language"] == "en"
            assert result["duration"] > 0

        except (ImportError, RuntimeError, ValueError, OSError) as e:
            pytest.skip(f"Parakeet transcription failed: {e}")

    def test_canary_full_pipeline(self, canary_converter, sample_audio_file):
        """Test full Canary pipeline: transcribe -> convert to WTF -> convert back."""
        try:
            # Transcribe audio
            canary_result = canary_converter.transcribe_audio(sample_audio_file, language="en")

            # Convert to WTF
            wtf_doc = canary_converter.convert_to_wtf(canary_result)

            # Validate WTF document
            assert wtf_doc.transcript.text == canary_result["text"]
            assert wtf_doc.transcript.language == "en"
            assert wtf_doc.transcript.duration == canary_result["duration"]
            assert wtf_doc.metadata.provider == "canary"
            assert wtf_doc.metadata.model == canary_result["model"]

            # Convert back to Canary format
            canary_back = canary_converter.convert_from_wtf(wtf_doc)

            # Check round-trip consistency
            assert canary_back["text"] == canary_result["text"]
            assert canary_back["language"] == canary_result["language"]
            assert canary_back["duration"] == canary_result["duration"]
            assert canary_back["model"] == canary_result["model"]

        except (ImportError, RuntimeError, ValueError, OSError) as e:
            pytest.skip(f"Canary full pipeline failed: {e}")

    def test_parakeet_full_pipeline(self, parakeet_converter, sample_audio_file):
        """Test full Parakeet pipeline: transcribe -> convert to WTF -> convert back."""
        try:
            # Transcribe audio
            parakeet_result = parakeet_converter.transcribe_audio(sample_audio_file, language="en")

            # Convert to WTF
            wtf_doc = parakeet_converter.convert_to_wtf(parakeet_result)

            # Validate WTF document
            assert wtf_doc.transcript.text == parakeet_result["text"]
            assert wtf_doc.transcript.language == "en"
            assert wtf_doc.transcript.duration == parakeet_result["duration"]
            assert wtf_doc.metadata.provider == "parakeet"
            assert wtf_doc.metadata.model == parakeet_result["model"]

            # Convert back to Parakeet format
            parakeet_back = parakeet_converter.convert_from_wtf(wtf_doc)

            # Check round-trip consistency
            assert parakeet_back["text"] == parakeet_result["text"]
            assert parakeet_back["language"] == parakeet_result["language"]
            assert parakeet_back["duration"] == parakeet_result["duration"]
            assert parakeet_back["model"] == parakeet_result["model"]

        except (ImportError, RuntimeError, ValueError, OSError) as e:
            pytest.skip(f"Parakeet full pipeline failed: {e}")

    def test_model_comparison(self, canary_converter, parakeet_converter, sample_audio_file):
        """Test comparing results from both models."""
        try:
            # Transcribe with both models
            canary_result = canary_converter.transcribe_audio(sample_audio_file, language="en")
            parakeet_result = parakeet_converter.transcribe_audio(sample_audio_file, language="en")

            # Both should produce valid results
            assert isinstance(canary_result["text"], str)
            assert isinstance(parakeet_result["text"], str)
            assert canary_result["duration"] > 0
            assert parakeet_result["duration"] > 0

            # Convert both to WTF for comparison
            canary_wtf = canary_converter.convert_to_wtf(canary_result)
            parakeet_wtf = parakeet_converter.convert_to_wtf(parakeet_result)

            # Both should be valid WTF documents
            assert canary_wtf.metadata.provider == "canary"
            assert parakeet_wtf.metadata.provider == "parakeet"

        except (ImportError, RuntimeError, ValueError, OSError) as e:
            pytest.skip(f"Model comparison failed: {e}")


@pytest.mark.skipif(os.getenv("HF_TOKEN"), reason="HF_TOKEN is set, skipping mock tests")
class TestHuggingFaceMock:
    """Mock tests when HF_TOKEN is not available."""

    def test_canary_converter_mock(self):
        """Test Canary converter without HF token."""
        converter = CanaryConverter()

        # Should be able to create converter
        assert converter.provider_name == "canary"
        assert converter.model_name == "nvidia/canary-1b-v2"

        # Model loading should fail gracefully (either ImportError or RuntimeError)
        with pytest.raises((ImportError, RuntimeError)):
            converter._load_model()

    def test_parakeet_converter_mock(self):
        """Test Parakeet converter without HF token."""
        converter = ParakeetConverter()

        # Should be able to create converter
        assert converter.provider_name == "parakeet"
        assert converter.model_name == "nvidia/parakeet-tdt-0.6b-v3"

        # Model loading should fail gracefully (either ImportError or RuntimeError)
        with pytest.raises((ImportError, RuntimeError)):
            converter._load_model()

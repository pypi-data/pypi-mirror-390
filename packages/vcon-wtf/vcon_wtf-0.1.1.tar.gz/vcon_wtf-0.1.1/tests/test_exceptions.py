"""Tests for custom exceptions."""

from wtf_transcript_converter.exceptions import (
    AudioProcessingError,
    ConfigurationError,
    ConversionError,
    ProviderError,
    ValidationError,
)


class TestConversionError:
    """Test ConversionError exception."""

    def test_conversion_error_basic(self):
        """Test basic ConversionError creation."""
        error = ConversionError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.provider is None
        assert error.original_error is None
        assert error.context == {}

    def test_conversion_error_with_provider(self):
        """Test ConversionError with provider."""
        error = ConversionError("Test error", provider="whisper")
        assert str(error) == "[whisper] Test error"
        assert error.provider == "whisper"

    def test_conversion_error_with_original_error(self):
        """Test ConversionError with original error."""
        original = ValueError("Original error")
        error = ConversionError("Test error", original_error=original)
        assert "Original: Original error" in str(error)
        assert error.original_error == original

    def test_conversion_error_with_context(self):
        """Test ConversionError with context."""
        context = {"file": "test.json", "line": 10}
        error = ConversionError("Test error", context=context)
        assert error.context == context

    def test_conversion_error_full(self):
        """Test ConversionError with all parameters."""
        original = ValueError("Original error")
        context = {"file": "test.json"}
        error = ConversionError(
            "Test error", provider="whisper", original_error=original, context=context
        )
        assert "[whisper] Test error (Original: Original error)" == str(error)
        assert error.provider == "whisper"
        assert error.original_error == original
        assert error.context == context


class TestValidationError:
    """Test ValidationError exception."""

    def test_validation_error_basic(self):
        """Test basic ValidationError creation."""
        error = ValidationError("Test validation error")
        assert str(error) == "Test validation error"
        assert error.message == "Test validation error"
        assert error.field is None
        assert error.value is None
        assert error.errors == []

    def test_validation_error_with_field(self):
        """Test ValidationError with field."""
        error = ValidationError("Test error", field="transcript")
        assert str(error) == "Field 'transcript': Test error"
        assert error.field == "transcript"

    def test_validation_error_with_value(self):
        """Test ValidationError with value."""
        error = ValidationError("Test error", value="invalid_value")
        assert error.value == "invalid_value"

    def test_validation_error_with_errors(self):
        """Test ValidationError with specific errors."""
        errors = ["Error 1", "Error 2"]
        error = ValidationError("Test error", errors=errors)
        assert "Errors: Error 1, Error 2" in str(error)
        assert error.errors == errors

    def test_validation_error_full(self):
        """Test ValidationError with all parameters."""
        errors = ["Error 1", "Error 2"]
        error = ValidationError(
            "Test error", field="transcript", value="invalid_value", errors=errors
        )
        assert "Field 'transcript': Test error Errors: Error 1, Error 2" == str(error)
        assert error.field == "transcript"
        assert error.value == "invalid_value"
        assert error.errors == errors


class TestProviderError:
    """Test ProviderError exception."""

    def test_provider_error_basic(self):
        """Test basic ProviderError creation."""
        error = ProviderError("Test error", provider="whisper")
        assert str(error) == "[whisper] Test error"
        assert error.message == "Test error"
        assert error.provider == "whisper"
        assert error.operation is None
        assert error.status_code is None
        assert error.response_data == {}

    def test_provider_error_with_operation(self):
        """Test ProviderError with operation."""
        error = ProviderError("Test error", provider="whisper", operation="transcribe")
        assert "[whisper] Test error (Operation: transcribe)" == str(error)
        assert error.operation == "transcribe"

    def test_provider_error_with_status_code(self):
        """Test ProviderError with status code."""
        error = ProviderError("Test error", provider="whisper", status_code=404)
        assert "[whisper] Test error (Status: 404)" == str(error)
        assert error.status_code == 404

    def test_provider_error_with_response_data(self):
        """Test ProviderError with response data."""
        response_data = {"error": "Not found", "code": 404}
        error = ProviderError("Test error", provider="whisper", response_data=response_data)
        assert error.response_data == response_data

    def test_provider_error_full(self):
        """Test ProviderError with all parameters."""
        response_data = {"error": "Not found"}
        error = ProviderError(
            "Test error",
            provider="whisper",
            operation="transcribe",
            status_code=404,
            response_data=response_data,
        )
        assert "[whisper] Test error (Operation: transcribe) (Status: 404)" == str(error)
        assert error.provider == "whisper"
        assert error.operation == "transcribe"
        assert error.status_code == 404
        assert error.response_data == response_data


class TestConfigurationError:
    """Test ConfigurationError exception."""

    def test_configuration_error_basic(self):
        """Test basic ConfigurationError creation."""
        error = ConfigurationError("Test config error")
        assert str(error) == "Test config error"
        assert error.message == "Test config error"
        assert error.setting is None
        assert error.value is None

    def test_configuration_error_with_setting(self):
        """Test ConfigurationError with setting."""
        error = ConfigurationError("Test error", setting="api_key")
        assert str(error) == "Setting 'api_key': Test error"
        assert error.setting == "api_key"

    def test_configuration_error_with_value(self):
        """Test ConfigurationError with value."""
        error = ConfigurationError("Test error", value="invalid_value")
        assert error.value == "invalid_value"

    def test_configuration_error_full(self):
        """Test ConfigurationError with all parameters."""
        error = ConfigurationError("Test error", setting="api_key", value="invalid_value")
        assert "Setting 'api_key': Test error (Value: invalid_value)" == str(error)
        assert error.setting == "api_key"
        assert error.value == "invalid_value"


class TestAudioProcessingError:
    """Test AudioProcessingError exception."""

    def test_audio_processing_error_basic(self):
        """Test basic AudioProcessingError creation."""
        error = AudioProcessingError("Test audio error")
        assert str(error) == "Test audio error"
        assert error.message == "Test audio error"
        assert error.file_path is None
        assert error.format is None
        assert error.original_error is None

    def test_audio_processing_error_with_file_path(self):
        """Test AudioProcessingError with file path."""
        error = AudioProcessingError("Test error", file_path="test.wav")
        assert str(error) == "File 'test.wav': Test error"
        assert error.file_path == "test.wav"

    def test_audio_processing_error_with_format(self):
        """Test AudioProcessingError with format."""
        error = AudioProcessingError("Test error", format="wav")
        assert error.format == "wav"

    def test_audio_processing_error_with_original_error(self):
        """Test AudioProcessingError with original error."""
        original = ValueError("Original error")
        error = AudioProcessingError("Test error", original_error=original)
        assert "Original: Original error" in str(error)
        assert error.original_error == original

    def test_audio_processing_error_full(self):
        """Test AudioProcessingError with all parameters."""
        original = ValueError("Original error")
        error = AudioProcessingError(
            "Test error", file_path="test.wav", format="wav", original_error=original
        )
        assert "File 'test.wav': Test error (Format: wav) (Original: Original error)" == str(error)
        assert error.file_path == "test.wav"
        assert error.format == "wav"
        assert error.original_error == original

"""Tests for the main CLI module."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from wtf_transcript_converter.cli.main import from_wtf, main, providers, to_wtf, validate


class TestMainCLI:
    """Test the main CLI functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_main_help(self):
        """Test main command help."""
        result = self.runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "vCon WTF" in result.output

    def test_providers_command(self):
        """Test providers command."""
        result = self.runner.invoke(providers)
        assert result.exit_code == 0
        assert "Supported Transcription Providers" in result.output
        assert "whisper" in result.output
        assert "deepgram" in result.output
        assert "assemblyai" in result.output
        assert "rev-ai" in result.output
        assert "canary" in result.output
        assert "parakeet" in result.output

    @patch("wtf_transcript_converter.cli.main.WhisperConverter")
    def test_to_wtf_whisper(self, mock_converter):
        """Test converting Whisper format to WTF."""
        mock_instance = MagicMock()
        mock_converter.return_value = mock_instance
        mock_instance.convert_to_wtf.return_value = {"transcript": {"text": "test"}}

        result = self.runner.invoke(
            to_wtf, ["tests/fixtures/whisper_sample.json", "-p", "whisper", "-o", "output.json"]
        )

        assert result.exit_code == 0
        mock_instance.convert_to_wtf.assert_called_once()

    @patch("wtf_transcript_converter.cli.main.WhisperConverter")
    def test_from_wtf_whisper(self, mock_converter):
        """Test converting WTF format to Whisper."""
        mock_instance = MagicMock()
        mock_converter.return_value = mock_instance
        mock_instance.convert_from_wtf.return_value = {"text": "test"}

        result = self.runner.invoke(
            from_wtf,
            ["tests/fixtures/whisper_sample.wtf.json", "-p", "whisper", "-o", "output.json"],
        )

        assert result.exit_code == 0
        mock_instance.convert_from_wtf.assert_called_once()

    def test_to_wtf_invalid_provider(self):
        """Test to-wtf with invalid provider."""
        result = self.runner.invoke(
            to_wtf, ["tests/fixtures/whisper_sample.json", "-p", "invalid", "-o", "output.json"]
        )

        # CLI shows error message but returns exit code 0
        assert result.exit_code == 0
        assert "Unsupported provider 'invalid'" in result.output

    def test_from_wtf_invalid_provider(self):
        """Test from-wtf with invalid provider."""
        result = self.runner.invoke(
            from_wtf,
            ["tests/fixtures/whisper_sample.wtf.json", "-p", "invalid", "-o", "output.json"],
        )

        # CLI shows error message but returns exit code 0
        assert result.exit_code == 0
        assert "Unsupported provider 'invalid'" in result.output

    def test_validate_command(self):
        """Test validate command."""
        result = self.runner.invoke(validate, ["tests/fixtures/whisper_sample.wtf.json"])

        assert result.exit_code == 0
        assert "WTF validation not yet implemented" in result.output
        assert "Input file: tests/fixtures/whisper_sample.wtf.json" in result.output

    def test_validate_command_invalid(self):
        """Test validate command with invalid document."""
        result = self.runner.invoke(validate, ["nonexistent.json"])

        assert result.exit_code != 0

    def test_to_wtf_missing_input_file(self):
        """Test to-wtf with missing input file."""
        result = self.runner.invoke(
            to_wtf, ["nonexistent.json", "-p", "whisper", "-o", "output.json"]
        )

        assert result.exit_code != 0

    def test_from_wtf_missing_input_file(self):
        """Test from-wtf with missing input file."""
        result = self.runner.invoke(
            from_wtf, ["nonexistent.json", "-p", "whisper", "-o", "output.json"]
        )

        assert result.exit_code != 0

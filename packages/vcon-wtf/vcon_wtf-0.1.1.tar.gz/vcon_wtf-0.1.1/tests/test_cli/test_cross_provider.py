"""Tests for the cross-provider CLI module."""

from click.testing import CliRunner

from wtf_transcript_converter.cli.cross_provider import (
    all,
    consistency,
    cross_provider,
    performance,
    quality,
)


class TestCrossProviderCLI:
    """Test the cross-provider CLI functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_cross_provider_help(self):
        """Test cross-provider command help."""
        result = self.runner.invoke(cross_provider, ["--help"])
        assert result.exit_code == 0
        assert "Cross-provider testing" in result.output

    def test_consistency_command(self):
        """Test consistency command."""
        result = self.runner.invoke(consistency, ["tests/fixtures/whisper_sample.json"])

        assert result.exit_code == 0
        assert "Testing consistency across providers" in result.output
        assert "Consistency Summary" in result.output
        assert "whisper" in result.output

    def test_performance_command(self):
        """Test performance command."""
        result = self.runner.invoke(performance, ["tests/fixtures/whisper_sample.json"])

        assert result.exit_code == 0
        assert "Benchmarking performance across providers" in result.output
        assert "Performance Summary" in result.output

    def test_quality_command(self):
        """Test quality command."""
        result = self.runner.invoke(quality, ["tests/fixtures/whisper_sample.json"])

        assert result.exit_code == 0
        assert "Comparing quality across providers" in result.output
        assert "Quality Summary" in result.output

    def test_all_tests_command(self):
        """Test all-tests command."""
        result = self.runner.invoke(
            all, ["tests/fixtures/whisper_sample.json", "-o", "output_dir"]
        )

        assert result.exit_code == 0
        assert "Running comprehensive cross-provider analysis" in result.output
        assert "Comprehensive cross-provider analysis complete" in result.output

    def test_consistency_missing_file(self):
        """Test consistency command with missing file."""
        result = self.runner.invoke(consistency, ["nonexistent.json"])

        assert result.exit_code != 0
        assert "does not exist" in result.output

    def test_performance_missing_file(self):
        """Test performance command with missing file."""
        result = self.runner.invoke(performance, ["nonexistent.json"])

        assert result.exit_code != 0
        assert "does not exist" in result.output

    def test_quality_missing_file(self):
        """Test quality command with missing file."""
        result = self.runner.invoke(quality, ["nonexistent.json"])

        assert result.exit_code != 0
        assert "does not exist" in result.output

    def test_all_tests_missing_file(self):
        """Test all command with missing file."""
        result = self.runner.invoke(all, ["nonexistent.json", "-o", "output_dir"])

        assert result.exit_code != 0

    def test_consistency_invalid_json(self):
        """Test consistency command with invalid JSON."""
        result = self.runner.invoke(consistency, ["tests/fixtures/invalid.json"])

        # CLI handles invalid JSON gracefully and returns exit code 0
        assert result.exit_code == 0
        assert "Error during consistency testing" in result.output

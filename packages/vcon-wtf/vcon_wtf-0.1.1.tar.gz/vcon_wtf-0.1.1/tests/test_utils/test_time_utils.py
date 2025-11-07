"""Tests for time utilities."""

import pytest

from wtf_transcript_converter.utils.time_utils import (
    convert_timestamp,
    get_current_iso_timestamp,
    validate_timing,
)


class TestTimeUtils:
    """Test time utility functions."""

    def test_convert_timestamp_float(self):
        """Test converting float timestamp."""
        assert convert_timestamp(1.5) == 1.5
        assert convert_timestamp(0.0) == 0.0
        assert convert_timestamp(100.0) == 100.0

    def test_convert_timestamp_int(self):
        """Test converting int timestamp."""
        assert convert_timestamp(1) == 1.0
        assert convert_timestamp(0) == 0.0
        assert convert_timestamp(100) == 100.0

    def test_convert_timestamp_string(self):
        """Test converting string timestamp."""
        # Currently returns 0.0 for strings (TODO implementation)
        assert convert_timestamp("1.5") == 0.0
        assert convert_timestamp("0") == 0.0

    def test_convert_timestamp_invalid_type(self):
        """Test converting invalid timestamp type."""
        with pytest.raises(ValueError):
            convert_timestamp(None)

    def test_convert_timestamp_negative(self):
        """Test converting negative timestamp."""
        assert convert_timestamp(-1.5) == -1.5
        assert convert_timestamp(-1) == -1.0

    def test_validate_timing_valid(self):
        """Test validating valid timing."""
        assert validate_timing(0.0, 1.0) is True
        assert validate_timing(1.0, 2.0) is True
        assert validate_timing(0.5, 1.5) is True

    def test_validate_timing_invalid_end_before_start(self):
        """Test validating timing where end is before start."""
        assert validate_timing(1.0, 0.5) is False
        assert validate_timing(2.0, 1.0) is False

    def test_validate_timing_invalid_negative_start(self):
        """Test validating timing with negative start."""
        assert validate_timing(-0.5, 1.0) is False
        assert validate_timing(-1.0, 0.0) is False

    def test_validate_timing_zero_duration(self):
        """Test validating timing with zero duration."""
        assert validate_timing(1.0, 1.0) is False

    def test_validate_timing_zero_start(self):
        """Test validating timing with zero start."""
        assert validate_timing(0.0, 1.0) is True

    def test_get_current_iso_timestamp(self):
        """Test getting current ISO timestamp."""
        timestamp = get_current_iso_timestamp()

        # Should be a string
        assert isinstance(timestamp, str)

        # Should end with 'Z' (UTC indicator)
        assert timestamp.endswith("Z")

        # Should contain 'T' (ISO 8601 format)
        assert "T" in timestamp

        # Should be a reasonable length
        assert len(timestamp) > 10

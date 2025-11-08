"""Unit tests for utility functions."""

from datetime import datetime

import pytest

from leapocr._internal.utils import calculate_progress, parse_datetime


class TestParseDatetime:
    """Tests for datetime parsing."""

    def test_parse_rfc3339_with_z(self):
        """Test parsing RFC3339 datetime with Z suffix."""
        result = parse_datetime("2024-01-15T10:30:00Z")
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 10
        assert result.minute == 30
        assert result.second == 0

    def test_parse_rfc3339_with_timezone(self):
        """Test parsing RFC3339 datetime with timezone offset."""
        result = parse_datetime("2024-01-15T10:30:00+00:00")
        assert isinstance(result, datetime)
        assert result.year == 2024

    def test_parse_rfc3339_with_positive_offset(self):
        """Test parsing with positive timezone offset."""
        result = parse_datetime("2024-01-15T10:30:00+05:30")
        assert isinstance(result, datetime)
        assert result.year == 2024

    def test_parse_invalid_datetime(self):
        """Test parsing invalid datetime returns epoch."""
        result = parse_datetime("not-a-date")
        assert isinstance(result, datetime)
        assert result == datetime.fromtimestamp(0)

    def test_parse_none(self):
        """Test parsing None returns epoch."""
        result = parse_datetime(None)
        assert isinstance(result, datetime)
        assert result == datetime.fromtimestamp(0)

    def test_parse_empty_string(self):
        """Test parsing empty string returns epoch."""
        result = parse_datetime("")
        assert isinstance(result, datetime)
        # Empty string should also fallback to epoch

    def test_parse_with_milliseconds(self):
        """Test parsing datetime with milliseconds."""
        result = parse_datetime("2024-01-15T10:30:00.123Z")
        assert isinstance(result, datetime)
        assert result.year == 2024

    def test_parse_datetime_always_returns_datetime(self):
        """Ensure parse_datetime never returns None."""
        test_cases = [
            "2024-01-15T10:30:00Z",
            "invalid",
            None,
            "",
            "2024-13-45T99:99:99Z",  # Invalid date
        ]

        for test_input in test_cases:
            result = parse_datetime(test_input)
            assert isinstance(result, datetime), f"Failed for input: {test_input}"


class TestCalculateProgress:
    """Tests for progress calculation."""

    def test_normal_progress(self):
        """Test normal progress calculation."""
        status_data = {"processed_pages": 5, "total_pages": 10}
        assert calculate_progress(status_data) == 50.0

    def test_zero_progress(self):
        """Test zero progress."""
        status_data = {"processed_pages": 0, "total_pages": 10}
        assert calculate_progress(status_data) == 0.0

    def test_complete_progress(self):
        """Test 100% progress."""
        status_data = {"processed_pages": 10, "total_pages": 10}
        assert calculate_progress(status_data) == 100.0

    def test_no_total_pages(self):
        """Test with zero total pages."""
        status_data = {"processed_pages": 0, "total_pages": 0}
        assert calculate_progress(status_data) == 0.0

    def test_missing_processed_pages(self):
        """Test with missing processed_pages key."""
        status_data = {"total_pages": 10}
        assert calculate_progress(status_data) == 0.0

    def test_missing_total_pages(self):
        """Test with missing total_pages key."""
        status_data = {"processed_pages": 5}
        assert calculate_progress(status_data) == 0.0

    def test_empty_status_data(self):
        """Test with empty status data."""
        status_data = {}
        assert calculate_progress(status_data) == 0.0

    def test_progress_clamped_to_100(self):
        """Test that progress is clamped to maximum 100."""
        # Edge case: more processed than total (shouldn't happen, but test boundary)
        status_data = {"processed_pages": 15, "total_pages": 10}
        progress = calculate_progress(status_data)
        assert progress <= 100.0

    def test_progress_clamped_to_0(self):
        """Test that progress is clamped to minimum 0."""
        # Edge case: negative values (shouldn't happen, but test boundary)
        status_data = {"processed_pages": -1, "total_pages": 10}
        progress = calculate_progress(status_data)
        assert progress >= 0.0

    def test_fractional_progress(self):
        """Test fractional progress values."""
        status_data = {"processed_pages": 1, "total_pages": 3}
        progress = calculate_progress(status_data)
        assert 33.0 < progress < 34.0  # Should be approximately 33.33%

    def test_large_numbers(self):
        """Test with large page counts."""
        status_data = {"processed_pages": 5000, "total_pages": 10000}
        assert calculate_progress(status_data) == 50.0

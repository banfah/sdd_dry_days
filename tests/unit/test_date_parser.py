"""Unit tests for DateParser utility.

This module tests the date parsing functionality including:
- Parsing dates in multiple formats (ISO, US, EU, compact)
- Invalid format handling with helpful error messages
- Leap year validation (accepts Feb 29 in leap years, rejects in non-leap years)
- Date range generation with validation
- Empty and whitespace input handling

The tests ensure >90% coverage of the date_parser.py module.
"""

from datetime import datetime
from unittest.mock import Mock
import pytest

from sdd_dry_days.utils.date_parser import DateParser, DateParseError


class TestDateParserParse:
    """Tests for DateParser.parse() method - date format parsing."""

    def test_parse_iso_format_succeeds(self):
        """Test parsing date in ISO format (YYYY-MM-DD)."""
        result = DateParser.parse("2026-03-06")

        assert result == datetime(2026, 3, 6)
        assert isinstance(result, datetime)

    def test_parse_us_format_succeeds(self):
        """Test parsing date in US format (MM/DD/YYYY)."""
        result = DateParser.parse("03/06/2026")

        assert result == datetime(2026, 3, 6)

    def test_parse_eu_dash_format_succeeds(self):
        """Test parsing date in European format with dashes (DD-MM-YYYY)."""
        result = DateParser.parse("06-03-2026")

        assert result == datetime(2026, 3, 6)

    def test_parse_eu_slash_format_succeeds(self):
        """Test parsing date in European format with slashes (DD/MM/YYYY)."""
        # Use a date that's unambiguous - day > 12 so it can't be month
        result = DateParser.parse("25/03/2026")

        assert result == datetime(2026, 3, 25)

    def test_parse_compact_format_succeeds(self):
        """Test parsing date in compact format (YYYYMMDD)."""
        result = DateParser.parse("20260306")

        assert result == datetime(2026, 3, 6)

    def test_parse_with_leading_whitespace_succeeds(self):
        """Test parsing date with leading whitespace is handled."""
        result = DateParser.parse("  2026-03-06")

        assert result == datetime(2026, 3, 6)

    def test_parse_with_trailing_whitespace_succeeds(self):
        """Test parsing date with trailing whitespace is handled."""
        result = DateParser.parse("2026-03-06  ")

        assert result == datetime(2026, 3, 6)

    def test_parse_with_leading_and_trailing_whitespace_succeeds(self):
        """Test parsing date with both leading and trailing whitespace."""
        result = DateParser.parse("  2026-03-06  ")

        assert result == datetime(2026, 3, 6)

    def test_parse_leap_year_date_succeeds(self):
        """Test parsing February 29 in a leap year."""
        result = DateParser.parse("2024-02-29")

        assert result == datetime(2024, 2, 29)

    def test_parse_various_months_succeeds(self):
        """Test parsing dates from different months."""
        dates = [
            ("2026-01-15", datetime(2026, 1, 15)),
            ("2026-06-30", datetime(2026, 6, 30)),
            ("2026-12-25", datetime(2026, 12, 25)),
        ]

        for date_str, expected in dates:
            result = DateParser.parse(date_str)
            assert result == expected

    def test_parse_invalid_format_raises_date_parse_error(self):
        """Test parsing invalid format raises DateParseError with helpful message."""
        with pytest.raises(DateParseError) as exc_info:
            DateParser.parse("invalid-date")

        error_message = str(exc_info.value)
        assert "Invalid date format: 'invalid-date'" in error_message
        assert "YYYY-MM-DD" in error_message
        assert "MM/DD/YYYY" in error_message
        assert "DD-MM-YYYY" in error_message
        assert "DD/MM/YYYY" in error_message
        assert "YYYYMMDD" in error_message

    def test_parse_empty_string_raises_date_parse_error(self):
        """Test parsing empty string raises DateParseError."""
        with pytest.raises(DateParseError) as exc_info:
            DateParser.parse("")

        assert "Invalid date format" in str(exc_info.value)

    def test_parse_whitespace_only_raises_date_parse_error(self):
        """Test parsing whitespace-only string raises DateParseError."""
        with pytest.raises(DateParseError) as exc_info:
            DateParser.parse("   ")

        assert "Invalid date format" in str(exc_info.value)

    def test_parse_partial_date_raises_date_parse_error(self):
        """Test parsing incomplete date raises DateParseError."""
        with pytest.raises(DateParseError):
            DateParser.parse("2026-03")

    def test_parse_invalid_month_raises_date_parse_error(self):
        """Test parsing invalid month (13) raises DateParseError."""
        with pytest.raises(DateParseError):
            DateParser.parse("2026-13-01")

    def test_parse_invalid_day_raises_date_parse_error(self):
        """Test parsing invalid day (32) raises DateParseError."""
        with pytest.raises(DateParseError):
            DateParser.parse("2026-03-32")

    def test_parse_text_instead_of_date_raises_date_parse_error(self):
        """Test parsing text string raises DateParseError with all format examples."""
        with pytest.raises(DateParseError) as exc_info:
            DateParser.parse("March 6, 2026")

        error_message = str(exc_info.value)
        assert "March 6, 2026" in error_message
        assert "Supported formats:" in error_message


class TestDateParserValidateLeapYear:
    """Tests for DateParser.validate_leap_year() method - leap year validation."""

    def test_validate_leap_year_accepts_feb_29_in_2024_leap_year(self):
        """Test that Feb 29, 2024 is accepted (2024 is a leap year)."""
        date = datetime(2024, 2, 29)

        result = DateParser.validate_leap_year(date)

        assert result is True

    def test_validate_leap_year_accepts_feb_29_in_2020_leap_year(self):
        """Test that Feb 29, 2020 is accepted (2020 is a leap year)."""
        date = datetime(2020, 2, 29)

        result = DateParser.validate_leap_year(date)

        assert result is True

    def test_validate_leap_year_accepts_feb_29_in_2000_leap_year(self):
        """Test that Feb 29, 2000 is accepted (2000 is a leap year - divisible by 400)."""
        date = datetime(2000, 2, 29)

        result = DateParser.validate_leap_year(date)

        assert result is True

    def test_validate_leap_year_rejects_feb_29_in_2025_non_leap_year(self):
        """Test that Feb 29, 2025 is rejected (2025 is not a leap year)."""
        # Create a mock datetime object with Feb 29, 2025
        date = Mock()
        date.month = 2
        date.day = 29
        date.year = 2025

        with pytest.raises(DateParseError) as exc_info:
            DateParser.validate_leap_year(date)

        error_message = str(exc_info.value)
        assert "February 29 does not exist in 2025" in error_message
        assert "not a leap year" in error_message

    def test_validate_leap_year_rejects_feb_29_in_2023_non_leap_year(self):
        """Test that Feb 29, 2023 is rejected (2023 is not a leap year)."""
        # Create a mock datetime object with Feb 29, 2023
        date = Mock()
        date.month = 2
        date.day = 29
        date.year = 2023

        with pytest.raises(DateParseError) as exc_info:
            DateParser.validate_leap_year(date)

        assert "2023" in str(exc_info.value)
        assert "not a leap year" in str(exc_info.value)

    def test_validate_leap_year_rejects_feb_29_in_1900_non_leap_year(self):
        """Test that Feb 29, 1900 is rejected (1900 is not a leap year - century not divisible by 400)."""
        # Create a mock datetime object with Feb 29, 1900
        date = Mock()
        date.month = 2
        date.day = 29
        date.year = 1900

        with pytest.raises(DateParseError) as exc_info:
            DateParser.validate_leap_year(date)

        assert "1900" in str(exc_info.value)

    def test_validate_leap_year_accepts_non_feb_29_dates(self):
        """Test that non-Feb-29 dates always pass validation."""
        dates = [
            datetime(2023, 2, 28),  # Non-leap year, Feb 28
            datetime(2026, 3, 6),   # Regular date
            datetime(2025, 12, 31), # Year end
            datetime(2024, 1, 1),   # Year start
        ]

        for date in dates:
            result = DateParser.validate_leap_year(date)
            assert result is True

    def test_validate_leap_year_accepts_feb_28_in_non_leap_year(self):
        """Test that Feb 28 in non-leap year is accepted."""
        date = datetime(2023, 2, 28)

        result = DateParser.validate_leap_year(date)

        assert result is True

    def test_validate_leap_year_accepts_march_in_leap_year(self):
        """Test that March dates in leap years are accepted."""
        date = datetime(2024, 3, 1)

        result = DateParser.validate_leap_year(date)

        assert result is True


class TestDateParserGenerateDateRange:
    """Tests for DateParser.generate_date_range() method - date range generation."""

    def test_generate_date_range_single_day_succeeds(self):
        """Test generating range with same start and end date (single day)."""
        start = datetime(2026, 3, 6)
        end = datetime(2026, 3, 6)

        result = DateParser.generate_date_range(start, end)

        assert len(result) == 1
        assert result[0] == datetime(2026, 3, 6)

    def test_generate_date_range_three_days_succeeds(self):
        """Test generating range spanning three consecutive days."""
        start = datetime(2026, 3, 1)
        end = datetime(2026, 3, 3)

        result = DateParser.generate_date_range(start, end)

        assert len(result) == 3
        assert result[0] == datetime(2026, 3, 1)
        assert result[1] == datetime(2026, 3, 2)
        assert result[2] == datetime(2026, 3, 3)

    def test_generate_date_range_full_week_succeeds(self):
        """Test generating range spanning a full week (7 days)."""
        start = datetime(2026, 3, 1)
        end = datetime(2026, 3, 7)

        result = DateParser.generate_date_range(start, end)

        assert len(result) == 7
        assert result[0] == datetime(2026, 3, 1)
        assert result[6] == datetime(2026, 3, 7)

    def test_generate_date_range_crosses_month_boundary_succeeds(self):
        """Test generating range that crosses month boundary."""
        start = datetime(2026, 2, 28)
        end = datetime(2026, 3, 2)

        result = DateParser.generate_date_range(start, end)

        assert len(result) == 3
        assert result[0] == datetime(2026, 2, 28)
        assert result[1] == datetime(2026, 3, 1)
        assert result[2] == datetime(2026, 3, 2)

    def test_generate_date_range_crosses_year_boundary_succeeds(self):
        """Test generating range that crosses year boundary."""
        start = datetime(2025, 12, 30)
        end = datetime(2026, 1, 2)

        result = DateParser.generate_date_range(start, end)

        assert len(result) == 4
        assert result[0] == datetime(2025, 12, 30)
        assert result[1] == datetime(2025, 12, 31)
        assert result[2] == datetime(2026, 1, 1)
        assert result[3] == datetime(2026, 1, 2)

    def test_generate_date_range_includes_leap_day_succeeds(self):
        """Test generating range that includes Feb 29 in leap year."""
        start = datetime(2024, 2, 28)
        end = datetime(2024, 3, 1)

        result = DateParser.generate_date_range(start, end)

        assert len(result) == 3
        assert result[0] == datetime(2024, 2, 28)
        assert result[1] == datetime(2024, 2, 29)
        assert result[2] == datetime(2024, 3, 1)

    def test_generate_date_range_returns_list_of_datetime_objects(self):
        """Test that generated range returns list of datetime objects."""
        start = datetime(2026, 3, 1)
        end = datetime(2026, 3, 3)

        result = DateParser.generate_date_range(start, end)

        assert isinstance(result, list)
        assert all(isinstance(date, datetime) for date in result)

    def test_generate_date_range_end_before_start_raises_date_parse_error(self):
        """Test that end date before start date raises DateParseError."""
        start = datetime(2026, 3, 10)
        end = datetime(2026, 3, 5)

        with pytest.raises(DateParseError) as exc_info:
            DateParser.generate_date_range(start, end)

        error_message = str(exc_info.value)
        assert "End date" in error_message
        assert "cannot be before start date" in error_message
        assert "2026-03-05" in error_message
        assert "2026-03-10" in error_message

    def test_generate_date_range_end_one_day_before_start_raises_error(self):
        """Test that end date one day before start raises DateParseError."""
        start = datetime(2026, 3, 7)
        end = datetime(2026, 3, 6)

        with pytest.raises(DateParseError) as exc_info:
            DateParser.generate_date_range(start, end)

        assert "cannot be before start date" in str(exc_info.value)

    def test_generate_date_range_preserves_time_component(self):
        """Test that generated dates preserve time component from start date."""
        start = datetime(2026, 3, 1, 12, 30, 45)
        end = datetime(2026, 3, 3, 18, 45, 30)

        result = DateParser.generate_date_range(start, end)

        # Each date should have time component of 12:30:45 from start
        assert result[0] == datetime(2026, 3, 1, 12, 30, 45)
        assert result[1] == datetime(2026, 3, 2, 12, 30, 45)
        assert result[2] == datetime(2026, 3, 3, 12, 30, 45)

    def test_generate_date_range_30_days_succeeds(self):
        """Test generating range spanning 30 days."""
        start = datetime(2026, 3, 1)
        end = datetime(2026, 3, 30)

        result = DateParser.generate_date_range(start, end)

        assert len(result) == 30
        assert result[0] == datetime(2026, 3, 1)
        assert result[29] == datetime(2026, 3, 30)

    def test_generate_date_range_consecutive_dates_have_one_day_difference(self):
        """Test that consecutive dates in range differ by exactly one day."""
        start = datetime(2026, 3, 1)
        end = datetime(2026, 3, 5)

        result = DateParser.generate_date_range(start, end)

        for i in range(len(result) - 1):
            diff = result[i + 1] - result[i]
            assert diff.days == 1
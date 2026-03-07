"""Date parsing utilities for flexible date input handling.

This module provides utilities for parsing dates in various formats commonly used
in different regions and contexts. It supports ISO format, US format, European format,
and compact numeric format.

Typical usage example:

    from sdd_dry_days.utils.date_parser import DateParser

    date = DateParser.parse("2026-03-06")
    dates = DateParser.generate_date_range(start_date, end_date)
"""

from datetime import datetime, timedelta
from typing import List


class DateParseError(Exception):
    """Raised when date parsing fails."""
    pass


class DateParser:
    """Utility for parsing dates in various formats.

    This class provides methods for parsing date strings in multiple formats,
    validating leap years, and generating date ranges. All methods are classmethods
    and the class does not need to be instantiated.
    """

    # Supported date formats in order of preference
    FORMATS = [
        "%Y-%m-%d",          # ISO: 2026-03-06
        "%m/%d/%Y",          # US: 03/06/2026
        "%d-%m-%Y",          # EU: 06-03-2026
        "%d/%m/%Y",          # EU: 06/03/2026
        "%Y%m%d",            # Compact: 20260306
    ]

    @classmethod
    def parse(cls, date_str: str) -> datetime:
        """Parse a date string in various formats.

        Attempts to parse the provided date string using multiple common date formats.
        The string is stripped of leading/trailing whitespace before parsing.

        Args:
            date_str: Date string to parse

        Returns:
            datetime object representing the parsed date

        Raises:
            DateParseError: If date cannot be parsed in any supported format

        Examples:
            >>> DateParser.parse("2026-03-06")
            datetime.datetime(2026, 3, 6, 0, 0)
            >>> DateParser.parse("03/06/2026")
            datetime.datetime(2026, 3, 6, 0, 0)
        """
        date_str = date_str.strip()

        # Try each format
        for fmt in cls.FORMATS:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        # If all formats fail, raise error with examples
        raise DateParseError(
            f"Invalid date format: '{date_str}'. "
            f"Supported formats: YYYY-MM-DD, MM/DD/YYYY, DD-MM-YYYY, DD/MM/YYYY, YYYYMMDD"
        )

    @classmethod
    def validate_leap_year(cls, date: datetime) -> bool:
        """Validate February 29 in non-leap years.

        Checks if a date represents February 29 and validates that the year is actually
        a leap year. A leap year is divisible by 4, except for century years which must
        be divisible by 400.

        Args:
            date: datetime object to validate

        Returns:
            True if the date is valid (always returns True if validation passes)

        Raises:
            DateParseError: If the date is February 29 in a non-leap year

        Examples:
            >>> DateParser.validate_leap_year(datetime(2024, 2, 29))  # Leap year
            True
            >>> DateParser.validate_leap_year(datetime(2023, 2, 29))  # Not a leap year
            DateParseError: February 29 does not exist in 2023 (not a leap year)
        """
        if date.month == 2 and date.day == 29:
            year = date.year
            is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
            if not is_leap:
                raise DateParseError(
                    f"February 29 does not exist in {year} (not a leap year)"
                )
        return True

    @classmethod
    def generate_date_range(cls, start: datetime, end: datetime) -> List[datetime]:
        """Generate list of dates between start and end (inclusive).

        Creates a list of consecutive dates starting from the start date through
        the end date, including both endpoints.

        Args:
            start: Start date (inclusive)
            end: End date (inclusive)

        Returns:
            List of datetime objects representing each day in the range

        Raises:
            DateParseError: If end date is before start date

        Examples:
            >>> start = datetime(2026, 3, 1)
            >>> end = datetime(2026, 3, 3)
            >>> dates = DateParser.generate_date_range(start, end)
            >>> len(dates)
            3
        """
        if end < start:
            raise DateParseError(
                f"End date ({end.strftime('%Y-%m-%d')}) "
                f"cannot be before start date ({start.strftime('%Y-%m-%d')})"
            )

        dates = []
        current = start

        while current <= end:
            dates.append(current)
            current += timedelta(days=1)

        return dates
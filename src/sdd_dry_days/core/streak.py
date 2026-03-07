"""Streak calculation for consecutive dry days.

This module provides functionality to calculate streaks (consecutive sequences)
of dry days, which is essential for user motivation and progress tracking. The
streak calculator focuses on the "current streak" - consecutive dry days that
include today.

The streak calculation is designed to be:
- Fast (< 200ms even with years of data)
- Accurate (handles gaps, unsorted data, edge cases)
- Motivating (focuses on current active progress)
"""

from datetime import datetime, timedelta
from typing import List

from .dry_day import DryDay


class StreakCalculator:
    """Calculate streaks of consecutive dry days.

    This class provides static methods for analyzing sequences of dry days to
    determine current streaks. A streak is defined as a consecutive sequence of
    dry days with no gaps (missing days).

    The primary use case is displaying the current streak when a user adds a new
    dry day, providing immediate positive feedback and motivation to continue.

    Example:
        >>> from datetime import datetime
        >>> from sdd_dry_days.core.dry_day import DryDay
        >>>
        >>> # Create some dry days
        >>> days = [
        ...     DryDay(date=datetime(2026, 3, 5)),
        ...     DryDay(date=datetime(2026, 3, 6)),
        ...     DryDay(date=datetime(2026, 3, 7)),
        ... ]
        >>> # Calculate current streak (assuming today is 2026-03-07)
        >>> streak = StreakCalculator.calculate_current_streak(days)
        >>> print(f"Current streak: {streak} days")
        Current streak: 3 days
    """

    @staticmethod
    def calculate_current_streak(dry_days: List[DryDay]) -> int:
        """Calculate current streak of consecutive dry days ending today.

        Counts the number of consecutive dry days in a sequence that includes
        today's date. If today is not a dry day, or if there are no dry days at
        all, the streak is 0. Any gap in the sequence breaks the streak.

        The algorithm works by:
        1. Sorting dry days by date (descending, most recent first)
        2. Checking if today is included in the list
        3. Counting backward from today until a gap is found

        Args:
            dry_days: List of DryDay objects. The list does not need to be sorted;
                     sorting is handled internally. Can be empty.

        Returns:
            The count of consecutive dry days ending with today. Returns 0 if:
            - The list is empty
            - Today is not in the list of dry days
            - There is a gap in the sequence before today

        Example:
            >>> # Consecutive days including today (2026-03-07)
            >>> days = [
            ...     DryDay(date=datetime(2026, 3, 5)),
            ...     DryDay(date=datetime(2026, 3, 6)),
            ...     DryDay(date=datetime(2026, 3, 7)),
            ... ]
            >>> StreakCalculator.calculate_current_streak(days)
            3

            >>> # Today not included
            >>> days = [
            ...     DryDay(date=datetime(2026, 3, 5)),
            ...     DryDay(date=datetime(2026, 3, 6)),
            ... ]
            >>> StreakCalculator.calculate_current_streak(days)
            0

            >>> # Gap in sequence
            >>> days = [
            ...     DryDay(date=datetime(2026, 3, 5)),
            ...     # Gap on 2026-03-06
            ...     DryDay(date=datetime(2026, 3, 7)),
            ... ]
            >>> StreakCalculator.calculate_current_streak(days)
            1
        """
        # Handle empty list case
        if not dry_days:
            return 0

        # Sort by date descending (most recent first)
        sorted_days = sorted(dry_days, key=lambda d: d.date, reverse=True)

        # Normalize today to midnight for comparison
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # Check if today is a dry day (most recent entry must be today)
        if sorted_days[0].date.date() != today.date():
            return 0

        # Start counting streak from today
        streak = 1
        expected_date = today - timedelta(days=1)

        # Count backward through consecutive days
        for dry_day in sorted_days[1:]:
            if dry_day.date.date() == expected_date.date():
                streak += 1
                expected_date -= timedelta(days=1)
            else:
                # Gap found, stop counting
                break

        return streak
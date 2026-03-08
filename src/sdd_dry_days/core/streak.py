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

    @staticmethod
    def calculate_longest_streak_in_period(
        dry_days: List[DryDay],
        start_date: datetime,
        end_date: datetime
    ) -> int:
        """Calculate longest consecutive dry day streak within a time period.

        Unlike calculate_current_streak() which only counts streaks ending today,
        this method finds the longest consecutive sequence of dry days anywhere
        within the specified period. This is useful for historical analysis and
        period-based statistics (e.g., "best streak in the last 30 days").

        The algorithm:
        1. Filters dry days to the specified period
        2. Sorts by date ascending
        3. Iterates through consecutive day pairs
        4. Tracks current streak and maximum streak encountered
        5. Returns the longest streak found

        Args:
            dry_days: List of DryDay objects. The list does not need to be sorted
                     or filtered; this is handled internally. Can be empty.
            start_date: Period start date (inclusive). Time component is ignored;
                       dates are compared at day granularity.
            end_date: Period end date (inclusive). Time component is ignored;
                     dates are compared at day granularity.

        Returns:
            The count of the longest consecutive dry day sequence in the period.
            Returns 0 if:
            - The list is empty
            - No dry days fall within the period
            - All dry days in the period are non-consecutive (max would be 1)

        Example:
            >>> # Multiple streaks in period
            >>> days = [
            ...     DryDay(date=datetime(2026, 2, 1)),
            ...     DryDay(date=datetime(2026, 2, 2)),  # Streak of 2
            ...     DryDay(date=datetime(2026, 2, 5)),
            ...     DryDay(date=datetime(2026, 2, 6)),
            ...     DryDay(date=datetime(2026, 2, 7)),  # Streak of 3 (longest)
            ...     DryDay(date=datetime(2026, 2, 10)),
            ... ]
            >>> start = datetime(2026, 2, 1)
            >>> end = datetime(2026, 2, 28)
            >>> StreakCalculator.calculate_longest_streak_in_period(days, start, end)
            3

            >>> # Single day (streak of 1)
            >>> days = [DryDay(date=datetime(2026, 2, 5))]
            >>> StreakCalculator.calculate_longest_streak_in_period(days, start, end)
            1

            >>> # No days in period
            >>> days = []
            >>> StreakCalculator.calculate_longest_streak_in_period(days, start, end)
            0

            >>> # All consecutive (one long streak)
            >>> days = [
            ...     DryDay(date=datetime(2026, 2, 5)),
            ...     DryDay(date=datetime(2026, 2, 6)),
            ...     DryDay(date=datetime(2026, 2, 7)),
            ...     DryDay(date=datetime(2026, 2, 8)),
            ... ]
            >>> StreakCalculator.calculate_longest_streak_in_period(days, start, end)
            4
        """
        # Handle empty list case
        if not dry_days:
            return 0

        # Normalize period boundaries to midnight for comparison
        start_normalized = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_normalized = end_date.replace(hour=0, minute=0, second=0, microsecond=0)

        # Filter dry days to the specified period
        filtered_days = [
            day for day in dry_days
            if start_normalized.date() <= day.date.date() <= end_normalized.date()
        ]

        # Handle case where no days fall in the period
        if not filtered_days:
            return 0

        # Handle single day case
        if len(filtered_days) == 1:
            return 1

        # Sort by date ascending (earliest first)
        sorted_days = sorted(filtered_days, key=lambda d: d.date)

        # Initialize streak tracking
        current_streak = 1  # Start with first day
        max_streak = 1

        # Iterate through sorted days to find longest consecutive sequence
        for i in range(1, len(sorted_days)):
            previous_date = sorted_days[i - 1].date.date()
            current_date = sorted_days[i].date.date()

            # Check if dates are consecutive (difference of exactly 1 day)
            if (current_date - previous_date).days == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                # Gap found, reset current streak
                current_streak = 1

        return max_streak
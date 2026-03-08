"""Statistics models for tracking dry day performance over time periods.

This module provides data structures for calculating and representing statistics
about dry days over specific time periods (e.g., 30, 60, 90 days). The models
support percentage calculations, streak tracking, and limited data indicators.

The PeriodStats dataclass is storage-agnostic and can be used by any component
that needs to represent aggregated dry day statistics over a defined period.
"""

import calendar
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from .dry_day import DryDay
from .streak import StreakCalculator


@dataclass
class PeriodStats:
    """Statistics for dry days over a specific time period.

    This dataclass encapsulates all statistical information about dry days
    within a defined time period. It includes basic counts, percentages,
    streak information, and metadata about data availability.

    The available_days and requested_days fields enable detection of periods
    with limited data, which should be indicated to users (e.g., when tracking
    started mid-period, showing "limited data: X/Y days").

    Attributes:
        start_date: Start of the period (inclusive).
        end_date: End of the period (inclusive).
        total_days: Total number of days in the period.
        dry_days_count: Number of days marked as dry in the period.
        percentage: Percentage of dry days (dry_days_count / total_days × 100).
        longest_streak: Longest consecutive streak of dry days in the period.
        dry_day_dates: List of actual dry day dates in the period (for display).
        available_days: Number of days with recorded data in the period.
        requested_days: Number of days requested for the period (30, 60, or 90).

    Example:
        >>> period = PeriodStats(
        ...     start_date=datetime(2026, 2, 5),
        ...     end_date=datetime(2026, 3, 7),
        ...     total_days=30,
        ...     dry_days_count=25,
        ...     percentage=83.33,
        ...     longest_streak=10,
        ...     dry_day_dates=[datetime(2026, 2, 5), datetime(2026, 2, 6), ...],
        ...     available_days=30,
        ...     requested_days=30
        ... )
    """

    start_date: datetime  # Start of period (inclusive)
    end_date: datetime  # End of period (inclusive)
    total_days: int  # Total days in period
    dry_days_count: int  # Number of dry days
    percentage: float  # (dry_days_count / total_days) × 100
    longest_streak: int  # Longest consecutive streak in period
    dry_day_dates: List[datetime]  # Actual dry day dates (for display)
    available_days: int  # Actual days with recorded data
    requested_days: int  # Requested days for the period (30, 60, or 90)


class StatisticsCalculator:
    """Calculate statistics for dry days over various time periods.

    This class provides static methods for calculating statistics about dry days
    across different time periods such as weeks (Monday-Sunday), calendar months,
    and custom day ranges (30, 60, 90 days). It supports period date calculations,
    dry day counting, percentage calculations, and streak analysis within periods.

    The calculator is designed to be stateless, following the same pattern as
    StreakCalculator. All methods are static and operate on provided dry day data
    without maintaining any internal state.

    Key capabilities:
    - Calculate week boundaries (Monday-Sunday) for any reference date
    - Calculate month boundaries (1st to last day) for any reference date
    - Calculate statistics for any time period (dry days, percentages, streaks)
    - Support custom date ranges for flexible reporting

    Example:
        >>> from datetime import datetime
        >>> from sdd_dry_days.core.dry_day import DryDay
        >>>
        >>> # Get current week date range
        >>> ref_date = datetime(2026, 3, 7)  # Saturday
        >>> start, end = StatisticsCalculator.get_week_dates(ref_date)
        >>> print(f"Week: {start.date()} to {end.date()}")
        Week: 2026-03-02 to 2026-03-08  # Monday to Sunday
        >>>
        >>> # Get current month date range
        >>> start, end = StatisticsCalculator.get_month_dates(ref_date)
        >>> print(f"Month: {start.date()} to {end.date()}")
        Month: 2026-03-01 to 2026-03-31  # First to last day
    """

    @staticmethod
    def get_week_dates(ref_date: datetime) -> Tuple[datetime, datetime]:
        """Calculate Monday-Sunday date range for the week containing ref_date.

        Determines the start (Monday) and end (Sunday) of the calendar week that
        contains the reference date. This follows the ISO week definition where
        weeks start on Monday and end on Sunday.

        Args:
            ref_date: Reference date within the week. The date is normalized to
                     midnight before calculation.

        Returns:
            Tuple of (start_date, end_date) where:
            - start_date: Monday at 00:00:00
            - end_date: Sunday at 23:59:59

        Example:
            >>> # Reference date is Saturday, March 7, 2026
            >>> ref = datetime(2026, 3, 7, 14, 30)  # Time doesn't matter
            >>> start, end = StatisticsCalculator.get_week_dates(ref)
            >>> print(start.date(), start.weekday())  # 0 = Monday
            2026-03-02 0
            >>> print(end.date(), end.weekday())  # 6 = Sunday
            2026-03-08 6
        """
        # Normalize ref_date to midnight
        ref_normalized = ref_date.replace(hour=0, minute=0, second=0, microsecond=0)

        # Get weekday (0 = Monday, 6 = Sunday)
        weekday = ref_normalized.weekday()

        # Calculate Monday (start of week)
        days_since_monday = weekday  # If Monday, 0 days back; if Sunday, 6 days back
        start_date = ref_normalized - timedelta(days=days_since_monday)

        # Calculate Sunday (end of week)
        days_until_sunday = 6 - weekday  # If Monday, 6 days forward; if Sunday, 0 days forward
        end_date = ref_normalized + timedelta(days=days_until_sunday)

        return (start_date, end_date)

    @staticmethod
    def get_month_dates(ref_date: datetime) -> Tuple[datetime, datetime]:
        """Calculate first-to-last day date range for the month containing ref_date.

        Determines the start (1st day) and end (last day) of the calendar month
        that contains the reference date. Handles varying month lengths correctly,
        including leap years.

        Args:
            ref_date: Reference date within the month. The date is normalized to
                     midnight before calculation.

        Returns:
            Tuple of (start_date, end_date) where:
            - start_date: First day of month at 00:00:00
            - end_date: Last day of month at 23:59:59

        Example:
            >>> # Reference date is March 7, 2026
            >>> ref = datetime(2026, 3, 7, 14, 30)  # Time doesn't matter
            >>> start, end = StatisticsCalculator.get_month_dates(ref)
            >>> print(start.date())
            2026-03-01
            >>> print(end.date())
            2026-03-31
            >>>
            >>> # February in non-leap year
            >>> ref = datetime(2026, 2, 15)
            >>> start, end = StatisticsCalculator.get_month_dates(ref)
            >>> print(end.date())
            2026-02-28
        """
        # Calculate first day of month
        start_date = ref_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Get the last day of the month using calendar.monthrange
        # monthrange returns (weekday of first day, number of days in month)
        _, last_day_num = calendar.monthrange(ref_date.year, ref_date.month)

        # Calculate last day of month
        end_date = ref_date.replace(day=last_day_num, hour=0, minute=0, second=0, microsecond=0)

        return (start_date, end_date)

    @staticmethod
    def calculate_period_stats(
        dry_days: List[DryDay],
        start_date: datetime,
        end_date: datetime,
        all_recorded_days: Optional[List[DryDay]] = None
    ) -> PeriodStats:
        """Calculate statistics for a time period.

        This method computes comprehensive statistics for dry days within a specified
        time period. It filters dry days to the period, calculates counts and percentages,
        and determines the longest streak. It also supports limited data indicators when
        tracking started mid-period.

        Args:
            dry_days: All dry days (will be filtered to the period). Each DryDay should
                     have a normalized date (midnight).
            start_date: Period start date (inclusive). Will be normalized to midnight.
            end_date: Period end date (inclusive). Will be normalized to midnight.
            all_recorded_days: Optional list of all recorded days (both dry and non-dry)
                             for limited data indicator (AC-4.7). If provided, enables
                             detection of periods with incomplete data.

        Returns:
            PeriodStats instance with all metrics:
            - start_date, end_date: Period boundaries (normalized)
            - total_days: Days in the period (always equals requested_days)
            - dry_days_count: Number of dry days in the period
            - percentage: (dry_days_count / total_days) × 100
            - longest_streak: Longest consecutive dry day streak in the period
            - dry_day_dates: List of dry day dates in the period
            - available_days: Days with recorded data (for limited data indicator)
            - requested_days: Days in the period (same as total_days)

        Example:
            >>> from datetime import datetime
            >>> from sdd_dry_days.core.dry_day import DryDay
            >>>
            >>> # Create dry days
            >>> dry_days = [
            ...     DryDay(date=datetime(2026, 2, 5)),
            ...     DryDay(date=datetime(2026, 2, 6)),
            ...     DryDay(date=datetime(2026, 2, 7)),
            ...     DryDay(date=datetime(2026, 3, 1)),
            ... ]
            >>>
            >>> # Calculate 30-day period stats (Feb 6 - Mar 7)
            >>> start = datetime(2026, 2, 6)
            >>> end = datetime(2026, 3, 7)
            >>> stats = StatisticsCalculator.calculate_period_stats(
            ...     dry_days=dry_days,
            ...     start_date=start,
            ...     end_date=end,
            ...     all_recorded_days=dry_days  # Started tracking Feb 5
            ... )
            >>> print(f"Dry days: {stats.dry_days_count}/{stats.total_days}")
            Dry days: 3/30
            >>> print(f"Percentage: {stats.percentage:.1f}%")
            Percentage: 10.0%
            >>> print(f"Data availability: {stats.available_days}/{stats.requested_days}")
            Data availability: 30/30  # All days covered (earliest record Feb 5)
        """
        # Normalize dates to midnight
        start_normalized = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_normalized = end_date.replace(hour=0, minute=0, second=0, microsecond=0)

        # 1. Filter dry days to period (using list comprehension)
        filtered_days = [
            day for day in dry_days
            if start_normalized.date() <= day.date.date() <= end_normalized.date()
        ]

        # 2. Calculate requested days in period (inclusive of both start and end)
        requested_days = (end_normalized - start_normalized).days + 1

        # 3. Calculate available days (for AC-4.7 limited data indicator)
        if all_recorded_days and len(all_recorded_days) > 0:
            # Find earliest recorded date
            earliest_record = min(day.date for day in all_recorded_days)
            earliest_normalized = earliest_record.replace(hour=0, minute=0, second=0, microsecond=0)

            # Calculate available days: from earliest record to end date (but not before start date)
            effective_start = max(start_normalized, earliest_normalized)
            available_days = (end_normalized - effective_start).days + 1

            # Clamp to requested_days (can't have more available than requested)
            available_days = min(available_days, requested_days)
        else:
            # No recorded days provided, assume all requested days are available
            available_days = requested_days

        # 4. Count dry days
        dry_days_count = len(filtered_days)

        # 5. Calculate percentage (handle edge case: 0 requested_days)
        if requested_days > 0:
            percentage = (dry_days_count / requested_days) * 100
        else:
            percentage = 0.0

        # 6. Calculate longest streak in period (stub for now, Task 5 will implement)
        longest_streak = StatisticsCalculator.calculate_longest_streak_in_period(
            dry_days=dry_days,
            start_date=start_normalized,
            end_date=end_normalized
        )

        # 7. Extract dry day dates
        dry_day_dates = [day.date for day in filtered_days]

        # Return PeriodStats instance
        return PeriodStats(
            start_date=start_normalized,
            end_date=end_normalized,
            total_days=requested_days,
            dry_days_count=dry_days_count,
            percentage=percentage,
            longest_streak=longest_streak,
            dry_day_dates=dry_day_dates,
            available_days=available_days,
            requested_days=requested_days
        )

    @staticmethod
    def calculate_longest_streak_in_period(
        dry_days: List[DryDay],
        start_date: datetime,
        end_date: datetime
    ) -> int:
        """Calculate longest consecutive dry day streak within a time period.

        This method delegates to StreakCalculator.calculate_longest_streak_in_period()
        to maintain separation of concerns. The StreakCalculator handles all streak
        logic, while StatisticsCalculator focuses on period-based aggregations.

        Args:
            dry_days: All dry days (will be filtered to the period).
            start_date: Period start date (inclusive).
            end_date: Period end date (inclusive).

        Returns:
            int: Longest consecutive dry day streak in the period.
        """
        # Delegate to StreakCalculator for streak logic
        return StreakCalculator.calculate_longest_streak_in_period(
            dry_days=dry_days,
            start_date=start_date,
            end_date=end_date
        )
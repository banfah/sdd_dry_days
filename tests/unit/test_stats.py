"""Unit tests for PeriodStats and StatisticsCalculator.

This module tests the statistics calculation functionality including:
- PeriodStats dataclass instantiation and field handling
- get_week_dates(): Monday-Sunday week boundary calculation
- get_month_dates(): First-to-last day month boundary calculation
- Date normalization to midnight
- Edge cases: year boundaries, leap years, different month lengths

The tests ensure accurate date calculations for weekly and monthly views,
supporting user statistics and progress tracking features.
"""

from datetime import datetime
import pytest

from sdd_dry_days.core.stats import PeriodStats, StatisticsCalculator


class TestPeriodStatsInstantiation:
    """Tests for PeriodStats dataclass instantiation and fields."""

    def test_period_stats_instantiation_with_all_fields_succeeds(self):
        """Test that PeriodStats can be instantiated with all 9 required fields."""
        start = datetime(2026, 2, 5)
        end = datetime(2026, 3, 7)
        dry_dates = [datetime(2026, 2, 5), datetime(2026, 2, 6), datetime(2026, 3, 1)]

        period = PeriodStats(
            start_date=start,
            end_date=end,
            total_days=30,
            dry_days_count=25,
            percentage=83.33,
            longest_streak=10,
            dry_day_dates=dry_dates,
            available_days=30,
            requested_days=30
        )

        # Verify all fields are set correctly
        assert period.start_date == start
        assert period.end_date == end
        assert period.total_days == 30
        assert period.dry_days_count == 25
        assert period.percentage == 83.33
        assert period.longest_streak == 10
        assert period.dry_day_dates == dry_dates
        assert period.available_days == 30
        assert period.requested_days == 30

    def test_period_stats_field_types_are_correct(self):
        """Test that PeriodStats fields have the correct types."""
        start = datetime(2026, 3, 1)
        end = datetime(2026, 3, 31)
        dry_dates = [datetime(2026, 3, 1), datetime(2026, 3, 2)]

        period = PeriodStats(
            start_date=start,
            end_date=end,
            total_days=31,
            dry_days_count=20,
            percentage=64.52,
            longest_streak=5,
            dry_day_dates=dry_dates,
            available_days=31,
            requested_days=31
        )

        # Verify field types
        assert isinstance(period.start_date, datetime)
        assert isinstance(period.end_date, datetime)
        assert isinstance(period.total_days, int)
        assert isinstance(period.dry_days_count, int)
        assert isinstance(period.percentage, float)
        assert isinstance(period.longest_streak, int)
        assert isinstance(period.dry_day_dates, list)
        assert isinstance(period.available_days, int)
        assert isinstance(period.requested_days, int)


class TestGetWeekDates:
    """Tests for StatisticsCalculator.get_week_dates() method."""

    def test_get_week_dates_with_monday_reference_returns_same_week(self):
        """Test that a Monday reference returns the same Monday-Sunday week."""
        # Monday, March 2, 2026
        ref_date = datetime(2026, 3, 2)

        start, end = StatisticsCalculator.get_week_dates(ref_date)

        # Verify start is Monday, March 2
        assert start.date() == datetime(2026, 3, 2).date()
        assert start.weekday() == 0  # 0 = Monday
        assert start.hour == 0
        assert start.minute == 0
        assert start.second == 0
        assert start.microsecond == 0

        # Verify end is Sunday, March 8
        assert end.date() == datetime(2026, 3, 8).date()
        assert end.weekday() == 6  # 6 = Sunday
        assert end.hour == 0
        assert end.minute == 0
        assert end.second == 0
        assert end.microsecond == 0

    def test_get_week_dates_with_wednesday_reference_returns_correct_week(self):
        """Test that a Wednesday reference returns correct Monday-Sunday week."""
        # Wednesday, March 4, 2026
        ref_date = datetime(2026, 3, 4, 14, 30, 45)

        start, end = StatisticsCalculator.get_week_dates(ref_date)

        # Verify start is Monday, March 2
        assert start.date() == datetime(2026, 3, 2).date()
        assert start.weekday() == 0  # 0 = Monday
        assert start.hour == 0
        assert start.minute == 0
        assert start.second == 0

        # Verify end is Sunday, March 8
        assert end.date() == datetime(2026, 3, 8).date()
        assert end.weekday() == 6  # 6 = Sunday
        assert end.hour == 0
        assert end.minute == 0
        assert end.second == 0

    def test_get_week_dates_with_saturday_reference_returns_correct_week(self):
        """Test that a Saturday reference returns correct Monday-Sunday week."""
        # Saturday, March 7, 2026 (today)
        ref_date = datetime(2026, 3, 7, 23, 59, 59)

        start, end = StatisticsCalculator.get_week_dates(ref_date)

        # Verify start is Monday, March 2
        assert start.date() == datetime(2026, 3, 2).date()
        assert start.weekday() == 0  # 0 = Monday
        assert start.hour == 0
        assert start.minute == 0
        assert start.second == 0

        # Verify end is Sunday, March 8
        assert end.date() == datetime(2026, 3, 8).date()
        assert end.weekday() == 6  # 6 = Sunday
        assert end.hour == 0
        assert end.minute == 0
        assert end.second == 0

    def test_get_week_dates_with_sunday_reference_returns_correct_week(self):
        """Test that a Sunday reference returns correct Monday-Sunday week (ending that Sunday)."""
        # Sunday, March 8, 2026
        ref_date = datetime(2026, 3, 8, 10, 0, 0)

        start, end = StatisticsCalculator.get_week_dates(ref_date)

        # Verify start is Monday, March 2
        assert start.date() == datetime(2026, 3, 2).date()
        assert start.weekday() == 0  # 0 = Monday

        # Verify end is Sunday, March 8 (same day as reference)
        assert end.date() == datetime(2026, 3, 8).date()
        assert end.weekday() == 6  # 6 = Sunday

    def test_get_week_dates_year_boundary_week_spans_correctly(self):
        """Test that a week spanning year boundary (Dec 31 / Jan 1) calculates correctly."""
        # Tuesday, December 30, 2025 (week spans into 2026)
        ref_date = datetime(2025, 12, 30)

        start, end = StatisticsCalculator.get_week_dates(ref_date)

        # Verify start is Monday, December 29, 2025
        assert start.date() == datetime(2025, 12, 29).date()
        assert start.weekday() == 0  # 0 = Monday
        assert start.year == 2025
        assert start.hour == 0
        assert start.minute == 0
        assert start.second == 0

        # Verify end is Sunday, January 4, 2026
        assert end.date() == datetime(2026, 1, 4).date()
        assert end.weekday() == 6  # 6 = Sunday
        assert end.year == 2026
        assert end.hour == 0
        assert end.minute == 0
        assert end.second == 0

    def test_get_week_dates_normalizes_time_to_midnight(self):
        """Test that get_week_dates normalizes reference date time to midnight."""
        # Thursday with afternoon time
        ref_date = datetime(2026, 3, 5, 15, 45, 30, 123456)

        start, end = StatisticsCalculator.get_week_dates(ref_date)

        # Verify both dates are normalized to midnight
        assert start.hour == 0
        assert start.minute == 0
        assert start.second == 0
        assert start.microsecond == 0

        assert end.hour == 0
        assert end.minute == 0
        assert end.second == 0
        assert end.microsecond == 0


class TestGetMonthDates:
    """Tests for StatisticsCalculator.get_month_dates() method."""

    def test_get_month_dates_with_march_reference_returns_correct_month(self):
        """Test that March reference returns March 1-31 (31 days)."""
        # March 7, 2026
        ref_date = datetime(2026, 3, 7, 14, 30, 0)

        start, end = StatisticsCalculator.get_month_dates(ref_date)

        # Verify start is March 1
        assert start.date() == datetime(2026, 3, 1).date()
        assert start.day == 1
        assert start.month == 3
        assert start.year == 2026
        assert start.hour == 0
        assert start.minute == 0
        assert start.second == 0
        assert start.microsecond == 0

        # Verify end is March 31
        assert end.date() == datetime(2026, 3, 31).date()
        assert end.day == 31
        assert end.month == 3
        assert end.year == 2026
        assert end.hour == 0
        assert end.minute == 0
        assert end.second == 0
        assert end.microsecond == 0

    def test_get_month_dates_with_april_reference_returns_30_days(self):
        """Test that April reference returns April 1-30 (30 days)."""
        # April 15, 2026
        ref_date = datetime(2026, 4, 15)

        start, end = StatisticsCalculator.get_month_dates(ref_date)

        # Verify start is April 1
        assert start.date() == datetime(2026, 4, 1).date()
        assert start.day == 1
        assert start.month == 4

        # Verify end is April 30 (not 31)
        assert end.date() == datetime(2026, 4, 30).date()
        assert end.day == 30
        assert end.month == 4

    def test_get_month_dates_with_february_non_leap_year_returns_28_days(self):
        """Test that February in non-leap year (2025) returns Feb 1-28 (28 days)."""
        # February 15, 2025 (non-leap year)
        ref_date = datetime(2025, 2, 15)

        start, end = StatisticsCalculator.get_month_dates(ref_date)

        # Verify start is February 1
        assert start.date() == datetime(2025, 2, 1).date()
        assert start.day == 1
        assert start.month == 2
        assert start.year == 2025

        # Verify end is February 28 (not 29)
        assert end.date() == datetime(2025, 2, 28).date()
        assert end.day == 28
        assert end.month == 2
        assert end.year == 2025

    def test_get_month_dates_with_february_leap_year_returns_29_days(self):
        """Test that February in leap year (2024) returns Feb 1-29 (29 days)."""
        # February 15, 2024 (leap year)
        ref_date = datetime(2024, 2, 15)

        start, end = StatisticsCalculator.get_month_dates(ref_date)

        # Verify start is February 1
        assert start.date() == datetime(2024, 2, 1).date()
        assert start.day == 1
        assert start.month == 2
        assert start.year == 2024

        # Verify end is February 29 (leap year)
        assert end.date() == datetime(2024, 2, 29).date()
        assert end.day == 29
        assert end.month == 2
        assert end.year == 2024

    def test_get_month_dates_with_january_reference_returns_correct_month(self):
        """Test that January reference returns Jan 1-31 (year boundary test)."""
        # January 10, 2026
        ref_date = datetime(2026, 1, 10)

        start, end = StatisticsCalculator.get_month_dates(ref_date)

        # Verify start is January 1
        assert start.date() == datetime(2026, 1, 1).date()
        assert start.day == 1
        assert start.month == 1
        assert start.year == 2026

        # Verify end is January 31
        assert end.date() == datetime(2026, 1, 31).date()
        assert end.day == 31
        assert end.month == 1
        assert end.year == 2026

    def test_get_month_dates_with_december_reference_returns_correct_month(self):
        """Test that December reference returns Dec 1-31 (year boundary test)."""
        # December 25, 2025
        ref_date = datetime(2025, 12, 25)

        start, end = StatisticsCalculator.get_month_dates(ref_date)

        # Verify start is December 1
        assert start.date() == datetime(2025, 12, 1).date()
        assert start.day == 1
        assert start.month == 12
        assert start.year == 2025

        # Verify end is December 31
        assert end.date() == datetime(2025, 12, 31).date()
        assert end.day == 31
        assert end.month == 12
        assert end.year == 2025

    def test_get_month_dates_normalizes_time_to_midnight(self):
        """Test that get_month_dates normalizes reference date time to midnight."""
        # March 15 with afternoon time
        ref_date = datetime(2026, 3, 15, 18, 45, 30, 999999)

        start, end = StatisticsCalculator.get_month_dates(ref_date)

        # Verify both dates are normalized to midnight
        assert start.hour == 0
        assert start.minute == 0
        assert start.second == 0
        assert start.microsecond == 0

        assert end.hour == 0
        assert end.minute == 0
        assert end.second == 0
        assert end.microsecond == 0

    def test_get_month_dates_with_first_day_reference_returns_full_month(self):
        """Test that reference on first day of month returns full month."""
        # March 1, 2026
        ref_date = datetime(2026, 3, 1)

        start, end = StatisticsCalculator.get_month_dates(ref_date)

        # Verify full month range
        assert start.date() == datetime(2026, 3, 1).date()
        assert end.date() == datetime(2026, 3, 31).date()

    def test_get_month_dates_with_last_day_reference_returns_full_month(self):
        """Test that reference on last day of month returns full month."""
        # March 31, 2026
        ref_date = datetime(2026, 3, 31)

        start, end = StatisticsCalculator.get_month_dates(ref_date)

        # Verify full month range
        assert start.date() == datetime(2026, 3, 1).date()
        assert end.date() == datetime(2026, 3, 31).date()


class TestCalculatePeriodStats:
    """Tests for StatisticsCalculator.calculate_period_stats() method."""

    def test_calculate_period_stats_with_empty_list_returns_zero_metrics(self):
        """Test that empty dry_days list returns 0 count, 0%, 0 streak."""
        # Empty list
        dry_days = []
        start = datetime(2026, 2, 6)
        end = datetime(2026, 3, 7)  # 30 days

        stats = StatisticsCalculator.calculate_period_stats(
            dry_days=dry_days,
            start_date=start,
            end_date=end
        )

        # Verify zero metrics
        assert stats.dry_days_count == 0
        assert stats.percentage == 0.0
        assert stats.longest_streak == 0
        assert stats.dry_day_dates == []
        assert stats.total_days == 30
        assert stats.requested_days == 30
        assert stats.available_days == 30

    def test_calculate_period_stats_with_single_dry_day_returns_correct_percentage(self):
        """Test that single dry day in period returns 1 count and correct percentage."""
        # Single dry day: March 5, 2026
        from sdd_dry_days.core.dry_day import DryDay
        dry_days = [DryDay(date=datetime(2026, 3, 5))]
        start = datetime(2026, 2, 6)
        end = datetime(2026, 3, 7)  # 30 days

        stats = StatisticsCalculator.calculate_period_stats(
            dry_days=dry_days,
            start_date=start,
            end_date=end
        )

        # Verify metrics for single dry day
        assert stats.dry_days_count == 1
        assert stats.percentage == pytest.approx(3.33, rel=0.01)  # 1/30 * 100 = 3.33%
        assert stats.longest_streak == 1
        assert len(stats.dry_day_dates) == 1
        assert stats.dry_day_dates[0].date() == datetime(2026, 3, 5).date()
        assert stats.total_days == 30
        assert stats.requested_days == 30

    def test_calculate_period_stats_with_multiple_dry_days_returns_correct_metrics(self, sample_dry_days_list):
        """Test that multiple dry days in period return correct count, percentage, and dates."""
        # sample_dry_days_list has 5 dry days:
        # 2026-03-01, 2026-03-02, 2026-03-04, 2026-03-07, 2026-03-10
        start = datetime(2026, 3, 1)
        end = datetime(2026, 3, 10)  # 10 days

        stats = StatisticsCalculator.calculate_period_stats(
            dry_days=sample_dry_days_list,
            start_date=start,
            end_date=end
        )

        # Verify metrics for multiple dry days
        assert stats.dry_days_count == 5
        assert stats.percentage == 50.0  # 5/10 * 100 = 50%
        assert stats.total_days == 10
        assert stats.requested_days == 10
        assert len(stats.dry_day_dates) == 5

        # Verify dates are correct
        expected_dates = [
            datetime(2026, 3, 1),
            datetime(2026, 3, 2),
            datetime(2026, 3, 4),
            datetime(2026, 3, 7),
            datetime(2026, 3, 10)
        ]
        for i, expected in enumerate(expected_dates):
            assert stats.dry_day_dates[i].date() == expected.date()

    def test_calculate_period_stats_filters_out_days_outside_period(self, sample_dry_days_list):
        """Test that dry days outside the period are filtered out correctly."""
        # sample_dry_days_list has dates: 03-01, 03-02, 03-04, 03-07, 03-10
        # Set period to only include March 3-6 (should only include 03-04)
        start = datetime(2026, 3, 3)
        end = datetime(2026, 3, 6)  # 4 days

        stats = StatisticsCalculator.calculate_period_stats(
            dry_days=sample_dry_days_list,
            start_date=start,
            end_date=end
        )

        # Only March 4 should be included
        assert stats.dry_days_count == 1
        assert stats.percentage == 25.0  # 1/4 * 100 = 25%
        assert stats.total_days == 4
        assert len(stats.dry_day_dates) == 1
        assert stats.dry_day_dates[0].date() == datetime(2026, 3, 4).date()

    def test_calculate_period_stats_with_consecutive_days_calculates_longest_streak(self, sample_consecutive_dry_days):
        """Test that consecutive dry days result in correct longest streak calculation."""
        # sample_consecutive_dry_days has 7 consecutive days: March 1-7
        start = datetime(2026, 3, 1)
        end = datetime(2026, 3, 7)  # 7 days

        stats = StatisticsCalculator.calculate_period_stats(
            dry_days=sample_consecutive_dry_days,
            start_date=start,
            end_date=end
        )

        # Verify streak for consecutive days
        assert stats.dry_days_count == 7
        assert stats.percentage == 100.0  # 7/7 * 100 = 100%
        assert stats.longest_streak == 7  # All consecutive
        assert stats.total_days == 7
        assert len(stats.dry_day_dates) == 7

    def test_calculate_period_stats_with_gaps_calculates_correct_longest_streak(self, sample_dry_days_list):
        """Test that dry days with gaps calculate correct longest streak."""
        # sample_dry_days_list has gaps:
        # 03-01, 03-02 (2-day streak), 03-04 (1-day), 03-07 (1-day), 03-10 (1-day)
        start = datetime(2026, 3, 1)
        end = datetime(2026, 3, 10)

        stats = StatisticsCalculator.calculate_period_stats(
            dry_days=sample_dry_days_list,
            start_date=start,
            end_date=end
        )

        # Longest streak should be 2 (March 1-2)
        assert stats.longest_streak == 2
        assert stats.dry_days_count == 5

    def test_calculate_period_stats_with_limited_data_shows_available_less_than_requested(self):
        """Test limited data scenario (AC-4.7) where available_days < requested_days."""
        from sdd_dry_days.core.dry_day import DryDay

        # User started tracking on March 5, but we're requesting 30-day period (Feb 6 - Mar 7)
        dry_days = [
            DryDay(date=datetime(2026, 3, 5)),
            DryDay(date=datetime(2026, 3, 6)),
            DryDay(date=datetime(2026, 3, 7))
        ]

        start = datetime(2026, 2, 6)
        end = datetime(2026, 3, 7)  # 30 days requested

        stats = StatisticsCalculator.calculate_period_stats(
            dry_days=dry_days,
            start_date=start,
            end_date=end,
            all_recorded_days=dry_days  # Earliest record is March 5
        )

        # Verify limited data indicator
        assert stats.requested_days == 30  # User requested 30 days
        assert stats.available_days == 3  # Only 3 days available (Mar 5-7)
        assert stats.available_days < stats.requested_days  # AC-4.7
        assert stats.dry_days_count == 3
        assert stats.total_days == 30
        # Percentage is still based on total days (30)
        assert stats.percentage == 10.0  # 3/30 * 100 = 10%

    def test_calculate_period_stats_with_sufficient_data_shows_full_availability(self):
        """Test that when all requested days are covered, available_days equals requested_days."""
        from sdd_dry_days.core.dry_day import DryDay

        # User started tracking on Feb 1, requesting period Feb 6 - Mar 7
        dry_days = [
            DryDay(date=datetime(2026, 2, 1)),  # Earliest record
            DryDay(date=datetime(2026, 2, 10)),
            DryDay(date=datetime(2026, 3, 5))
        ]

        start = datetime(2026, 2, 6)
        end = datetime(2026, 3, 7)  # 30 days requested

        stats = StatisticsCalculator.calculate_period_stats(
            dry_days=dry_days,
            start_date=start,
            end_date=end,
            all_recorded_days=dry_days  # Earliest record is Feb 1 (before period start)
        )

        # Verify full data availability
        assert stats.requested_days == 30
        assert stats.available_days == 30  # All requested days are covered
        assert stats.dry_days_count == 2  # Only 2 in period (Feb 10, Mar 5)
        assert stats.total_days == 30

    def test_calculate_period_stats_normalizes_dates_to_midnight(self):
        """Test that calculate_period_stats normalizes dates to midnight."""
        from sdd_dry_days.core.dry_day import DryDay

        # Create dry day with time component
        dry_days = [DryDay(date=datetime(2026, 3, 5, 14, 30, 45))]
        start = datetime(2026, 3, 1, 18, 0, 0)
        end = datetime(2026, 3, 10, 22, 15, 30)

        stats = StatisticsCalculator.calculate_period_stats(
            dry_days=dry_days,
            start_date=start,
            end_date=end
        )

        # Verify dates are normalized to midnight
        assert stats.start_date.hour == 0
        assert stats.start_date.minute == 0
        assert stats.start_date.second == 0
        assert stats.start_date.microsecond == 0

        assert stats.end_date.hour == 0
        assert stats.end_date.minute == 0
        assert stats.end_date.second == 0
        assert stats.end_date.microsecond == 0

    def test_calculate_period_stats_without_all_recorded_days_assumes_full_availability(self):
        """Test that when all_recorded_days is None, available_days equals requested_days."""
        from sdd_dry_days.core.dry_day import DryDay

        dry_days = [
            DryDay(date=datetime(2026, 3, 5)),
            DryDay(date=datetime(2026, 3, 6))
        ]

        start = datetime(2026, 2, 6)
        end = datetime(2026, 3, 7)  # 30 days

        # Don't provide all_recorded_days
        stats = StatisticsCalculator.calculate_period_stats(
            dry_days=dry_days,
            start_date=start,
            end_date=end,
            all_recorded_days=None  # Explicit None
        )

        # Should assume full availability
        assert stats.available_days == 30
        assert stats.requested_days == 30
        assert stats.dry_days_count == 2
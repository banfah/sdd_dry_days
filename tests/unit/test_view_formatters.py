"""Unit tests for ViewFormatter.

This module tests the ViewFormatter functionality including:
- Progress bar creation with color coding based on percentage
- Progress bar width calculation (20 characters)
- Percentage text inclusion for accessibility (AC-9.2)
- Calendar grid creation with day markers and current day highlighting

The tests use mocked Rich Console and OutputFormatter to verify formatting logic
without actual terminal rendering.
"""

from unittest.mock import Mock, patch
from datetime import datetime
import pytest

from sdd_dry_days.ui.view_formatters import ViewFormatter
from sdd_dry_days.ui.formatters import OutputFormatter
from sdd_dry_days.core.stats import PeriodStats


class TestProgressBar:
    """Tests for progress bar creation."""

    def test_progress_bar_less_than_50_percent_uses_red_color(self):
        """Test progress bar uses red color when percentage < 50%."""
        # Mock dependencies
        mock_console = Mock()
        mock_output_formatter = Mock(spec=OutputFormatter)

        # Create ViewFormatter with mocks
        formatter = ViewFormatter(mock_console, mock_output_formatter)

        # Test percentage < 50%
        result = formatter.create_progress_bar(25.0)

        # Verify red color is used
        assert "[red]" in result
        assert "[/red]" in result
        # Verify percentage text is included (AC-9.2)
        assert "25%" in result

    def test_progress_bar_at_50_percent_uses_yellow_color(self):
        """Test progress bar uses yellow color when percentage = 50%."""
        # Mock dependencies
        mock_console = Mock()
        mock_output_formatter = Mock(spec=OutputFormatter)

        # Create ViewFormatter with mocks
        formatter = ViewFormatter(mock_console, mock_output_formatter)

        # Test percentage = 50%
        result = formatter.create_progress_bar(50.0)

        # Verify yellow color is used (50 is in the yellow range)
        assert "[yellow]" in result
        assert "[/yellow]" in result
        # Verify percentage text is included (AC-9.2)
        assert "50%" in result

    def test_progress_bar_between_50_and_75_percent_uses_yellow_color(self):
        """Test progress bar uses yellow color when percentage is 50-75%."""
        # Mock dependencies
        mock_console = Mock()
        mock_output_formatter = Mock(spec=OutputFormatter)

        # Create ViewFormatter with mocks
        formatter = ViewFormatter(mock_console, mock_output_formatter)

        # Test percentage in yellow range (60%)
        result = formatter.create_progress_bar(60.0)

        # Verify yellow color is used
        assert "[yellow]" in result
        assert "[/yellow]" in result
        # Verify percentage text is included (AC-9.2)
        assert "60%" in result

    def test_progress_bar_at_75_percent_uses_green_color(self):
        """Test progress bar uses green color when percentage = 75%."""
        # Mock dependencies
        mock_console = Mock()
        mock_output_formatter = Mock(spec=OutputFormatter)

        # Create ViewFormatter with mocks
        formatter = ViewFormatter(mock_console, mock_output_formatter)

        # Test percentage = 75% (boundary case, should be green)
        result = formatter.create_progress_bar(75.0)

        # Verify green color is used (75 is the boundary, implementation uses >= 75 for green)
        assert "[green]" in result
        assert "[/green]" in result
        # Verify percentage text is included (AC-9.2)
        assert "75%" in result

    def test_progress_bar_greater_than_75_percent_uses_green_color(self):
        """Test progress bar uses green color when percentage > 75%."""
        # Mock dependencies
        mock_console = Mock()
        mock_output_formatter = Mock(spec=OutputFormatter)

        # Create ViewFormatter with mocks
        formatter = ViewFormatter(mock_console, mock_output_formatter)

        # Test percentage > 75%
        result = formatter.create_progress_bar(85.0)

        # Verify green color is used
        assert "[green]" in result
        assert "[/green]" in result
        # Verify percentage text is included (AC-9.2)
        assert "85%" in result

    def test_progress_bar_at_100_percent_uses_green_color(self):
        """Test progress bar uses green color when percentage = 100%."""
        # Mock dependencies
        mock_console = Mock()
        mock_output_formatter = Mock(spec=OutputFormatter)

        # Create ViewFormatter with mocks
        formatter = ViewFormatter(mock_console, mock_output_formatter)

        # Test percentage = 100%
        result = formatter.create_progress_bar(100.0)

        # Verify green color is used
        assert "[green]" in result
        assert "[/green]" in result
        # Verify percentage text is included (AC-9.2)
        assert "100%" in result

    def test_progress_bar_width_is_20_characters(self):
        """Test progress bar width calculation: filled + empty = 20 characters."""
        # Mock dependencies
        mock_console = Mock()
        mock_output_formatter = Mock(spec=OutputFormatter)

        # Create ViewFormatter with mocks
        formatter = ViewFormatter(mock_console, mock_output_formatter)

        # Test various percentages and verify width
        test_cases = [0.0, 25.0, 50.0, 75.0, 100.0]

        for percentage in test_cases:
            result = formatter.create_progress_bar(percentage)

            # Extract the bar portion (between color tags)
            # Format: [color]▓▓▓░░░[/color] XX%
            start_tag_end = result.find("]") + 1
            end_tag_start = result.rfind("[")
            bar = result[start_tag_end:end_tag_start]

            # Verify bar width is exactly 20 characters
            assert len(bar) == 20, f"Bar width should be 20 characters for {percentage}%"

    def test_progress_bar_uses_correct_filled_and_empty_characters(self):
        """Test progress bar uses correct Unicode characters (▓ filled, ░ empty)."""
        # Mock dependencies
        mock_console = Mock()
        mock_output_formatter = Mock(spec=OutputFormatter)

        # Create ViewFormatter with mocks
        formatter = ViewFormatter(mock_console, mock_output_formatter)

        # Test 50% (should have 10 filled, 10 empty)
        result = formatter.create_progress_bar(50.0)

        # Extract the bar portion
        start_tag_end = result.find("]") + 1
        end_tag_start = result.rfind("[")
        bar = result[start_tag_end:end_tag_start]

        # Verify characters used
        assert "▓" in bar  # Filled character (U+2593)
        assert "░" in bar  # Empty character (U+2591)

    def test_progress_bar_at_0_percent_has_all_empty_characters(self):
        """Test progress bar at 0% has all empty characters."""
        # Mock dependencies
        mock_console = Mock()
        mock_output_formatter = Mock(spec=OutputFormatter)

        # Create ViewFormatter with mocks
        formatter = ViewFormatter(mock_console, mock_output_formatter)

        # Test 0%
        result = formatter.create_progress_bar(0.0)

        # Extract the bar portion
        start_tag_end = result.find("]") + 1
        end_tag_start = result.rfind("[")
        bar = result[start_tag_end:end_tag_start]

        # Verify all characters are empty
        assert bar == "░" * 20
        # Verify percentage text is included (AC-9.2)
        assert "0%" in result

    def test_progress_bar_at_100_percent_has_all_filled_characters(self):
        """Test progress bar at 100% has all filled characters."""
        # Mock dependencies
        mock_console = Mock()
        mock_output_formatter = Mock(spec=OutputFormatter)

        # Create ViewFormatter with mocks
        formatter = ViewFormatter(mock_console, mock_output_formatter)

        # Test 100%
        result = formatter.create_progress_bar(100.0)

        # Extract the bar portion
        start_tag_end = result.find("]") + 1
        end_tag_start = result.rfind("[")
        bar = result[start_tag_end:end_tag_start]

        # Verify all characters are filled
        assert bar == "▓" * 20
        # Verify percentage text is included (AC-9.2)
        assert "100%" in result

    def test_progress_bar_always_includes_percentage_text(self):
        """Test progress bar always includes percentage text for accessibility (AC-9.2)."""
        # Mock dependencies
        mock_console = Mock()
        mock_output_formatter = Mock(spec=OutputFormatter)

        # Create ViewFormatter with mocks
        formatter = ViewFormatter(mock_console, mock_output_formatter)

        # Test various percentages
        test_cases = [0.0, 25.0, 50.0, 75.0, 100.0, 33.333, 66.667]

        for percentage in test_cases:
            result = formatter.create_progress_bar(percentage)

            # Verify percentage text is present
            # Format should be rounded to nearest integer
            expected_text = f"{percentage:.0f}%"
            assert expected_text in result, f"Progress bar should include '{expected_text}' for accessibility"

    def test_progress_bar_correct_filled_count_calculation(self):
        """Test progress bar calculates correct filled character count."""
        # Mock dependencies
        mock_console = Mock()
        mock_output_formatter = Mock(spec=OutputFormatter)

        # Create ViewFormatter with mocks
        formatter = ViewFormatter(mock_console, mock_output_formatter)

        # Test specific percentages and verify filled count
        test_cases = [
            (0.0, 0),    # 0% = 0 filled
            (25.0, 5),   # 25% = 5 filled
            (50.0, 10),  # 50% = 10 filled
            (75.0, 15),  # 75% = 15 filled
            (100.0, 20), # 100% = 20 filled
        ]

        for percentage, expected_filled in test_cases:
            result = formatter.create_progress_bar(percentage)

            # Extract the bar portion
            start_tag_end = result.find("]") + 1
            end_tag_start = result.rfind("[")
            bar = result[start_tag_end:end_tag_start]

            # Count filled characters
            filled_count = bar.count("▓")
            empty_count = bar.count("░")

            # Verify counts
            assert filled_count == expected_filled, f"Expected {expected_filled} filled chars for {percentage}%"
            assert empty_count == 20 - expected_filled, f"Expected {20 - expected_filled} empty chars for {percentage}%"
            assert filled_count + empty_count == 20, "Total characters should always be 20"


class TestViewFormatterInitialization:
    """Tests for ViewFormatter initialization."""

    def test_viewformatter_initializes_with_console_and_output_formatter(self):
        """Test ViewFormatter initializes with Console and OutputFormatter instances."""
        # Mock dependencies
        mock_console = Mock()
        mock_output_formatter = Mock(spec=OutputFormatter)

        # Create ViewFormatter
        formatter = ViewFormatter(mock_console, mock_output_formatter)

        # Verify attributes exist
        assert hasattr(formatter, 'console')
        assert hasattr(formatter, 'output_formatter')
        assert formatter.console is mock_console
        assert formatter.output_formatter is mock_output_formatter


class TestCalendarGrid:
    """Tests for calendar grid creation (_create_calendar_grid)."""

    def test_calendar_grid_with_empty_stats_returns_grid_with_no_markers(self):
        """Test calendar grid with no dry days shows only day numbers with - markers."""
        # Mock dependencies
        mock_console = Mock()
        mock_output_formatter = Mock(spec=OutputFormatter)

        # Create ViewFormatter
        formatter = ViewFormatter(mock_console, mock_output_formatter)

        # Create PeriodStats for March 2026 (starts on Sunday) with no dry days
        stats = PeriodStats(
            start_date=datetime(2026, 3, 1),
            end_date=datetime(2026, 3, 31),
            total_days=31,
            dry_days_count=0,
            percentage=0.0,
            longest_streak=0,
            dry_day_dates=[],  # No dry days
            available_days=31,
            requested_days=31
        )

        # Mock today to be outside the month (to avoid current day marker)
        with patch('sdd_dry_days.ui.view_formatters.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2026, 4, 15)  # Outside March

            # Generate calendar grid
            result = formatter._create_calendar_grid(stats)

            # Verify header is present
            assert "Mon  Tue  Wed  Thu  Fri  Sat  Sun" in result

            # Verify day 1 is present with - marker (red)
            assert "1[red]-[/red]" in result

            # Verify no green checkmarks (no dry days)
            assert "[green]✓[/green]" not in result

            # Verify all days have red - markers
            assert "[red]-[/red]" in result

    def test_calendar_grid_with_first_day_on_monday(self):
        """Test calendar grid when first day of month is Monday."""
        # Mock dependencies
        mock_console = Mock()
        mock_output_formatter = Mock(spec=OutputFormatter)

        # Create ViewFormatter
        formatter = ViewFormatter(mock_console, mock_output_formatter)

        # Create PeriodStats for February 2026 (starts on Sunday, but we need one that starts on Monday)
        # Use May 2026 which starts on Friday (weekday=4)
        # Actually, use a date that starts on Monday
        # April 2026 starts on Wednesday (weekday=2)
        # June 2026 starts on Monday (weekday=0)
        stats = PeriodStats(
            start_date=datetime(2026, 6, 1),  # June 1, 2026 is Monday
            end_date=datetime(2026, 6, 30),
            total_days=30,
            dry_days_count=5,
            percentage=16.67,
            longest_streak=2,
            dry_day_dates=[
                datetime(2026, 6, 1),  # Monday
                datetime(2026, 6, 2),  # Tuesday
                datetime(2026, 6, 15),
                datetime(2026, 6, 20),
                datetime(2026, 6, 30)
            ],
            available_days=30,
            requested_days=30
        )

        # Mock today to be outside the month
        with patch('sdd_dry_days.ui.view_formatters.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2026, 7, 15)  # Outside June

            # Generate calendar grid
            result = formatter._create_calendar_grid(stats)

            # Verify header is present
            assert "Mon  Tue  Wed  Thu  Fri  Sat  Sun" in result

            # Verify first day (1) appears at the start of the week (Monday column)
            # Since June 1 is Monday, there should be no empty cells before it
            lines = result.split('\n')
            first_data_line = lines[1]  # Skip header

            # First day should be in the Monday position (first position in line)
            assert first_data_line.strip().startswith("1")

            # Verify dry days are marked with checkmark
            assert " 1[green]✓[/green]" in result or "1[green]✓[/green]" in result
            assert " 2[green]✓[/green]" in result or "2[green]✓[/green]" in result

    def test_calendar_grid_with_first_day_on_sunday(self):
        """Test calendar grid when first day of month is Sunday."""
        # Mock dependencies
        mock_console = Mock()
        mock_output_formatter = Mock(spec=OutputFormatter)

        # Create ViewFormatter
        formatter = ViewFormatter(mock_console, mock_output_formatter)

        # Create PeriodStats for March 2026 (March 1 is Sunday)
        stats = PeriodStats(
            start_date=datetime(2026, 3, 1),  # March 1, 2026 is Sunday
            end_date=datetime(2026, 3, 31),
            total_days=31,
            dry_days_count=3,
            percentage=9.68,
            longest_streak=2,
            dry_day_dates=[
                datetime(2026, 3, 1),  # Sunday
                datetime(2026, 3, 8),  # Sunday
                datetime(2026, 3, 15)
            ],
            available_days=31,
            requested_days=31
        )

        # Mock today to be outside the month
        with patch('sdd_dry_days.ui.view_formatters.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2026, 4, 15)  # Outside March

            # Generate calendar grid
            result = formatter._create_calendar_grid(stats)

            # Verify header is present
            assert "Mon  Tue  Wed  Thu  Fri  Sat  Sun" in result

            # Verify first day (1) appears at the end of the first week (Sunday column)
            # Since March 1 is Sunday, there should be 6 empty cells before it
            lines = result.split('\n')
            first_data_line = lines[1]  # Skip header

            # Count empty cells at the start (should be 6 days worth: Mon-Sat)
            # Empty cells are represented as 5 spaces each
            assert first_data_line.count("     ") >= 6

            # Verify dry days are marked with checkmark
            assert "1[green]✓[/green]" in result

    def test_calendar_grid_with_28_day_month(self):
        """Test calendar grid with 28-day month (February non-leap year)."""
        # Mock dependencies
        mock_console = Mock()
        mock_output_formatter = Mock(spec=OutputFormatter)

        # Create ViewFormatter
        formatter = ViewFormatter(mock_console, mock_output_formatter)

        # Create PeriodStats for February 2026 (28 days, non-leap year)
        stats = PeriodStats(
            start_date=datetime(2026, 2, 1),  # February 1, 2026
            end_date=datetime(2026, 2, 28),  # February 28, 2026 (non-leap year)
            total_days=28,
            dry_days_count=14,
            percentage=50.0,
            longest_streak=7,
            dry_day_dates=[
                datetime(2026, 2, d) for d in [1, 2, 3, 7, 14, 15, 16, 17, 18, 19, 20, 21, 27, 28]
            ],
            available_days=28,
            requested_days=28
        )

        # Mock today to be outside the month
        with patch('sdd_dry_days.ui.view_formatters.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2026, 3, 15)  # Outside February

            # Generate calendar grid
            result = formatter._create_calendar_grid(stats)

            # Verify header is present
            assert "Mon  Tue  Wed  Thu  Fri  Sat  Sun" in result

            # Verify day 28 is present (last day of February)
            assert "28" in result

            # Verify day 29 is NOT present (not a leap year)
            assert "29[" not in result  # Check for "29" followed by markup

            # Verify some dry days are marked
            assert "[green]✓[/green]" in result

            # Count the number of checkmarks (should be 14)
            checkmark_count = result.count("[green]✓[/green]")
            assert checkmark_count == 14

    def test_calendar_grid_with_31_day_month(self):
        """Test calendar grid with 31-day month."""
        # Mock dependencies
        mock_console = Mock()
        mock_output_formatter = Mock(spec=OutputFormatter)

        # Create ViewFormatter
        formatter = ViewFormatter(mock_console, mock_output_formatter)

        # Create PeriodStats for March 2026 (31 days)
        stats = PeriodStats(
            start_date=datetime(2026, 3, 1),  # March 1, 2026
            end_date=datetime(2026, 3, 31),  # March 31, 2026
            total_days=31,
            dry_days_count=15,
            percentage=48.39,
            longest_streak=5,
            dry_day_dates=[
                datetime(2026, 3, d) for d in [1, 5, 10, 11, 12, 13, 14, 15, 20, 21, 22, 25, 28, 30, 31]
            ],
            available_days=31,
            requested_days=31
        )

        # Mock today to be outside the month
        with patch('sdd_dry_days.ui.view_formatters.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2026, 4, 15)  # Outside March

            # Generate calendar grid
            result = formatter._create_calendar_grid(stats)

            # Verify header is present
            assert "Mon  Tue  Wed  Thu  Fri  Sat  Sun" in result

            # Verify day 31 is present (last day of March)
            assert "31" in result

            # Verify some dry days are marked
            assert "[green]✓[/green]" in result

            # Count the number of checkmarks (should be 15)
            checkmark_count = result.count("[green]✓[/green]")
            assert checkmark_count == 15

            # Verify some non-dry days are marked with -
            assert "[red]-[/red]" in result

    def test_calendar_grid_marks_current_day_with_asterisk(self):
        """Test calendar grid marks current day with asterisk (AC-3.5)."""
        # Mock dependencies
        mock_console = Mock()
        mock_output_formatter = Mock(spec=OutputFormatter)

        # Create ViewFormatter
        formatter = ViewFormatter(mock_console, mock_output_formatter)

        # Create PeriodStats for March 2026
        stats = PeriodStats(
            start_date=datetime(2026, 3, 1),
            end_date=datetime(2026, 3, 31),
            total_days=31,
            dry_days_count=5,
            percentage=16.13,
            longest_streak=2,
            dry_day_dates=[
                datetime(2026, 3, 1),
                datetime(2026, 3, 5),
                datetime(2026, 3, 7),  # Current day (will be dry)
                datetime(2026, 3, 15),
                datetime(2026, 3, 20)
            ],
            available_days=31,
            requested_days=31
        )

        # Mock today to be March 7, 2026 (a dry day)
        with patch('sdd_dry_days.ui.view_formatters.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2026, 3, 7, 14, 30)  # March 7 at 2:30 PM

            # Generate calendar grid
            result = formatter._create_calendar_grid(stats)

            # Verify current day (7) is marked with asterisk and bold
            # Format should be: [bold]7[green]✓[/green]*[/bold]
            assert "[bold] 7[green]✓[/green]*[/bold]" in result or "[bold]7[green]✓[/green]*[/bold]" in result

            # Verify asterisk is present
            assert "*" in result

            # Verify bold markup is present
            assert "[bold]" in result
            assert "[/bold]" in result

    def test_calendar_grid_marks_current_day_as_not_dry_with_asterisk(self):
        """Test calendar grid marks current day with asterisk even when not dry."""
        # Mock dependencies
        mock_console = Mock()
        mock_output_formatter = Mock(spec=OutputFormatter)

        # Create ViewFormatter
        formatter = ViewFormatter(mock_console, mock_output_formatter)

        # Create PeriodStats for March 2026
        stats = PeriodStats(
            start_date=datetime(2026, 3, 1),
            end_date=datetime(2026, 3, 31),
            total_days=31,
            dry_days_count=2,
            percentage=6.45,
            longest_streak=1,
            dry_day_dates=[
                datetime(2026, 3, 1),
                datetime(2026, 3, 15)
                # Note: March 7 (today) is NOT a dry day
            ],
            available_days=31,
            requested_days=31
        )

        # Mock today to be March 7, 2026 (NOT a dry day)
        with patch('sdd_dry_days.ui.view_formatters.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2026, 3, 7, 14, 30)  # March 7 at 2:30 PM

            # Generate calendar grid
            result = formatter._create_calendar_grid(stats)

            # Verify current day (7) is marked with asterisk and bold, but with - marker
            # Format should be: [bold]7[red]-[/red]*[/bold]
            assert "[bold] 7[red]-[/red]*[/bold]" in result or "[bold]7[red]-[/red]*[/bold]" in result

            # Verify asterisk is present
            assert "*" in result

            # Verify bold markup is present
            assert "[bold]" in result
            assert "[/bold]" in result

    def test_calendar_grid_marks_dry_days_with_checkmark(self):
        """Test calendar grid marks dry days with green checkmark (AC-3.2)."""
        # Mock dependencies
        mock_console = Mock()
        mock_output_formatter = Mock(spec=OutputFormatter)

        # Create ViewFormatter
        formatter = ViewFormatter(mock_console, mock_output_formatter)

        # Create PeriodStats for March 2026
        stats = PeriodStats(
            start_date=datetime(2026, 3, 1),
            end_date=datetime(2026, 3, 31),
            total_days=31,
            dry_days_count=10,
            percentage=32.26,
            longest_streak=5,
            dry_day_dates=[
                datetime(2026, 3, d) for d in [1, 2, 3, 4, 5, 10, 15, 20, 25, 30]
            ],
            available_days=31,
            requested_days=31
        )

        # Mock today to be outside the month
        with patch('sdd_dry_days.ui.view_formatters.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2026, 4, 15)  # Outside March

            # Generate calendar grid
            result = formatter._create_calendar_grid(stats)

            # Verify dry days are marked with green checkmark
            assert "[green]✓[/green]" in result

            # Count the number of checkmarks (should be 10)
            checkmark_count = result.count("[green]✓[/green]")
            assert checkmark_count == 10

            # Verify specific dry days have checkmarks
            # Day 1 should have checkmark
            assert "1[green]✓[/green]" in result

            # Verify non-dry days have red dash
            assert "[red]-[/red]" in result

            # Count dashes (should be 21 for 31 total - 10 dry days)
            dash_count = result.count("[red]-[/red]")
            assert dash_count == 21
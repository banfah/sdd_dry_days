"""Integration tests for CLI.

This module tests the command-line interface end-to-end with actual storage operations.
Tests include:
- Adding today as a dry day (default behavior)
- Adding specific dates in various formats (ISO, US format)
- Adding dates with notes
- Adding date ranges
- Duplicate date handling
- Invalid date format error handling
- Invalid date range error handling (end < start)
- Large range confirmation (>90 days)

These tests use pytest's tmp_path fixture for isolated filesystem testing and mock
the OutputFormatter to capture output calls instead of printing to the terminal.
Coverage target: End-to-end CLI workflow validation.
"""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import pytest

from sdd_dry_days.cli import CLI
from sdd_dry_days.storage.json_storage import JsonStorage


class TestAddToday:
    """Tests for adding today as a dry day (default behavior)."""

    def test_add_command_without_args_adds_today(self, tmp_path):
        """Test 'sdd add' without arguments adds today as a dry day."""
        cli = CLI()
        cli.storage = JsonStorage(data_dir=tmp_path)
        cli.formatter = Mock()

        # Run add command without arguments
        cli.run(["add"])

        # Verify success formatter was called
        cli.formatter.success.assert_called_once()
        call_args = cli.formatter.success.call_args
        date_arg = call_args[0][1]

        # Verify today's date was added
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        assert date_arg.date() == today.date()

        # Verify dry day was stored
        all_days = cli.storage.get_all_dry_days()
        assert len(all_days) == 1
        assert all_days[0].date.date() == today.date()

    def test_add_today_with_note_saves_note(self, tmp_path):
        """Test 'sdd add --note' adds today with a note."""
        cli = CLI()
        cli.storage = JsonStorage(data_dir=tmp_path)
        cli.formatter = Mock()

        # Run add command with note
        cli.run(["add", "--note", "Feeling great!"])

        # Verify success formatter was called
        cli.formatter.success.assert_called_once()

        # Verify dry day was stored with note
        all_days = cli.storage.get_all_dry_days()
        assert len(all_days) == 1
        assert all_days[0].note == "Feeling great!"

    def test_add_today_displays_current_streak(self, tmp_path):
        """Test adding today displays current streak count."""
        cli = CLI()
        cli.storage = JsonStorage(data_dir=tmp_path)
        cli.formatter = Mock()

        # Add previous days to create a streak
        yesterday = datetime.now() - timedelta(days=1)
        two_days_ago = datetime.now() - timedelta(days=2)

        from sdd_dry_days.core.dry_day import DryDay
        cli.storage.add_dry_day(DryDay(date=two_days_ago))
        cli.storage.add_dry_day(DryDay(date=yesterday))

        # Add today
        cli.run(["add"])

        # Verify success formatter was called with streak
        cli.formatter.success.assert_called_once()
        call_args = cli.formatter.success.call_args
        streak_arg = call_args[0][2]

        # Should have 3-day streak
        assert streak_arg == 3


class TestAddSpecificDate:
    """Tests for adding specific dates."""

    def test_add_specific_date_in_iso_format(self, tmp_path):
        """Test 'sdd add 2026-03-06' adds specific date in ISO format."""
        cli = CLI()
        cli.storage = JsonStorage(data_dir=tmp_path)
        cli.formatter = Mock()

        # Run add command with ISO date
        cli.run(["add", "2026-03-06"])

        # Verify success formatter was called
        cli.formatter.success.assert_called_once()
        call_args = cli.formatter.success.call_args
        date_arg = call_args[0][1]

        # Verify correct date was added
        assert date_arg.date() == datetime(2026, 3, 6).date()

        # Verify dry day was stored
        all_days = cli.storage.get_all_dry_days()
        assert len(all_days) == 1
        assert all_days[0].date.date() == datetime(2026, 3, 6).date()

    def test_add_specific_date_in_us_format(self, tmp_path):
        """Test 'sdd add 03/06/2026' parses US format correctly."""
        cli = CLI()
        cli.storage = JsonStorage(data_dir=tmp_path)
        cli.formatter = Mock()

        # Run add command with US date format
        cli.run(["add", "03/06/2026"])

        # Verify success formatter was called
        cli.formatter.success.assert_called_once()
        call_args = cli.formatter.success.call_args
        date_arg = call_args[0][1]

        # Verify correct date was parsed (MM/DD/YYYY -> March 6, 2026)
        assert date_arg.date() == datetime(2026, 3, 6).date()

        # Verify dry day was stored
        all_days = cli.storage.get_all_dry_days()
        assert len(all_days) == 1
        assert all_days[0].date.date() == datetime(2026, 3, 6).date()

    def test_add_specific_date_with_note(self, tmp_path):
        """Test 'sdd add 2026-03-06 --note' adds date with note."""
        cli = CLI()
        cli.storage = JsonStorage(data_dir=tmp_path)
        cli.formatter = Mock()

        # Run add command with date and note
        cli.run(["add", "2026-03-06", "--note", "First day success"])

        # Verify success formatter was called
        cli.formatter.success.assert_called_once()

        # Verify dry day was stored with note
        all_days = cli.storage.get_all_dry_days()
        assert len(all_days) == 1
        assert all_days[0].date.date() == datetime(2026, 3, 6).date()
        assert all_days[0].note == "First day success"

    def test_add_past_date_calculates_streak(self, tmp_path):
        """Test adding a past date calculates streak correctly."""
        cli = CLI()
        cli.storage = JsonStorage(data_dir=tmp_path)
        cli.formatter = Mock()

        # Add today and yesterday first
        from sdd_dry_days.core.dry_day import DryDay
        today = datetime.now()
        yesterday = today - timedelta(days=1)

        cli.storage.add_dry_day(DryDay(date=yesterday))
        cli.storage.add_dry_day(DryDay(date=today))

        # Add two days ago
        two_days_ago = today - timedelta(days=2)
        date_str = two_days_ago.strftime("%Y-%m-%d")
        cli.run(["add", date_str])

        # Verify success formatter was called with streak
        cli.formatter.success.assert_called_once()
        call_args = cli.formatter.success.call_args
        streak_arg = call_args[0][2]

        # Should have 3-day streak
        assert streak_arg == 3

    def test_add_future_date_marks_as_planned(self, tmp_path):
        """Test adding a future date marks it as planned."""
        cli = CLI()
        cli.storage = JsonStorage(data_dir=tmp_path)
        cli.formatter = Mock()

        # Add future date
        future = datetime.now() + timedelta(days=7)
        date_str = future.strftime("%Y-%m-%d")
        cli.run(["add", date_str])

        # Verify success formatter was called with 0 streak (planned days don't count)
        cli.formatter.success.assert_called_once()
        call_args = cli.formatter.success.call_args
        streak_arg = call_args[0][2]
        assert streak_arg == 0

        # Verify dry day was stored as planned
        all_days = cli.storage.get_all_dry_days()
        assert len(all_days) == 1
        assert all_days[0].is_planned is True


class TestAddDateRange:
    """Tests for adding date ranges."""

    def test_add_date_range_adds_all_dates(self, tmp_path):
        """Test 'sdd add --range 2026-03-01 2026-03-05' adds all dates in range."""
        cli = CLI()
        cli.storage = JsonStorage(data_dir=tmp_path)
        cli.formatter = Mock()

        # Run add command with date range
        cli.run(["add", "--range", "2026-03-01", "2026-03-05"])

        # Verify range summary formatter was called
        cli.formatter.range_summary.assert_called_once()
        call_args = cli.formatter.range_summary.call_args
        added, skipped, total = call_args[0]

        # Should have added 5 days (Mar 1-5 inclusive)
        assert added == 5
        assert skipped == 0
        assert total == 5

        # Verify all dry days were stored
        all_days = cli.storage.get_all_dry_days()
        assert len(all_days) == 5
        assert all_days[0].date.date() == datetime(2026, 3, 1).date()
        assert all_days[4].date.date() == datetime(2026, 3, 5).date()

    def test_add_date_range_skips_existing_dates(self, tmp_path):
        """Test date range skips dates that already exist."""
        cli = CLI()
        cli.storage = JsonStorage(data_dir=tmp_path)
        cli.formatter = Mock()

        # Pre-add some dates in the range
        from sdd_dry_days.core.dry_day import DryDay
        cli.storage.add_dry_day(DryDay(date=datetime(2026, 3, 2)))
        cli.storage.add_dry_day(DryDay(date=datetime(2026, 3, 4)))

        # Run add command with date range
        cli.run(["add", "--range", "2026-03-01", "2026-03-05"])

        # Verify range summary shows correct counts
        cli.formatter.range_summary.assert_called_once()
        call_args = cli.formatter.range_summary.call_args
        added, skipped, total = call_args[0]

        # Should have added 3 days (1, 3, 5), skipped 2 (2, 4)
        assert added == 3
        assert skipped == 2
        assert total == 5

        # Verify total count is correct
        all_days = cli.storage.get_all_dry_days()
        assert len(all_days) == 5

    def test_add_date_range_with_note_applies_to_all(self, tmp_path):
        """Test date range with note applies note to all dates."""
        cli = CLI()
        cli.storage = JsonStorage(data_dir=tmp_path)
        cli.formatter = Mock()

        # Run add command with date range and note
        cli.run(["add", "--range", "2026-03-01", "2026-03-03", "--note", "Recovery week"])

        # Verify range summary was called
        cli.formatter.range_summary.assert_called_once()

        # Verify all dry days have the note
        all_days = cli.storage.get_all_dry_days()
        assert len(all_days) == 3
        for day in all_days:
            assert day.note == "Recovery week"

    def test_add_large_range_prompts_confirmation(self, tmp_path):
        """Test date range >90 days prompts for confirmation."""
        cli = CLI()
        cli.storage = JsonStorage(data_dir=tmp_path)
        cli.formatter = Mock()
        cli.formatter.confirm.return_value = True  # User confirms

        # Run add command with large date range (100 days)
        start = datetime(2026, 1, 1)
        end = start + timedelta(days=99)  # 100 days inclusive
        cli.run(["add", "--range", start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")])

        # Verify confirmation prompt was shown
        cli.formatter.confirm.assert_called_once()
        call_args = cli.formatter.confirm.call_args
        prompt = call_args[0][0]
        assert "100 days" in prompt

        # Verify range summary was called (user confirmed)
        cli.formatter.range_summary.assert_called_once()

    def test_add_large_range_cancels_if_not_confirmed(self, tmp_path):
        """Test large date range cancelled if user doesn't confirm."""
        cli = CLI()
        cli.storage = JsonStorage(data_dir=tmp_path)
        cli.formatter = Mock()
        cli.formatter.confirm.return_value = False  # User declines

        # Run add command with large date range
        start = datetime(2026, 1, 1)
        end = start + timedelta(days=99)
        cli.run(["add", "--range", start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")])

        # Verify confirmation prompt was shown
        cli.formatter.confirm.assert_called_once()

        # Verify range summary was NOT called (user cancelled)
        cli.formatter.range_summary.assert_not_called()

        # Verify no days were added
        all_days = cli.storage.get_all_dry_days()
        assert len(all_days) == 0


class TestDuplicateHandling:
    """Tests for duplicate date handling."""

    def test_add_duplicate_date_shows_already_exists_message(self, tmp_path):
        """Test adding a duplicate date shows 'already exists' message."""
        cli = CLI()
        cli.storage = JsonStorage(data_dir=tmp_path)
        cli.formatter = Mock()

        # Add date first time
        cli.run(["add", "2026-03-06"])

        # Add same date again
        cli.run(["add", "2026-03-06"])

        # Verify already_exists formatter was called on second attempt
        cli.formatter.already_exists.assert_called_once()
        call_args = cli.formatter.already_exists.call_args
        date_arg = call_args[0][0]
        assert date_arg.date() == datetime(2026, 3, 6).date()

        # Verify only one entry exists
        all_days = cli.storage.get_all_dry_days()
        assert len(all_days) == 1

    def test_add_duplicate_today_shows_already_exists_message(self, tmp_path):
        """Test adding today twice shows 'already exists' message."""
        cli = CLI()
        cli.storage = JsonStorage(data_dir=tmp_path)
        cli.formatter = Mock()

        # Add today first time
        cli.run(["add"])

        # Reset mock to check second call
        cli.formatter.reset_mock()

        # Add today again
        cli.run(["add"])

        # Verify already_exists formatter was called on second attempt
        cli.formatter.already_exists.assert_called_once()

        # Verify only one entry exists
        all_days = cli.storage.get_all_dry_days()
        assert len(all_days) == 1


class TestErrorHandling:
    """Tests for error handling."""

    def test_invalid_date_format_shows_error(self, tmp_path):
        """Test invalid date format shows clear error message."""
        cli = CLI()
        cli.storage = JsonStorage(data_dir=tmp_path)
        cli.formatter = Mock()

        # Run add command with invalid date
        cli.run(["add", "not-a-date"])

        # Verify error formatter was called
        cli.formatter.error.assert_called_once()
        call_args = cli.formatter.error.call_args
        message = call_args[0][0]
        details = call_args[0][1]

        assert "Invalid date" in message
        assert "not-a-date" in details or "format" in details.lower()

        # Verify no days were added
        all_days = cli.storage.get_all_dry_days()
        assert len(all_days) == 0

    def test_invalid_date_range_end_before_start_shows_error(self, tmp_path):
        """Test invalid date range (end < start) shows error."""
        cli = CLI()
        cli.storage = JsonStorage(data_dir=tmp_path)
        cli.formatter = Mock()

        # Run add command with invalid range (end before start)
        cli.run(["add", "--range", "2026-03-10", "2026-03-05"])

        # Verify error formatter was called
        cli.formatter.error.assert_called_once()
        call_args = cli.formatter.error.call_args
        message = call_args[0][0]
        details = call_args[0][1]

        assert "Invalid date" in message
        assert "before" in details.lower() or "after" in details.lower()

        # Verify no days were added
        all_days = cli.storage.get_all_dry_days()
        assert len(all_days) == 0

    def test_invalid_leap_year_date_shows_error(self, tmp_path):
        """Test invalid leap year date (Feb 29 in non-leap year) shows error."""
        cli = CLI()
        cli.storage = JsonStorage(data_dir=tmp_path)
        cli.formatter = Mock()

        # Run add command with Feb 29 in non-leap year (2023)
        # Note: Python's strptime rejects this at parsing stage, so we get
        # a date format error rather than a leap year validation error
        cli.run(["add", "2023-02-29"])

        # Verify error formatter was called
        cli.formatter.error.assert_called_once()
        call_args = cli.formatter.error.call_args
        message = call_args[0][0]
        details = call_args[0][1]

        assert "Invalid date" in message
        # The error comes from the parser not recognizing the invalid date
        assert "format" in details.lower() or "2023-02-29" in details

        # Verify no days were added
        all_days = cli.storage.get_all_dry_days()
        assert len(all_days) == 0

    def test_storage_error_handled_gracefully(self, tmp_path):
        """Test storage errors are handled gracefully."""
        cli = CLI()
        cli.storage = JsonStorage(data_dir=tmp_path)
        cli.formatter = Mock()

        # Mock storage to raise an exception
        cli.storage.add_dry_day = Mock(side_effect=Exception("Disk full"))

        # Run add command
        cli.run(["add", "2026-03-06"])

        # Verify error formatter was called
        cli.formatter.error.assert_called_once()
        call_args = cli.formatter.error.call_args
        message = call_args[0][0]

        assert "error occurred" in message.lower()


class TestCLIIntegration:
    """Integration tests for complete CLI workflows."""

    def test_add_multiple_dates_in_sequence(self, tmp_path):
        """Test adding multiple dates in sequence works correctly."""
        cli = CLI()
        cli.storage = JsonStorage(data_dir=tmp_path)
        cli.formatter = Mock()

        # Add multiple dates
        dates = ["2026-03-01", "2026-03-05", "2026-03-10", "2026-03-15"]
        for date in dates:
            cli.run(["add", date])

        # Verify all dates were added
        all_days = cli.storage.get_all_dry_days()
        assert len(all_days) == 4

        # Verify dates are sorted
        for i in range(len(all_days) - 1):
            assert all_days[i].date < all_days[i + 1].date

    def test_mix_of_single_dates_and_ranges(self, tmp_path):
        """Test mixing single dates and ranges works correctly."""
        cli = CLI()
        cli.storage = JsonStorage(data_dir=tmp_path)
        cli.formatter = Mock()

        # Add single date
        cli.run(["add", "2026-03-01"])

        # Add range
        cli.run(["add", "--range", "2026-03-05", "2026-03-07"])

        # Add another single date
        cli.run(["add", "2026-03-10"])

        # Verify all dates were added (1 + 3 + 1 = 5)
        all_days = cli.storage.get_all_dry_days()
        assert len(all_days) == 5

    def test_data_persists_across_cli_instances(self, tmp_path):
        """Test data persists when creating new CLI instances."""
        # First CLI instance
        cli1 = CLI()
        cli1.storage = JsonStorage(data_dir=tmp_path)
        cli1.formatter = Mock()
        cli1.run(["add", "2026-03-06"])

        # Second CLI instance with same storage directory
        cli2 = CLI()
        cli2.storage = JsonStorage(data_dir=tmp_path)
        cli2.formatter = Mock()

        # Verify data persists
        all_days = cli2.storage.get_all_dry_days()
        assert len(all_days) == 1
        assert all_days[0].date.date() == datetime(2026, 3, 6).date()

        # Add another date with second instance
        cli2.run(["add", "2026-03-07"])

        # Verify both dates exist
        all_days = cli2.storage.get_all_dry_days()
        assert len(all_days) == 2
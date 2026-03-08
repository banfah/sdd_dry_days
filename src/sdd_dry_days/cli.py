"""Command-line interface handler for SDD Dry Days.

This module provides the CLI class that handles command-line argument parsing
and routing for the SDD Dry Days application. It integrates all core components
(DryDay model, storage, date parsing, output formatting, and streak calculation)
to provide a cohesive command-line experience.

The CLI supports multiple commands and flexible date input formats, making it
easy for users to track their alcohol-free days.
"""

import argparse
from datetime import datetime, timedelta
from typing import List, Optional

from rich.console import Console

from .core.dry_day import DryDay
from .core.streak import StreakCalculator
from .core.stats import StatisticsCalculator
from .storage.json_storage import JsonStorage
from .utils.date_parser import DateParser, DateParseError
from .ui.formatters import OutputFormatter
from .ui.view_formatters import ViewFormatter


class CLI:
    """Command-line interface handler.

    This class manages the command-line interface for the SDD Dry Days application.
    It handles argument parsing, command routing, and coordinates between business
    logic (DryDay, StreakCalculator) and presentation (OutputFormatter).

    The CLI follows a subcommand pattern where each major operation (add, view, stats)
    is a separate subcommand with its own arguments and options.

    Attributes:
        storage: JsonStorage instance for data persistence.
        formatter: OutputFormatter instance for styled terminal output.
        parser: ArgumentParser instance for command-line argument parsing.

    Example:
        >>> cli = CLI()
        >>> cli.run(["add"])  # Add today as a dry day
        >>> cli.run(["add", "2026-03-06", "--note", "Feeling great!"])
    """

    def __init__(self):
        """Initialize CLI with storage, formatter, and argument parser.

        Creates instances of JsonStorage for data persistence and OutputFormatter
        for styled terminal output. Sets up the argument parser with all supported
        commands and options.
        """
        self.storage = JsonStorage()
        self.formatter = OutputFormatter()
        self.console = Console()
        self.streak_calculator = StreakCalculator()
        self.view_formatter = ViewFormatter(self.console, self.formatter)
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser with all commands and options.

        Sets up the argparse ArgumentParser with the main program definition and
        all subcommands. Currently supports the "add" subcommand with options for
        adding single dates, date ranges, and notes.

        Returns:
            Configured ArgumentParser instance ready to parse command-line arguments.

        Example structure:
            sdd add                              # Add today
            sdd add 2026-03-06                  # Add specific date
            sdd add --note "Feeling great!"     # Add today with note
            sdd add --range 2026-03-01 2026-03-05  # Add date range
        """
        parser = argparse.ArgumentParser(
            prog="sdd",
            description="SDD Dry Days - Track your alcohol-free days"
        )

        subparsers = parser.add_subparsers(dest="command", help="Commands")

        # Add command
        add_parser = subparsers.add_parser("add", help="Add dry day(s)")
        add_parser.add_argument(
            "date",
            nargs="?",
            help="Date to add (defaults to today). Format: YYYY-MM-DD, MM/DD/YYYY, etc."
        )
        add_parser.add_argument(
            "--note", "-n",
            help="Optional note for the dry day"
        )
        add_parser.add_argument(
            "--range", "-r",
            nargs=2,
            metavar=("START", "END"),
            help="Add date range (inclusive)"
        )

        # View command
        view_parser = subparsers.add_parser("view", help="View dry days and statistics")
        view_parser.add_argument(
            "--sort",
            choices=["asc", "desc"],
            default="desc",
            help="Sort order (desc=newest first, asc=oldest first)"
        )
        view_parser.add_argument(
            "--filter",
            choices=["planned", "actual"],
            help="Filter by type (planned=future, actual=past/today)"
        )
        view_parser.add_argument(
            "--week",
            action="store_true",
            help="Show current week"
        )
        view_parser.add_argument(
            "--month",
            action="store_true",
            help="Show current month"
        )
        view_parser.add_argument(
            "--stats",
            action="store_true",
            help="Show 30/60/90 day stats"
        )
        view_parser.add_argument(
            "--range",
            nargs=2,
            metavar=("START", "END"),
            help="Show custom date range"
        )

        return parser

    def run(self, args: List[str] = None):
        """Run the CLI with provided arguments.

        Parses command-line arguments and routes to the appropriate command handler.
        This is the main entry point for the CLI application.

        Args:
            args: List of command-line arguments. If None, uses sys.argv.
                 Typically provided as a list like ["add", "2026-03-06"] for testing.

        Example:
            >>> cli = CLI()
            >>> cli.run(["add"])  # Add today
            >>> cli.run(["add", "2026-03-06"])  # Add specific date
            >>> cli.run(["add", "--range", "2026-03-01", "2026-03-05"])  # Add range
        """
        parsed_args = self.parser.parse_args(args)

        if parsed_args.command == "add":
            self._handle_add(parsed_args)
        elif parsed_args.command == "view":
            self._handle_view(parsed_args)
        else:
            self.parser.print_help()

    def _handle_add(self, args):
        """Handle the add command by dispatching to specific methods.

        Routes the add command to the appropriate handler based on arguments:
        - If --range is provided: call _add_date_range()
        - If date argument is provided: call _add_single_date()
        - Otherwise: call _add_today()

        Args:
            args: Parsed arguments from argparse containing command options.
        """
        try:
            if args.range:
                self._add_date_range(args.range[0], args.range[1], args.note)
            elif args.date:
                self._add_single_date(args.date, args.note)
            else:
                self._add_today(args.note)
        except DateParseError as e:
            self.formatter.error("Invalid date", str(e))
        except Exception as e:
            self.formatter.error("An error occurred", str(e))

    def _handle_view(self, args):
        """Handle the view command by routing to specific view methods.

        Routes the view command to the appropriate handler based on arguments:
        - If --week is provided: call _view_week()
        - If --month is provided: call _view_month()
        - If --stats is provided: call _view_stats()
        - If --range is provided: call _view_range() with start and end dates
        - Otherwise: call _view_list() with sort and filter options (default view)

        The routing follows priority order: week, month, stats, range, then list view.
        All exceptions are caught and displayed as user-friendly error messages.

        Args:
            args: Parsed arguments from argparse containing view command options.

        Example:
            >>> cli._handle_view(args)  # args.week=True -> calls _view_week()
            >>> cli._handle_view(args)  # args.month=True -> calls _view_month()
            >>> cli._handle_view(args)  # no flags -> calls _view_list(sort, filter)
        """
        try:
            if args.week:
                self._view_week()
            elif args.month:
                self._view_month()
            elif args.stats:
                self._view_stats()
            elif args.range:
                self._view_range(args.range[0], args.range[1])
            else:
                # Default: list view with optional sort/filter
                self._view_list(args.sort, args.filter)
        except Exception as e:
            # Display user-friendly error (not stack trace)
            self.formatter.error("Error displaying view", str(e))

    def _add_today(self, note: str = ""):
        """Add today as a dry day.

        Creates a DryDay entry for the current date and adds it to storage.
        Shows success message with current streak, or a duplicate message if
        today is already recorded.

        Args:
            note: Optional note to attach to the dry day entry.

        Example output:
            Success: "Dry day added: 2026-03-07"
                     "Current streak: 5 days"
            Duplicate: "Dry day already recorded for 2026-03-07"
        """
        today = datetime.now()
        dry_day = DryDay(date=today, note=note or "")

        if self.storage.add_dry_day(dry_day):
            # Calculate streak
            all_days = self.storage.get_all_dry_days()
            streak = StreakCalculator.calculate_current_streak(all_days)
            self.formatter.success("", dry_day.date, streak)
        else:
            self.formatter.already_exists(dry_day.date)

    def _add_single_date(self, date_str: str, note: str = ""):
        """Add a specific date as a dry day.

        Parses the date string, validates it (including leap year validation),
        determines if it's a planned day (future date), and adds it to storage.

        Args:
            date_str: Date string in various formats (YYYY-MM-DD, MM/DD/YYYY, etc.)
            note: Optional note to attach to the dry day entry.

        Raises:
            DateParseError: If date format is invalid or leap year validation fails.

        Example output:
            Success: "Dry day added: 2026-03-06"
            Duplicate: "Dry day already recorded for 2026-03-06"
        """
        # Parse date
        date = DateParser.parse(date_str)

        # Validate leap year
        DateParser.validate_leap_year(date)

        # Determine if it's a planned day (future date)
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        is_planned = date.date() > today.date()

        # Create and add dry day
        dry_day = DryDay(date=date, note=note or "", is_planned=is_planned)

        if self.storage.add_dry_day(dry_day):
            # Calculate streak (only if not planned)
            streak = 0
            if not is_planned:
                all_days = self.storage.get_all_dry_days()
                streak = StreakCalculator.calculate_current_streak(all_days)
            self.formatter.success("", dry_day.date, streak)
        else:
            self.formatter.already_exists(dry_day.date)

    def _add_date_range(self, start_str: str, end_str: str, note: str = ""):
        """Add a range of dates as dry days.

        Parses start and end dates, generates all dates in the range (inclusive),
        confirms with user if the range exceeds 90 days, and adds all dates to storage.
        Shows summary of how many dates were added vs already existed.

        Args:
            start_str: Start date string in various formats.
            end_str: End date string in various formats.
            note: Optional note to attach to all dry day entries in the range.

        Raises:
            DateParseError: If date formats are invalid, leap year validation fails,
                          or end date is before start date.

        Example output:
            Confirmation (>90 days): "Are you sure you want to add 120 days? (y/N): "
            Summary: "Added 115/120 dry days"
                    "5 already existed"
        """
        # Parse dates
        start = DateParser.parse(start_str)
        end = DateParser.parse(end_str)

        # Validate leap years
        DateParser.validate_leap_year(start)
        DateParser.validate_leap_year(end)

        # Generate date range (this also validates that end >= start)
        dates = DateParser.generate_date_range(start, end)

        # Confirm if range is large (>90 days)
        if len(dates) > 90:
            if not self.formatter.confirm(
                f"Are you sure you want to add {len(dates)} days?"
            ):
                return

        # Add all dates
        added = 0
        skipped = 0
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        for date in dates:
            is_planned = date.date() > today.date()
            dry_day = DryDay(date=date, note=note or "", is_planned=is_planned)

            if self.storage.add_dry_day(dry_day):
                added += 1
            else:
                skipped += 1

        # Show summary
        self.formatter.range_summary(added, skipped, len(dates))

    def _apply_sort(self, dry_days: List[DryDay], order: str) -> List[DryDay]:
        """Sort dry days by date.

        Sorts the list of dry days by date in ascending or descending order.
        This helper method is used by view commands to order results based on
        user preference.

        Args:
            dry_days: List of DryDay instances to sort.
            order: Sort order - "asc" for oldest first, "desc" for newest first.

        Returns:
            Sorted list of DryDay instances.

        Example:
            >>> sorted_days = self._apply_sort(dry_days, "desc")
            # Returns days sorted newest to oldest
        """
        return sorted(dry_days, key=lambda dd: dd.date, reverse=(order == "desc"))

    def _apply_filter(self, dry_days: List[DryDay], filter_type: str) -> List[DryDay]:
        """Filter dry days by type (planned vs actual).

        Filters the list of dry days based on whether they are planned (future)
        or actual (past/today). This helper method is used by view commands to
        show only relevant entries.

        Args:
            dry_days: List of DryDay instances to filter.
            filter_type: Filter type - "planned" for future days, "actual" for past/today.

        Returns:
            Filtered list of DryDay instances.

        Example:
            >>> future_days = self._apply_filter(dry_days, "planned")
            # Returns only days with date > today
        """
        today = datetime.now().date()

        if filter_type == "planned":
            # Return only future days
            return [dd for dd in dry_days if dd.date.date() > today]
        elif filter_type == "actual":
            # Return only past/today days
            return [dd for dd in dry_days if dd.date.date() <= today]
        else:
            # No filter, return all
            return dry_days

    def _view_list(self, sort_order: str = "desc", filter_type: Optional[str] = None):
        """Display list view with optional sorting and filtering.

        Shows all dry days in a table format with sorting and filtering options.
        Displays total count and current streak at the top. If no dry days exist
        after filtering, shows an encouraging message to start tracking.

        This is the default view when running "sdd view" without specific flags.

        Args:
            sort_order: Sort order - "desc" for newest first (default), "asc" for oldest first.
            filter_type: Optional filter - "planned" for future days, "actual" for past/today,
                        None for all days.

        Example:
            >>> self._view_list()  # Show all days, newest first
            >>> self._view_list("asc", "actual")  # Show past/today days, oldest first
        """
        # 1. Fetch all dry days from storage
        dry_days = self.storage.get_all_dry_days()

        # 2. Apply filter FIRST (reduces dataset before sorting)
        if filter_type:
            dry_days = self._apply_filter(dry_days, filter_type)

        # 3. Check if list is empty after filtering
        if not dry_days:
            # Display encouraging message
            self.formatter.error(
                "No dry days yet!",
                "Start your journey with: sdd add"
            )
            return

        # 4. Apply sort SECOND (on filtered dataset)
        dry_days = self._apply_sort(dry_days, sort_order)

        # 5. Calculate current streak
        # Note: For streak calculation, we need all actual dry days (not filtered)
        all_dry_days = self.storage.get_all_dry_days()
        current_streak = self.streak_calculator.calculate_current_streak(all_dry_days)

        # 6. Display the list view
        self.view_formatter.display_list_view(dry_days, current_streak)

    def _view_week(self):
        """Display week view with Monday-Sunday breakdown.

        Shows the current week (Monday through Sunday) with a day-by-day breakdown
        of dry days. Displays a table with day names, dates, dry day status, and notes.
        Includes statistics for the week (count, percentage, progress bar).

        If the week has no dry days, displays an encouraging message to get started.

        The week starts from the most recent Monday and extends through Sunday.

        Example output:
            Week of March 3-9, 2026
            5 out of 7 days (71%)
            [Progress bar visualization]

            | Day | Date       | Status | Notes |
            |-----|------------|--------|-------|
            | Mon | 2026-03-03 | Dry    | ...   |
            | Tue | 2026-03-04 | -      |       |
            ...
        """
        # Get week dates (Monday through Sunday)
        start, end = StatisticsCalculator.get_week_dates(datetime.now())

        # Fetch dry days for the week
        dry_days = self.storage.get_dry_days_in_range(start, end)

        # Calculate statistics for the week
        stats = StatisticsCalculator.calculate_period_stats(dry_days, start, end)

        # Build week_days list: List[Tuple[str, datetime, bool, Optional[str]]]
        week_days = []
        for day in range(7):  # Mon-Sun (0-6)
            current_date = start + timedelta(days=day)
            day_name = current_date.strftime("%a")  # Mon, Tue, Wed, etc.

            # Check if this day is a dry day
            matching_dry_day = next(
                (dd for dd in dry_days if dd.date.date() == current_date.date()),
                None
            )
            is_dry = matching_dry_day is not None
            note = matching_dry_day.note if matching_dry_day else None

            week_days.append((day_name, current_date, is_dry, note))

        # Display the week view
        if stats.dry_days_count == 0:
            # Show encouraging message for empty week
            self.formatter.info("Start your week strong! Add your first dry day.")
        else:
            # Display formatted week view with stats
            self.view_formatter.display_week_view(stats, week_days)

    def _view_month(self):
        """Display month view with calendar grid.

        Shows the current month (1st to last day) with a calendar grid visualization
        displaying day numbers and dry day status. Includes statistics for the month
        (count, percentage, progress bar) and highlights the current day.

        The calendar grid uses checkmarks (✓) to indicate dry days and an asterisk (*)
        to highlight today. Also displays current and longest streak counts.

        If the month has no dry days, displays an encouraging message to get started.

        Example output:
            March 2026
            12 out of 31 days (39%)
            [Progress bar visualization]

            Su Mo Tu We Th Fr Sa
             1  2  3✓ 4  5✓ 6  7*
             8  9 10 11 12 13 14
            ...

            Current streak: 3 days | Longest streak: 5 days
        """
        # Get month dates (1st to last day of current month)
        start, end = StatisticsCalculator.get_month_dates(datetime.now())

        # Fetch dry days for the month
        dry_days = self.storage.get_dry_days_in_range(start, end)

        # Calculate statistics for the month
        stats = StatisticsCalculator.calculate_period_stats(dry_days, start, end)

        # Display the month view
        if stats.dry_days_count == 0:
            # Show encouraging message for empty month
            self.formatter.info("Your journey starts now! Add today as your first dry day.")
        else:
            # Display formatted month view with calendar grid
            self.view_formatter.display_month_view(stats)

    def _view_stats(self):
        """Display 30/60/90 day statistics view.

        Shows a comprehensive statistics table with three time periods (30, 60, and 90 days).
        For each period, displays dry days count, total days, percentage, and longest streak.
        Includes visual progress bars and the current active streak at the top.

        The method handles limited data scenarios gracefully, showing indicators when fewer
        than the requested days are available (e.g., only 20/90 days recorded).

        Example output:
            Current Streak: 5 days

            | Period    | Dry Days | Total Days | Percentage | Longest Streak |
            |-----------|----------|------------|------------|----------------|
            | Last 30d  | 25       | 30         | 83%        | 7 days         |
            | Last 60d  | 45       | 60         | 75%        | 12 days        |
            | Last 90d  | 60       | 90         | 67%        | 15 days        |

            Each row includes a visual progress bar showing percentage completion.
        """
        # Get today
        today = datetime.now()

        # Calculate dates for 30/60/90 days ago
        start_30 = today - timedelta(days=30)
        start_60 = today - timedelta(days=60)
        start_90 = today - timedelta(days=90)

        # Fetch all dry days
        all_dry_days = self.storage.get_all_dry_days()

        # Calculate stats for each period (pass all_dry_days for limited data indicator)
        stats_30 = StatisticsCalculator.calculate_period_stats(
            all_dry_days, start_30, today, all_dry_days
        )
        stats_60 = StatisticsCalculator.calculate_period_stats(
            all_dry_days, start_60, today, all_dry_days
        )
        stats_90 = StatisticsCalculator.calculate_period_stats(
            all_dry_days, start_90, today, all_dry_days
        )

        # Calculate current streak
        current_streak = self.streak_calculator.calculate_current_streak(all_dry_days)

        # Display
        self.view_formatter.display_stats_view(stats_30, stats_60, stats_90, current_streak)

    def _view_range(self, start_str: str, end_str: str):
        """Display custom date range view with validation.

        Shows dry days and statistics for a specified date range (inclusive). Validates
        date formats and ensures the end date is not before the start date. Displays
        a table with dates, statuses, and notes, along with summary statistics including
        count, percentage, and longest streak.

        The method handles several edge cases:
        - Invalid date formats: Shows error with format examples
        - Invalid range (end before start): Shows error with format examples
        - Empty range (no dry days): Shows encouraging message to start tracking
        - Planned days: Displayed with (P) indicator in the table

        Args:
            start_str: Start date string in various formats (YYYY-MM-DD, MM/DD/YYYY, etc.)
            end_str: End date string in various formats (YYYY-MM-DD, MM/DD/YYYY, etc.)

        Example output (valid range):
            Date Range: 2026-03-01 to 2026-03-31
            15 out of 31 days (48%)
            [Progress bar visualization]

            | Date       | Status | Notes              |
            |------------|--------|--------------------|
            | 2026-03-01 | Dry    | Feeling great!     |
            | 2026-03-02 | -      |                    |
            | 2026-03-03 | Dry    |                    |
            ...

            Longest streak: 7 days

        Example output (invalid range):
            Error: Invalid range: end date must be after start date
            Try: sdd view --range 2026-03-01 2026-03-31

        Example output (empty range):
            No dry days in this period. Add your first dry day to start tracking!
        """
        try:
            # Parse dates using DateParser
            start = DateParser.parse(start_str)
            end = DateParser.parse(end_str)
        except ValueError as e:
            # Handle parse errors with format examples (AC-10.3)
            self.formatter.error(
                f"Invalid date format: {str(e)}\n"
                "Try: sdd view --range 2026-03-01 2026-03-31"
            )
            return

        # Validate: end >= start (AC-5.3)
        if end < start:
            self.formatter.error(
                "Invalid range: end date must be after start date\n"
                "Try: sdd view --range 2026-03-01 2026-03-31"
            )
            return

        # Fetch dry days for range
        dry_days = self.storage.get_dry_days_in_range(start, end)

        # Calculate stats
        stats = StatisticsCalculator.calculate_period_stats(dry_days, start, end)

        # Display
        if stats.dry_days_count == 0:
            self.formatter.info(
                "No dry days in this period. Add your first dry day to start tracking!"
            )
        else:
            self.view_formatter.display_range_view(stats, dry_days)
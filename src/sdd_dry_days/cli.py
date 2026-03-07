"""Command-line interface handler for SDD Dry Days.

This module provides the CLI class that handles command-line argument parsing
and routing for the SDD Dry Days application. It integrates all core components
(DryDay model, storage, date parsing, output formatting, and streak calculation)
to provide a cohesive command-line experience.

The CLI supports multiple commands and flexible date input formats, making it
easy for users to track their alcohol-free days.
"""

import argparse
from datetime import datetime
from typing import List

from .core.dry_day import DryDay
from .core.streak import StreakCalculator
from .storage.json_storage import JsonStorage
from .utils.date_parser import DateParser, DateParseError
from .ui.formatters import OutputFormatter


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
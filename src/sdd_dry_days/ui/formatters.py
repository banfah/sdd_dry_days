"""Output formatting for SDD Dry Days CLI.

This module provides the OutputFormatter class for displaying colorful, styled
messages in the terminal using the Rich library. It handles success messages,
error messages, confirmations, and range summaries with consistent visual styling.
"""

from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class OutputFormatter:
    """Format output messages with colors and styling.

    This class uses the Rich library to create visually appealing terminal output
    with colors, icons, and styled panels. It provides methods for different types
    of messages (success, error, info, confirmation) with appropriate styling.

    Attributes:
        console: Rich Console instance for output rendering.
    """

    def __init__(self):
        """Initialize the OutputFormatter with a Rich Console instance."""
        self.console = Console()

    def success(self, message: str, date: datetime, streak: int = 0):
        """Display success message when dry day is added.

        Shows a green panel with a checkmark icon, the date added, and optionally
        the current streak count if provided.

        Args:
            message: Success message to display (not currently used, reserved for future).
            date: The date that was added as a dry day.
            streak: Current streak count (consecutive dry days). Defaults to 0.
                   If 0, streak information is not displayed.

        Example:
            ✓ Dry day added: 2026-03-07
              Current streak: 5 days
        """
        text = Text()
        text.append("✓ ", style="bold green")
        text.append(f"Dry day added: ", style="green")
        text.append(f"{date.strftime('%Y-%m-%d')}", style="bold cyan")

        if streak > 0:
            text.append(f"\nCurrent streak: ", style="yellow")
            text.append(f"{streak} day{'s' if streak != 1 else ''}", style="bold yellow")

        panel = Panel(text, border_style="green", expand=False)
        self.console.print(panel)

    def already_exists(self, date: datetime):
        """Display message when dry day already exists.

        Shows a blue informational panel indicating that the date is already
        recorded as a dry day.

        Args:
            date: The date that already exists in the records.

        Example:
            ℹ Dry day already recorded for 2026-03-07
        """
        text = Text()
        text.append("ℹ ", style="bold blue")
        text.append(f"Dry day already recorded for ", style="blue")
        text.append(f"{date.strftime('%Y-%m-%d')}", style="bold cyan")

        panel = Panel(text, border_style="blue", expand=False)
        self.console.print(panel)

    def range_summary(self, added: int, skipped: int, total: int):
        """Display summary for date range addition.

        Shows a green panel with statistics about how many dates were added
        versus how many already existed when adding a date range.

        Args:
            added: Number of new dry days added.
            skipped: Number of dates that already existed (not added).
            total: Total number of dates in the range.

        Example:
            ✓ Added 3/5 dry days
            ℹ 2 already existed
        """
        text = Text()
        text.append("✓ ", style="bold green")
        text.append(f"Added {added}/{total} dry days", style="green")

        if skipped > 0:
            text.append(f"\nℹ {skipped} already existed", style="blue")

        panel = Panel(text, border_style="green", expand=False)
        self.console.print(panel)

    def error(self, message: str, details: str = ""):
        """Display error message.

        Shows a red panel with an X icon and the error message. Optionally
        includes additional details in a dimmed style.

        Args:
            message: Primary error message to display.
            details: Optional additional details or context. Defaults to empty string.

        Example:
            ✗ Invalid date format
            Please use YYYY-MM-DD format
        """
        text = Text()
        text.append("✗ ", style="bold red")
        text.append(message, style="red")

        if details:
            text.append(f"\n{details}", style="dim")

        panel = Panel(text, border_style="red", expand=False)
        self.console.print(panel)

    def info(self, message: str):
        """Display informational message.

        Shows a blue panel with an info icon and the message. Used for
        general informational messages, encouragement, and guidance.

        Args:
            message: Informational message to display.

        Example:
            ℹ Start your week strong! Add your first dry day.
        """
        text = Text()
        text.append("ℹ ", style="bold blue")
        text.append(message, style="blue")

        panel = Panel(text, border_style="blue", expand=False)
        self.console.print(panel)

    def confirm(self, message: str) -> bool:
        """Ask for user confirmation.

        Displays a yellow confirmation prompt and waits for user input.
        Returns True if user enters 'y' (case-insensitive), False otherwise.

        Args:
            message: Confirmation question to display.

        Returns:
            True if user confirms with 'y', False for any other input.

        Example:
            Are you sure you want to continue? (y/N): y
            -> Returns True
        """
        return self.console.input(f"[yellow]{message} (y/N): [/yellow]").lower() == 'y'

    def display_import_summary(self, total_lines: int, success_count: int,
                                duplicate_count: int, errors: list):
        """Display import summary with counts and errors.

        Shows a panel with statistics about the import operation including total
        lines processed, successfully added dates, duplicates skipped, and errors.
        If errors exist, displays a table with line numbers, content, and reasons.
        Shows special messages based on import results.

        Args:
            total_lines: Total number of lines processed from the import file.
            success_count: Number of dry days successfully added.
            duplicate_count: Number of dates that were already recorded (duplicates).
            errors: List of tuples containing (line_number, content, reason) for each error.

        Example:
            📥 Import Summary
            Total lines processed: 10
            ✓ Successfully added: 5
            ℹ Duplicates skipped: 3
            ❌ Errors: 2

            [Error table if errors exist]

            ✓ Import completed successfully!
        """
        text = Text()

        # Display counts
        text.append(f"Total lines processed: {total_lines}\n", style="bold")

        # Success count - green if > 0
        if success_count > 0:
            text.append("✓ ", style="bold green")
            text.append(f"Successfully added: ", style="green")
            text.append(f"{success_count}\n", style="bold #00FF00")
        else:
            text.append(f"Successfully added: {success_count}\n")

        # Duplicates count
        if duplicate_count > 0:
            text.append("ℹ ", style="bold blue")
            text.append(f"Duplicates skipped: ", style="blue")
            text.append(f"{duplicate_count}\n", style="bold blue")
        else:
            text.append(f"Duplicates skipped: {duplicate_count}\n")

        # Errors count
        if errors:
            text.append("❌ ", style="bold red")
            text.append(f"Errors: ", style="red")
            text.append(f"{len(errors)}", style="bold red")
        else:
            text.append(f"Errors: 0")

        panel = Panel(text, title="📥 Import Summary", border_style="green", expand=False)
        self.console.print(panel)

        # Display error table if there are errors
        if errors:
            self.console.print()
            table = Table(title="Import Errors", show_header=True, header_style="bold red")
            table.add_column("Line", style="cyan", justify="right")
            table.add_column("Content", style="yellow")
            table.add_column("Reason", style="red")

            for line_num, content, reason in errors:
                table.add_row(str(line_num), content, reason)

            self.console.print(table)

        # Display success message or special case message
        self.console.print()
        if success_count > 0:
            success_text = Text()
            success_text.append("✓ ", style="bold green")
            success_text.append("Import completed successfully!", style="green")
            self.console.print(success_text)
        elif success_count == 0 and duplicate_count > 0:
            info_text = Text()
            info_text.append("ℹ ", style="bold blue")
            info_text.append("All dates already recorded. No new dry days added.", style="blue")
            self.console.print(info_text)
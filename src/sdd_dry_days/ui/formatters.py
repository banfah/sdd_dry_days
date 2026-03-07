"""Output formatting for SDD Dry Days CLI.

This module provides the OutputFormatter class for displaying colorful, styled
messages in the terminal using the Rich library. It handles success messages,
error messages, confirmations, and range summaries with consistent visual styling.
"""

from datetime import datetime

from rich.console import Console
from rich.panel import Panel
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
            🔥 Current streak: 5 days
        """
        text = Text()
        text.append("✓ ", style="bold green")
        text.append(f"Dry day added: ", style="green")
        text.append(f"{date.strftime('%Y-%m-%d')}", style="bold cyan")

        if streak > 0:
            text.append(f"\n🔥 Current streak: ", style="yellow")
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
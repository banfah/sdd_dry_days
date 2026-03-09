"""View-specific formatting for SDD Dry Days CLI.

This module provides the ViewFormatter class for displaying rich, structured views
of dry day data using the Rich library. It handles list views, week views, month
views, statistics views, and range views with tables, panels, and visual indicators.

The ViewFormatter uses COMPOSITION with OutputFormatter rather than inheritance.
This allows ViewFormatter to add view-specific formatting methods (tables, progress
bars, calendars) while reusing OutputFormatter's basic formatting capabilities
(error panels, success messages) through delegation.

Key responsibilities:
- Format dry day lists with tables and pagination
- Display week views with day-by-day breakdowns
- Display month views with calendar-style layouts
- Display statistics with metrics from multiple periods (30, 60, 90 days)
- Display custom range views with statistics and dry day lists

All output uses Rich library widgets (Panel, Table, Text, Progress) for colorful,
structured terminal presentation. Green (#00FF00) is used for positive metrics
per AC-6.2.
"""

import calendar
from datetime import datetime, timedelta
from typing import Any, Generator, List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table
from rich.text import Text

from ..core.dry_day import DryDay
from ..core.stats import PeriodStats
from .formatters import OutputFormatter


class ViewFormatter:
    """Format and display dry day views using Rich library widgets.

    This class provides specialized formatting methods for different view types
    in the SDD Dry Days application. It uses composition to leverage OutputFormatter
    for basic formatting operations while adding view-specific capabilities.

    The ViewFormatter does NOT inherit from OutputFormatter. Instead, it accepts
    an OutputFormatter instance as a dependency and delegates to it when needed
    for error messages, success messages, or other basic formatting operations.
    This composition pattern provides better separation of concerns: OutputFormatter
    handles simple messages, while ViewFormatter handles complex structured views.

    Attributes:
        console: Rich Console instance for output rendering.
        output_formatter: OutputFormatter instance for basic formatting operations.

    Example:
        >>> console = Console()
        >>> output_formatter = OutputFormatter()
        >>> view_formatter = ViewFormatter(console, output_formatter)
        >>> view_formatter.display_list_view(dry_days, current_streak=5)
    """

    def __init__(self, console: Console, output_formatter: OutputFormatter):
        """Initialize the ViewFormatter with dependencies.

        Args:
            console: Rich Console instance for rendering output.
            output_formatter: OutputFormatter instance for delegating basic
                            formatting operations (errors, success messages).
        """
        self.console = console
        self.output_formatter = output_formatter

    def _paginate_output(
        self,
        items: List[Any],
        page_size: int = 50
    ) -> Generator[List[Any], None, None]:
        """Paginate a list of items into pages.

        Args:
            items: List of items to paginate.
            page_size: Number of items per page. Defaults to 50.

        Yields:
            List of items for each page.
        """
        for i in range(0, len(items), page_size):
            yield items[i:i + page_size]

    def display_list_view(
        self,
        dry_days: List[DryDay],
        current_streak: int,
        page_size: int = 50
    ):
        """Display list view of dry days with pagination.

        Shows a table of dry days sorted by date (most recent first) with columns
        for date, note, and status. Includes current streak at the top and supports
        pagination for large datasets.

        Args:
            dry_days: List of DryDay instances to display.
            current_streak: Current consecutive dry day streak.
            page_size: Number of entries to display per page. Defaults to 50.
        """
        total_entries = len(dry_days)

        # Display header panel with summary information
        header_text = f"Total Dry Days: [green bold]{total_entries}[/green bold]\n"
        header_text += f"Current Streak: 🔥 [green bold]{current_streak}[/green bold] days"

        header_panel = Panel(
            header_text,
            title="📊 Dry Days Summary",
            border_style="green",
            padding=(1, 2)
        )
        self.console.print(header_panel)
        self.console.print()  # Add spacing

        # Handle pagination if needed
        if total_entries > page_size:
            # Paginate and display
            for page_num, page_items in enumerate(self._paginate_output(dry_days, page_size)):
                self._display_page(page_items)

                # Show prompt for more (except on last page)
                if (page_num + 1) * page_size < total_entries:
                    try:
                        input("\n[Press ENTER for more, Ctrl+C to stop]")
                    except KeyboardInterrupt:
                        self.console.print("\n[yellow]Display stopped by user[/yellow]")
                        break
        else:
            # Display all at once
            self._display_page(dry_days)

    def _display_page(self, page_items: List[DryDay]):
        """Display a single page of dry days as a Rich Table.

        Args:
            page_items: List of DryDay instances to display on this page.
        """
        # Create Rich Table
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Date", justify="left", style="cyan")
        table.add_column("Status", justify="center", style="")
        table.add_column("Notes", justify="left", style="dim")

        # Add rows for each dry day
        for dd in page_items:
            # Format date as ISO 8601
            date_str = dd.date.strftime('%Y-%m-%d')

            # Format status with symbols and colors
            if dd.is_planned:
                status = "[yellow]✓(P)[/yellow]"
            else:
                status = "[green]✓[/green]"

            # Handle empty notes gracefully
            note_str = dd.note if dd.note else "-"

            table.add_row(date_str, status, note_str)

        self.console.print(table)

    def display_week_view(
        self,
        stats: PeriodStats,
        week_days: List[Tuple[str, datetime, bool, Optional[str]]]
    ):
        """Display week view with day-by-day breakdown (Monday-Sunday).

        Shows a week summary with statistics and a day-by-day breakdown indicating
        which days were dry, which were not, and any notes. The week_days parameter
        provides detailed information for each day of the week.

        Args:
            stats: PeriodStats instance for the week period.
            week_days: List of tuples containing day information:
                      (day_name, date, is_dry, note) for each day in the week.
        """
        # Determine week range from week_days
        if not week_days:
            # Handle empty week_days gracefully
            self.console.print("[yellow]No data available for week view[/yellow]")
            return

        first_date = week_days[0][1]
        last_date = week_days[-1][1]

        # Format week range: "Week of March 3-9, 2026"
        if first_date.month == last_date.month:
            # Same month
            week_range = f"Week of {first_date.strftime('%B')} {first_date.day}-{last_date.day}, {first_date.year}"
        else:
            # Different months
            week_range = f"Week of {first_date.strftime('%B')} {first_date.day} - {last_date.strftime('%B')} {last_date.day}, {first_date.year}"

        # Create header text with progress information
        header_text = f"{week_range}\n"
        header_text += f"Progress: [green bold]{stats.dry_days}/7 days ({stats.percentage}%)[/green bold]\n"

        # Add progress bar using create_progress_bar
        header_text += self.create_progress_bar(stats.percentage)

        # Create header panel
        header_panel = Panel(
            header_text,
            title="Week View",
            border_style="green",
            padding=(1, 2),
            expand=True  # Align with table width below
        )
        self.console.print(header_panel)
        self.console.print()  # Add spacing

        # Create Rich Table for day-by-day breakdown
        table = Table(show_header=True, header_style="bold cyan", expand=True)
        table.add_column("Day", justify="left", style="cyan")
        table.add_column("Date", justify="left", style="")
        table.add_column("Status", justify="center", style="")
        table.add_column("Notes", justify="left", style="dim")

        # Add rows for each day in the week
        for day_name, date, is_dry, note in week_days:
            # Format date as ISO 8601 (YYYY-MM-DD)
            date_str = date.strftime('%Y-%m-%d')

            # Format status with symbols and colors
            if is_dry:
                status = "[green]✓[/green]"
            else:
                status = "[red]-[/red]"

            # Handle notes: truncate to 20 characters if longer
            if note:
                note_str = note if len(note) <= 20 else note[:20] + "..."
            else:
                note_str = "-"

            table.add_row(day_name, date_str, status, note_str)

        # Display table
        self.console.print(table)

    def _create_calendar_grid(self, stats: PeriodStats) -> str:
        """Create a calendar grid string for the given month.

        Generates a 6x7 grid (weeks x days) representing a month calendar with
        day numbers, status indicators (✓ for dry, - for not dry), and today
        marker (*). Days outside the current month are left blank.

        Args:
            stats: PeriodStats instance for the month period.

        Returns:
            Formatted calendar grid as a string with Rich markup.
        """
        # Get first and last day of month
        first_day = stats.start_date
        last_day = stats.end_date

        # Get day of week for first day (0=Monday, 6=Sunday)
        first_weekday = first_day.weekday()

        # Get today's date for highlighting
        today = datetime.now().date()

        # Convert dry day dates to a set for fast lookup
        dry_day_dates_set = {d.date() for d in stats.dry_day_dates}

        # Build grid header (day names)
        header = "Mon  Tue  Wed  Thu  Fri  Sat  Sun\n"

        # Build grid (list of lists, 6 rows × 7 columns)
        grid_lines = []
        current_date = first_day - timedelta(days=first_weekday)  # Start from Monday before 1st

        for week in range(6):  # Max 6 weeks in a month
            week_cells = []
            for day in range(7):  # 7 days per week
                if current_date.month == first_day.month:
                    day_num = current_date.day
                    is_dry = current_date.date() in dry_day_dates_set
                    is_today = current_date.date() == today

                    # Format cell: "DD✓*" or "DD-" with Rich markup
                    # Use 5 characters per cell for alignment (including spaces)
                    if is_dry:
                        status = "[green]✓[/green]"
                    else:
                        status = "[red]-[/red]"

                    if is_today:
                        # Bold the day number and add asterisk
                        cell = f"[bold]{day_num:2d}{status}*[/bold]"
                    else:
                        cell = f"{day_num:2d}{status} "

                    week_cells.append(cell)
                else:
                    # Day outside current month - empty cell
                    week_cells.append("     ")

                current_date += timedelta(days=1)

            # Join cells with space separator
            grid_lines.append(" ".join(week_cells))

        # Combine header and grid
        return header + "\n".join(grid_lines)

    def display_month_view(self, stats: PeriodStats):
        """Display month view with calendar-style layout.

        Shows a month summary with statistics and a calendar-style grid displaying
        which days were dry, which were not, and highlighting the current day.
        The layout follows standard calendar conventions (weeks as rows, days as columns).

        Args:
            stats: PeriodStats instance for the month period.
        """
        # Get month name from start date
        month_name = stats.start_date.strftime('%B %Y')

        # Calculate total days in month
        total_days = (stats.end_date - stats.start_date).days + 1

        # Create header text with progress information
        header_text = f"{month_name}\n"
        header_text += f"Progress: [green bold]{stats.dry_days}/{total_days} days ({stats.percentage}%)[/green bold]\n"

        # Add progress bar using create_progress_bar
        header_text += self.create_progress_bar(stats.percentage)

        # Create header panel
        header_panel = Panel(
            header_text,
            title="📅 Month View",
            border_style="green",
            padding=(1, 2)
        )
        self.console.print(header_panel)
        self.console.print()  # Add spacing

        # Create and display calendar grid
        calendar_grid = self._create_calendar_grid(stats)
        calendar_panel = Panel(
            calendar_grid,
            title="Calendar",
            border_style="cyan",
            padding=(1, 2)
        )
        self.console.print(calendar_panel)
        self.console.print()  # Add spacing

        # Display legend
        legend_text = "[green]✓[/green]=Dry  [red]-[/red]=Not Dry  [bold]*[/bold]=Today"
        legend_panel = Panel(
            legend_text,
            title="Legend",
            border_style="dim",
            padding=(0, 2)
        )
        self.console.print(legend_panel)
        self.console.print()  # Add spacing

        # Display current streak with fire emoji
        streak_text = f"Current Streak: 🔥 [green bold]{stats.current_streak}[/green bold] days"
        if stats.longest_streak > 0:
            streak_text += f"\nLongest Streak: 🔥 [green bold]{stats.longest_streak}[/green bold] days"

        streak_panel = Panel(
            streak_text,
            title="Streaks",
            border_style="yellow",
            padding=(1, 2)
        )
        self.console.print(streak_panel)

    def display_stats_view(
        self,
        stats_30: PeriodStats,
        stats_60: PeriodStats,
        stats_90: PeriodStats,
        stats_120: PeriodStats,
        stats_150: PeriodStats,
        stats_180: PeriodStats,
        current_streak: int
    ):
        """Display statistics view with metrics from 30, 60, 90, 120, 150 and 180-day periods.

        Shows comprehensive statistics including dry day counts, percentages,
        longest streaks, and current streak across three time periods. Uses tables
        and visual indicators to present the data clearly.

        Args:
            stats_30: PeriodStats instance for the 30-day period.
            stats_60: PeriodStats instance for the 60-day period.
            stats_90: PeriodStats instance for the 90-day period.
            stats_120: PeriodStats instance for the 120-day period.
            stats_150: PeriodStats instance for the 150-day period.
            stats_180: PeriodStats instance for the 180-day period.
            current_streak: Current consecutive dry day streak.
        """
        # Create header panel with current streak
        header_text = f"Current Streak: [green bold]{current_streak}[/green bold] days"
        header_panel = Panel(
            header_text,
            title="Statistics Overview",
            border_style="green",
            padding=(1, 2),
            expand=True  # Align with table width below
        )
        self.console.print(header_panel)
        self.console.print()  # Add spacing

        # Create Rich Table with columns
        table = Table(show_header=True, header_style="bold cyan", expand=True)
        table.add_column("Period", justify="right", style="cyan")
        table.add_column("Dry Days", justify="center", style="")
        table.add_column("Total Days", justify="center", style="")
        table.add_column("Progress", justify="left", style="")
        table.add_column("Longest Streak", justify="center", style="")

        # Add rows for each period (30d, 60d, 90d, 120d, 150d, 180d)
        for period_name, stats in [("30d", stats_30), ("60d", stats_60), ("90d", stats_90), ("120d", stats_120), ("150d", stats_150), ("180d", stats_180)]:
            # Check for limited data and format period display
            if stats.available_days < stats.requested_days:
                period_display = f"{period_name} [dim](limited data: {stats.available_days}/{stats.requested_days} days)[/dim]"
            else:
                period_display = period_name

            # Format dry days count
            dry_days_str = str(stats.dry_days_count)

            # Format total days (available_days, not requested_days)
            total_days_str = str(stats.available_days)

            # Use create_progress_bar for visual progress display
            progress_display = self.create_progress_bar(stats.percentage)

            # Format longest streak
            if stats.longest_streak > 0:
                longest_streak_str = f"{stats.longest_streak} days"
            else:
                longest_streak_str = "-"

            # Add row to table
            table.add_row(
                period_display,
                dry_days_str,
                total_days_str,
                progress_display,
                longest_streak_str
            )

        # Display table
        self.console.print(table)

    def create_progress_bar(self, percentage: float) -> str:
        """Create progress bar with text percentage (AC-9.2).

        Generates a visual progress bar using Unicode box characters with
        color-coded styling based on percentage. The bar is 20 characters wide
        and always includes the percentage as text for accessibility.

        Color coding:
        - Red: < 50%
        - Yellow: 50-75%
        - Green: > 75%

        Args:
            percentage: Progress percentage (0-100).

        Returns:
            Formatted progress bar string with Rich markup and percentage text.

        Example:
            >>> formatter.create_progress_bar(75.0)
            '[yellow]▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░[/yellow] 75%'
        """
        # Calculate filled and empty portions (20 char width)
        filled = int(percentage / 100 * 20)
        empty = 20 - filled

        # Choose color based on percentage
        if percentage < 50:
            color = "red"
        elif percentage < 75:
            color = "yellow"
        else:
            color = "green"

        # Use Unicode box characters: ▓ (filled), ░ (empty)
        bar = "▓" * filled + "░" * empty

        # CRITICAL: Always show percentage as text (AC-9.2)
        return f"[{color}]{bar}[/{color}] {percentage:.0f}%"

    def display_range_view(self, stats: PeriodStats, dry_days: List[DryDay]):
        """Display custom range view with statistics and dry day list.

        Shows statistics for a custom date range along with a list of dry days
        within that range. Combines statistical summary with detailed day-by-day
        information.

        Args:
            stats: PeriodStats instance for the custom date range.
            dry_days: List of DryDay instances within the date range.
        """
        # Format date range: "Range: March 1-10, 2026" or "Range: March 30 - April 5, 2026"
        start_date = stats.start_date
        end_date = stats.end_date

        if start_date.month == end_date.month:
            # Same month
            range_str = f"Range: {start_date.strftime('%B')} {start_date.day}-{end_date.day}, {start_date.year}"
        else:
            # Different months (handle cross-month ranges)
            range_str = f"Range: {start_date.strftime('%B')} {start_date.day} - {end_date.strftime('%B')} {end_date.day}, {start_date.year}"

        # Calculate total days in range
        total_days = (end_date - start_date).days + 1

        # Create header text with progress information
        header_text = f"{range_str}\n"
        header_text += f"Progress: [green bold]{stats.dry_days_count}/{total_days} days ({stats.percentage}%)[/green bold]\n"

        # Add progress bar using create_progress_bar
        header_text += self.create_progress_bar(stats.percentage)

        # Add longest streak if present
        if stats.longest_streak > 0:
            header_text += f"\nLongest Streak: [green bold]{stats.longest_streak}[/green bold] days"

        # Create header panel
        header_panel = Panel(
            header_text,
            title="Range View",
            border_style="green",
            padding=(1, 2),
            expand=True  # Align with table width below
        )
        self.console.print(header_panel)
        self.console.print()  # Add spacing

        # Create Rich Table for day-by-day breakdown
        table = Table(show_header=True, header_style="bold cyan", expand=True)
        table.add_column("Date", justify="left", style="cyan")
        table.add_column("Status", justify="center", style="")
        table.add_column("Notes", justify="left", style="dim")

        # Sort dry_days by date
        sorted_dry_days = sorted(dry_days, key=lambda d: d.date)

        # Convert to set for fast lookup
        dry_day_dates_set = {d.date.date() for d in sorted_dry_days}

        # Iterate through all dates in range
        current_date = start_date
        while current_date <= end_date:
            # Format date as ISO 8601 (YYYY-MM-DD)
            date_str = current_date.strftime('%Y-%m-%d')

            # Check if this date is a dry day
            is_dry = current_date.date() in dry_day_dates_set

            # Format status with symbols and colors
            if is_dry:
                status = "[green]✓[/green]"
                # Find the DryDay instance for notes
                dry_day = next((d for d in sorted_dry_days if d.date.date() == current_date.date()), None)
                if dry_day and dry_day.note:
                    note_str = dry_day.note if len(dry_day.note) <= 20 else dry_day.note[:20] + "..."
                else:
                    note_str = "-"
            else:
                status = "[red]-[/red]"
                note_str = "-"

            table.add_row(date_str, status, note_str)

            # Move to next day
            current_date += timedelta(days=1)

        # Display table
        self.console.print(table)
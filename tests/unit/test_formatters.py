"""Unit tests for OutputFormatter.

This module tests the output formatting functionality including:
- Success message formatting with and without streak
- Already exists message formatting
- Range summary formatting with conditional skipped display
- Error message formatting with and without details
- Confirmation prompt with different user inputs

The tests use mocked Rich Console to verify formatting logic without
actual terminal rendering.
"""

from datetime import datetime
from unittest.mock import Mock, patch
import pytest

from sdd_dry_days.ui.formatters import OutputFormatter
from rich.panel import Panel
from rich.text import Text


class TestSuccessMessage:
    """Tests for success message formatting."""

    def test_success_message_without_streak_displays_date_only(self):
        """Test success message displays date without streak when streak is 0."""
        formatter = OutputFormatter()
        formatter.console = Mock()

        date = datetime(2026, 3, 7, 14, 30, 0)
        formatter.success("Added", date, streak=0)

        # Verify console.print was called once
        formatter.console.print.assert_called_once()

        # Get the Panel that was printed
        call_args = formatter.console.print.call_args
        panel = call_args[0][0]

        # Verify it's a Panel with correct border style
        assert isinstance(panel, Panel)
        assert panel.border_style == "green"
        assert panel.expand is False

        # Verify text content
        renderable = panel.renderable
        assert isinstance(renderable, Text)
        text_str = renderable.plain
        assert "✓" in text_str
        assert "Dry day added:" in text_str
        assert "2026-03-07" in text_str
        assert "streak" not in text_str.lower()

    def test_success_message_with_streak_displays_date_and_streak(self):
        """Test success message displays both date and streak when streak > 0."""
        formatter = OutputFormatter()
        formatter.console = Mock()

        date = datetime(2026, 3, 7)
        formatter.success("Added", date, streak=5)

        # Verify console.print was called once
        formatter.console.print.assert_called_once()

        # Get the Panel that was printed
        call_args = formatter.console.print.call_args
        panel = call_args[0][0]

        # Verify panel properties
        assert isinstance(panel, Panel)
        assert panel.border_style == "green"

        # Verify text content includes date and streak
        renderable = panel.renderable
        text_str = renderable.plain
        assert "✓" in text_str
        assert "Dry day added:" in text_str
        assert "2026-03-07" in text_str
        assert "🔥" in text_str
        assert "Current streak:" in text_str
        assert "5 days" in text_str

    def test_success_message_with_streak_of_one_uses_singular_day(self):
        """Test success message uses singular 'day' when streak is 1."""
        formatter = OutputFormatter()
        formatter.console = Mock()

        date = datetime(2026, 3, 7)
        formatter.success("Added", date, streak=1)

        # Get the Panel that was printed
        call_args = formatter.console.print.call_args
        panel = call_args[0][0]

        # Verify text uses singular form
        renderable = panel.renderable
        text_str = renderable.plain
        assert "1 day" in text_str
        assert "1 days" not in text_str

    def test_success_message_formats_date_as_iso(self):
        """Test success message formats date in ISO format (YYYY-MM-DD)."""
        formatter = OutputFormatter()
        formatter.console = Mock()

        date = datetime(2026, 12, 25, 10, 15, 30)
        formatter.success("Added", date)

        # Get the Panel that was printed
        call_args = formatter.console.print.call_args
        panel = call_args[0][0]

        # Verify ISO date format
        renderable = panel.renderable
        text_str = renderable.plain
        assert "2026-12-25" in text_str


class TestAlreadyExistsMessage:
    """Tests for already exists message formatting."""

    def test_already_exists_message_displays_blue_panel_with_date(self):
        """Test already exists message displays blue info panel with date."""
        formatter = OutputFormatter()
        formatter.console = Mock()

        date = datetime(2026, 3, 7)
        formatter.already_exists(date)

        # Verify console.print was called once
        formatter.console.print.assert_called_once()

        # Get the Panel that was printed
        call_args = formatter.console.print.call_args
        panel = call_args[0][0]

        # Verify it's a Panel with blue border style
        assert isinstance(panel, Panel)
        assert panel.border_style == "blue"
        assert panel.expand is False

        # Verify text content
        renderable = panel.renderable
        assert isinstance(renderable, Text)
        text_str = renderable.plain
        assert "ℹ" in text_str
        assert "Dry day already recorded for" in text_str
        assert "2026-03-07" in text_str

    def test_already_exists_message_formats_date_as_iso(self):
        """Test already exists message formats date in ISO format (YYYY-MM-DD)."""
        formatter = OutputFormatter()
        formatter.console = Mock()

        date = datetime(2026, 1, 5, 8, 45, 0)
        formatter.already_exists(date)

        # Get the Panel that was printed
        call_args = formatter.console.print.call_args
        panel = call_args[0][0]

        # Verify ISO date format
        renderable = panel.renderable
        text_str = renderable.plain
        assert "2026-01-05" in text_str


class TestRangeSummaryMessage:
    """Tests for range summary message formatting."""

    def test_range_summary_without_skipped_displays_counts_only(self):
        """Test range summary displays counts without skipped when skipped is 0."""
        formatter = OutputFormatter()
        formatter.console = Mock()

        formatter.range_summary(added=5, skipped=0, total=5)

        # Verify console.print was called once
        formatter.console.print.assert_called_once()

        # Get the Panel that was printed
        call_args = formatter.console.print.call_args
        panel = call_args[0][0]

        # Verify it's a Panel with green border style
        assert isinstance(panel, Panel)
        assert panel.border_style == "green"
        assert panel.expand is False

        # Verify text content
        renderable = panel.renderable
        assert isinstance(renderable, Text)
        text_str = renderable.plain
        assert "✓" in text_str
        assert "Added 5/5 dry days" in text_str
        assert "already existed" not in text_str

    def test_range_summary_with_skipped_displays_skipped_count(self):
        """Test range summary displays skipped count when skipped > 0."""
        formatter = OutputFormatter()
        formatter.console = Mock()

        formatter.range_summary(added=3, skipped=2, total=5)

        # Get the Panel that was printed
        call_args = formatter.console.print.call_args
        panel = call_args[0][0]

        # Verify panel properties
        assert isinstance(panel, Panel)
        assert panel.border_style == "green"

        # Verify text content includes both added and skipped
        renderable = panel.renderable
        text_str = renderable.plain
        assert "✓" in text_str
        assert "Added 3/5 dry days" in text_str
        assert "ℹ" in text_str
        assert "2 already existed" in text_str

    def test_range_summary_with_all_skipped_shows_zero_added(self):
        """Test range summary when all dates already existed (added=0)."""
        formatter = OutputFormatter()
        formatter.console = Mock()

        formatter.range_summary(added=0, skipped=5, total=5)

        # Get the Panel that was printed
        call_args = formatter.console.print.call_args
        panel = call_args[0][0]

        # Verify text content
        renderable = panel.renderable
        text_str = renderable.plain
        assert "Added 0/5 dry days" in text_str
        assert "5 already existed" in text_str

    def test_range_summary_displays_correct_ratio(self):
        """Test range summary displays correct added/total ratio."""
        formatter = OutputFormatter()
        formatter.console = Mock()

        formatter.range_summary(added=7, skipped=3, total=10)

        # Get the Panel that was printed
        call_args = formatter.console.print.call_args
        panel = call_args[0][0]

        # Verify text content
        renderable = panel.renderable
        text_str = renderable.plain
        assert "Added 7/10 dry days" in text_str


class TestErrorMessage:
    """Tests for error message formatting."""

    def test_error_message_without_details_displays_message_only(self):
        """Test error message displays message without details when details is empty."""
        formatter = OutputFormatter()
        formatter.console = Mock()

        formatter.error("Invalid date format")

        # Verify console.print was called once
        formatter.console.print.assert_called_once()

        # Get the Panel that was printed
        call_args = formatter.console.print.call_args
        panel = call_args[0][0]

        # Verify it's a Panel with red border style
        assert isinstance(panel, Panel)
        assert panel.border_style == "red"
        assert panel.expand is False

        # Verify text content
        renderable = panel.renderable
        assert isinstance(renderable, Text)
        text_str = renderable.plain
        assert "✗" in text_str
        assert "Invalid date format" in text_str

    def test_error_message_with_details_displays_both_message_and_details(self):
        """Test error message displays both message and details when details provided."""
        formatter = OutputFormatter()
        formatter.console = Mock()

        formatter.error("Invalid date format", details="Please use YYYY-MM-DD format")

        # Get the Panel that was printed
        call_args = formatter.console.print.call_args
        panel = call_args[0][0]

        # Verify panel properties
        assert isinstance(panel, Panel)
        assert panel.border_style == "red"

        # Verify text content includes both message and details
        renderable = panel.renderable
        text_str = renderable.plain
        assert "✗" in text_str
        assert "Invalid date format" in text_str
        assert "Please use YYYY-MM-DD format" in text_str

    def test_error_message_with_empty_string_details_displays_message_only(self):
        """Test error message with empty string details behaves same as no details."""
        formatter = OutputFormatter()
        formatter.console = Mock()

        formatter.error("Error occurred", details="")

        # Get the Panel that was printed
        call_args = formatter.console.print.call_args
        panel = call_args[0][0]

        # Verify text content doesn't have extra line
        renderable = panel.renderable
        text_str = renderable.plain
        assert "✗" in text_str
        assert "Error occurred" in text_str
        # Should not have newline followed by nothing
        lines = text_str.strip().split('\n')
        assert len(lines) == 1


class TestConfirmPrompt:
    """Tests for confirmation prompt."""

    def test_confirm_returns_true_for_lowercase_y(self):
        """Test confirm returns True when user inputs lowercase 'y'."""
        formatter = OutputFormatter()
        formatter.console = Mock()
        formatter.console.input.return_value = 'y'

        result = formatter.confirm("Are you sure?")

        # Verify console.input was called with correct prompt
        formatter.console.input.assert_called_once()
        call_args = formatter.console.input.call_args
        prompt = call_args[0][0]
        assert "Are you sure?" in prompt
        assert "(y/N)" in prompt
        assert "[yellow]" in prompt

        # Verify return value
        assert result is True

    def test_confirm_returns_true_for_uppercase_y(self):
        """Test confirm returns True when user inputs uppercase 'Y'."""
        formatter = OutputFormatter()
        formatter.console = Mock()
        formatter.console.input.return_value = 'Y'

        result = formatter.confirm("Continue?")

        # Verify return value (case-insensitive)
        assert result is True

    def test_confirm_returns_false_for_n(self):
        """Test confirm returns False when user inputs 'n'."""
        formatter = OutputFormatter()
        formatter.console = Mock()
        formatter.console.input.return_value = 'n'

        result = formatter.confirm("Proceed?")

        # Verify return value
        assert result is False

    def test_confirm_returns_false_for_empty_input(self):
        """Test confirm returns False when user presses Enter (empty input)."""
        formatter = OutputFormatter()
        formatter.console = Mock()
        formatter.console.input.return_value = ''

        result = formatter.confirm("Delete all?")

        # Verify return value
        assert result is False

    def test_confirm_returns_false_for_arbitrary_input(self):
        """Test confirm returns False for any input other than 'y'."""
        formatter = OutputFormatter()
        formatter.console = Mock()

        test_inputs = ['no', 'yes', 'N', '1', 'maybe', 'x']

        for test_input in test_inputs:
            formatter.console.input.return_value = test_input
            result = formatter.confirm("Test?")
            assert result is False, f"Expected False for input '{test_input}'"

    def test_confirm_formats_prompt_correctly(self):
        """Test confirm formats the prompt with yellow styling and (y/N) suffix."""
        formatter = OutputFormatter()
        formatter.console = Mock()
        formatter.console.input.return_value = 'n'

        message = "Do you want to continue?"
        formatter.confirm(message)

        # Verify the prompt format
        call_args = formatter.console.input.call_args
        prompt = call_args[0][0]
        assert prompt == "[yellow]Do you want to continue? (y/N): [/yellow]"


class TestOutputFormatterInitialization:
    """Tests for OutputFormatter initialization."""

    def test_outputformatter_initializes_with_console(self):
        """Test OutputFormatter initializes with a Rich Console instance."""
        formatter = OutputFormatter()

        # Verify console attribute exists and is a Console
        assert hasattr(formatter, 'console')
        from rich.console import Console
        assert isinstance(formatter.console, Console)
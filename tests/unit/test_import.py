"""Unit tests for import command handler.

This module tests the import functionality including:
- File validation and error handling
- Empty line and comment skipping
- Date parsing integration
- Duplicate detection and counting
- Summary display coordination

The tests use mocking to isolate the CLI import handler from external dependencies
like filesystem operations, storage, and UI formatting.
"""

from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, mock_open
import pytest

from sdd_dry_days.cli import CLI
from sdd_dry_days.utils.date_parser import DateParseError


class TestImportFileOperations:
    """Tests for import handler file operations and validation."""

    def test_import_with_file_not_found_displays_error(self):
        """Test that importing non-existent file displays appropriate error."""
        # Setup
        cli = CLI()
        cli.formatter = Mock()

        # Create args with non-existent file
        args = Mock()
        args.filepath = "/path/to/nonexistent.txt"

        # Mock Path.exists() to return False
        with patch('sdd_dry_days.cli.Path') as mock_path_class:
            mock_path = MagicMock()
            mock_path.exists.return_value = False
            mock_path_class.return_value = mock_path

            # Execute
            cli._handle_import(args)

        # Verify error was displayed
        cli.formatter.error.assert_called_once()
        error_call = cli.formatter.error.call_args
        assert "File not found" in error_call[0][0]
        assert args.filepath in error_call[0][0]
        assert "check the path" in error_call[0][1].lower()

    def test_import_with_permission_error_displays_error(self):
        """Test that permission denied displays appropriate error."""
        # Setup
        cli = CLI()
        cli.formatter = Mock()

        args = Mock()
        args.filepath = "/path/to/restricted.txt"

        # Mock file operations to raise PermissionError
        with patch('sdd_dry_days.cli.Path') as mock_path_class:
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            mock_path_class.return_value = mock_path

            with patch('builtins.open', side_effect=PermissionError("Access denied")):
                # Execute
                cli._handle_import(args)

        # Verify error was displayed
        cli.formatter.error.assert_called_once()
        error_call = cli.formatter.error.call_args
        assert "Cannot read file" in error_call[0][0]
        assert args.filepath in error_call[0][0]
        assert "permission" in error_call[0][1].lower()

    def test_import_with_empty_file_displays_error(self):
        """Test that importing empty file displays appropriate error."""
        # Setup
        cli = CLI()
        cli.formatter = Mock()

        args = Mock()
        args.filepath = "/path/to/empty.txt"

        # Mock file operations to return empty content
        with patch('sdd_dry_days.cli.Path') as mock_path_class:
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            mock_path_class.return_value = mock_path

            with patch('builtins.open', mock_open(read_data="")):
                # Execute
                cli._handle_import(args)

        # Verify error was displayed
        cli.formatter.error.assert_called_once()
        error_call = cli.formatter.error.call_args
        assert "File is empty" in error_call[0][0]
        assert "Add dates" in error_call[0][1]

    def test_import_skips_empty_lines(self):
        """Test that empty lines are skipped during import."""
        # Setup
        cli = CLI()
        cli.formatter = Mock()
        cli.storage = Mock()
        cli.storage.add_dry_day.return_value = True

        args = Mock()
        args.filepath = "/path/to/file.txt"

        # File content with empty lines
        file_content = "2026-03-01\n\n2026-03-02\n   \n2026-03-03\n"

        with patch('sdd_dry_days.cli.Path') as mock_path_class:
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            mock_path_class.return_value = mock_path

            with patch('builtins.open', mock_open(read_data=file_content)):
                # Execute
                cli._handle_import(args)

        # Verify display_import_summary was called with correct count
        cli.formatter.display_import_summary.assert_called_once()
        summary_call = cli.formatter.display_import_summary.call_args
        total_lines = summary_call[0][0]
        success_count = summary_call[0][1]

        # Should process 3 lines (skip 2 empty lines)
        assert total_lines == 3
        assert success_count == 3

    def test_import_skips_comment_lines(self):
        """Test that comment lines (starting with #) are skipped."""
        # Setup
        cli = CLI()
        cli.formatter = Mock()
        cli.storage = Mock()
        cli.storage.add_dry_day.return_value = True

        args = Mock()
        args.filepath = "/path/to/file.txt"

        # File content with comments
        file_content = """# This is a comment
2026-03-01
# Another comment
2026-03-02
#Comment without space
2026-03-03
"""

        with patch('sdd_dry_days.cli.Path') as mock_path_class:
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            mock_path_class.return_value = mock_path

            with patch('builtins.open', mock_open(read_data=file_content)):
                # Execute
                cli._handle_import(args)

        # Verify display_import_summary was called with correct count
        cli.formatter.display_import_summary.assert_called_once()
        summary_call = cli.formatter.display_import_summary.call_args
        total_lines = summary_call[0][0]
        success_count = summary_call[0][1]

        # Should process 3 lines (skip 3 comment lines)
        assert total_lines == 3
        assert success_count == 3


class TestImportDateParsing:
    """Tests for import handler date parsing integration."""

    def test_import_parses_iso_format_dates(self):
        """Test that ISO format dates (YYYY-MM-DD) are parsed correctly."""
        # Setup
        cli = CLI()
        cli.formatter = Mock()
        cli.storage = Mock()
        cli.storage.add_dry_day.return_value = True

        args = Mock()
        args.filepath = "/path/to/file.txt"

        # File content with ISO format dates
        file_content = """2026-03-01
2026-03-02
2026-03-03
"""

        with patch('sdd_dry_days.cli.Path') as mock_path_class:
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            mock_path_class.return_value = mock_path

            with patch('builtins.open', mock_open(read_data=file_content)):
                # Execute
                cli._handle_import(args)

        # Verify all dates were successfully parsed and added
        assert cli.storage.add_dry_day.call_count == 3
        cli.formatter.display_import_summary.assert_called_once()
        summary_call = cli.formatter.display_import_summary.call_args
        success_count = summary_call[0][1]
        errors = summary_call[0][3]

        assert success_count == 3
        assert len(errors) == 0

    def test_import_parses_us_format_dates(self):
        """Test that US format dates (MM/DD/YYYY) are parsed correctly."""
        # Setup
        cli = CLI()
        cli.formatter = Mock()
        cli.storage = Mock()
        cli.storage.add_dry_day.return_value = True

        args = Mock()
        args.filepath = "/path/to/file.txt"

        # File content with US format dates
        file_content = """03/01/2026
03/02/2026
03/03/2026
"""

        with patch('sdd_dry_days.cli.Path') as mock_path_class:
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            mock_path_class.return_value = mock_path

            with patch('builtins.open', mock_open(read_data=file_content)):
                # Execute
                cli._handle_import(args)

        # Verify all dates were successfully parsed and added
        assert cli.storage.add_dry_day.call_count == 3
        cli.formatter.display_import_summary.assert_called_once()
        summary_call = cli.formatter.display_import_summary.call_args
        success_count = summary_call[0][1]
        errors = summary_call[0][3]

        assert success_count == 3
        assert len(errors) == 0

    def test_import_parses_mixed_formats(self):
        """Test that mixed date formats in same file are parsed correctly."""
        # Setup
        cli = CLI()
        cli.formatter = Mock()
        cli.storage = Mock()
        cli.storage.add_dry_day.return_value = True

        args = Mock()
        args.filepath = "/path/to/file.txt"

        # File content with mixed formats (ISO, US, EU, compact)
        file_content = """2026-03-01
03/02/2026
03/03/2026
20260304
"""

        with patch('sdd_dry_days.cli.Path') as mock_path_class:
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            mock_path_class.return_value = mock_path

            with patch('builtins.open', mock_open(read_data=file_content)):
                # Execute
                cli._handle_import(args)

        # Verify all dates were successfully parsed and added
        assert cli.storage.add_dry_day.call_count == 4
        cli.formatter.display_import_summary.assert_called_once()
        summary_call = cli.formatter.display_import_summary.call_args
        success_count = summary_call[0][1]
        errors = summary_call[0][3]

        assert success_count == 4
        assert len(errors) == 0

    def test_import_logs_error_for_invalid_date_format(self):
        """Test that invalid date formats are logged as errors."""
        # Setup
        cli = CLI()
        cli.formatter = Mock()
        cli.storage = Mock()
        cli.storage.add_dry_day.return_value = True

        args = Mock()
        args.filepath = "/path/to/file.txt"

        # File content with one valid and one invalid date
        file_content = """2026-03-01
not-a-date
2026-03-03
"""

        with patch('sdd_dry_days.cli.Path') as mock_path_class:
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            mock_path_class.return_value = mock_path

            with patch('builtins.open', mock_open(read_data=file_content)):
                # Execute
                cli._handle_import(args)

        # Verify: 2 successful, 1 error
        assert cli.storage.add_dry_day.call_count == 2
        cli.formatter.display_import_summary.assert_called_once()
        summary_call = cli.formatter.display_import_summary.call_args
        total_lines = summary_call[0][0]
        success_count = summary_call[0][1]
        errors = summary_call[0][3]

        assert total_lines == 3  # All non-empty lines counted
        assert success_count == 2
        assert len(errors) == 1

        # Verify error contains line number, content, and reason
        error_line_num, error_content, error_reason = errors[0]
        assert error_line_num == 2
        assert error_content == "not-a-date"
        assert len(error_reason) > 0

    def test_import_continues_processing_after_parse_error(self):
        """Test that processing continues after encountering parse errors."""
        # Setup
        cli = CLI()
        cli.formatter = Mock()
        cli.storage = Mock()
        cli.storage.add_dry_day.return_value = True

        args = Mock()
        args.filepath = "/path/to/file.txt"

        # File content with multiple errors interspersed with valid dates
        file_content = """2026-03-01
invalid1
2026-03-02
invalid2
2026-03-03
invalid3
2026-03-04
"""

        with patch('sdd_dry_days.cli.Path') as mock_path_class:
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            mock_path_class.return_value = mock_path

            with patch('builtins.open', mock_open(read_data=file_content)):
                # Execute
                cli._handle_import(args)

        # Verify: 4 successful, 3 errors, but all lines processed
        assert cli.storage.add_dry_day.call_count == 4
        cli.formatter.display_import_summary.assert_called_once()
        summary_call = cli.formatter.display_import_summary.call_args
        total_lines = summary_call[0][0]
        success_count = summary_call[0][1]
        errors = summary_call[0][3]

        assert total_lines == 7  # All lines were attempted
        assert success_count == 4  # 4 valid dates added
        assert len(errors) == 3  # 3 parse errors logged

        # Verify error line numbers are correct
        error_line_nums = [err[0] for err in errors]
        assert error_line_nums == [2, 4, 6]


class TestImportDuplicateHandling:
    """Tests for import handler duplicate detection and counting."""

    def test_import_counts_successfully_added_dates(self):
        """Test that successfully added dates are counted correctly."""
        # Setup
        cli = CLI()
        cli.formatter = Mock()
        cli.storage = Mock()
        # All dates are new (add_dry_day returns True)
        cli.storage.add_dry_day.return_value = True

        args = Mock()
        args.filepath = "/path/to/file.txt"

        # File content with 5 dates
        file_content = """2026-03-01
2026-03-02
2026-03-03
2026-03-04
2026-03-05
"""

        with patch('sdd_dry_days.cli.Path') as mock_path_class:
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            mock_path_class.return_value = mock_path

            with patch('builtins.open', mock_open(read_data=file_content)):
                # Execute
                cli._handle_import(args)

        # Verify all dates were added
        assert cli.storage.add_dry_day.call_count == 5
        cli.formatter.display_import_summary.assert_called_once()
        summary_call = cli.formatter.display_import_summary.call_args
        total_lines = summary_call[0][0]
        success_count = summary_call[0][1]
        duplicate_count = summary_call[0][2]

        assert total_lines == 5
        assert success_count == 5
        assert duplicate_count == 0

    def test_import_counts_duplicate_dates_separately(self):
        """Test that duplicate dates are counted separately from successful adds."""
        # Setup
        cli = CLI()
        cli.formatter = Mock()
        cli.storage = Mock()

        # Mock add_dry_day to return True for first 3, False for last 2 (duplicates)
        cli.storage.add_dry_day.side_effect = [True, True, True, False, False]

        args = Mock()
        args.filepath = "/path/to/file.txt"

        # File content with 5 dates
        file_content = """2026-03-01
2026-03-02
2026-03-03
2026-03-01
2026-03-02
"""

        with patch('sdd_dry_days.cli.Path') as mock_path_class:
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            mock_path_class.return_value = mock_path

            with patch('builtins.open', mock_open(read_data=file_content)):
                # Execute
                cli._handle_import(args)

        # Verify counts
        assert cli.storage.add_dry_day.call_count == 5
        cli.formatter.display_import_summary.assert_called_once()
        summary_call = cli.formatter.display_import_summary.call_args
        total_lines = summary_call[0][0]
        success_count = summary_call[0][1]
        duplicate_count = summary_call[0][2]
        errors = summary_call[0][3]

        assert total_lines == 5
        assert success_count == 3  # First 3 added successfully
        assert duplicate_count == 2  # Last 2 were duplicates
        assert len(errors) == 0  # Duplicates are not errors

    def test_import_displays_all_duplicates_message(self):
        """Test that special message is shown when all dates are duplicates."""
        # Setup
        cli = CLI()
        cli.formatter = Mock()
        cli.storage = Mock()

        # All dates are duplicates (add_dry_day returns False)
        cli.storage.add_dry_day.return_value = False

        args = Mock()
        args.filepath = "/path/to/file.txt"

        # File content with dates (all duplicates)
        file_content = """2026-03-01
2026-03-02
2026-03-03
"""

        with patch('sdd_dry_days.cli.Path') as mock_path_class:
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            mock_path_class.return_value = mock_path

            with patch('builtins.open', mock_open(read_data=file_content)):
                # Execute
                cli._handle_import(args)

        # Verify summary shows all duplicates
        cli.formatter.display_import_summary.assert_called_once()
        summary_call = cli.formatter.display_import_summary.call_args
        total_lines = summary_call[0][0]
        success_count = summary_call[0][1]
        duplicate_count = summary_call[0][2]

        assert total_lines == 3
        assert success_count == 0  # No new dates added
        assert duplicate_count == 3  # All were duplicates

        # The formatter's display_import_summary method will handle
        # displaying the "All dates already recorded" message
        # based on these counts (AC-2.3)

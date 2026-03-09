"""Integration tests for import command.

This module tests the import command end-to-end with actual file operations
and storage. Tests include:
- Importing valid dates from text file
- Handling duplicates during import
- Processing mixed valid and invalid dates
- Skipping comments and empty lines
- Error handling (file not found, permissions, empty file)
- Performance verification (100 dates < 1 second)

These tests use pytest's tmp_path fixture for isolated filesystem testing and mock
the OutputFormatter to capture output calls instead of printing to the terminal.
Coverage target: End-to-end import workflow validation.
"""

from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock
import pytest
import time

from sdd_dry_days.cli import CLI
from sdd_dry_days.storage.json_storage import JsonStorage
from sdd_dry_days.core.dry_day import DryDay


class TestImportIntegration:
    """Integration tests for import command happy path scenarios."""

    def test_import_valid_file_adds_dry_days_to_storage(self, tmp_path):
        """Test importing a file with valid dates adds them to storage."""
        # Setup
        cli = CLI()
        cli.storage = JsonStorage(data_dir=tmp_path)
        cli.formatter = Mock()

        # Create test file with valid dates
        import_file = tmp_path / "import.txt"
        import_file.write_text("""2026-03-01
2026-03-02
2026-03-03
2026-03-04
2026-03-05
""")

        # Run import command
        cli.run(["import", str(import_file)])

        # Verify display_import_summary was called
        cli.formatter.display_import_summary.assert_called_once()
        call_args = cli.formatter.display_import_summary.call_args
        total_lines = call_args[0][0]
        success_count = call_args[0][1]
        duplicate_count = call_args[0][2]
        errors = call_args[0][3]

        # Verify counts
        assert total_lines == 5
        assert success_count == 5
        assert duplicate_count == 0
        assert len(errors) == 0

        # Verify dry days were stored
        all_days = cli.storage.get_all_dry_days()
        assert len(all_days) == 5

        # Verify dates are correct
        dates = [day.date for day in all_days]
        expected_dates = [
            datetime(2026, 3, 1),
            datetime(2026, 3, 2),
            datetime(2026, 3, 3),
            datetime(2026, 3, 4),
            datetime(2026, 3, 5),
        ]
        assert sorted(dates) == sorted(expected_dates)

    def test_import_with_duplicates_skips_correctly(self, tmp_path):
        """Test importing file with duplicates skips them without errors."""
        # Setup
        cli = CLI()
        cli.storage = JsonStorage(data_dir=tmp_path)
        cli.formatter = Mock()

        # Pre-add some dates to storage
        cli.storage.add_dry_day(DryDay(date=datetime(2026, 3, 1)))
        cli.storage.add_dry_day(DryDay(date=datetime(2026, 3, 2)))

        # Create test file with some duplicates
        import_file = tmp_path / "import.txt"
        import_file.write_text("""2026-03-01
2026-03-02
2026-03-03
2026-03-04
2026-03-05
""")

        # Run import command
        cli.run(["import", str(import_file)])

        # Verify display_import_summary was called
        cli.formatter.display_import_summary.assert_called_once()
        call_args = cli.formatter.display_import_summary.call_args
        total_lines = call_args[0][0]
        success_count = call_args[0][1]
        duplicate_count = call_args[0][2]
        errors = call_args[0][3]

        # Verify counts
        assert total_lines == 5
        assert success_count == 3  # Only 3 new dates
        assert duplicate_count == 2  # 2 duplicates (03-01, 03-02)
        assert len(errors) == 0

        # Verify storage has 5 unique dates total
        all_days = cli.storage.get_all_dry_days()
        assert len(all_days) == 5

    def test_import_with_mixed_valid_invalid_dates(self, tmp_path):
        """Test importing file with mix of valid and invalid dates."""
        # Setup
        cli = CLI()
        cli.storage = JsonStorage(data_dir=tmp_path)
        cli.formatter = Mock()

        # Create test file with mixed content
        import_file = tmp_path / "import.txt"
        import_file.write_text("""2026-03-01
not-a-date
2026-03-02
invalid-date
2026-03-03
99/99/9999
2026-03-04
""")

        # Run import command
        cli.run(["import", str(import_file)])

        # Verify display_import_summary was called
        cli.formatter.display_import_summary.assert_called_once()
        call_args = cli.formatter.display_import_summary.call_args
        total_lines = call_args[0][0]
        success_count = call_args[0][1]
        duplicate_count = call_args[0][2]
        errors = call_args[0][3]

        # Verify counts
        assert total_lines == 7  # All non-empty lines
        assert success_count == 4  # 4 valid dates
        assert duplicate_count == 0
        assert len(errors) == 3  # 3 invalid dates

        # Verify error details
        error_line_nums = [err[0] for err in errors]
        assert 2 in error_line_nums  # "not-a-date" on line 2
        assert 4 in error_line_nums  # "invalid-date" on line 4
        assert 6 in error_line_nums  # "99/99/9999" on line 6

        # Verify valid dates were stored
        all_days = cli.storage.get_all_dry_days()
        assert len(all_days) == 4

        # Verify correct dates stored
        dates = [day.date for day in all_days]
        expected_dates = [
            datetime(2026, 3, 1),
            datetime(2026, 3, 2),
            datetime(2026, 3, 3),
            datetime(2026, 3, 4),
        ]
        assert sorted(dates) == sorted(expected_dates)

    def test_import_with_comments_and_empty_lines(self, tmp_path):
        """Test importing file with comments and empty lines skips them."""
        # Setup
        cli = CLI()
        cli.storage = JsonStorage(data_dir=tmp_path)
        cli.formatter = Mock()

        # Create test file with comments and empty lines
        import_file = tmp_path / "import.txt"
        import_file.write_text("""# This is my dry days history
# Imported from old tracker

2026-03-01
2026-03-02

# Week 2
2026-03-08

2026-03-09
#Comment without space
2026-03-10
""")

        # Run import command
        cli.run(["import", str(import_file)])

        # Verify display_import_summary was called
        cli.formatter.display_import_summary.assert_called_once()
        call_args = cli.formatter.display_import_summary.call_args
        total_lines = call_args[0][0]
        success_count = call_args[0][1]
        duplicate_count = call_args[0][2]
        errors = call_args[0][3]

        # Verify counts (should only count non-comment, non-empty lines)
        assert total_lines == 5
        assert success_count == 5
        assert duplicate_count == 0
        assert len(errors) == 0

        # Verify dry days were stored
        all_days = cli.storage.get_all_dry_days()
        assert len(all_days) == 5

        # Verify correct dates stored
        dates = [day.date for day in all_days]
        expected_dates = [
            datetime(2026, 3, 1),
            datetime(2026, 3, 2),
            datetime(2026, 3, 8),
            datetime(2026, 3, 9),
            datetime(2026, 3, 10),
        ]
        assert sorted(dates) == sorted(expected_dates)


class TestImportErrorHandling:
    """Integration tests for import command error scenarios."""

    def test_import_nonexistent_file_displays_error(self, tmp_path):
        """Test importing non-existent file displays appropriate error."""
        # Setup
        cli = CLI()
        cli.storage = JsonStorage(data_dir=tmp_path)
        cli.formatter = Mock()

        # Create path to non-existent file
        nonexistent_file = tmp_path / "does_not_exist.txt"

        # Run import command with non-existent file
        cli.run(["import", str(nonexistent_file)])

        # Verify error was displayed
        cli.formatter.error.assert_called_once()
        call_args = cli.formatter.error.call_args
        error_title = call_args[0][0]
        error_message = call_args[0][1]

        # Verify error message content
        assert "File not found" in error_title
        assert str(nonexistent_file) in error_title
        assert "check the path" in error_message.lower()

        # Verify display_import_summary was NOT called (error exit early)
        cli.formatter.display_import_summary.assert_not_called()

        # Verify no dry days were added
        all_days = cli.storage.get_all_dry_days()
        assert len(all_days) == 0

    def test_import_with_permission_denied(self, tmp_path):
        """Test importing file with no read permissions displays error."""
        # Setup
        cli = CLI()
        cli.storage = JsonStorage(data_dir=tmp_path)
        cli.formatter = Mock()

        # Create test file
        import_file = tmp_path / "restricted.txt"
        import_file.write_text("2026-03-01\n")

        # Remove read permissions (chmod 000)
        import pytest
        import os
        import stat

        # Change permissions to no-access
        os.chmod(import_file, 0o000)

        try:
            # Run import command
            cli.run(["import", str(import_file)])

            # Verify error was displayed
            cli.formatter.error.assert_called_once()
            call_args = cli.formatter.error.call_args
            error_title = call_args[0][0]
            error_message = call_args[0][1]

            # Verify error message content
            assert "Cannot read file" in error_title
            assert str(import_file) in error_title
            assert "permission" in error_message.lower()

            # Verify display_import_summary was NOT called (error exit early)
            cli.formatter.display_import_summary.assert_not_called()

            # Verify no dry days were added
            all_days = cli.storage.get_all_dry_days()
            assert len(all_days) == 0

        finally:
            # Restore permissions for cleanup
            os.chmod(import_file, stat.S_IRUSR | stat.S_IWUSR)

    def test_import_empty_file_displays_message(self, tmp_path):
        """Test importing empty file displays appropriate message."""
        # Setup
        cli = CLI()
        cli.storage = JsonStorage(data_dir=tmp_path)
        cli.formatter = Mock()

        # Create empty file
        import_file = tmp_path / "empty.txt"
        import_file.write_text("")

        # Run import command
        cli.run(["import", str(import_file)])

        # Verify error was displayed
        cli.formatter.error.assert_called_once()
        call_args = cli.formatter.error.call_args
        error_title = call_args[0][0]
        error_message = call_args[0][1]

        # Verify error message content
        assert "File is empty" in error_title
        assert "Add dates" in error_message

        # Verify display_import_summary was NOT called (error exit early)
        cli.formatter.display_import_summary.assert_not_called()

        # Verify no dry days were added
        all_days = cli.storage.get_all_dry_days()
        assert len(all_days) == 0


class TestImportPerformance:
    """Integration tests for import command performance."""

    def test_import_100_dates_completes_within_1_second(self, tmp_path):
        """Test importing 100 dates completes within 1 second (performance requirement)."""
        # Setup
        cli = CLI()
        cli.storage = JsonStorage(data_dir=tmp_path)
        cli.formatter = Mock()

        # Create test file with 100 valid dates
        import_file = tmp_path / "large_import.txt"

        # Generate 100 dates (100 consecutive days starting from 2026-01-01)
        start_date = datetime(2026, 1, 1)
        dates = []
        for i in range(100):
            date = start_date + timedelta(days=i)
            dates.append(date.strftime("%Y-%m-%d"))

        import_file.write_text("\n".join(dates))

        # Measure import time
        start_time = time.time()
        cli.run(["import", str(import_file)])
        end_time = time.time()

        duration = end_time - start_time

        # Verify performance requirement (< 1 second)
        assert duration < 1.0, f"Import took {duration:.3f}s, expected < 1.0s"

        # Verify import was successful
        cli.formatter.display_import_summary.assert_called_once()
        call_args = cli.formatter.display_import_summary.call_args
        success_count = call_args[0][1]

        assert success_count == 100

        # Verify all dates were stored
        all_days = cli.storage.get_all_dry_days()
        assert len(all_days) == 100

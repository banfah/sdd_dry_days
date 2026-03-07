"""Integration tests for JsonStorage.

This module tests the JSON storage implementation with actual filesystem operations.
Tests include:
- Data directory and file creation with correct permissions
- CRUD operations (Create, Read, Update, Delete queries)
- Duplicate detection
- Sorting and ordering
- Date range queries
- Corrupted file recovery with backup creation
- Atomic write operations with failure simulation

These tests use pytest's tmp_path fixture for isolated filesystem testing.
Coverage target: >90% of json_storage.py module.
"""

import json
import stat
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
import pytest
import shutil

from sdd_dry_days.storage.json_storage import JsonStorage
from sdd_dry_days.core.dry_day import DryDay


class TestDataDirectoryAndFileCreation:
    """Tests for automatic directory and file creation with correct permissions."""

    def test_creates_data_directory_if_not_exists(self, tmp_path):
        """Test that data directory is created automatically."""
        data_dir = tmp_path / "test_sdd"
        assert not data_dir.exists()

        storage = JsonStorage(data_dir=data_dir)

        assert data_dir.exists()
        assert data_dir.is_dir()

    def test_data_directory_has_correct_permissions(self, tmp_path):
        """Test that data directory is created with mode 0o700 (user-only access)."""
        data_dir = tmp_path / "test_sdd"
        storage = JsonStorage(data_dir=data_dir)

        # Get file permissions and mask to check only permission bits
        mode = data_dir.stat().st_mode
        permissions = stat.S_IMODE(mode)

        assert permissions == 0o700

    def test_creates_data_file_if_not_exists(self, tmp_path):
        """Test that data file is created automatically."""
        data_dir = tmp_path / "test_sdd"
        storage = JsonStorage(data_dir=data_dir)

        data_file = data_dir / "data.json"
        assert data_file.exists()
        assert data_file.is_file()

    def test_data_file_has_correct_permissions(self, tmp_path):
        """Test that data file is created with mode 0o600 (user-only read/write)."""
        data_dir = tmp_path / "test_sdd"
        storage = JsonStorage(data_dir=data_dir)

        data_file = data_dir / "data.json"
        mode = data_file.stat().st_mode
        permissions = stat.S_IMODE(mode)

        assert permissions == 0o600

    def test_initializes_data_file_with_correct_schema(self, tmp_path):
        """Test that new data file has correct initial structure."""
        data_dir = tmp_path / "test_sdd"
        storage = JsonStorage(data_dir=data_dir)

        data_file = data_dir / "data.json"
        with data_file.open('r') as f:
            data = json.load(f)

        assert "dry_days" in data
        assert "version" in data
        assert data["dry_days"] == []
        assert data["version"] == "1.0"

    def test_uses_existing_directory_if_already_exists(self, tmp_path):
        """Test that existing directory is reused without errors."""
        data_dir = tmp_path / "test_sdd"
        data_dir.mkdir()

        storage = JsonStorage(data_dir=data_dir)

        assert data_dir.exists()
        assert data_dir.is_dir()

    def test_uses_existing_file_if_already_exists(self, tmp_path):
        """Test that existing data file is reused without overwriting."""
        data_dir = tmp_path / "test_sdd"
        data_dir.mkdir()
        data_file = data_dir / "data.json"

        # Create existing file with some data
        existing_data = {
            "dry_days": [{"date": "2026-03-06", "note": "Existing", "added_at": "2026-03-06T12:00:00", "is_planned": False}],
            "version": "1.0"
        }
        with data_file.open('w') as f:
            json.dump(existing_data, f)

        storage = JsonStorage(data_dir=data_dir)

        # Should not overwrite existing data
        with data_file.open('r') as f:
            data = json.load(f)

        assert len(data["dry_days"]) == 1
        assert data["dry_days"][0]["note"] == "Existing"


class TestAddDryDay:
    """Tests for adding dry day entries."""

    def test_add_dry_day_creates_new_entry(self, tmp_path):
        """Test that add_dry_day creates a new entry in storage."""
        storage = JsonStorage(data_dir=tmp_path)
        dry_day = DryDay(date=datetime(2026, 3, 6), note="Test day")

        result = storage.add_dry_day(dry_day)

        assert result is True
        all_days = storage.get_all_dry_days()
        assert len(all_days) == 1
        assert all_days[0].date == datetime(2026, 3, 6, 0, 0, 0)
        assert all_days[0].note == "Test day"

    def test_add_dry_day_returns_true_on_success(self, tmp_path):
        """Test that add_dry_day returns True when entry is added."""
        storage = JsonStorage(data_dir=tmp_path)
        dry_day = DryDay(date=datetime(2026, 3, 6))

        result = storage.add_dry_day(dry_day)

        assert result is True

    def test_add_dry_day_detects_duplicates(self, tmp_path):
        """Test that add_dry_day detects and rejects duplicate dates."""
        storage = JsonStorage(data_dir=tmp_path)
        dry_day1 = DryDay(date=datetime(2026, 3, 6), note="First")
        dry_day2 = DryDay(date=datetime(2026, 3, 6), note="Second")

        result1 = storage.add_dry_day(dry_day1)
        result2 = storage.add_dry_day(dry_day2)

        assert result1 is True
        assert result2 is False
        all_days = storage.get_all_dry_days()
        assert len(all_days) == 1
        assert all_days[0].note == "First"  # Original entry unchanged

    def test_add_dry_day_detects_duplicates_ignoring_time(self, tmp_path):
        """Test that duplicates are detected even with different times."""
        storage = JsonStorage(data_dir=tmp_path)
        dry_day1 = DryDay(date=datetime(2026, 3, 6, 8, 30))
        dry_day2 = DryDay(date=datetime(2026, 3, 6, 18, 45))

        result1 = storage.add_dry_day(dry_day1)
        result2 = storage.add_dry_day(dry_day2)

        assert result1 is True
        assert result2 is False

    def test_add_multiple_dry_days_succeeds(self, tmp_path):
        """Test adding multiple different dry days."""
        storage = JsonStorage(data_dir=tmp_path)
        days = [
            DryDay(date=datetime(2026, 3, 1)),
            DryDay(date=datetime(2026, 3, 5)),
            DryDay(date=datetime(2026, 3, 10))
        ]

        for day in days:
            result = storage.add_dry_day(day)
            assert result is True

        all_days = storage.get_all_dry_days()
        assert len(all_days) == 3

    def test_add_dry_day_maintains_sorted_order(self, tmp_path):
        """Test that entries are kept sorted by date."""
        storage = JsonStorage(data_dir=tmp_path)

        # Add in non-chronological order
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 10)))
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 5)))
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 15)))
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 1)))

        all_days = storage.get_all_dry_days()

        # Should be sorted earliest to latest
        assert all_days[0].date == datetime(2026, 3, 1, 0, 0, 0)
        assert all_days[1].date == datetime(2026, 3, 5, 0, 0, 0)
        assert all_days[2].date == datetime(2026, 3, 10, 0, 0, 0)
        assert all_days[3].date == datetime(2026, 3, 15, 0, 0, 0)


class TestGetDryDay:
    """Tests for retrieving individual dry day entries."""

    def test_get_dry_day_retrieves_existing_entry(self, tmp_path):
        """Test that get_dry_day returns the correct entry."""
        storage = JsonStorage(data_dir=tmp_path)
        original = DryDay(date=datetime(2026, 3, 6), note="Test note")
        storage.add_dry_day(original)

        retrieved = storage.get_dry_day(datetime(2026, 3, 6))

        assert retrieved is not None
        assert retrieved.date == datetime(2026, 3, 6, 0, 0, 0)
        assert retrieved.note == "Test note"

    def test_get_dry_day_returns_none_for_nonexistent_date(self, tmp_path):
        """Test that get_dry_day returns None for dates not in storage."""
        storage = JsonStorage(data_dir=tmp_path)
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 6)))

        retrieved = storage.get_dry_day(datetime(2026, 3, 7))

        assert retrieved is None

    def test_get_dry_day_returns_none_for_empty_storage(self, tmp_path):
        """Test that get_dry_day returns None when storage is empty."""
        storage = JsonStorage(data_dir=tmp_path)

        retrieved = storage.get_dry_day(datetime(2026, 3, 6))

        assert retrieved is None

    def test_get_dry_day_ignores_time_component(self, tmp_path):
        """Test that get_dry_day matches dates ignoring time."""
        storage = JsonStorage(data_dir=tmp_path)
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 6, 10, 30)))

        # Query with different time
        retrieved = storage.get_dry_day(datetime(2026, 3, 6, 18, 45))

        assert retrieved is not None
        assert retrieved.date == datetime(2026, 3, 6, 0, 0, 0)


class TestGetAllDryDays:
    """Tests for retrieving all dry day entries."""

    def test_get_all_dry_days_returns_empty_list_for_new_storage(self, tmp_path):
        """Test that get_all_dry_days returns empty list initially."""
        storage = JsonStorage(data_dir=tmp_path)

        all_days = storage.get_all_dry_days()

        assert all_days == []

    def test_get_all_dry_days_returns_all_entries(self, tmp_path):
        """Test that get_all_dry_days returns all stored entries."""
        storage = JsonStorage(data_dir=tmp_path)

        dates = [datetime(2026, 3, 1), datetime(2026, 3, 5), datetime(2026, 3, 10)]
        for date in dates:
            storage.add_dry_day(DryDay(date=date))

        all_days = storage.get_all_dry_days()

        assert len(all_days) == 3

    def test_get_all_dry_days_returns_sorted_list(self, tmp_path):
        """Test that get_all_dry_days returns entries sorted by date."""
        storage = JsonStorage(data_dir=tmp_path)

        # Add in random order
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 15)))
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 5)))
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 20)))
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 1)))

        all_days = storage.get_all_dry_days()

        # Verify sorted
        for i in range(len(all_days) - 1):
            assert all_days[i].date < all_days[i + 1].date


class TestUpdateDryDay:
    """Tests for updating existing dry day entries."""

    def test_update_dry_day_modifies_existing_entry(self, tmp_path):
        """Test that update_dry_day changes an existing entry."""
        storage = JsonStorage(data_dir=tmp_path)
        original = DryDay(date=datetime(2026, 3, 6), note="Original")
        storage.add_dry_day(original)

        # Update the entry
        updated = DryDay(date=datetime(2026, 3, 6), note="Updated")
        result = storage.update_dry_day(updated)

        assert result is True
        retrieved = storage.get_dry_day(datetime(2026, 3, 6))
        assert retrieved.note == "Updated"

    def test_update_dry_day_returns_true_on_success(self, tmp_path):
        """Test that update_dry_day returns True when entry is updated."""
        storage = JsonStorage(data_dir=tmp_path)
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 6)))

        updated = DryDay(date=datetime(2026, 3, 6), note="Updated")
        result = storage.update_dry_day(updated)

        assert result is True

    def test_update_dry_day_returns_false_for_nonexistent_entry(self, tmp_path):
        """Test that update_dry_day returns False if entry doesn't exist."""
        storage = JsonStorage(data_dir=tmp_path)
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 6)))

        # Try to update non-existent date
        updated = DryDay(date=datetime(2026, 3, 7), note="Updated")
        result = storage.update_dry_day(updated)

        assert result is False

    def test_update_dry_day_does_not_create_new_entry(self, tmp_path):
        """Test that update_dry_day doesn't create entries for new dates."""
        storage = JsonStorage(data_dir=tmp_path)

        updated = DryDay(date=datetime(2026, 3, 6), note="New")
        result = storage.update_dry_day(updated)

        assert result is False
        all_days = storage.get_all_dry_days()
        assert len(all_days) == 0

    def test_update_dry_day_preserves_other_entries(self, tmp_path):
        """Test that updating one entry doesn't affect others."""
        storage = JsonStorage(data_dir=tmp_path)
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 1), note="First"))
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 5), note="Second"))
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 10), note="Third"))

        # Update middle entry
        updated = DryDay(date=datetime(2026, 3, 5), note="Updated Second")
        storage.update_dry_day(updated)

        # Check all entries
        all_days = storage.get_all_dry_days()
        assert len(all_days) == 3
        assert all_days[0].note == "First"
        assert all_days[1].note == "Updated Second"
        assert all_days[2].note == "Third"


class TestExists:
    """Tests for checking dry day existence."""

    def test_exists_returns_true_for_existing_date(self, tmp_path):
        """Test that exists returns True for stored dates."""
        storage = JsonStorage(data_dir=tmp_path)
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 6)))

        result = storage.exists(datetime(2026, 3, 6))

        assert result is True

    def test_exists_returns_false_for_nonexistent_date(self, tmp_path):
        """Test that exists returns False for dates not in storage."""
        storage = JsonStorage(data_dir=tmp_path)
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 6)))

        result = storage.exists(datetime(2026, 3, 7))

        assert result is False

    def test_exists_returns_false_for_empty_storage(self, tmp_path):
        """Test that exists returns False when storage is empty."""
        storage = JsonStorage(data_dir=tmp_path)

        result = storage.exists(datetime(2026, 3, 6))

        assert result is False

    def test_exists_ignores_time_component(self, tmp_path):
        """Test that exists matches dates ignoring time."""
        storage = JsonStorage(data_dir=tmp_path)
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 6, 8, 30)))

        # Check with different time
        result = storage.exists(datetime(2026, 3, 6, 20, 15))

        assert result is True


class TestGetDryDaysInRange:
    """Tests for retrieving dry days within a date range."""

    def test_get_dry_days_in_range_returns_entries_within_range(self, tmp_path):
        """Test that get_dry_days_in_range returns entries within date range."""
        storage = JsonStorage(data_dir=tmp_path)

        # Add entries across multiple dates
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 1)))
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 5)))
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 10)))
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 15)))
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 20)))

        # Query range from 3/5 to 3/15 (inclusive)
        days = storage.get_dry_days_in_range(
            datetime(2026, 3, 5),
            datetime(2026, 3, 15)
        )

        assert len(days) == 3
        assert days[0].date == datetime(2026, 3, 5, 0, 0, 0)
        assert days[1].date == datetime(2026, 3, 10, 0, 0, 0)
        assert days[2].date == datetime(2026, 3, 15, 0, 0, 0)

    def test_get_dry_days_in_range_includes_start_date(self, tmp_path):
        """Test that date range is inclusive of start date."""
        storage = JsonStorage(data_dir=tmp_path)
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 5)))

        days = storage.get_dry_days_in_range(
            datetime(2026, 3, 5),
            datetime(2026, 3, 10)
        )

        assert len(days) == 1

    def test_get_dry_days_in_range_includes_end_date(self, tmp_path):
        """Test that date range is inclusive of end date."""
        storage = JsonStorage(data_dir=tmp_path)
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 10)))

        days = storage.get_dry_days_in_range(
            datetime(2026, 3, 5),
            datetime(2026, 3, 10)
        )

        assert len(days) == 1

    def test_get_dry_days_in_range_returns_empty_list_for_no_matches(self, tmp_path):
        """Test that get_dry_days_in_range returns empty list when no matches."""
        storage = JsonStorage(data_dir=tmp_path)
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 1)))
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 20)))

        days = storage.get_dry_days_in_range(
            datetime(2026, 3, 5),
            datetime(2026, 3, 15)
        )

        assert len(days) == 0

    def test_get_dry_days_in_range_returns_empty_list_for_empty_storage(self, tmp_path):
        """Test that get_dry_days_in_range returns empty list for empty storage."""
        storage = JsonStorage(data_dir=tmp_path)

        days = storage.get_dry_days_in_range(
            datetime(2026, 3, 1),
            datetime(2026, 3, 31)
        )

        assert len(days) == 0

    def test_get_dry_days_in_range_returns_sorted_list(self, tmp_path):
        """Test that get_dry_days_in_range returns sorted entries."""
        storage = JsonStorage(data_dir=tmp_path)

        # Add in random order
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 15)))
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 5)))
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 10)))

        days = storage.get_dry_days_in_range(
            datetime(2026, 3, 1),
            datetime(2026, 3, 20)
        )

        # Verify sorted
        assert days[0].date < days[1].date < days[2].date


class TestCorruptedFileRecovery:
    """Tests for handling corrupted JSON files."""

    def test_corrupted_json_creates_backup(self, tmp_path):
        """Test that corrupted JSON file is backed up."""
        storage = JsonStorage(data_dir=tmp_path)

        # Create corrupted JSON file
        with storage.data_file.open('w') as f:
            f.write("{invalid json content")

        # Trigger read operation
        storage.get_all_dry_days()

        # Check backup was created
        backup_files = list(tmp_path.glob("data.json.backup.*"))
        assert len(backup_files) == 1

    def test_corrupted_json_reinitializes_file(self, tmp_path):
        """Test that corrupted file is replaced with fresh data."""
        storage = JsonStorage(data_dir=tmp_path)

        # Create corrupted JSON file
        with storage.data_file.open('w') as f:
            f.write("{invalid json content")

        # Trigger read operation
        all_days = storage.get_all_dry_days()

        # Should get empty list from fresh file
        assert all_days == []

        # File should now be valid JSON
        with storage.data_file.open('r') as f:
            data = json.load(f)
        assert "dry_days" in data
        assert data["dry_days"] == []

    def test_corrupted_json_backup_contains_original_content(self, tmp_path):
        """Test that backup file contains the original corrupted content."""
        storage = JsonStorage(data_dir=tmp_path)

        corrupted_content = "{invalid json content"
        with storage.data_file.open('w') as f:
            f.write(corrupted_content)

        # Trigger read operation
        storage.get_all_dry_days()

        # Check backup contains original content
        backup_files = list(tmp_path.glob("data.json.backup.*"))
        with backup_files[0].open('r') as f:
            backup_content = f.read()

        assert backup_content == corrupted_content

    def test_missing_dry_days_key_creates_backup(self, tmp_path):
        """Test that JSON missing 'dry_days' key is treated as corrupted."""
        storage = JsonStorage(data_dir=tmp_path)

        # Create invalid JSON structure (valid JSON but wrong schema)
        with storage.data_file.open('w') as f:
            json.dump({"version": "1.0", "wrong_key": []}, f)

        # Trigger read operation
        storage.get_all_dry_days()

        # Check backup was created
        backup_files = list(tmp_path.glob("data.json.backup.*"))
        assert len(backup_files) == 1

    def test_can_continue_after_corruption_recovery(self, tmp_path):
        """Test that storage can be used normally after corruption recovery."""
        storage = JsonStorage(data_dir=tmp_path)

        # Create corrupted JSON file
        with storage.data_file.open('w') as f:
            f.write("{invalid")

        # Trigger recovery
        storage.get_all_dry_days()

        # Add new entries after recovery
        result = storage.add_dry_day(DryDay(date=datetime(2026, 3, 6)))
        assert result is True

        all_days = storage.get_all_dry_days()
        assert len(all_days) == 1


class TestAtomicWrites:
    """Tests for atomic write operations."""

    def test_atomic_write_uses_temp_file(self, tmp_path):
        """Test that write operations use temporary files."""
        storage = JsonStorage(data_dir=tmp_path)

        # Track temp file creation
        temp_files_created = []
        original_tempfile = tempfile.NamedTemporaryFile

        def mock_temp(*args, **kwargs):
            temp = original_tempfile(*args, **kwargs)
            temp_files_created.append(temp.name)
            return temp

        with patch('tempfile.NamedTemporaryFile', side_effect=mock_temp):
            storage.add_dry_day(DryDay(date=datetime(2026, 3, 6)))

        # Temp file should have been created
        assert len(temp_files_created) > 0

    def test_failed_write_does_not_corrupt_existing_data(self, tmp_path):
        """Test that write failures don't corrupt existing data."""
        storage = JsonStorage(data_dir=tmp_path)

        # Add initial data
        storage.add_dry_day(DryDay(date=datetime(2026, 3, 6), note="Original"))

        # Simulate write failure during move operation
        with patch('shutil.move', side_effect=IOError("Simulated crash")):
            with pytest.raises(IOError):
                storage.add_dry_day(DryDay(date=datetime(2026, 3, 7)))

        # Original data should still be intact
        all_days = storage.get_all_dry_days()
        assert len(all_days) == 1
        assert all_days[0].date == datetime(2026, 3, 6, 0, 0, 0)
        assert all_days[0].note == "Original"

    def test_failed_write_cleans_up_temp_file(self, tmp_path):
        """Test that temporary files are cleaned up on write failure."""
        storage = JsonStorage(data_dir=tmp_path)

        # Track temp files before operation
        temp_files_before = list(tmp_path.glob("*.tmp"))

        # Simulate write failure
        with patch('shutil.move', side_effect=IOError("Simulated crash")):
            with pytest.raises(IOError):
                storage.add_dry_day(DryDay(date=datetime(2026, 3, 6)))

        # No temp files should remain
        temp_files_after = list(tmp_path.glob("*.tmp"))
        assert len(temp_files_after) == len(temp_files_before)

    def test_successful_write_removes_temp_file(self, tmp_path):
        """Test that temp file is removed after successful write."""
        storage = JsonStorage(data_dir=tmp_path)

        storage.add_dry_day(DryDay(date=datetime(2026, 3, 6)))

        # No temp files should remain
        temp_files = list(tmp_path.glob("*.tmp"))
        assert len(temp_files) == 0

    def test_atomic_write_sets_correct_permissions(self, tmp_path):
        """Test that written files have correct permissions (0o600)."""
        storage = JsonStorage(data_dir=tmp_path)

        storage.add_dry_day(DryDay(date=datetime(2026, 3, 6)))

        mode = storage.data_file.stat().st_mode
        permissions = stat.S_IMODE(mode)

        assert permissions == 0o600


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_handles_leap_year_dates(self, tmp_path):
        """Test that storage handles leap year dates correctly."""
        storage = JsonStorage(data_dir=tmp_path)

        # 2024 is a leap year
        leap_day = DryDay(date=datetime(2024, 2, 29))
        result = storage.add_dry_day(leap_day)

        assert result is True
        retrieved = storage.get_dry_day(datetime(2024, 2, 29))
        assert retrieved is not None

    def test_handles_year_boundaries(self, tmp_path):
        """Test that storage handles dates across year boundaries."""
        storage = JsonStorage(data_dir=tmp_path)

        storage.add_dry_day(DryDay(date=datetime(2025, 12, 31)))
        storage.add_dry_day(DryDay(date=datetime(2026, 1, 1)))

        days = storage.get_dry_days_in_range(
            datetime(2025, 12, 30),
            datetime(2026, 1, 2)
        )

        assert len(days) == 2

    def test_handles_very_long_notes(self, tmp_path):
        """Test that storage handles long note strings."""
        storage = JsonStorage(data_dir=tmp_path)

        long_note = "A" * 10000  # 10,000 character note
        dry_day = DryDay(date=datetime(2026, 3, 6), note=long_note)

        result = storage.add_dry_day(dry_day)
        assert result is True

        retrieved = storage.get_dry_day(datetime(2026, 3, 6))
        assert retrieved.note == long_note

    def test_handles_special_characters_in_notes(self, tmp_path):
        """Test that storage handles special characters in notes."""
        storage = JsonStorage(data_dir=tmp_path)

        special_note = "Note with 'quotes', \"double quotes\", and \n newlines \t tabs"
        dry_day = DryDay(date=datetime(2026, 3, 6), note=special_note)

        result = storage.add_dry_day(dry_day)
        assert result is True

        retrieved = storage.get_dry_day(datetime(2026, 3, 6))
        assert retrieved.note == special_note

    def test_handles_unicode_in_notes(self, tmp_path):
        """Test that storage handles Unicode characters in notes."""
        storage = JsonStorage(data_dir=tmp_path)

        unicode_note = "Note with emoji 🎉 and Chinese 你好 and Arabic مرحبا"
        dry_day = DryDay(date=datetime(2026, 3, 6), note=unicode_note)

        result = storage.add_dry_day(dry_day)
        assert result is True

        retrieved = storage.get_dry_day(datetime(2026, 3, 6))
        assert retrieved.note == unicode_note
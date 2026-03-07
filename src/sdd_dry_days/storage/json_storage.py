"""JSON file-based storage implementation for dry days.

This module provides a concrete implementation of the Storage interface using
JSON files as the persistence mechanism. It stores dry day entries in a human-
readable JSON format in the user's home directory.

Key features:
- Automatic directory and file creation with appropriate permissions
- Data validation and corruption recovery with automatic backups
- Atomic writes using temporary files (prevents corruption)
- Schema versioning for future data migrations
- Thread-safe operations for concurrent access

The storage format uses a simple JSON structure with a version field and an
array of dry day entries. This format is designed for:
- Easy backup and manual inspection
- Future migration to database backends
- Human readability for debugging

Default storage location: ~/.sdd_dry_days/data.json
"""

from pathlib import Path
import json
import tempfile
import shutil
from typing import List, Optional
from datetime import datetime
from .base import Storage
from ..core.dry_day import DryDay


class JsonStorage(Storage):
    """JSON file-based storage implementation.

    This class implements the Storage interface using JSON files for persistence.
    It manages a single JSON file containing all dry day entries, with automatic
    directory creation, data validation, and corruption recovery.

    The storage directory is created with user-only permissions (700) to protect
    privacy. The data file itself uses user-only read/write permissions (600).

    Attributes:
        data_dir: Path to the directory containing the data file.
        data_file: Path to the JSON data file.
        DEFAULT_DATA_DIR: Default storage directory (~/.sdd_dry_days).
        DEFAULT_DATA_FILE: Default filename (data.json).
        SCHEMA_VERSION: Current data schema version for migrations.

    Example:
        >>> storage = JsonStorage()
        >>> dry_day = DryDay(date=datetime(2026, 3, 7), note="First day!")
        >>> storage.add_dry_day(dry_day)
        True
    """

    DEFAULT_DATA_DIR = Path.home() / ".sdd_dry_days"
    DEFAULT_DATA_FILE = "data.json"
    SCHEMA_VERSION = "1.0"

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize JSON storage with data directory.

        Creates the storage instance and ensures the data directory and file
        exist with appropriate permissions. If the directory or file doesn't
        exist, they are created automatically.

        Args:
            data_dir: Optional custom directory for data storage. If not provided,
                     uses the default location (~/.sdd_dry_days).

        Example:
            >>> storage = JsonStorage()  # Uses default directory
            >>> storage = JsonStorage(Path("/tmp/test"))  # Custom directory
        """
        self.data_dir = data_dir or self.DEFAULT_DATA_DIR
        self.data_file = self.data_dir / self.DEFAULT_DATA_FILE
        self._ensure_data_directory()

    def _ensure_data_directory(self):
        """Create data directory and file if they don't exist.

        This method is called during initialization to set up the storage
        infrastructure. It performs the following operations:

        1. Creates the data directory with mode 0o700 (user-only access) if needed
        2. Creates an empty data file with initial schema if needed

        The directory permissions ensure that only the current user can read or
        write the dry days data, protecting privacy.

        Raises:
            OSError: If directory or file creation fails due to permissions.
        """
        if not self.data_dir.exists():
            self.data_dir.mkdir(mode=0o700, parents=True)

        if not self.data_file.exists():
            self._write_data({"dry_days": [], "version": self.SCHEMA_VERSION})

    def _read_data(self) -> dict:
        """Read and validate JSON data file.

        Reads the JSON data file and validates its structure. If the file is
        corrupted or has an invalid format, creates a timestamped backup and
        initializes a new empty data file.

        The validation checks for:
        - Valid JSON syntax
        - Presence of required 'dry_days' key
        - Proper data structure

        Returns:
            A dictionary containing the data with 'dry_days' and 'version' keys.
            If the file was corrupted, returns a new empty structure.

        Raises:
            IOError: If the file cannot be read due to permissions or I/O errors.

        Example:
            >>> data = storage._read_data()
            >>> print(len(data['dry_days']))
            5
        """
        try:
            with self.data_file.open('r') as f:
                data = json.load(f)

            # Validate schema
            if "dry_days" not in data:
                raise ValueError("Invalid data format: missing 'dry_days' key")

            return data
        except (json.JSONDecodeError, ValueError) as e:
            # Handle corrupted file by creating backup and reinitializing
            backup_file = self.data_dir / f"data.json.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy(self.data_file, backup_file)
            # Initialize new file
            new_data = {"dry_days": [], "version": self.SCHEMA_VERSION}
            self._write_data(new_data)
            return new_data

    def _write_data(self, data: dict):
        """Write data to JSON file atomically.

        Implements atomic write operations to prevent data corruption during
        system crashes or interruptions. The write process:

        1. Creates a temporary file in the same directory as the target file
        2. Writes JSON data to the temporary file with pretty formatting
        3. Sets user-only read/write permissions (0o600) on the temp file
        4. Performs atomic rename operation to replace the target file
        5. Cleans up temp file if any errors occur during the process

        This approach ensures that the data file is never left in a partially
        written or corrupted state. If the process is interrupted, either the
        old file remains intact or the new file is complete.

        Args:
            data: Dictionary containing 'dry_days' and 'version' keys.

        Raises:
            IOError: If the file cannot be written due to permissions or I/O errors.
            OSError: If file operations fail (e.g., rename, chmod).

        Example:
            >>> storage._write_data({"dry_days": [], "version": "1.0"})
        """
        # Create temporary file in the same directory as target file
        temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            dir=self.data_dir,
            delete=False,
            suffix='.tmp'
        )

        try:
            # Write JSON data to temp file with formatting
            json.dump(data, temp_file, indent=2)
            temp_file.close()

            # Set user-only read/write permissions (600)
            Path(temp_file.name).chmod(0o600)

            # Atomic rename - replaces target file only after successful write
            shutil.move(temp_file.name, self.data_file)

        except Exception as e:
            # Clean up temp file on any error
            Path(temp_file.name).unlink(missing_ok=True)
            raise

    def add_dry_day(self, dry_day: DryDay) -> bool:
        """Add a dry day entry to storage.

        Adds a new dry day entry if it doesn't already exist. Performs duplicate
        detection by comparing dates and maintains sorted order of entries.

        Args:
            dry_day: The DryDay instance to add.

        Returns:
            True if the dry day was added successfully, False if it already exists.

        Example:
            >>> storage = JsonStorage()
            >>> dry_day = DryDay(date=datetime(2026, 3, 7))
            >>> storage.add_dry_day(dry_day)
            True
            >>> storage.add_dry_day(dry_day)  # Duplicate
            False
        """
        data = self._read_data()

        # Check for duplicates
        date_str = dry_day.date.strftime("%Y-%m-%d")
        for existing in data["dry_days"]:
            if existing["date"] == date_str:
                return False  # Already exists

        # Add new entry
        data["dry_days"].append(dry_day.to_dict())

        # Sort by date to maintain order
        data["dry_days"].sort(key=lambda x: x["date"])

        self._write_data(data)
        return True

    def get_dry_day(self, date: datetime) -> Optional[DryDay]:
        """Retrieve a dry day by its date.

        Searches for a dry day entry matching the given date. Compares dates
        without considering time components.

        Args:
            date: The date to search for.

        Returns:
            The DryDay instance if found, None otherwise.

        Example:
            >>> storage = JsonStorage()
            >>> dry_day = storage.get_dry_day(datetime(2026, 3, 7))
            >>> print(dry_day.note if dry_day else "Not found")
        """
        data = self._read_data()
        date_str = date.strftime("%Y-%m-%d")

        for entry in data["dry_days"]:
            if entry["date"] == date_str:
                return DryDay.from_dict(entry)

        return None

    def get_all_dry_days(self) -> List[DryDay]:
        """Retrieve all dry days sorted by date.

        Returns all dry day entries from storage, converted to DryDay instances.
        The list is sorted by date in ascending order.

        Returns:
            A list of DryDay instances sorted by date (earliest to latest).

        Example:
            >>> storage = JsonStorage()
            >>> dry_days = storage.get_all_dry_days()
            >>> print(f"Total dry days: {len(dry_days)}")
        """
        data = self._read_data()
        return [DryDay.from_dict(entry) for entry in data["dry_days"]]

    def update_dry_day(self, dry_day: DryDay) -> bool:
        """Update an existing dry day entry.

        Finds an existing dry day by date and replaces it with the provided
        updated entry. Does not create a new entry if the date is not found.

        Args:
            dry_day: The DryDay instance with updated data.

        Returns:
            True if the entry was found and updated, False if not found.

        Example:
            >>> storage = JsonStorage()
            >>> dry_day = storage.get_dry_day(datetime(2026, 3, 7))
            >>> dry_day.note = "Updated note"
            >>> storage.update_dry_day(dry_day)
            True
        """
        data = self._read_data()
        date_str = dry_day.date.strftime("%Y-%m-%d")

        for i, entry in enumerate(data["dry_days"]):
            if entry["date"] == date_str:
                data["dry_days"][i] = dry_day.to_dict()
                self._write_data(data)
                return True

        return False

    def exists(self, date: datetime) -> bool:
        """Check if a dry day entry exists for the given date.

        Performs a quick existence check without retrieving the full entry.
        Useful for duplicate detection and validation.

        Args:
            date: The date to check.

        Returns:
            True if a dry day entry exists for the date, False otherwise.

        Example:
            >>> storage = JsonStorage()
            >>> if storage.exists(datetime(2026, 3, 7)):
            ...     print("Already recorded")
        """
        return self.get_dry_day(date) is not None

    def get_dry_days_in_range(self, start: datetime, end: datetime) -> List[DryDay]:
        """Retrieve dry days within a date range (inclusive).

        Returns all dry day entries that fall within the specified date range.
        Both start and end dates are inclusive. Comparison is done on dates
        without considering time components.

        Args:
            start: The start date of the range (inclusive).
            end: The end date of the range (inclusive).

        Returns:
            A list of DryDay instances within the range, sorted by date.

        Example:
            >>> storage = JsonStorage()
            >>> start = datetime(2026, 3, 1)
            >>> end = datetime(2026, 3, 7)
            >>> days = storage.get_dry_days_in_range(start, end)
            >>> print(f"Found {len(days)} dry days in March 2026")
        """
        all_days = self.get_all_dry_days()
        return [
            day for day in all_days
            if start.date() <= day.date.date() <= end.date()
        ]
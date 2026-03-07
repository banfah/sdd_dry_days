"""Abstract storage interface for dry days persistence.

This module defines the Storage abstract base class that serves as the contract
for all storage backend implementations in the SDD (Sober/Dry Days) tracking system.
The interface follows the Repository Pattern, enabling:

- **Storage backend abstraction**: Business logic remains independent of storage details
- **Multiple implementations**: JSON files, MongoDB, SQL databases, etc.
- **Easy testing**: Mock implementations for unit tests
- **Future migration**: Swap backends (e.g., JSON → MongoDB) without changing CLI code

The Storage interface defines six core operations:
1. add_dry_day: Create a new dry day entry
2. get_dry_day: Retrieve a dry day by date
3. get_all_dry_days: List all dry days
4. update_dry_day: Modify an existing entry
5. exists: Check if a date has an entry
6. get_dry_days_in_range: Query by date range

All implementations must handle date normalization consistently (storing dates
without time components) and maintain sorted order by date.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from ..core.dry_day import DryDay


class Storage(ABC):
    """Abstract interface for dry days storage.

    This abstract base class defines the contract that all storage backend
    implementations must follow. It provides a consistent API for CRUD operations
    on DryDay entries, enabling the application to work with any storage backend
    (JSON, database, cloud, etc.) without modification.

    Implementations must:
    - Handle duplicate detection (same date = duplicate)
    - Normalize dates to start of day (no time component)
    - Return dry days sorted by date in ascending order
    - Raise appropriate exceptions for invalid operations
    - Be thread-safe if used in concurrent contexts

    Example:
        This class cannot be instantiated directly:

        >>> storage = Storage()  # Raises TypeError

        Instead, use a concrete implementation:

        >>> from .json_storage import JsonStorage
        >>> storage = JsonStorage("dry_days.json")
        >>> storage.add_dry_day(dry_day)
    """

    @abstractmethod
    def add_dry_day(self, dry_day: DryDay) -> bool:
        """Add a dry day entry to storage.

        Attempts to add a new dry day to the storage backend. If a dry day
        already exists for the same calendar date, the operation fails and
        returns False. This ensures no duplicate entries for the same day.

        Args:
            dry_day: The DryDay instance to add. The date will be normalized
                     to the start of the day (00:00:00) if not already.

        Returns:
            True if the dry day was successfully added.
            False if a dry day already exists for that date (duplicate).

        Raises:
            IOError: If storage backend is unavailable or write fails.
            ValueError: If dry_day is invalid or malformed.

        Example:
            >>> dry_day = DryDay(date=datetime(2026, 3, 7), note="First day!")
            >>> success = storage.add_dry_day(dry_day)
            >>> print(success)
            True
            >>> success = storage.add_dry_day(dry_day)  # Same date
            >>> print(success)
            False
        """
        pass

    @abstractmethod
    def get_dry_day(self, date: datetime) -> Optional[DryDay]:
        """Retrieve a dry day by its date.

        Searches for a dry day entry with the specified calendar date. The time
        component of the date parameter is ignored; only the calendar date
        (year, month, day) is used for lookup.

        Args:
            date: The date to search for. Time component is ignored.

        Returns:
            The DryDay instance if found, None if no entry exists for that date.

        Raises:
            IOError: If storage backend is unavailable or read fails.

        Example:
            >>> dry_day = storage.get_dry_day(datetime(2026, 3, 7))
            >>> if dry_day:
            ...     print(dry_day.note)
            ... else:
            ...     print("No entry for that date")
        """
        pass

    @abstractmethod
    def get_all_dry_days(self) -> List[DryDay]:
        """Retrieve all dry days, sorted by date in ascending order.

        Returns the complete list of all dry day entries in the storage backend,
        ordered chronologically from oldest to newest. This is useful for
        generating reports, calculating streaks, and displaying history.

        Returns:
            A list of DryDay instances sorted by date (ascending). Returns an
            empty list if no dry days are stored.

        Raises:
            IOError: If storage backend is unavailable or read fails.

        Example:
            >>> all_days = storage.get_all_dry_days()
            >>> for day in all_days:
            ...     print(f"{day.date.strftime('%Y-%m-%d')}: {day.note}")
            2026-03-01: Started challenge
            2026-03-02: Feeling good
            2026-03-07: One week in!
        """
        pass

    @abstractmethod
    def update_dry_day(self, dry_day: DryDay) -> bool:
        """Update an existing dry day entry.

        Modifies an existing dry day entry in storage, identified by the date
        field. This is typically used to update the note or other metadata.
        The date itself cannot be changed; to move an entry to a different date,
        delete the old entry and create a new one.

        Args:
            dry_day: The DryDay instance with updated data. The date field
                     identifies which entry to update.

        Returns:
            True if the dry day was found and successfully updated.
            False if no entry exists for that date (nothing to update).

        Raises:
            IOError: If storage backend is unavailable or write fails.
            ValueError: If dry_day is invalid or malformed.

        Example:
            >>> dry_day = storage.get_dry_day(datetime(2026, 3, 7))
            >>> dry_day.note = "Updated note"
            >>> success = storage.update_dry_day(dry_day)
            >>> print(success)
            True
        """
        pass

    @abstractmethod
    def exists(self, date: datetime) -> bool:
        """Check if a dry day entry exists for the given date.

        Performs a quick existence check without retrieving the full DryDay
        object. This is more efficient than get_dry_day() when you only need
        to know if an entry exists.

        Args:
            date: The date to check. Time component is ignored.

        Returns:
            True if a dry day entry exists for the date, False otherwise.

        Raises:
            IOError: If storage backend is unavailable or read fails.

        Example:
            >>> if storage.exists(datetime(2026, 3, 7)):
            ...     print("Already logged")
            ... else:
            ...     storage.add_dry_day(DryDay(date=datetime(2026, 3, 7)))
        """
        pass

    @abstractmethod
    def get_dry_days_in_range(self, start: datetime, end: datetime) -> List[DryDay]:
        """Retrieve dry days within a date range (inclusive).

        Returns all dry day entries that fall within the specified date range,
        including both the start and end dates. Results are sorted by date in
        ascending order. This is useful for generating reports for specific
        time periods (e.g., "show me all dry days in March").

        Args:
            start: The start date of the range (inclusive). Time component ignored.
            end: The end date of the range (inclusive). Time component ignored.

        Returns:
            A list of DryDay instances within the range, sorted by date
            (ascending). Returns an empty list if no dry days exist in the range.

        Raises:
            IOError: If storage backend is unavailable or read fails.
            ValueError: If start date is after end date.

        Example:
            >>> start = datetime(2026, 3, 1)
            >>> end = datetime(2026, 3, 7)
            >>> march_days = storage.get_dry_days_in_range(start, end)
            >>> print(f"Dry days in range: {len(march_days)}")
            Dry days in range: 7
        """
        pass
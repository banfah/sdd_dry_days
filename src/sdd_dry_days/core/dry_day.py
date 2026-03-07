"""DryDay model for tracking individual dry day entries.

This module provides the core data model for representing a single dry day entry
in the SDD (Sober/Dry Days) tracking system. Each DryDay instance represents one
day without alcohol consumption, with optional notes and metadata.

The model supports:
- Date normalization (removes time component)
- Automatic timestamp tracking (when entry was added)
- Planned vs. completed day tracking
- JSON serialization/deserialization
- Duplicate detection by date
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class DryDay:
    """Represents a single dry day entry.

    A dry day is a calendar date on which no alcohol was consumed (or is planned
    to be consumed). This dataclass stores the date along with optional metadata
    such as notes, timestamps, and planning status.

    Attributes:
        date: Date of the dry day (time component is normalized to 00:00:00).
        note: Optional note or context about the day (default: empty string).
        added_at: Timestamp when the entry was created (auto-set if None).
        is_planned: True if the date is in the future, False for past/today.

    Example:
        >>> dry_day = DryDay(date=datetime(2026, 3, 6), note="First day!")
        >>> dry_day.date
        datetime.datetime(2026, 3, 6, 0, 0)
        >>> dry_day.to_dict()
        {'date': '2026-03-06', 'note': 'First day!', 'added_at': '...', 'is_planned': False}
    """

    date: datetime  # Date of the dry day (date only, no time)
    note: str = ""  # Optional note/context
    added_at: datetime = None  # Timestamp when entry was created
    is_planned: bool = False  # True if future date, False if past/today

    def __post_init__(self):
        """Initialize added_at and normalize date to start of day.

        This method is automatically called after __init__. It performs two tasks:
        1. Sets added_at to current time if not explicitly provided
        2. Normalizes the date to midnight (removes time component)

        The date normalization ensures that all DryDay instances use consistent
        date values for comparison and deduplication, regardless of how the
        datetime was initially constructed.
        """
        if self.added_at is None:
            self.added_at = datetime.now()
        # Normalize date to start of day (remove time component)
        self.date = self.date.replace(hour=0, minute=0, second=0, microsecond=0)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization.

        Converts the DryDay instance into a JSON-serializable dictionary format.
        Dates are formatted as ISO strings for portability and human readability.

        Returns:
            A dictionary with keys: 'date', 'note', 'added_at', 'is_planned'.
            Dates are formatted as ISO strings (YYYY-MM-DD for date, full ISO
            format for added_at timestamp).

        Example:
            >>> dry_day = DryDay(date=datetime(2026, 3, 6), note="Test")
            >>> dry_day.to_dict()
            {'date': '2026-03-06', 'note': 'Test', 'added_at': '2026-03-06T...', 'is_planned': False}
        """
        return {
            "date": self.date.strftime("%Y-%m-%d"),
            "note": self.note,
            "added_at": self.added_at.isoformat(),
            "is_planned": self.is_planned
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DryDay":
        """Create DryDay from dictionary (JSON deserialization).

        Constructs a DryDay instance from a dictionary, typically one that was
        created by to_dict() or loaded from JSON storage. This is the inverse
        operation of to_dict().

        Args:
            data: Dictionary with keys matching DryDay fields. Required keys:
                  'date' (str in ISO format), 'added_at' (str in ISO format).
                  Optional keys: 'note' (str), 'is_planned' (bool).

        Returns:
            A new DryDay instance populated with the data from the dictionary.

        Raises:
            KeyError: If required keys ('date', 'added_at') are missing.
            ValueError: If date strings are not in valid ISO format.

        Example:
            >>> data = {'date': '2026-03-06', 'note': 'Test', 'added_at': '2026-03-06T12:00:00', 'is_planned': False}
            >>> dry_day = DryDay.from_dict(data)
            >>> dry_day.date
            datetime.datetime(2026, 3, 6, 0, 0)
        """
        return cls(
            date=datetime.fromisoformat(data["date"]),
            note=data.get("note", ""),
            added_at=datetime.fromisoformat(data["added_at"]),
            is_planned=data.get("is_planned", False)
        )

    def is_duplicate(self, other: "DryDay") -> bool:
        """Check if this dry day has the same date as another.

        Compares the calendar date (ignoring time) of this DryDay with another
        DryDay instance. This is used for duplicate detection when adding new
        entries to prevent multiple entries for the same day.

        Args:
            other: Another DryDay instance to compare against.

        Returns:
            True if both DryDay instances represent the same calendar date,
            False otherwise.

        Example:
            >>> day1 = DryDay(date=datetime(2026, 3, 6, 10, 30))
            >>> day2 = DryDay(date=datetime(2026, 3, 6, 14, 45))
            >>> day1.is_duplicate(day2)
            True
            >>> day3 = DryDay(date=datetime(2026, 3, 7))
            >>> day1.is_duplicate(day3)
            False
        """
        return self.date.date() == other.date.date()
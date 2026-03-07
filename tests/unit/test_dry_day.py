"""Unit tests for DryDay model.

This module tests the core functionality of the DryDay dataclass including:
- Instantiation with defaults
- Date normalization
- Automatic timestamp tracking
- JSON serialization/deserialization
- Duplicate detection by date

The tests ensure >90% coverage of the dry_day.py module.
"""

from datetime import datetime
import pytest

from sdd_dry_days.core.dry_day import DryDay

class TestDryDayInstantiation:
    """Tests for DryDay instantiation and initialization."""

    def test_instantiate_with_minimal_required_fields_succeeds(self):
        """Test DryDay can be created with only date field."""
        date = datetime(2026, 3, 6)
        dry_day = DryDay(date=date)

        assert dry_day.date == datetime(2026, 3, 6, 0, 0, 0)
        assert dry_day.note == ""
        assert dry_day.added_at is not None
        assert dry_day.is_planned is False

    def test_instantiate_with_all_fields_succeeds(self):
        """Test DryDay can be created with all fields explicitly set."""
        date = datetime(2026, 3, 6)
        added_at = datetime(2026, 3, 6, 12, 30, 0)

        dry_day = DryDay(
            date=date,
            note="Test note",
            added_at=added_at,
            is_planned=True
        )

        assert dry_day.date == datetime(2026, 3, 6, 0, 0, 0)
        assert dry_day.note == "Test note"
        assert dry_day.added_at == added_at
        assert dry_day.is_planned is True

    def test_instantiate_with_default_note_is_empty_string(self):
        """Test that note defaults to empty string when not provided."""
        date = datetime(2026, 3, 6)
        dry_day = DryDay(date=date)

        assert dry_day.note == ""
        assert isinstance(dry_day.note, str)

    def test_instantiate_with_default_is_planned_is_false(self):
        """Test that is_planned defaults to False when not provided."""
        date = datetime(2026, 3, 6)
        dry_day = DryDay(date=date)

        assert dry_day.is_planned is False


class TestDryDayPostInit:
    """Tests for __post_init__ behavior (date normalization and added_at)."""

    def test_post_init_normalizes_date_to_midnight(self):
        """Test that __post_init__ removes time component from date."""
        date_with_time = datetime(2026, 3, 6, 15, 45, 30, 123456)
        dry_day = DryDay(date=date_with_time)

        assert dry_day.date == datetime(2026, 3, 6, 0, 0, 0, 0)
        assert dry_day.date.hour == 0
        assert dry_day.date.minute == 0
        assert dry_day.date.second == 0
        assert dry_day.date.microsecond == 0

    def test_post_init_sets_added_at_when_not_provided(self):
        """Test that __post_init__ auto-sets added_at if None."""
        before = datetime.now()
        dry_day = DryDay(date=datetime(2026, 3, 6))
        after = datetime.now()

        assert dry_day.added_at is not None
        assert before <= dry_day.added_at <= after

    def test_post_init_preserves_added_at_when_provided(self):
        """Test that __post_init__ does not override explicit added_at."""
        date = datetime(2026, 3, 6)
        added_at = datetime(2026, 3, 5, 10, 30, 0)
        dry_day = DryDay(date=date, added_at=added_at)

        assert dry_day.added_at == added_at

    def test_post_init_normalizes_date_even_with_explicit_added_at(self):
        """Test that date normalization happens regardless of added_at."""
        date_with_time = datetime(2026, 3, 6, 18, 30, 45)
        added_at = datetime(2026, 3, 5, 12, 0, 0)
        dry_day = DryDay(date=date_with_time, added_at=added_at)

        assert dry_day.date == datetime(2026, 3, 6, 0, 0, 0)
        assert dry_day.added_at == added_at


class TestDryDayToDict:
    """Tests for to_dict() serialization method."""

    def test_to_dict_produces_correct_json_structure(self):
        """Test that to_dict() returns dictionary with all expected keys."""
        date = datetime(2026, 3, 6)
        added_at = datetime(2026, 3, 6, 12, 30, 0)
        dry_day = DryDay(
            date=date,
            note="Test note",
            added_at=added_at,
            is_planned=True
        )

        result = dry_day.to_dict()

        assert isinstance(result, dict)
        assert "date" in result
        assert "note" in result
        assert "added_at" in result
        assert "is_planned" in result

    def test_to_dict_formats_date_as_iso_string(self):
        """Test that to_dict() formats date as YYYY-MM-DD string."""
        date = datetime(2026, 3, 6, 15, 30)  # Time should be ignored
        added_at = datetime(2026, 3, 6, 12, 30, 0)
        dry_day = DryDay(date=date, added_at=added_at)

        result = dry_day.to_dict()

        assert result["date"] == "2026-03-06"
        assert isinstance(result["date"], str)

    def test_to_dict_formats_added_at_as_iso_string(self):
        """Test that to_dict() formats added_at as full ISO string."""
        date = datetime(2026, 3, 6)
        added_at = datetime(2026, 3, 6, 12, 30, 45)
        dry_day = DryDay(date=date, added_at=added_at)

        result = dry_day.to_dict()

        assert result["added_at"] == "2026-03-06T12:30:45"
        assert isinstance(result["added_at"], str)

    def test_to_dict_preserves_note_field(self):
        """Test that to_dict() includes note field correctly."""
        date = datetime(2026, 3, 6)
        added_at = datetime(2026, 3, 6, 12, 30, 0)
        dry_day = DryDay(date=date, note="My note", added_at=added_at)

        result = dry_day.to_dict()

        assert result["note"] == "My note"

    def test_to_dict_preserves_is_planned_field(self):
        """Test that to_dict() includes is_planned field correctly."""
        date = datetime(2026, 3, 6)
        added_at = datetime(2026, 3, 6, 12, 30, 0)
        dry_day = DryDay(date=date, added_at=added_at, is_planned=True)

        result = dry_day.to_dict()

        assert result["is_planned"] is True

    def test_to_dict_with_empty_note(self):
        """Test that to_dict() handles empty note correctly."""
        date = datetime(2026, 3, 6)
        added_at = datetime(2026, 3, 6, 12, 30, 0)
        dry_day = DryDay(date=date, note="", added_at=added_at)

        result = dry_day.to_dict()

        assert result["note"] == ""


class TestDryDayFromDict:
    """Tests for from_dict() deserialization method."""

    def test_from_dict_recreates_dry_day_correctly(self):
        """Test that from_dict() creates DryDay from dictionary."""
        data = {
            "date": "2026-03-06",
            "note": "Test note",
            "added_at": "2026-03-06T12:30:00",
            "is_planned": True
        }

        dry_day = DryDay.from_dict(data)

        assert dry_day.date == datetime(2026, 3, 6, 0, 0, 0)
        assert dry_day.note == "Test note"
        assert dry_day.added_at == datetime(2026, 3, 6, 12, 30, 0)
        assert dry_day.is_planned is True

    def test_from_dict_with_minimal_required_fields(self):
        """Test that from_dict() works with only required fields."""
        data = {
            "date": "2026-03-06",
            "added_at": "2026-03-06T12:30:00"
        }

        dry_day = DryDay.from_dict(data)

        assert dry_day.date == datetime(2026, 3, 6, 0, 0, 0)
        assert dry_day.note == ""
        assert dry_day.is_planned is False

    def test_from_dict_uses_note_default_when_missing(self):
        """Test that from_dict() uses empty string for missing note."""
        data = {
            "date": "2026-03-06",
            "added_at": "2026-03-06T12:30:00"
        }

        dry_day = DryDay.from_dict(data)

        assert dry_day.note == ""

    def test_from_dict_uses_is_planned_default_when_missing(self):
        """Test that from_dict() uses False for missing is_planned."""
        data = {
            "date": "2026-03-06",
            "added_at": "2026-03-06T12:30:00"
        }

        dry_day = DryDay.from_dict(data)

        assert dry_day.is_planned is False

    def test_from_dict_round_trip_preserves_data(self):
        """Test that to_dict() followed by from_dict() preserves data."""
        original = DryDay(
            date=datetime(2026, 3, 6, 15, 30),  # Time will be normalized
            note="Round trip test",
            added_at=datetime(2026, 3, 6, 12, 30, 45),
            is_planned=True
        )

        data = original.to_dict()
        recreated = DryDay.from_dict(data)

        assert recreated.date == original.date
        assert recreated.note == original.note
        assert recreated.added_at == original.added_at
        assert recreated.is_planned == original.is_planned

    def test_from_dict_raises_key_error_when_date_missing(self):
        """Test that from_dict() raises KeyError when date is missing."""
        data = {
            "added_at": "2026-03-06T12:30:00"
        }

        with pytest.raises(KeyError):
            DryDay.from_dict(data)

    def test_from_dict_raises_key_error_when_added_at_missing(self):
        """Test that from_dict() raises KeyError when added_at is missing."""
        data = {
            "date": "2026-03-06"
        }

        with pytest.raises(KeyError):
            DryDay.from_dict(data)

    def test_from_dict_raises_value_error_for_invalid_date_format(self):
        """Test that from_dict() raises ValueError for invalid date string."""
        data = {
            "date": "invalid-date",
            "added_at": "2026-03-06T12:30:00"
        }

        with pytest.raises(ValueError):
            DryDay.from_dict(data)


class TestDryDayIsDuplicate:
    """Tests for is_duplicate() method."""

    def test_is_duplicate_returns_true_for_same_date(self):
        """Test that is_duplicate() returns True for same calendar date."""
        day1 = DryDay(date=datetime(2026, 3, 6, 10, 30))
        day2 = DryDay(date=datetime(2026, 3, 6, 14, 45))

        assert day1.is_duplicate(day2) is True
        assert day2.is_duplicate(day1) is True

    def test_is_duplicate_returns_false_for_different_dates(self):
        """Test that is_duplicate() returns False for different dates."""
        day1 = DryDay(date=datetime(2026, 3, 6))
        day2 = DryDay(date=datetime(2026, 3, 7))

        assert day1.is_duplicate(day2) is False
        assert day2.is_duplicate(day1) is False

    def test_is_duplicate_ignores_time_component(self):
        """Test that is_duplicate() ignores time, only compares date."""
        day1 = DryDay(date=datetime(2026, 3, 6, 0, 0, 0))
        day2 = DryDay(date=datetime(2026, 3, 6, 23, 59, 59))

        assert day1.is_duplicate(day2) is True

    def test_is_duplicate_ignores_note_field(self):
        """Test that is_duplicate() only compares date, not note."""
        day1 = DryDay(date=datetime(2026, 3, 6), note="Note 1")
        day2 = DryDay(date=datetime(2026, 3, 6), note="Note 2")

        assert day1.is_duplicate(day2) is True

    def test_is_duplicate_ignores_is_planned_field(self):
        """Test that is_duplicate() only compares date, not is_planned."""
        day1 = DryDay(date=datetime(2026, 3, 6), is_planned=True)
        day2 = DryDay(date=datetime(2026, 3, 6), is_planned=False)

        assert day1.is_duplicate(day2) is True

    def test_is_duplicate_with_same_instance_returns_true(self):
        """Test that is_duplicate() returns True when comparing to self."""
        day = DryDay(date=datetime(2026, 3, 6))

        assert day.is_duplicate(day) is True

    def test_is_duplicate_with_dates_one_day_apart(self):
        """Test that is_duplicate() returns False for adjacent dates."""
        day1 = DryDay(date=datetime(2026, 3, 6))
        day2 = DryDay(date=datetime(2026, 3, 7))

        assert day1.is_duplicate(day2) is False

    def test_is_duplicate_with_dates_one_month_apart(self):
        """Test that is_duplicate() returns False for dates in different months."""
        day1 = DryDay(date=datetime(2026, 3, 6))
        day2 = DryDay(date=datetime(2026, 4, 6))

        assert day1.is_duplicate(day2) is False

    def test_is_duplicate_with_dates_one_year_apart(self):
        """Test that is_duplicate() returns False for dates in different years."""
        day1 = DryDay(date=datetime(2026, 3, 6))
        day2 = DryDay(date=datetime(2027, 3, 6))

        assert day1.is_duplicate(day2) is False

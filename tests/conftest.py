"""Pytest configuration and shared fixtures for SDD Dry Days tests.

This module provides pytest fixtures that are available to all test modules.
Fixtures include:
- Sample DryDay instances for testing
- Sample lists of DryDay instances
- Temporary storage directories for isolated testing
- Mock "today" date for time-dependent tests

These fixtures ensure consistent test data and make tests more readable and maintainable.
"""

import pytest
from datetime import datetime
from pathlib import Path

from sdd_dry_days.core.dry_day import DryDay


@pytest.fixture
def sample_dry_day():
    """Provide a sample DryDay instance for testing.

    Returns a DryDay with a fixed date (2026-03-06) and a simple note.
    This is useful for tests that need a single, consistent DryDay instance.

    Returns:
        DryDay: A DryDay instance with date=2026-03-06, note="Test note"
    """
    return DryDay(
        date=datetime(2026, 3, 6),
        note="Test note",
        added_at=datetime(2026, 3, 6, 12, 0, 0),
        is_planned=False
    )


@pytest.fixture
def sample_dry_days_list():
    """Provide a list of sample DryDay instances for testing.

    Returns a list of 5 DryDay instances spanning March 1-10, 2026
    (with gaps on March 3 and 8-9). This is useful for testing
    operations on collections of dry days, such as:
    - Streak calculations
    - Sorting and filtering
    - Date range queries
    - Duplicate detection

    Returns:
        list[DryDay]: List of 5 DryDay instances with dates:
            2026-03-01, 2026-03-02, 2026-03-04, 2026-03-07, 2026-03-10
    """
    return [
        DryDay(date=datetime(2026, 3, 1), note="Day 1"),
        DryDay(date=datetime(2026, 3, 2), note="Day 2"),
        DryDay(date=datetime(2026, 3, 4), note="Day 4"),  # Gap on 3/3
        DryDay(date=datetime(2026, 3, 7), note="Day 7"),  # Gap on 3/5-3/6
        DryDay(date=datetime(2026, 3, 10), note="Day 10"),  # Gap on 3/8-3/9
    ]


@pytest.fixture
def temp_storage_dir(tmp_path):
    """Provide a temporary directory for isolated storage testing.

    Creates a unique temporary directory for each test that uses this fixture.
    The directory is automatically cleaned up after the test completes.

    This fixture is useful for:
    - Testing JsonStorage without affecting real user data
    - Ensuring test isolation (no shared state between tests)
    - Testing file system operations (permissions, atomic writes, etc.)

    Args:
        tmp_path: Pytest's built-in tmp_path fixture

    Returns:
        Path: Path to a temporary directory for storage operations
    """
    storage_dir = tmp_path / "sdd_test_storage"
    storage_dir.mkdir(exist_ok=True)
    return storage_dir


@pytest.fixture
def mock_today():
    """Provide a fixed "today" date for time-dependent tests.

    Returns a consistent datetime representing "today" (2026-03-07).
    This is useful for tests that need to control the current date,
    such as:
    - Streak calculations (need to know if today is included)
    - Date validation (checking if dates are in the past/future)
    - Time-sensitive business logic

    Note: This fixture returns the date but doesn't automatically patch
    datetime.now(). Tests should use unittest.mock.patch to actually
    mock the current time if needed.

    Returns:
        datetime: A fixed datetime representing "today" (2026-03-07 10:00:00)
    """
    return datetime(2026, 3, 7, 10, 0, 0)


@pytest.fixture
def sample_consecutive_dry_days():
    """Provide a list of consecutive DryDay instances for streak testing.

    Returns a list of 7 consecutive DryDay instances (March 1-7, 2026).
    This is useful for testing streak calculation with no gaps.

    Returns:
        list[DryDay]: List of 7 consecutive DryDay instances
    """
    return [
        DryDay(date=datetime(2026, 3, 1)),
        DryDay(date=datetime(2026, 3, 2)),
        DryDay(date=datetime(2026, 3, 3)),
        DryDay(date=datetime(2026, 3, 4)),
        DryDay(date=datetime(2026, 3, 5)),
        DryDay(date=datetime(2026, 3, 6)),
        DryDay(date=datetime(2026, 3, 7)),
    ]


@pytest.fixture
def sample_unsorted_dry_days():
    """Provide a list of unsorted DryDay instances for testing sorting logic.

    Returns a list of DryDay instances in random order. This is useful for
    testing that storage and business logic properly sort dates.

    Returns:
        list[DryDay]: List of DryDay instances in non-chronological order
    """
    return [
        DryDay(date=datetime(2026, 3, 10)),
        DryDay(date=datetime(2026, 3, 2)),
        DryDay(date=datetime(2026, 3, 7)),
        DryDay(date=datetime(2026, 3, 1)),
        DryDay(date=datetime(2026, 3, 5)),
    ]
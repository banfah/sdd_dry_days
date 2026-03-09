# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SDD Dry Days is a Python CLI application for tracking alcohol-free days ("dry days"). The application emphasizes simplicity, visual motivation through colorful console output, and privacy-focused local storage.

## Development Commands

### Setup
```bash
# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_dry_day.py

# Run specific test class or method
pytest tests/unit/test_dry_day.py::TestDryDayInstantiation
pytest tests/unit/test_dry_day.py::TestDryDayInstantiation::test_dry_day_creation_with_valid_date

# Run with coverage report
pytest --cov=src/sdd_dry_days --cov-report=html

# Run with verbose output
pytest -v

# Coverage target: >80% (some modules require >90%)
# Current status: 324 tests passing (188 unit, 136 integration)
```

### Running the Application
```bash
# Via module
python -m sdd_dry_days add

# Via installed command (after pip install -e .)
sdd add
```

## Architecture

### Four-Layer Architecture

The application follows strict separation of concerns across four layers:

1. **CLI Layer** (`cli.py`, `__main__.py`)
   - Argument parsing with argparse
   - Routes commands to business logic
   - Coordinates between business logic and presentation

2. **Business Logic Layer** (`core/`)
   - `dry_day.py`: DryDay model, validation, serialization
   - `streak.py`: Streak calculation (consecutive dry days, period-specific streaks)
   - `stats.py`: PeriodStats model and StatisticsCalculator for time-period analytics
   - Independent of storage implementation

3. **Storage Layer** (`storage/`)
   - `base.py`: Abstract Storage interface
   - `json_storage.py`: JSON file implementation (current)
   - **Critical Pattern**: Repository pattern enables future MongoDB migration without touching business logic
   - Data stored at `~/.sdd_dry_days/data.json`

4. **Presentation Layer** (`ui/`)
   - `formatters.py`: Basic Rich library formatting (success/error messages, panels)
   - `view_formatters.py`: View-specific formatting (tables, progress bars, calendars)
   - **Composition Pattern**: ViewFormatter uses OutputFormatter as dependency (not inheritance)

### Data Flow
```
User Command → CLI → Business Logic → Storage → JSON File
                ↓
           Presentation (Rich UI)
```

### Key Design Patterns

**Storage Abstraction**: All storage operations go through the abstract `Storage` interface. This allows swapping JSON storage for MongoDB without changing business logic or CLI code.

**Data Model Independence**: The `DryDay` model is storage-agnostic. It serializes to/from dictionaries, letting storage implementations handle persistence.

**Composition Over Inheritance**: ViewFormatter uses OutputFormatter as a dependency rather than inheriting from it. This provides better separation of concerns: OutputFormatter handles simple messages, ViewFormatter handles complex structured views.

**Test-Driven Development**: Tests are written alongside or before implementation. Each component has corresponding unit tests.

## Spec-Driven Development Workflow

This project uses a structured specification workflow. Key directories:

- `.claude/steering/`: Product vision, tech standards, project structure guidelines
- `.claude/specs/`: Feature specifications with requirements, design, and tasks
- `.claude/bugs/`: Bug tracking with report, analysis, and verification documents

**Steering documents are the source of truth** for:
- Product vision and principles (`product.md`)
- Technology choices and architecture (`tech.md`)
- Coding standards and conventions (`structure.md`)

**Bug Workflow**: When fixing bugs, create a bug directory with:
- `report.md`: Bug description, reproduction steps, impact assessment
- `analysis.md`: Root cause investigation and solution approach
- `verification.md`: Test results and deployment verification

When implementing features, always reference steering documents to ensure alignment.

## Coding Standards

### Naming Conventions
- **Modules**: `lowercase_with_underscores.py`
- **Classes**: `PascalCase`
- **Functions/Methods**: `lowercase_with_underscores`
- **Constants**: `UPPERCASE_WITH_UNDERSCORES`

### Documentation
- **Docstrings**: Google style for all public functions/classes
- **Type hints**: Required for public APIs
- **Module docstrings**: Explain purpose at top of file

### Import Order
```python
# Standard library
import json
from datetime import datetime

# Third-party
from rich.console import Console

# Local
from sdd_dry_days.core.dry_day import DryDay
```

## Storage Implementation Notes

### Current: JSON Storage
- Location: `~/.sdd_dry_days/data.json`
- Atomic writes using tempfile (prevents corruption)
- File permissions: 700 (directory), 600 (data file)
- Schema versioning for future migrations

### Future: MongoDB
- Storage abstraction designed for this migration
- Keep `DryDay` model database-agnostic
- No changes required to CLI or business logic layers when migrating

## Testing Requirements

### Coverage Targets
- Overall: >80%
- Core models: >90%
- Integration tests must use actual filesystem (with `tmp_path` or `temp_storage_dir` fixture)
- Current status: 324 tests passing (188 unit, 136 integration)

### Test Organization
- Mirror source structure in `tests/`
- Use descriptive names: `test_add_dry_day_for_today_succeeds()`
- Group related tests in classes: `TestDryDayInstantiation`
- Integration tests in `tests/integration/` test full CLI workflows
- Mock `ViewFormatter` display methods in integration tests to verify parameters

### Key Test Patterns
```python
# Use pytest fixtures for test data
def test_example(sample_dry_day):
    # sample_dry_day from conftest.py
    pass

# Use tmp_path for isolated filesystem tests
def test_storage(tmp_path):
    storage = JsonStorage(data_dir=tmp_path)
    # Test with isolated directory

# Mock view formatter in integration tests
def test_view_command(tmp_path, mocker):
    cli = CLI(data_dir=tmp_path)
    mock_display = mocker.patch.object(cli.view_formatter, 'display_list_view')
    cli._view_list()
    mock_display.assert_called_once()
```

## Important Implementation Notes

### Data Model: DryDay
- **Date normalization**: `__post_init__()` normalizes dates to midnight (removes time component)
- **Auto-timestamps**: `added_at` auto-set to current time if not provided
- **Future dates**: `is_planned` flag distinguishes future vs past/today
- **Serialization**: `to_dict()` and `from_dict()` for JSON compatibility

### Statistics Model: PeriodStats
- **9-field dataclass** for period statistics: start_date, end_date, total_days, dry_days_count, percentage, longest_streak, dry_day_dates, available_days, requested_days
- **Attribute naming**: Always use `dry_days_count`, never `dry_days` (common mistake)
- **Percentage rounding**: Percentages are rounded to 2 decimal places for display
- **Limited data indicator**: `available_days < requested_days` triggers "(limited data: X/Y days)" display
- **Used by all view commands** for consistent statistics calculation

### Current Streak Pattern
**Critical**: Current streak is a **global metric** (across all dry days), NOT period-specific:
- **Never** part of PeriodStats (which contains period-specific stats only)
- **Always** calculated separately using `StreakCalculator.calculate_current_streak(all_dry_days)`
- **Always** passed as a parameter to view display methods (never accessed as an attribute)
- **Pattern**: `display_month_view(stats: PeriodStats, current_streak: int)`
- **Wrong**: Accessing `stats.current_streak` (doesn't exist and will cause AttributeError)

### View Architecture
- **StatisticsCalculator** (static methods):
  - `get_week_dates()`: Returns Monday-Sunday range for a given date
  - `get_month_dates()`: Returns first-to-last day of month
  - `calculate_period_stats()`: Calculates all statistics for a date range
- **ViewFormatter** (composition pattern):
  - Accepts Console and OutputFormatter as dependencies
  - Handles pagination (50 entries per page with "[Press ENTER for more]")
  - Creates progress bars with color coding (red <50%, yellow 50-75%, green >75%)
  - Generates calendar grids with colored numbers (green for dry days, red for non-dry days)
  - Current day highlighted with blue background: `[green on blue]` or `[red on blue]`
  - **Filter-then-sort pattern**: Always applies filter before sort (AC-8.5)

### OutputFormatter Methods
The OutputFormatter class provides styled message methods:
- `success(message)`: Green panel with ✓ for successful operations
- `error(message)`: Red panel with ✗ for errors
- `info(message)`: Blue panel with ℹ for informational messages
- `already_exists(date)`: Blue panel for duplicate dry days
- `confirm(message)`: Yellow input prompt for confirmations
- `range_summary(...)`: Formatted summary for range additions
- `display_import_summary(...)`: Results table for import operations

### Performance Constraints
- Startup time: < 1 second (lazy load dependencies)
- Response time: < 200ms for common operations
- Support 5+ years of daily entries efficiently

### Security Considerations
- User data stored locally only (no external transmission)
- File permissions enforced (700/600)
- No telemetry or tracking
- Input validation on all date inputs

## CLI Command Structure

### Add Commands (Implemented)
```bash
sdd add                              # Add today as dry day
sdd add 2026-03-06                  # Add specific date (ISO format)
sdd add 03/06/2026                  # Add specific date (US format)
sdd add --note "Feeling great!"     # Add with note
sdd add --range 2026-03-01 2026-03-05  # Add date range
```

### Import Commands (Implemented)
```bash
sdd import <file>                    # Import dates from text file
                                     # Supports: ISO (2026-03-06), US (03/06/2026),
                                     # European (06-03-2026), compact (20260306)
                                     # Shows summary with success/error counts
```

### View Commands (Implemented)
```bash
sdd view                            # List all dry days (default: newest first)
sdd view --sort asc                 # List oldest first
sdd view --sort desc                # List newest first (default)
sdd view --filter planned           # Show only future/planned days
sdd view --filter actual            # Show only past/today days
sdd view --week                     # Week view (Mon-Sun)
sdd view --month                    # Month calendar view
sdd view --stats                    # 30/60/90 day statistics
sdd view --range 2026-03-01 2026-03-31  # Custom date range
```

### Future Commands
```bash
sdd goal set                        # Set goals (planned)
```

## Rich Library Usage

The application uses the Rich library for colorful, engaging terminal output:
- Success messages: Green with checkmark
- Errors: Red with X
- Info: Blue with info icon
- Confirmation prompts: Yellow
- All output wrapped in Rich `Panel` widgets for visual consistency

### Important Rich Library Patterns
**Emoji Width Issues**: Avoid using emojis in Panel titles or content that needs precise alignment:
- Emojis have visual width of 2 characters but may be counted as 1
- This causes jagged borders when Panels and Tables need to align
- Prefer text-only titles: `"Statistics Overview"` not `"📈 Statistics Overview"`
- If emojis are needed, use them in content where alignment isn't critical

**Panel and Table Alignment**: When displaying Panel above Table:
- Use `expand=True` on both Panel and Table for consistent width
- Avoid emojis in Panel titles for perfect border alignment
- Test visual output to ensure right borders form straight vertical line

**Calendar Grid Display**:
- Uses Rich markup for colored numbers: `[green]15[/green]` or `[red]16[/red]`
- Current day uses background color: `[green on blue]9[/green on blue]`
- Format: Two-digit numbers with consistent spacing for grid alignment
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

# Run with coverage report
pytest --cov=src/sdd_dry_days --cov-report=html

# Run with verbose output
pytest -v

# Coverage target: >80% (some modules require >90%)
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
   - `streak.py`: Streak calculation (consecutive dry days)
   - Independent of storage implementation

3. **Storage Layer** (`storage/`)
   - `base.py`: Abstract Storage interface
   - `json_storage.py`: JSON file implementation (current)
   - **Critical Pattern**: Repository pattern enables future MongoDB migration without touching business logic
   - Data stored at `~/.sdd_dry_days/data.json`

4. **Presentation Layer** (`ui/`)
   - `formatters.py`: Rich library-based colorful output
   - Success messages, error messages, progress indicators

### Data Flow
```
User Command → CLI → Business Logic → Storage → JSON File
                ↓
           Presentation (Rich UI)
```

### Key Design Patterns

**Storage Abstraction**: All storage operations go through the abstract `Storage` interface. This allows swapping JSON storage for MongoDB without changing business logic or CLI code.

**Data Model Independence**: The `DryDay` model is storage-agnostic. It serializes to/from dictionaries, letting storage implementations handle persistence.

**Test-Driven Development**: Tests are written alongside or before implementation. Each component has corresponding unit tests.

## Spec-Driven Development Workflow

This project uses a structured specification workflow. Key directories:

- `.claude/steering/`: Product vision, tech standards, project structure guidelines
- `.claude/specs/`: Feature specifications with requirements, design, and tasks

**Steering documents are the source of truth** for:
- Product vision and principles (`product.md`)
- Technology choices and architecture (`tech.md`)
- Coding standards and conventions (`structure.md`)

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
- Integration tests must use actual filesystem (with `tmp_path` fixture)

### Test Organization
- Mirror source structure in `tests/`
- Use descriptive names: `test_add_dry_day_for_today_succeeds()`
- Group related tests in classes: `TestDryDayInstantiation`

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
```

## Important Implementation Notes

### Data Model: DryDay
- **Date normalization**: `__post_init__()` normalizes dates to midnight (removes time component)
- **Auto-timestamps**: `added_at` auto-set to current time if not provided
- **Future dates**: `is_planned` flag distinguishes future vs past/today
- **Serialization**: `to_dict()` and `from_dict()` for JSON compatibility

### Performance Constraints
- Startup time: < 1 second (lazy load dependencies)
- Response time: < 200ms for common operations
- Support 5+ years of daily entries efficiently

### Security Considerations
- User data stored locally only (no external transmission)
- File permissions enforced (700/600)
- No telemetry or tracking
- Input validation on all date inputs

## CLI Command Structure (Planned)

```bash
sdd add                              # Add today as dry day
sdd add 2026-03-06                  # Add specific date (ISO format)
sdd add 03/06/2026                  # Add specific date (US format)
sdd add --note "Feeling great!"     # Add with note
sdd add --range 2026-03-01 2026-03-05  # Add date range
sdd view                            # Calendar view (future)
sdd stats                           # Statistics (future)
sdd goal set                        # Set goals (future)
```

## Rich Library Usage

The application uses the Rich library for colorful, engaging terminal output:
- Success messages: Green with checkmark
- Errors: Red with X
- Info: Blue with info icon
- Confirmation prompts: Yellow
- All output wrapped in Rich `Panel` widgets for visual consistency
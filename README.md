# SDD Dry Days

A Python CLI application for tracking alcohol-free days ("dry days"). Simple, visual, and privacy-focused.

## Overview

SDD Dry Days helps you track your alcohol-free days with minimal effort. The application emphasizes simplicity, visual motivation through colorful console output, and privacy-focused local storage.

**Core Principles:**
- Simplicity First: Make adding a dry day effortless
- Visual Motivation: Use colors and patterns to celebrate progress
- Privacy Focused: Personal data stays personal (no forced sharing)
- Non-Judgmental: Focus on positive progress, not failures
- Encouraging: Celebrate every dry day, no matter how many

## Features

- Add today as a dry day (default, fastest option)
- Add specific dates (multiple formats supported)
- Add date ranges for backfilling
- Optional notes for context
- Automatic duplicate detection
- Streak tracking (consecutive dry days)
- Colorful, encouraging terminal output
- Privacy-focused local storage

## Installation

### Development Installation

```bash
# Clone the repository
git clone <repository-url>
cd sdd_dry_days

# Install in development mode
pip install -e .

# Install development dependencies (for testing)
pip install -r requirements-dev.txt
```

### Requirements

- Python 3.8 or higher
- Dependencies will be installed automatically

## Usage

### Basic Commands

#### Add Today as a Dry Day

The fastest way to track your progress:

```bash
sdd add
```

#### Add a Specific Date

Supports multiple date formats:

```bash
# ISO format (recommended)
sdd add 2026-03-06

# US format
sdd add 03/06/2026

# European format (dash)
sdd add 06-03-2026

# European format (slash)
sdd add 06/03/2026

# Compact format
sdd add 20260306
```

#### Add with a Note

Record context or how you're feeling:

```bash
sdd add --note "First dry day!"
sdd add --note "Feeling great today"
sdd add 2026-03-06 --note "Started my journey"
```

#### Add a Date Range

Backfill multiple dates at once:

```bash
# Add a week
sdd add --range 2026-03-01 2026-03-07

# Add a month
sdd add --range 2026-03-01 2026-03-31

# Large ranges (>90 days) will prompt for confirmation
sdd add --range 2026-01-01 2026-06-01
```

### Example Output

When you add a dry day, you'll see colorful, encouraging feedback:

```
┌─────────────────────────────────────┐
│ ✓ Dry day added: 2026-03-07        │
│ 🔥 Current streak: 5 days           │
└─────────────────────────────────────┘
```

If a date already exists:

```
┌─────────────────────────────────────┐
│ ℹ Dry day already recorded for      │
│   2026-03-07                        │
└─────────────────────────────────────┘
```

## Data Storage

All data is stored locally on your machine:

- **Location**: `~/.sdd_dry_days/data.json`
- **Format**: JSON (human-readable)
- **Permissions**: User-only access (700 for directory, 600 for file)
- **Privacy**: No external transmission, no telemetry

## Development

### Project Structure

```
src/sdd_dry_days/
├── __init__.py
├── __main__.py              # Entry point for CLI
├── cli.py                   # Command-line interface logic
├── core/
│   ├── __init__.py
│   ├── dry_day.py          # DryDay model and business logic
│   └── streak.py           # Streak calculation logic
├── storage/
│   ├── __init__.py
│   ├── base.py             # Abstract Storage interface
│   └── json_storage.py     # JSON file implementation
├── ui/
│   ├── __init__.py
│   └── formatters.py       # Rich-based output formatting
└── utils/
    ├── __init__.py
    └── date_parser.py      # Date parsing utilities
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_dry_day.py

# Run with coverage report
pytest --cov=src/sdd_dry_days --cov-report=html

# Run with verbose output
pytest -v
```

**Coverage Target**: >80% overall (some modules require >90%)

### Running the Application

```bash
# Via module (useful during development)
python -m sdd_dry_days add

# Via installed command (after pip install -e .)
sdd add
```

### Code Style

- **Line length**: 88 characters (Black default)
- **Docstrings**: Google style
- **Type hints**: Required for public APIs
- **Import order**: Standard library → third-party → local

### Architecture

The application follows a four-layer architecture:

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
   - Repository pattern enables future MongoDB migration

4. **Presentation Layer** (`ui/`)
   - `formatters.py`: Rich library-based colorful output
   - Success messages, error messages, progress indicators

## Performance

- **Startup time**: < 1 second
- **Response time**: < 200ms for common operations
- **Data capacity**: Efficiently handles 5+ years of daily entries

## Security

- User data stored locally only (no external transmission)
- File permissions enforced (700/600)
- No telemetry or tracking
- Input validation on all date inputs
- Atomic writes prevent data corruption

## Future Features

Planned features include:

- Calendar view to visualize your progress
- Statistics and trends
- Goal setting and tracking
- Undo/remove entries
- MongoDB storage option for syncing across devices

## Product Vision

For more details on the product vision and principles, see [`.claude/steering/product.md`](.claude/steering/product.md).

## Contributing

This project follows a spec-driven development workflow:

- `.claude/steering/`: Product vision, tech standards, project structure guidelines
- `.claude/specs/`: Feature specifications with requirements, design, and tasks

Please review the steering documents before contributing to ensure alignment with project goals.

## License

[Add your license here]

## Support

For issues or questions, please [open an issue](link-to-issues) on the project repository.
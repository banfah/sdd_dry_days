# Project Structure: SDD Dry Days

## Repository Organization

### Monorepo Structure
Single repository containing all project code, tests, and documentation.

```
sdd_dry_days/
├── src/
│   └── sdd_dry_days/
│       ├── __init__.py
│       ├── __main__.py          # Entry point for CLI
│       ├── cli.py                # Command-line interface logic
│       ├── core/                 # Core business logic
│       │   ├── __init__.py
│       │   ├── dry_day.py        # Dry day models and logic
│       │   ├── goal.py           # Goal tracking logic
│       │   └── stats.py          # Statistics calculations
│       ├── storage/              # Data persistence layer
│       │   ├── __init__.py
│       │   ├── base.py           # Abstract storage interface
│       │   ├── json_storage.py   # JSON file implementation
│       │   └── mongo_storage.py  # MongoDB implementation (future)
│       ├── ui/                   # User interface components
│       │   ├── __init__.py
│       │   ├── calendar.py       # Calendar view rendering
│       │   ├── theme.py          # Theme management
│       │   └── formatters.py     # Output formatting utilities
│       └── config.py             # Configuration management
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Pytest fixtures and configuration
│   ├── unit/                     # Unit tests
│   │   ├── test_dry_day.py
│   │   ├── test_goal.py
│   │   └── test_stats.py
│   ├── integration/              # Integration tests
│   │   ├── test_storage.py
│   │   └── test_cli.py
│   └── fixtures/                 # Test data
│       └── sample_data.json
├── docs/                         # Documentation
│   ├── README.md
│   └── user_guide.md
├── .claude/                      # Claude Code configuration
│   └── steering/                 # Steering documents
│       ├── product.md
│       ├── tech.md
│       └── structure.md
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
├── setup.py                      # Package setup
├── .gitignore
├── README.md                     # Project overview
└── pytest.ini                    # Pytest configuration
```

## Coding Standards

### Python Conventions (PEP 8)

#### Naming Conventions
- **Modules**: lowercase with underscores (`dry_day.py`, `json_storage.py`)
- **Classes**: PascalCase (`DryDay`, `GoalTracker`, `JsonStorage`)
- **Functions/Methods**: lowercase with underscores (`add_dry_day`, `calculate_streak`)
- **Constants**: UPPERCASE with underscores (`MAX_STREAK`, `DEFAULT_THEME`)
- **Private**: prefix with underscore (`_internal_method`, `_cache`)

#### Code Style
- **Line length**: 88 characters (Black default) or 79 (PEP 8 strict)
- **Indentation**: 4 spaces
- **Quotes**: Consistent (prefer double quotes for strings)
- **Imports**: Standard library → third-party → local (separated by blank lines)

#### Documentation
- **Docstrings**: Google or NumPy style
- **Module docstrings**: At top of file explaining purpose
- **Function docstrings**: For public functions
- **Inline comments**: Only where logic is non-obvious

Example:
```python
def calculate_dry_days(start_date: datetime, end_date: datetime) -> int:
    """Calculate the number of dry days in a date range.

    Args:
        start_date: Beginning of the date range
        end_date: End of the date range (inclusive)

    Returns:
        The count of dry days in the range
    """
    pass
```

### Type Hints
- Use type hints for function signatures where helpful
- Not mandatory but encouraged for public APIs
- Use `typing` module for complex types

### Error Handling
- Use specific exceptions (not bare `except:`)
- Create custom exceptions for domain errors
- Provide helpful error messages to users

## Testing Philosophy

### Test Emphasis
Testing is a priority in this project. Every feature should have corresponding tests.

#### Test Structure
- **Unit tests**: Test individual functions/classes in isolation
- **Integration tests**: Test components working together
- **Fixture-based**: Use pytest fixtures for common test data
- **Coverage target**: Aim for >80% code coverage

#### Test Naming
```python
def test_add_dry_day_for_today_succeeds():
    """Test adding a dry day for today's date."""
    pass

def test_calculate_streak_with_gap_resets():
    """Test that streak resets when there's a gap in dry days."""
    pass
```

#### Test Organization
- Mirror source structure in tests/
- Group related tests in classes if helpful
- Use descriptive test names that explain what's being tested

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/sdd_dry_days --cov-report=html

# Run specific test file
pytest tests/unit/test_dry_day.py

# Run tests with verbose output
pytest -v
```

## File Organization Patterns

### Module Responsibility
Each module should have a single, clear responsibility:
- `dry_day.py`: Core dry day model and operations
- `goal.py`: Goal setting and tracking logic
- `stats.py`: Statistical calculations and analysis
- `json_storage.py`: JSON file I/O operations

### Imports
```python
# Standard library
import json
from datetime import datetime, timedelta
from pathlib import Path

# Third-party
from rich.console import Console
from rich.calendar import Calendar

# Local
from sdd_dry_days.core.dry_day import DryDay
from sdd_dry_days.storage.base import Storage
```

### Configuration
- User configuration in `~/.sdd_dry_days/config.json`
- Data storage in `~/.sdd_dry_days/data.json`
- Use `pathlib` for cross-platform path handling

## Development Workflow

### Adding a New Feature

1. **Write tests first** (TDD approach encouraged)
   ```bash
   # Create test file
   tests/unit/test_new_feature.py
   ```

2. **Implement feature**
   ```bash
   # Create source file
   src/sdd_dry_days/core/new_feature.py
   ```

3. **Run tests**
   ```bash
   pytest tests/unit/test_new_feature.py
   ```

4. **Integration**
   - Wire up to CLI if needed
   - Add integration tests
   - Update documentation

5. **Verify**
   - Run full test suite
   - Check coverage
   - Manual testing

### Code Review Checklist
- [ ] Follows PEP 8 conventions
- [ ] Has corresponding tests
- [ ] Tests pass
- [ ] Docstrings for public functions
- [ ] No hardcoded paths or values
- [ ] Error handling implemented
- [ ] Works cross-platform

## Common Patterns

### Storage Abstraction
```python
# Use base class for storage operations
from sdd_dry_days.storage.base import Storage

class JsonStorage(Storage):
    def save_dry_day(self, date: datetime) -> None:
        # Implementation
        pass
```

### CLI Commands
```python
# Use clear, action-oriented command names
# sdd add              # Add today as dry day
# sdd add 2024-03-01   # Add specific date
# sdd view             # Show calendar
# sdd stats            # Show statistics
# sdd goal set         # Set a new goal
```

### Data Models
```python
# Use dataclasses or simple classes for models
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DryDay:
    date: datetime
    note: str = ""
```

## Documentation

### README.md
- Project overview
- Quick start guide
- Installation instructions
- Basic usage examples

### Code Documentation
- Module docstrings explaining purpose
- Function docstrings for public APIs
- Inline comments for complex logic only

### User Documentation
- Command reference
- Examples and tutorials
- FAQ section

## Version Control

### Git Practices
- Clear, descriptive commit messages
- Feature branches for new development
- Keep commits atomic and focused
- Tag releases (v0.1.0, v0.2.0, etc.)

### .gitignore
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDE
.idea/
.vscode/
*.swp

# Data (don't commit user data)
*.json
!tests/fixtures/*.json
```

## Future Structure Considerations

### Plugin System
```
plugins/
├── __init__.py
└── custom_goal_types.py
```

### API Layer (if web interface added)
```
src/sdd_dry_days/
└── api/
    ├── __init__.py
    └── routes.py
```

### Multiple Languages (if internationalization needed)
```
locales/
├── en.json
└── th.json
```
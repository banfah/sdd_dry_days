# Implementation Plan: Add Dry Days

## Task Overview

This implementation plan breaks down the "Add Dry Days" feature into atomic, executable tasks. Each task is designed to be completed independently by an agent in 15-30 minutes, touching 1-3 related files maximum. The tasks follow a bottom-up approach: establishing the foundation (models, utilities) first, then building up through storage, business logic, and finally the CLI interface.

**Implementation Strategy:** Test-Driven Development (TDD) approach where possible - write tests before or alongside implementation.

## Steering Document Compliance

All tasks follow the conventions established in steering documents:

- **structure.md Compliance**: Files organized in `src/sdd_dry_days/` with proper module structure (core/, storage/, ui/, utils/)
- **tech.md Compliance**: Python 3.8+, standard library + Rich, pytest for testing, PEP 8 conventions
- **product.md Compliance**: Focus on simplicity, low friction, privacy-focused design

## Atomic Task Requirements

Each task in this plan meets these criteria:
- ✓ **File Scope**: Touches 1-3 related files maximum
- ✓ **Time Boxing**: Completable in 15-30 minutes by experienced developer
- ✓ **Single Purpose**: One testable outcome per task
- ✓ **Specific Files**: Exact file paths specified
- ✓ **Agent-Friendly**: Clear acceptance criteria and minimal context switching

## Tasks

### Phase 1: Project Foundation

- [x] 1. Create project directory structure
  - **Files to create**:
    - `src/sdd_dry_days/__init__.py`
    - `src/sdd_dry_days/core/__init__.py`
    - `src/sdd_dry_days/storage/__init__.py`
    - `src/sdd_dry_days/ui/__init__.py`
    - `src/sdd_dry_days/utils/__init__.py`
    - `tests/__init__.py`
    - `tests/unit/__init__.py`
    - `tests/integration/__init__.py`
    - `tests/fixtures/__init__.py`
  - Create all directories following structure.md layout
  - Add empty `__init__.py` files to make packages importable
  - Purpose: Establish Python package structure
  - **Acceptance**: All directories exist, Python can import packages
  - _Requirements: All (foundation)_
  - _Leverage: structure.md directory layout_

- [x] 2. Create package configuration files
  - **Files to create**:
    - `setup.py`
    - `requirements.txt`
    - `requirements-dev.txt`
    - `pytest.ini`
    - `.gitignore`
  - Copy setup.py from design.md Dependencies section
  - Add `rich>=13.0.0` to requirements.txt
  - Add pytest, pytest-cov, black, flake8 to requirements-dev.txt
  - Configure pytest with pytest.ini
  - Purpose: Enable package installation and dependency management
  - **Acceptance**: `pip install -e .` works, pytest can be run
  - _Requirements: All (foundation)_
  - _Leverage: design.md Dependencies section_

### Phase 2: Core Data Models

- [x] 3. Create DryDay model in src/sdd_dry_days/core/dry_day.py
  - **File**: `src/sdd_dry_days/core/dry_day.py`
  - Implement `DryDay` dataclass with fields: date, note, added_at, is_planned
  - Implement `__post_init__()` for date normalization and added_at default
  - Implement `to_dict()` method for JSON serialization
  - Implement `from_dict()` classmethod for JSON deserialization
  - Implement `is_duplicate()` method for date comparison
  - Add type hints and docstrings (Google style)
  - Purpose: Foundation data model for all dry day operations
  - **Acceptance**: DryDay can be instantiated, serialized, deserialized
  - _Requirements: 1.1, 2.1, 4.1, 5.1_
  - _Leverage: design.md Component 1 specification_

- [x] 4. Create unit tests for DryDay model in tests/unit/test_dry_day.py
  - **File**: `tests/unit/test_dry_day.py`
  - Test DryDay instantiation with defaults
  - Test `to_dict()` serialization produces correct JSON structure
  - Test `from_dict()` deserialization recreates DryDay correctly
  - Test `is_duplicate()` logic for same and different dates
  - Test `__post_init__()` date normalization (removes time component)
  - Test `__post_init__()` auto-sets added_at if not provided
  - Purpose: Ensure DryDay model reliability
  - **Acceptance**: All tests pass, >90% coverage of dry_day.py
  - _Requirements: 1.1, 2.1, 4.1, 5.1_
  - _Leverage: design.md Testing Strategy, pytest fixtures_

### Phase 3: Date Parsing Utilities

- [x] 5. Create DateParser utility in src/sdd_dry_days/utils/date_parser.py
  - **File**: `src/sdd_dry_days/utils/date_parser.py`
  - Create `DateParseError` exception class
  - Implement `DateParser.parse()` classmethod supporting formats: YYYY-MM-DD, MM/DD/YYYY, DD-MM-YYYY, DD/MM/YYYY, YYYYMMDD
  - Implement `DateParser.validate_leap_year()` classmethod
  - Implement `DateParser.generate_date_range()` classmethod
  - Add helpful error messages with format examples
  - Purpose: Flexible date input parsing
  - **Acceptance**: Can parse all specified formats, rejects invalid formats with helpful messages
  - _Requirements: 2.2, 2.3, 3.1, 3.5_
  - _Leverage: design.md Component 4 specification_

- [x] 6. Create unit tests for DateParser in tests/unit/test_date_parser.py
  - **File**: `tests/unit/test_date_parser.py`
  - Test parsing each supported format (ISO, US, EU variants)
  - Test invalid format raises DateParseError with helpful message
  - Test leap year validation accepts Feb 29 in leap years (2024, 2020)
  - Test leap year validation rejects Feb 29 in non-leap years (2025, 2023)
  - Test date range generation for valid ranges
  - Test date range validation rejects end < start
  - Test empty/whitespace input handling
  - Purpose: Ensure date parsing robustness
  - **Acceptance**: All tests pass, >90% coverage of date_parser.py
  - _Requirements: 2.2, 2.3, 3.1, 3.5_
  - _Leverage: design.md Testing Strategy_

### Phase 4: Storage Layer - Interfaces

- [x] 7. Create abstract Storage interface in src/sdd_dry_days/storage/base.py
  - **File**: `src/sdd_dry_days/storage/base.py`
  - Import ABC and abstractmethod from abc module
  - Create abstract `Storage` class
  - Define abstract methods: add_dry_day, get_dry_day, get_all_dry_days, update_dry_day, exists, get_dry_days_in_range
  - Add type hints for all methods
  - Add docstrings explaining contract for each method
  - Purpose: Storage abstraction enabling multiple backends (JSON, MongoDB)
  - **Acceptance**: Abstract class defined, cannot be instantiated directly
  - _Requirements: 4.1, 4.2, 4.3_
  - _Leverage: design.md Component 2 specification_

### Phase 5: Storage Layer - JSON Implementation

- [x] 8. Create JsonStorage class in src/sdd_dry_days/storage/json_storage.py (Part 1: Setup and Read)
  - **File**: `src/sdd_dry_days/storage/json_storage.py`
  - Import required modules: Path, json, tempfile, shutil, datetime
  - Implement `JsonStorage` class inheriting from `Storage`
  - Define class constants: DEFAULT_DATA_DIR, DEFAULT_DATA_FILE, SCHEMA_VERSION
  - Implement `__init__()` method accepting optional data_dir parameter
  - Implement `_ensure_data_directory()` method to create directory with mode 0o700
  - Implement `_read_data()` method with JSON parsing and validation
  - Add error handling for corrupted files (backup and reinitialize)
  - Purpose: JSON storage initialization and reading
  - **Acceptance**: Can initialize storage, read valid JSON, handle corrupted files
  - _Requirements: 4.1, 4.2, 4.3, 4.6_
  - _Leverage: design.md Component 3 specification_

- [x] 9. Create JsonStorage class in src/sdd_dry_days/storage/json_storage.py (Part 2: Write Operations)
  - **File**: `src/sdd_dry_days/storage/json_storage.py` (continue from task 8)
  - Implement `_write_data()` method with atomic writes using tempfile
  - Set file permissions to 0o600 on written file
  - Implement atomic rename for data integrity
  - Add cleanup of temp file on error
  - Purpose: Safe, atomic JSON writes
  - **Acceptance**: Writes are atomic, permissions set correctly, temp files cleaned up
  - _Requirements: 4.4, 4.5_
  - _Leverage: design.md Component 3 specification, atomic write pattern_

- [x] 10. Create JsonStorage class in src/sdd_dry_days/storage/json_storage.py (Part 3: CRUD Operations)
  - **File**: `src/sdd_dry_days/storage/json_storage.py` (continue from task 9)
  - Implement `add_dry_day()` method with duplicate detection
  - Implement `get_dry_day()` method to retrieve by date
  - Implement `get_all_dry_days()` method returning sorted list
  - Implement `update_dry_day()` method for updating existing entries
  - Implement `exists()` method for duplicate checking
  - Implement `get_dry_days_in_range()` method for date range queries
  - Purpose: Complete storage interface implementation
  - **Acceptance**: All Storage interface methods implemented and functional
  - _Requirements: 1.1, 1.4, 2.1, 3.1, 3.3, 4.1, 5.4_
  - _Leverage: design.md Component 3 specification, Storage interface_

- [x] 11. Create integration tests for JsonStorage in tests/integration/test_storage.py
  - **File**: `tests/integration/test_storage.py`
  - Use pytest tmp_path fixture for isolated test directory
  - Test data directory creation with correct permissions (0o700)
  - Test data file creation with correct permissions (0o600)
  - Test add_dry_day adds new entry and returns True
  - Test add_dry_day detects duplicates and returns False
  - Test get_dry_day retrieves existing entry
  - Test get_dry_day returns None for non-existent date
  - Test get_all_dry_days returns sorted list
  - Test update_dry_day updates existing entry
  - Test exists returns True/False correctly
  - Test get_dry_days_in_range filters correctly
  - Test corrupted file recovery (backup and reinitialize)
  - Test atomic write (simulate crash during write)
  - Purpose: Ensure storage reliability with actual filesystem
  - **Acceptance**: All tests pass, storage operations work correctly with real files
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_
  - _Leverage: design.md Testing Strategy, pytest fixtures_

### Phase 6: Business Logic - Streak Calculation

- [x] 12. Create StreakCalculator in src/sdd_dry_days/core/streak.py
  - **File**: `src/sdd_dry_days/core/streak.py`
  - Import datetime, timedelta, List from typing
  - Import DryDay from core.dry_day
  - Create `StreakCalculator` class
  - Implement `calculate_current_streak()` static method
  - Logic: Sort dry days descending, check if today is included, count consecutive days backward
  - Return 0 if today not included or no dry days
  - Purpose: Calculate consecutive dry days ending today
  - **Acceptance**: Returns correct streak count for various scenarios
  - _Requirements: 1.3_
  - _Leverage: design.md Component 5 specification_

- [x] 13. Create unit tests for StreakCalculator in tests/unit/test_streak.py
  - **File**: `tests/unit/test_streak.py`
  - Test empty list returns 0
  - Test today not included returns 0
  - Test single day (today only) returns 1
  - Test consecutive days ending today returns correct count
  - Test gap in sequence resets streak
  - Test multiple gaps only counts from most recent
  - Test unsorted input (verify sorting works)
  - Purpose: Ensure streak calculation accuracy
  - **Acceptance**: All tests pass, >90% coverage of streak.py
  - _Requirements: 1.3_
  - _Leverage: design.md Testing Strategy_

### Phase 7: Presentation Layer - Output Formatting

- [x] 14. Create OutputFormatter in src/sdd_dry_days/ui/formatters.py
  - **File**: `src/sdd_dry_days/ui/formatters.py`
  - Import Console, Panel, Text from rich
  - Create `OutputFormatter` class
  - Implement `__init__()` to initialize Console
  - Implement `success()` method for dry day added confirmation (green, with date and streak)
  - Implement `already_exists()` method for duplicate info (blue)
  - Implement `range_summary()` method for date range results (green with counts)
  - Implement `error()` method for error messages (red with details)
  - Implement `confirm()` method for yes/no prompts (yellow)
  - Purpose: Consistent, colorful, encouraging user feedback
  - **Acceptance**: All formatter methods create Rich panels with appropriate styling
  - _Requirements: 1.2, 1.3, 1.4, 3.2, 3.4_
  - _Leverage: design.md Component 6 specification, Rich library_

- [x] 15. Create unit tests for OutputFormatter in tests/unit/test_formatters.py
  - **File**: `tests/unit/test_formatters.py`
  - Mock Rich Console to avoid actual terminal output
  - Test success message format (check for date, streak, green styling)
  - Test already_exists message format (check for date, blue styling)
  - Test range_summary format (check for counts, skipped info)
  - Test error message format (check for message, details, red styling)
  - Test confirm prompt (mock input response)
  - Purpose: Ensure output formatting correctness
  - **Acceptance**: All tests pass, formatter methods tested with mocked console
  - _Requirements: 1.2, 1.3, 1.4, 3.2, 3.4_
  - _Leverage: design.md Testing Strategy, pytest mocking_

### Phase 8: CLI Layer - Argument Parsing and Command Handling

- [x] 16. Create CLI class in src/sdd_dry_days/cli.py (Part 1: Parser Setup)
  - **File**: `src/sdd_dry_days/cli.py`
  - Import argparse, datetime, List
  - Import all required components: DryDay, StreakCalculator, JsonStorage, DateParser, DateParseError, OutputFormatter
  - Create `CLI` class
  - Implement `__init__()` to initialize storage and formatter
  - Implement `_create_parser()` method to create ArgumentParser
  - Define "add" subcommand with arguments: date (optional positional), --note/-n, --range/-r
  - Purpose: CLI argument parsing structure
  - **Acceptance**: Parser created, can parse add command with all argument variations
  - _Requirements: 1.1, 2.1, 3.1, 5.1_
  - _Leverage: design.md Component 7 specification_

- [x] 17. Create CLI class in src/sdd_dry_days/cli.py (Part 2: Add Command Handlers)
  - **File**: `src/sdd_dry_days/cli.py` (continue from task 16)
  - Implement `run()` method to parse args and route to handlers
  - Implement `_handle_add()` method to dispatch based on args (range vs single vs today)
  - Implement `_add_today()` method: create DryDay for today, add to storage, calculate streak, show success/duplicate message
  - Implement `_add_single_date()` method: parse date, validate leap year, determine is_planned, add to storage, show feedback
  - Implement `_add_date_range()` method: parse start/end, generate dates, confirm if >90 days, add all dates, show summary
  - Add try/except blocks for DateParseError and general exceptions
  - Purpose: Complete CLI command handling logic
  - **Acceptance**: All add command variations work correctly with proper error handling
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.6, 5.1, 5.2, 5.3, 5.4_
  - _Leverage: design.md Component 7 specification_

- [x] 18. Create integration tests for CLI in tests/integration/test_cli.py
  - **File**: `tests/integration/test_cli.py`
  - Use pytest tmp_path fixture for isolated storage
  - Mock OutputFormatter to capture output calls instead of printing
  - Test `sdd add` (no args) adds today
  - Test `sdd add 2026-03-06` adds specific date
  - Test `sdd add 03/06/2026` parses US format
  - Test `sdd add --note "test"` saves note
  - Test `sdd add --range 2026-03-01 2026-03-05` adds range
  - Test duplicate date shows "already exists" message
  - Test invalid date format shows error
  - Test invalid date range (end < start) shows error
  - Test large range (>90 days) prompts for confirmation
  - Purpose: End-to-end CLI workflow validation
  - **Acceptance**: All CLI commands work correctly with storage and formatting
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4, 3.6, 5.1, 5.3_
  - _Leverage: design.md Testing Strategy_

### Phase 9: Application Entry Point

- [x] 19. Create entry point in src/sdd_dry_days/__main__.py
  - **File**: `src/sdd_dry_days/__main__.py`
  - Import CLI from .cli
  - Define `main()` function that instantiates CLI and calls run()
  - Add `if __name__ == "__main__":` block calling main()
  - Add docstring explaining this is the entry point
  - Purpose: Enable `python -m sdd_dry_days` and `sdd` command execution
  - **Acceptance**: Can run `python -m sdd_dry_days add` successfully
  - _Requirements: All (entry point)_
  - _Leverage: design.md Component 8 specification_

- [x] 20. Create pytest configuration and fixtures in tests/conftest.py
  - **File**: `tests/conftest.py`
  - Import pytest, datetime, Path
  - Import DryDay from sdd_dry_days.core.dry_day
  - Create `sample_dry_day` fixture returning a DryDay instance
  - Create `sample_dry_days_list` fixture returning list of DryDay instances
  - Create `temp_storage_dir` fixture using tmp_path for isolated storage
  - Create `mock_today` fixture to control "today" in tests
  - Purpose: Shared test fixtures for consistent test data
  - **Acceptance**: Fixtures available in all test files, tests can use them
  - _Requirements: All (testing infrastructure)_
  - _Leverage: design.md Testing Strategy, pytest fixtures_

### Phase 10: Final Integration and Testing

- [x] 21. Run full test suite and verify coverage
  - **Commands to run**:
    - `pytest` (run all tests)
    - `pytest --cov=src/sdd_dry_days --cov-report=html` (generate coverage report)
  - Review coverage report in htmlcov/index.html
  - Verify >80% coverage target met
  - Fix any failing tests
  - Purpose: Ensure all components work together and coverage target met
  - **Acceptance**: All tests pass, coverage >80%
  - _Requirements: All_
  - _Leverage: design.md Testing Strategy_

- [x] 22. Manual testing - Fresh installation scenario
  - Delete `~/.sdd_dry_days/` directory if exists
  - Run `sdd add` and verify directory/file created with correct permissions
  - Check `~/.sdd_dry_days/data.json` contains valid JSON
  - Verify output shows success message with today's date
  - Purpose: Validate first-run experience
  - **Acceptance**: Fresh install works, permissions correct, data persisted
  - _Requirements: 4.1, 4.2, 4.3_
  - _Leverage: design.md Manual Testing Scenarios_

- [x] 23. Manual testing - Date format variations
  - Run `sdd add 2026-03-06` (ISO format)
  - Run `sdd add 03/06/2026` (US format)
  - Run `sdd add 06-03-2026` (EU format)
  - Run `sdd add invalid` (should show error with examples)
  - Verify all valid formats accepted, invalid rejected with helpful message
  - Purpose: Validate date parsing flexibility
  - **Acceptance**: All valid formats work, errors are helpful
  - _Requirements: 2.2, 2.3_
  - _Leverage: design.md Manual Testing Scenarios_

- [x] 24. Manual testing - Duplicate handling and streak calculation
  - Run `sdd add` twice in the same day
  - Verify second attempt shows "already recorded" message
  - Add consecutive days and verify streak count increases
  - Add non-consecutive day and verify streak resets
  - Purpose: Validate duplicate detection and streak logic
  - **Acceptance**: Duplicates handled gracefully, streaks calculated correctly
  - _Requirements: 1.3, 1.4_
  - _Leverage: design.md Manual Testing Scenarios_

- [x] 25. Manual testing - Date range and notes
  - Run `sdd add --range 2026-03-01 2026-03-05`
  - Verify summary shows 5 dates added
  - Run same command again, verify shows 0 added, 5 skipped
  - Run `sdd add --note "Test note"` and verify note saved in JSON
  - Run `sdd add --range 2026-01-01 2026-06-01` and verify confirmation prompt
  - Purpose: Validate range addition and notes
  - **Acceptance**: Ranges work, notes persist, large ranges prompt
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.6, 5.1, 5.3_
  - _Leverage: design.md Manual Testing Scenarios_

### Phase 11: Documentation

- [x] 26. Create project README.md
  - **File**: `README.md`
  - Add project title and description
  - Add installation instructions (`pip install -e .`)
  - Add usage examples for all add command variations
  - Add development setup instructions
  - Add testing instructions
  - Add link to product vision (optional)
  - Purpose: User-facing documentation
  - **Acceptance**: README complete and accurate
  - _Requirements: All (documentation)_
  - _Leverage: design.md CLI examples_

## Task Summary

**Total Tasks**: 26 tasks organized into 11 phases

**Breakdown by Phase**:
1. Project Foundation: 2 tasks
2. Core Data Models: 2 tasks
3. Date Parsing Utilities: 2 tasks
4. Storage Layer - Interfaces: 1 task
5. Storage Layer - JSON Implementation: 4 tasks
6. Business Logic - Streak Calculation: 2 tasks
7. Presentation Layer - Output Formatting: 2 tasks
8. CLI Layer - Argument Parsing: 3 tasks
9. Application Entry Point: 2 tasks
10. Final Integration and Testing: 5 tasks
11. Documentation: 1 task

**Estimated Time**: 26 tasks × 20 minutes average = ~8.5 hours of development time

**Parallel Execution Opportunities**:
- After Phase 1 complete, Phases 2-4 can be done in parallel (data models, utilities, storage interface are independent)
- Phase 6 (streak) and Phase 7 (formatting) can be done in parallel after Phase 2 complete
- Manual testing tasks (22-25) can be done in parallel

## Implementation Notes

### Testing Strategy
- Write unit tests immediately after implementing each component (TDD approach)
- Run tests frequently during development (`pytest -v`)
- Use `pytest --cov` to monitor coverage as you go
- Integration tests come after unit tests for each layer

### Development Workflow
1. Start with Phase 1 (foundation)
2. Implement each task sequentially within a phase
3. Run tests after each task completion
4. Commit after each completed task (or small group of related tasks)
5. Move to next phase only after all tests in current phase pass

### Common Pitfalls to Avoid
- **Don't skip tests**: Every component should have corresponding tests
- **Don't hardcode paths**: Use `Path.home()` and configurable paths
- **Don't ignore errors**: Handle all exceptions gracefully with user-friendly messages
- **Don't forget permissions**: Set 700/600 on directories/files
- **Don't skip manual testing**: Automated tests don't catch everything

### Quality Checklist per Task
- [ ] Code follows PEP 8 conventions
- [ ] Type hints added for function signatures
- [ ] Docstrings added for public functions/classes
- [ ] Unit/integration tests written and passing
- [ ] No hardcoded values (use constants or config)
- [ ] Error handling implemented
- [ ] Works on the specified platform (macOS primary)

## Next Steps After Implementation

After all tasks are complete:
1. Create a git repository and commit all code
2. Tag release as `v0.1.0` (MVP)
3. Test installation on clean system
4. Begin work on next feature (Calendar View, Goals, or Statistics)
5. Consider publishing to PyPI for easier installation

## Future Feature Integration Points

Components built in this spec will be reused by:
- **Calendar View**: Will use `Storage.get_all_dry_days()` and `DryDay` model
- **Goal Tracking**: Will use `StreakCalculator` and `Storage` interface
- **Statistics**: Will use `Storage.get_dry_days_in_range()` for period calculations
- **MongoDB Migration**: Will implement new `MongoStorage(Storage)` without changing other layers
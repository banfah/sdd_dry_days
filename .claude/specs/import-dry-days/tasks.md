# Implementation Plan: Import Dry Days

## Task Overview

The import-dry-days feature implementation follows a simple, focused approach: extend existing CLI and OutputFormatter components to enable batch import from text files. All business logic (date parsing, storage, duplicate detection) already exists and will be reused without modification.

**Implementation Strategy**:
1. Add CLI import command handler in 3 atomic steps (1 file, extended method)
2. Add formatter import summary display (1 file, new method)
3. Wire up CLI argument parser (1 file, minor change)
4. Comprehensive testing in 7 atomic steps (2 test files)

**Estimated Effort**: 4-6 hours total implementation time (12 atomic tasks, 20-30 min each)

## Steering Document Compliance

**Following structure.md**:
- Extends existing files in appropriate layers (CLI, UI)
- Uses existing core components unchanged (DateParser, DryDay, Storage)
- Mirrors test structure (unit tests in tests/unit/, integration in tests/integration/)
- Follows naming conventions (lowercase_with_underscores)
- Google-style docstrings for all methods

**Following tech.md**:
- Python standard library only (pathlib, open())
- Rich library for formatted display
- Works through Storage abstraction
- No external dependencies

## Atomic Task Requirements

Each task below meets the atomic criteria:
- **File Scope**: Touches 1-2 related files maximum
- **Time Boxing**: Completable in 15-30 minutes
- **Single Purpose**: One testable outcome per task
- **Specific Files**: Exact file paths specified
- **Agent-Friendly**: Clear input/output with minimal context switching

## Tasks

### Phase 1: Core Implementation (5 tasks)

- [ ] 1. Core CLI Implementation
  - [x] 1.1. Add import command file operations to CLI
    - File: src/sdd_dry_days/cli.py (extend existing)
    - Add method: `_handle_import(self, args)` skeleton
    - Implementation:
      - Validate file path exists using `pathlib.Path`
      - Handle `FileNotFoundError` → display "File not found: <filepath>. Please check the path and try again."
      - Handle `PermissionError` → display "Cannot read file: <filepath>. Check file permissions."
      - Open file with context manager (`with open()`)
      - Read all lines with `readlines()`
      - Check if empty (len == 0) → display "File is empty. Add dates (one per line) and try again."
      - Return list of lines for further processing
    - Error handling: Display errors via `self.formatter.error()` and exit early
    - Purpose: File reading and validation only
    - _Leverage: pathlib.Path, self.formatter.error()_
    - _Requirements: 1.1, 1.2, 3.1, 3.2, 3.3_

  - [x] 1.2. Add import line parsing logic to CLI
    - File: src/sdd_dry_days/cli.py (extend `_handle_import`)
    - **Depends on**: Task 1.1
    - Implementation:
      - Iterate through lines with enumerate (start=1 for line numbers)
      - Strip whitespace from each line
      - Skip empty lines (after strip)
      - Skip comment lines (lines starting with #)
      - Parse each line with `DateParser.parse(line)`
      - Catch `DateParseError` per line → add to errors list (line_num, line, error_msg)
      - Continue processing on errors (don't stop)
      - Track total_lines count (excluding empty/comments)
    - Return: parsed_dates list and errors list
    - Purpose: Date parsing and error tracking
    - _Leverage: DateParser.parse()_
    - _Requirements: 1.2, 1.3, 1.4, 3.4, 3.5, 4.2, 4.3, 4.4_

  - [x] 1.3. Add import storage operations to CLI
    - File: src/sdd_dry_days/cli.py (extend `_handle_import`)
    - **Depends on**: Task 1.2
    - Implementation:
      - Create `DryDay` instance for each parsed date
      - Call `self.storage.add_dry_day(dry_day)` for each
      - Track result: if True → increment success_count, if False → increment duplicate_count
      - After all dates processed: call `self.formatter.display_import_summary(total_lines, success_count, duplicate_count, errors)`
    - Purpose: Storage operations and summary display coordination
    - _Leverage: DryDay(), self.storage.add_dry_day(), self.formatter.display_import_summary()_
    - _Requirements: 1.5, 2.1, 2.2, 2.3, 6.2, 6.3_

- [x] 2. Add import summary display to OutputFormatter
  - File: src/sdd_dry_days/ui/formatters.py (extend existing OutputFormatter class)
  - Add method: `display_import_summary(self, total_lines: int, success_count: int, duplicate_count: int, errors: List[Tuple[int, str, str]])`
  - Implementation:
    - Create Rich Panel with title "📥 Import Summary"
    - Display total lines processed
    - Display successfully added count (green color #00FF00 if > 0)
    - Display duplicates skipped count
    - Display errors count
    - If errors exist: create Rich Table with columns (Line, Content, Reason)
    - Add each error to table
    - Display success message "✓ Import completed successfully!" if success_count > 0
    - Special case: if all duplicates, display "All dates already recorded. No new dry days added."
  - Purpose: Formatted import results display
  - _Leverage: Rich Panel, Rich Table, Rich Text, existing OutputFormatter patterns_
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 2.2, 2.3_

- [x] 3. Add import subcommand to CLI argument parser
  - File: src/sdd_dry_days/cli.py (extend _create_parser() method)
  - Add import subparser to argparse structure
  - Add filepath positional argument
  - Wire up to route to `_handle_import` in `run()` method
  - Implementation:
    - In `_create_parser()`: add `import_parser = subparsers.add_parser("import", help="...")`
    - Add `import_parser.add_argument("filepath", type=str, help="...")`
    - In `run()`: add `elif parsed_args.command == "import": self._handle_import(parsed_args)`
  - Purpose: CLI routing for import command
  - _Leverage: Existing argparse subparser pattern from add/view commands_
  - _Requirements: 1.1, 4.1_

### Phase 2: Testing (7 tasks)

- [x] 4. Unit Tests - File Operations
  - [x] 4.1. Create unit tests for import handler file operations
    - File: tests/unit/test_import.py (new file)
    - **Depends on**: Task 1.1
    - Test class: `TestImportFileOperations`
    - Test methods:
      - `test_import_with_file_not_found_displays_error`
      - `test_import_with_permission_error_displays_error`
      - `test_import_with_empty_file_displays_error`
      - `test_import_skips_empty_lines`
      - `test_import_skips_comment_lines`
    - Mock: `pathlib.Path.exists()`, `open()`, `formatter.error()`, `formatter.display_import_summary()`
    - Purpose: Verify file handling and error scenarios
    - _Leverage: pytest, unittest.mock, tmp_path fixture_
    - _Requirements: 1.2, 3.1, 3.2, 3.3, 4.3_

  - [x] 4.2. Create unit tests for import handler date parsing
    - File: tests/unit/test_import.py (continue from task 4.1)
    - **Depends on**: Task 1.2
    - Test class: `TestImportDateParsing`
    - Test methods:
      - `test_import_parses_iso_format_dates`
      - `test_import_parses_us_format_dates`
      - `test_import_parses_mixed_formats`
      - `test_import_logs_error_for_invalid_date_format`
      - `test_import_continues_processing_after_parse_error`
    - Mock: `DateParser.parse()`, `storage.add_dry_day()`, `formatter.display_import_summary()`
    - Purpose: Verify date parsing integration
    - _Leverage: DateParser, unittest.mock_
    - _Requirements: 1.3, 1.4, 2.1, 3.4, 3.5, 4.4_

  - [x] 4.3. Create unit tests for import handler duplicate detection
    - File: tests/unit/test_import.py (continue from task 4.2)
    - **Depends on**: Task 1.3
    - Test class: `TestImportDuplicateHandling`
    - Test methods:
      - `test_import_counts_successfully_added_dates`
      - `test_import_counts_duplicate_dates_separately`
      - `test_import_displays_all_duplicates_message`
    - Mock: `storage.add_dry_day()` to return True (success) or False (duplicate)
    - Purpose: Verify duplicate tracking
    - _Leverage: unittest.mock_
    - _Requirements: 2.1, 2.2, 2.3_

- [ ] 5. Unit Tests - Formatter
  - [ ] 5.1. Create unit tests for import summary formatter
    - File: tests/unit/test_formatters.py (extend existing)
    - **Depends on**: Task 2
    - Test class: `TestImportSummaryDisplay`
    - Test methods:
      - `test_display_import_summary_shows_all_counts`
      - `test_display_import_summary_with_no_errors`
      - `test_display_import_summary_with_errors_shows_table`
      - `test_display_import_summary_all_duplicates_message`
      - `test_display_import_summary_uses_green_for_success`
    - Mock: Rich Console to capture output
    - Purpose: Verify formatted summary display
    - _Leverage: Rich Panel, Rich Table, unittest.mock_
    - _Requirements: 2.2, 2.3, 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 6. Integration Tests
  - [ ] 6.1. Create integration tests for import command happy path
    - File: tests/integration/test_import_cli.py (new file)
    - **Depends on**: Tasks 1.1, 1.2, 1.3, 2, 3
    - Test class: `TestImportIntegration`
    - Test methods:
      - `test_import_valid_file_adds_dry_days_to_storage`
      - `test_import_with_duplicates_skips_correctly`
      - `test_import_with_mixed_valid_invalid_dates`
      - `test_import_with_comments_and_empty_lines`
    - Use real: CLI instance, JsonStorage with tmp_path, actual file creation
    - Purpose: End-to-end import verification
    - _Leverage: tmp_path fixture, CLI, JsonStorage_
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 4.2, 4.3, 4.4, 5.1, 6.2_

  - [ ] 6.2. Create integration tests for import error scenarios
    - File: tests/integration/test_import_cli.py (continue from task 6.1)
    - **Depends on**: Task 6.1
    - Test class: `TestImportErrorHandling`
    - Test methods:
      - `test_import_nonexistent_file_displays_error`
      - `test_import_with_permission_denied`
      - `test_import_empty_file_displays_message`
    - Use real: CLI instance, filesystem operations
    - Purpose: Verify error handling end-to-end
    - _Leverage: tmp_path fixture, os.chmod for permission tests_
    - _Requirements: 1.2, 3.1, 3.2, 3.3, 6.3_

  - [ ] 6.3. Add performance verification test
    - File: tests/integration/test_import_cli.py (continue from task 6.2)
    - **Depends on**: Task 6.1
    - Test class: `TestImportPerformance`
    - Test method:
      - `test_import_100_dates_completes_within_1_second`
    - Implementation:
      - Create test file with 100 valid dates
      - Use `time.time()` to measure import duration
      - Assert duration < 1.0 seconds
    - Purpose: Verify performance requirement
    - _Leverage: tmp_path fixture, time module_
    - _Requirements: 6.1, 6.2_

## Task Completion Order

**Recommended execution order** (optimized for testing along the way):

1. **Task 3** → Add argparse structure (quick, enables CLI routing)
2. **Task 1.1** → Add file operations (foundation)
3. **Task 1.2** → Add parsing logic (builds on 1.1)
4. **Task 1.3** → Add storage operations (completes handler)
5. **Task 2** → Add summary formatter (display logic)
6. **Tasks 4.1-4.3** → Unit tests for handler (verify components in isolation)
7. **Task 5.1** → Formatter unit tests (verify display)
8. **Tasks 6.1-6.3** → Integration tests (verify end-to-end)

## Notes

- **No new files in core/**: All business logic already exists (DateParser, DryDay, Storage)
- **Extension only**: Only extending CLI and OutputFormatter, not modifying existing methods
- **Test coverage target**: >90% for new import handler code, >80% overall
- **Performance verification**: Include integration test with 100 dates to verify <1 second processing
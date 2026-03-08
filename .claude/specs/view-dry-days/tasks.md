# Implementation Plan: View Dry Days

## Task Overview

This implementation adds visualization and statistics capabilities to the SDD Dry Days application. The feature is built entirely on existing infrastructure (JsonStorage, DryDay model, Rich UI) and follows a read-only, statistics-focused approach.

**Implementation Strategy:**
1. **Phase 1: Core Statistics (Tasks 1-4)** - Build data models and calculation logic
2. **Phase 2: Presentation Layer (Tasks 5-11)** - Create formatters for visual output
3. **Phase 3: CLI Integration (Tasks 12-18)** - Wire up commands and handlers
4. **Phase 4: Testing (Tasks 19-29)** - Comprehensive unit and integration tests

## Steering Document Compliance

**structure.md Alignment:**
- New statistics logic in `src/sdd_dry_days/core/stats.py` (business logic layer)
- New formatters in `src/sdd_dry_days/ui/view_formatters.py` (presentation layer)
- CLI extensions in `src/sdd_dry_days/cli.py` (CLI layer)
- Tests mirror source structure in `tests/unit/` and `tests/integration/`

**tech.md Alignment:**
- Uses Rich library for all visualizations (Tables, Panels, Progress)
- Works through Storage interface (JsonStorage) for data access
- Python 3.8+ features: dataclasses, type hints, generators
- Performance target: <200ms response time with efficient data access patterns
- Testing: >90% coverage for core, >80% for CLI/UI

## Atomic Task Requirements

**Each task must meet these criteria for optimal agent execution:**
- **File Scope**: Touches 1-3 related files maximum
- **Time Boxing**: Completable in 15-30 minutes
- **Single Purpose**: One testable outcome per task
- **Specific Files**: Must specify exact files to create/modify
- **Agent-Friendly**: Clear input/output with minimal context switching

## Task Format Guidelines

- Use checkbox format: `- [ ] Task number. Task description`
- **Specify files**: Always include exact file paths to create/modify
- **Include implementation details** as bullet points
- Reference requirements using: `_Requirements: X.Y, Z.A_`
- Reference existing code to leverage using: `_Leverage: path/to/file.py_`
- Focus only on coding tasks (no deployment, user testing, etc.)
- **Avoid broad terms**: No "system", "integration", "complete" in task titles

## Tasks

### Phase 1: Core Statistics Layer

- [x] 1. Create PeriodStats data class in src/sdd_dry_days/core/stats.py
  - File: src/sdd_dry_days/core/stats.py (new file)
  - Create new file with module docstring
  - Import dataclass, datetime, List from typing
  - Define PeriodStats dataclass with 9 fields: start_date, end_date, total_days, dry_days_count, percentage, longest_streak, dry_day_dates, available_days, requested_days
  - Add field type hints and inline comments for each field
  - Purpose: Establish data structure for period statistics
  - _Leverage: src/sdd_dry_days/core/dry_day.py (similar dataclass pattern)_
  - _Requirements: 4.1, 4.2_

- [x] 2. Create StatisticsCalculator class skeleton in core/stats.py
  - File: src/sdd_dry_days/core/stats.py (continue from task 1)
  - Create StatisticsCalculator class with docstring
  - Add imports for datetime, timedelta, List, Optional
  - Import DryDay from core.dry_day
  - Add static method stubs: get_week_dates(), get_month_dates()
  - Purpose: Establish calculator class structure
  - _Leverage: src/sdd_dry_days/core/streak.py (similar calculator pattern)_
  - _Requirements: 2.1, 3.1, 4.1_

- [x] 3. Implement get_week_dates() and get_month_dates() in StatisticsCalculator
  - File: src/sdd_dry_days/core/stats.py (continue from task 2)
  - Implement get_week_dates(ref_date: datetime) -> Tuple[datetime, datetime]
    - Calculate Monday of ref_date's week as start
    - Calculate Sunday of ref_date's week as end
    - Return tuple (start, end)
  - Implement get_month_dates(ref_date: datetime) -> Tuple[datetime, datetime]
    - Calculate first day of ref_date's month as start
    - Calculate last day of ref_date's month as end
    - Return tuple (start, end)
  - Add docstrings with parameters, returns, and examples
  - Purpose: Provide date range helpers for week/month views
  - _Leverage: Python datetime.weekday(), calendar.monthrange()_
  - _Requirements: 2.1, 3.1_

- [x] 4. Implement calculate_period_stats() in StatisticsCalculator
  - File: src/sdd_dry_days/core/stats.py (continue from task 3)
  - Add method signature: calculate_period_stats(dry_days: List[DryDay], start_date: datetime, end_date: datetime, all_recorded_days: Optional[List[DryDay]] = None) -> PeriodStats
  - Filter dry_days to period using list comprehension
  - Calculate requested_days: (end_date - start_date).days + 1
  - Calculate available_days from earliest record (for AC-4.7 limited data indicator)
  - Count dry days: len(filtered_days)
  - Calculate percentage: (dry_days_count / requested_days) * 100
  - Extract dry_day_dates list
  - Call calculate_longest_streak_in_period() for longest_streak (to be implemented in task 5)
  - Return PeriodStats instance with all fields
  - Add comprehensive docstring with Args, Returns, and example
  - Purpose: Core statistics calculation logic
  - _Leverage: List comprehensions, datetime arithmetic_
  - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2, 4.1, 4.2, 4.7_

- [x] 5. Add calculate_longest_streak_in_period() to StreakCalculator in core/streak.py
  - File: src/sdd_dry_days/core/streak.py (extend existing)
  - Add static method: calculate_longest_streak_in_period(dry_days: List[DryDay], start_date: datetime, end_date: datetime) -> int
  - Filter dry_days to period
  - Sort by date
  - Iterate to find longest consecutive streak (similar to calculate_current_streak logic)
  - Return max_streak (0 if no days)
  - Add docstring with Args, Returns
  - Purpose: Extend existing streak calculator with period-specific logic
  - _Leverage: src/sdd_dry_days/core/streak.py (existing calculate_current_streak algorithm)_
  - _Requirements: 2.4, 4.4_

### Phase 2: Presentation Layer

- [x] 6. Create ViewFormatter class skeleton in ui/view_formatters.py
  - File: src/sdd_dry_days/ui/view_formatters.py (new file)
  - Create new file with module docstring
  - Import Rich (Console, Table, Panel, Text, Progress), datetime, List, Optional, Generator
  - Import PeriodStats from core.stats, DryDay from core.dry_day, OutputFormatter from ui.formatters
  - Define ViewFormatter class with __init__(self, console: Console, output_formatter: OutputFormatter)
  - Store console and output_formatter as instance variables
  - Add method stubs: display_list_view(), display_week_view(), display_month_view(), display_stats_view(), display_range_view()
  - Purpose: Establish formatter class structure with composition
  - _Leverage: src/sdd_dry_days/ui/formatters.py (OutputFormatter pattern)_
  - _Requirements: 6.1, 6.2_

- [x] 7. Implement display_list_view() with pagination in ViewFormatter
  - File: src/sdd_dry_days/ui/view_formatters.py (continue from task 6)
  - Add helper method: _paginate_output(self, items: List[Any], page_size: int = 50) -> Generator
    - Yield pages of items using slicing
  - Implement display_list_view(self, dry_days: List[DryDay], current_streak: int, page_size: int = 50)
    - Display header panel with total count and streak (using Rich Panel)
    - Create Rich Table with columns: Date, Status, Notes
    - If len(dry_days) > page_size:
      - Paginate using _paginate_output()
      - Display each page
      - Show "[Press ENTER for more, Ctrl+C to stop]" prompt
      - Handle KeyboardInterrupt gracefully
    - Else: display all at once
  - Add status formatting: ✓ (green) for dry, ✓(P) (yellow) for planned
  - Purpose: List view with pagination for large datasets (AC-1.5)
  - _Leverage: Rich Panel, Rich Table, input() for pagination_
  - _Requirements: 1.1, 1.2, 1.4, 1.5, 6.1, 6.2, 6.5, 6.6, 6.7_

- [x] 8. Implement display_week_view() in ViewFormatter
  - File: src/sdd_dry_days/ui/view_formatters.py (continue from task 7)
  - Add method: display_week_view(self, stats: PeriodStats, week_days: List[Tuple[str, datetime, bool, Optional[str]]])
    - week_days format: (day_name, date, is_dry, note)
  - Create header Panel with week range, progress (X/7 days), percentage, progress bar
  - Create Rich Table with columns: Day, Date, Status, Notes
  - Add rows for Mon-Sun with status symbols (✓/-)
  - Display table
  - Purpose: Week view with table and progress visualization
  - _Leverage: Rich Panel, Rich Table, create_progress_bar() (to be implemented in task 11)_
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 6.1, 6.3, 6.4, 6.7_

- [x] 9. Implement display_month_view() in ViewFormatter
  - File: src/sdd_dry_days/ui/view_formatters.py (continue from task 8)
  - Add helper method: _create_calendar_grid(self, stats: PeriodStats) -> str
    - Get first day of month, calculate weekday offset
    - Build 6x7 grid (weeks x days)
    - Format each cell: day_number + status (✓/-)
    - Mark today with * (bold)
    - Return formatted string
  - Implement display_month_view(self, stats: PeriodStats)
    - Create header Panel with month name, progress (X/Y days), percentage, progress bar
    - Display calendar grid using _create_calendar_grid()
    - Show legend: "✓=Dry  -=Not Dry  *=Today"
    - Show current streak with 🔥 emoji
  - Purpose: Month calendar view with visual grid
  - _Leverage: Python calendar module, Rich Panel_
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 6.1, 6.3, 6.5, 6.6, 6.7_

- [x] 10. Implement display_stats_view() in ViewFormatter
  - File: src/sdd_dry_days/ui/view_formatters.py (continue from task 9)
  - Add method: display_stats_view(self, stats_30: PeriodStats, stats_60: PeriodStats, stats_90: PeriodStats, current_streak: int)
  - Create header Panel with "📈 Statistics Overview" and current streak
  - Create Rich Table with columns: Period, Dry Days, Total Days, Percentage, Longest Streak
  - Add rows for 30d, 60d, 90d with:
    - Check if stats.available_days < stats.requested_days
    - If true: show "(limited data: X/Y days)" indicator
    - Show progress bar for percentage
    - Show longest streak with 🔥 emoji
  - Display table
  - Purpose: Statistics view with 30/60/90 day breakdown and limited data indicators (AC-4.7)
  - _Leverage: Rich Panel, Rich Table, create_progress_bar()_
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 6.1, 6.3, 6.4, 6.6_

- [x] 11. Implement display_range_view() and create_progress_bar() in ViewFormatter
  - File: src/sdd_dry_days/ui/view_formatters.py (continue from task 10)
  - Implement create_progress_bar(self, percentage: float) -> str
    - Calculate filled/empty portions (20 char width)
    - Choose color based on percentage: red (<50%), yellow (50-75%), green (>75%)
    - Use Unicode box characters: ▓ (filled), ░ (empty)
    - Return formatted string with percentage text: "[color]bar[/color] percentage%"
    - Purpose: Accessible progress bars (AC-9.2)
  - Implement display_range_view(self, stats: PeriodStats, dry_days: List[DryDay])
    - Create header Panel with date range, progress, percentage, progress bar, longest streak
    - Create Rich Table with columns: Date, Status, Notes
    - Add rows for each day in range
    - Display table
  - Purpose: Custom range view with statistics and list
  - _Leverage: Rich Panel, Rich Table_
  - _Requirements: 5.1, 5.2, 5.5, 6.1, 6.3, 6.4, 6.6, 9.2_

### Phase 3: CLI Integration

- [x] 12. Add view subparser to CLI in cli.py
  - File: src/sdd_dry_days/cli.py (extend existing)
  - In _setup_parsers() method, add view subparser:
    - view_parser = subparsers.add_parser("view", help="View dry days and statistics")
    - Add arguments: --sort (choices: asc/desc, default: desc)
    - Add arguments: --filter (choices: planned/actual)
    - Add arguments: --week (action: store_true)
    - Add arguments: --month (action: store_true)
    - Add arguments: --stats (action: store_true)
    - Add arguments: --range (nargs: 2, metavar: ("START", "END"))
  - Purpose: CLI argument parsing for view commands
  - _Leverage: src/sdd_dry_days/cli.py (existing argparse pattern)_
  - _Requirements: 1.1, 2.1, 3.1, 4.1, 5.1, 8.1, 8.2, 8.3, 8.4_

- [x] 13. Add _handle_view() routing method to CLI
  - File: src/sdd_dry_days/cli.py (continue from task 12)
  - Add method: _handle_view(self, args)
    - Check args.week → call _view_week()
    - Check args.month → call _view_month()
    - Check args.stats → call _view_stats()
    - Check args.range → call _view_range(args.range[0], args.range[1])
    - Else → call _view_list(args.sort, args.filter)
  - Add error handling: catch exceptions, display error panel using output_formatter
  - Purpose: Route view subcommand to appropriate handler
  - _Leverage: src/sdd_dry_days/cli.py (existing _handle_add pattern)_
  - _Requirements: 1.1, 2.1, 3.1, 4.1, 5.1, 10.1, 10.5_

- [x] 14. Implement _view_list() with sort and filter in CLI
  - File: src/sdd_dry_days/cli.py (continue from task 13)
  - Add helper method: _apply_sort(self, dry_days: List[DryDay], order: str) -> List[DryDay]
    - Sort by date: reverse=(order == "desc")
    - Return sorted list
  - Add helper method: _apply_filter(self, dry_days: List[DryDay], filter_type: Optional[str]) -> List[DryDay]
    - If filter_type == "planned": return [dd for dd in dry_days if dd.date.date() > today]
    - If filter_type == "actual": return [dd for dd in dry_days if dd.date.date() <= today]
    - Else: return dry_days
  - Implement _view_list(self, sort_order: str = "desc", filter_type: Optional[str] = None)
    - Fetch all dry days: self.storage.get_all_dry_days()
    - Apply filter first: _apply_filter()
    - Apply sort second: _apply_sort()
    - Calculate current streak: self.streak_calculator.calculate_current_streak()
    - Display: self.view_formatter.display_list_view()
    - Handle empty list: display encouraging message using output_formatter
  - Purpose: List view with sorting and filtering (AC-8.1-8.5)
  - _Leverage: src/sdd_dry_days/storage/json_storage.py (get_all_dry_days), src/sdd_dry_days/core/streak.py (calculate_current_streak)_
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 8.1, 8.2, 8.3, 8.4, 8.5, 10.1_

- [x] 15. Implement _view_week() in CLI
  - File: src/sdd_dry_days/cli.py (continue from task 14)
  - Add method: _view_week(self)
    - Get week dates: StatisticsCalculator.get_week_dates(datetime.now())
    - Fetch dry days for week: self.storage.get_dry_days_in_range(start, end)
    - Calculate stats: StatisticsCalculator.calculate_period_stats(dry_days, start, end)
    - Build week_days list: List[Tuple[str, datetime, bool, Optional[str]]]
      - For each day Mon-Sun, check if in dry_days, extract note
    - Display: self.view_formatter.display_week_view(stats, week_days)
    - Handle empty week: display encouraging message
  - Purpose: Week view handler
  - _Leverage: src/sdd_dry_days/core/stats.py (StatisticsCalculator), src/sdd_dry_days/storage/json_storage.py (get_dry_days_in_range)_
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 10.1_

- [x] 16. Implement _view_month() in CLI
  - File: src/sdd_dry_days/cli.py (continue from task 15)
  - Add method: _view_month(self)
    - Get month dates: StatisticsCalculator.get_month_dates(datetime.now())
    - Fetch dry days for month: self.storage.get_dry_days_in_range(start, end)
    - Calculate stats: StatisticsCalculator.calculate_period_stats(dry_days, start, end)
    - Display: self.view_formatter.display_month_view(stats)
    - Handle empty month: display encouraging message
  - Purpose: Month view handler
  - _Leverage: src/sdd_dry_days/core/stats.py (StatisticsCalculator), src/sdd_dry_days/storage/json_storage.py (get_dry_days_in_range)_
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 10.1_

- [x] 17. Implement _view_stats() in CLI
  - File: src/sdd_dry_days/cli.py (continue from task 16)
  - Add method: _view_stats(self)
    - Get today: datetime.now()
    - Calculate dates for 30/60/90 days ago
    - Fetch all dry days: self.storage.get_all_dry_days()
    - Calculate stats for each period:
      - stats_30 = StatisticsCalculator.calculate_period_stats(dry_days, today - 30 days, today, all_dry_days)
      - stats_60 = StatisticsCalculator.calculate_period_stats(dry_days, today - 60 days, today, all_dry_days)
      - stats_90 = StatisticsCalculator.calculate_period_stats(dry_days, today - 90 days, today, all_dry_days)
    - Calculate current streak: self.streak_calculator.calculate_current_streak(dry_days)
    - Display: self.view_formatter.display_stats_view(stats_30, stats_60, stats_90, current_streak)
    - Handle insufficient data: display with limited data indicators (AC-4.7)
  - Purpose: Statistics view handler with 30/60/90 day breakdown
  - _Leverage: src/sdd_dry_days/core/stats.py (StatisticsCalculator), src/sdd_dry_days/storage/json_storage.py (get_all_dry_days)_
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 10.1_

- [x] 18. Implement _view_range() with date validation in CLI
  - File: src/sdd_dry_days/cli.py (continue from task 17)
  - Add method: _view_range(self, start_str: str, end_str: str)
    - Parse dates using DateParser.parse()
    - Validate: end_date >= start_date
      - If invalid: display error with format examples using output_formatter.display_error()
    - Fetch dry days for range: self.storage.get_dry_days_in_range(start, end)
    - Calculate stats: StatisticsCalculator.calculate_period_stats(dry_days, start, end)
    - Display: self.view_formatter.display_range_view(stats, dry_days)
    - Handle empty range: display encouraging message
    - Handle parse errors: display error with format examples
  - Purpose: Custom range view with validation (AC-5.3, AC-10.3)
  - _Leverage: src/sdd_dry_days/utils/date_parser.py (DateParser.parse), src/sdd_dry_days/storage/json_storage.py (get_dry_days_in_range)_
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 10.3_

### Phase 4: Testing
let's execute task 25 to 29.
- [x] 19. Create unit tests for PeriodStats and StatisticsCalculator helpers in tests/unit/test_stats.py
  - File: tests/unit/test_stats.py (new file)
  - Import pytest, datetime, PeriodStats, StatisticsCalculator from core.stats
  - Test PeriodStats instantiation with all fields
  - Test StatisticsCalculator.get_week_dates():
    - Test Monday start, Sunday end
    - Test with different days of week
    - Test edge cases: year boundary
  - Test StatisticsCalculator.get_month_dates():
    - Test first day start, last day end
    - Test different months (28/29/30/31 days)
    - Test edge cases: February, year boundary
  - Purpose: Verify date helper methods
  - _Leverage: tests/conftest.py (pytest fixtures), Python datetime_
  - _Requirements: 2.1, 3.1_

- [x] 20. Add unit tests for calculate_period_stats() in test_stats.py
  - File: tests/unit/test_stats.py (continue from task 19)
  - Test calculate_period_stats() with:
    - Empty dry_days list → 0 count, 0%, 0 streak
    - Single dry day in period → 1 count, correct percentage
    - Multiple dry days in period → correct count, percentage, dates
    - Dry days outside period → filtered out correctly
    - Consecutive dry days → longest streak calculated
    - Limited data scenario (AC-4.7) → available_days < requested_days
  - Use sample_dry_days_list fixture from conftest.py
  - Purpose: Verify core statistics calculation logic
  - _Leverage: tests/conftest.py (sample_dry_days_list fixture)_
  - _Requirements: 2.2, 2.3, 4.2, 4.3, 4.7_

- [x] 21. Add unit tests for calculate_longest_streak_in_period() in tests/unit/test_streak.py
  - File: tests/unit/test_streak.py (extend existing)
  - Import calculate_longest_streak_in_period from core.streak
  - Test with:
    - Empty list → 0 streak
    - Single day → 1 streak
    - Consecutive days → correct streak count
    - Days with gaps → correct longest streak
    - Days outside period → filtered correctly
  - Use sample_consecutive_dry_days and sample_dry_days_list fixtures
  - Purpose: Verify period-specific streak calculation
  - _Leverage: tests/conftest.py (sample fixtures), existing test_streak.py structure_
  - _Requirements: 2.4, 4.4_

- [x] 22. Create unit tests for ViewFormatter progress bars in tests/unit/test_view_formatters.py
  - File: tests/unit/test_view_formatters.py (new file)
  - Import pytest, ViewFormatter from ui.view_formatters
  - Mock Rich Console and OutputFormatter
  - Create ViewFormatter instance with mocks
  - Test create_progress_bar():
    - Test percentage < 50% → red color
    - Test percentage 50-75% → yellow color
    - Test percentage > 75% → green color
    - Test width calculation: filled + empty = 20
    - Test percentage text included (AC-9.2)
  - Purpose: Verify progress bar rendering and accessibility
  - _Leverage: unittest.mock for Console mocking_
  - _Requirements: 6.4, 9.2_

- [x] 23. Add unit tests for ViewFormatter calendar grid in test_view_formatters.py
  - File: tests/unit/test_view_formatters.py (continue from task 22)
  - Test _create_calendar_grid():
    - Test with empty stats → blank grid
    - Test with first day of month on Monday
    - Test with first day of month on Sunday
    - Test with 28-day month (February)
    - Test with 31-day month
    - Test current day marked with *
    - Test dry days marked with ✓
  - Use sample PeriodStats instances
  - Purpose: Verify calendar grid generation logic
  - _Leverage: datetime, calendar modules for test data_
  - _Requirements: 3.2, 3.5, 6.5_

- [x] 24. Create integration tests for sdd view (list) in tests/integration/test_view_cli.py
  - File: tests/integration/test_view_cli.py (new file)
  - Import pytest, CLI from cli, JsonStorage from storage.json_storage
  - Use temp_storage_dir fixture for isolated testing
  - Test scenarios:
    - No data → displays encouraging message (AC-1.3)
    - With data → displays table with dates, status, notes (AC-1.2)
    - Default sort (desc) → most recent first (AC-1.1, AC-8.1)
    - Sort asc → oldest first (AC-8.2)
    - Filter planned → only future days (AC-8.3)
    - Filter actual → only past/today days (AC-8.4)
    - Large dataset (>50 entries) → pagination triggered (AC-1.5)
  - Purpose: Verify list view end-to-end
  - _Leverage: tests/conftest.py (temp_storage_dir fixture), tests/integration/ patterns_
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 25. Add integration tests for sdd view --week in test_view_cli.py
  - File: tests/integration/test_view_cli.py (continue from task 24)
  - Test scenarios:
    - Empty week → encouraging message (AC-2.5)
    - With data → displays week table Mon-Sun (AC-2.1, AC-2.2)
    - Shows percentage and progress bar (AC-2.3)
    - Shows "X out of 7 days" format (AC-2.4)
  - Create sample data for current week
  - Purpose: Verify week view end-to-end
  - _Leverage: StatisticsCalculator.get_week_dates() for test data setup_
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 26. Add integration tests for sdd view --month in test_view_cli.py
  - File: tests/integration/test_view_cli.py (continue from task 25)
  - Test scenarios:
    - Empty month → encouraging message (AC-3.6)
    - With data → displays calendar grid (AC-3.2)
    - Shows percentage and progress bar (AC-3.3)
    - Shows "X out of Y days" format (AC-3.4)
    - Highlights current day (AC-3.5)
    - Shows streak count (AC-3.5)
  - Create sample data for current month
  - Purpose: Verify month view end-to-end
  - _Leverage: StatisticsCalculator.get_month_dates() for test data setup_
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [x] 27. Add integration tests for sdd view --stats in test_view_cli.py
  - File: tests/integration/test_view_cli.py (continue from task 26)
  - Test scenarios:
    - Displays 30/60/90 day rows (AC-4.1, AC-4.2)
    - Shows correct percentages (AC-4.3)
    - Shows longest streaks (AC-4.4)
    - Shows current streak at top (AC-4.5)
    - Shows progress bars (AC-4.6)
    - Limited data scenario → displays "(limited data: X/Y days)" (AC-4.7)
  - Create sample data spanning different periods
  - Purpose: Verify stats view end-to-end with limited data handling
  - _Leverage: Sample data with known statistics_
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

- [x] 28. Add integration tests for sdd view --range in test_view_cli.py
  - File: tests/integration/test_view_cli.py (continue from task 27)
  - Test scenarios:
    - Valid range → displays range with stats (AC-5.1, AC-5.2)
    - Invalid range (end < start) → displays error (AC-5.3)
    - Range with planned days → shows (P) indicator (AC-5.4)
    - Empty range → displays encouraging message (AC-5.5)
    - Invalid date format → displays error with examples (AC-10.3)
  - Purpose: Verify custom range view with validation
  - _Leverage: DateParser for date validation testing_
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 10.3_

- [x] 29. Add integration tests for error handling in test_view_cli.py
  - File: tests/integration/test_view_cli.py (continue from task 28)
  - Test error scenarios:
    - Data file doesn't exist → friendly message (AC-10.1)
    - Corrupted data file → error message (AC-10.2)
    - Storage unavailable (permissions) → permissions error (AC-10.4)
    - Unexpected error → user-friendly error panel (AC-10.5)
  - Mock storage errors to trigger scenarios
  - Purpose: Verify error handling across all view commands
  - _Leverage: unittest.mock to simulate errors_
  - _Requirements: 10.1, 10.2, 10.4, 10.5_

## Implementation Notes

**Performance Considerations:**
- Use `get_dry_days_in_range()` for week/month/range views (more efficient than get_all + filter)
- Use `get_all_dry_days()` only for list and stats views where full dataset is needed
- List comprehensions for filtering (faster than loops)
- Generators for pagination (memory efficient)

**Accessibility Compliance (AC-9.1-9.5):**
- All status indicators use BOTH color AND symbols (✓, -, P, *)
- All progress bars include percentage text alongside visual bar
- Color choices ensure WCAG 2.1 AA contrast (4.5:1)
- Legends provided for all symbols
- Screen reader friendly with plain text alternatives

**Testing Priority:**
- Unit tests first (tasks 19-23): Fast, isolated, high coverage
- Integration tests second (tasks 24-29): End-to-end validation
- Focus on edge cases: empty data, invalid dates, large datasets, limited data scenarios

**Dependencies Between Tasks:**
- Tasks 1-5 must complete before tasks 6-11 (formatters need stats classes)
- Tasks 6-11 must complete before tasks 12-18 (CLI needs formatters)
- Tasks 1-18 must complete before tasks 19-29 (tests need implementations)
- Within each phase, tasks are generally sequential (numbered order)

**Requirement Traceability:**
- All 10 requirements covered across 29 tasks
- All 55 acceptance criteria mapped to specific tasks
- Each task references specific requirements for validation
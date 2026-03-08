# Requirements Document: View Dry Days

## Introduction

The "View Dry Days" feature enables users to visualize their dry day progress across different time periods. This feature provides immediate visual feedback on progress patterns, helping users understand their journey and stay motivated through data-driven insights.

This feature builds upon the existing "Add Dry Days" functionality, transforming raw data entries into meaningful visualizations and statistics that support the user's wellness goals.

## Alignment with Product Vision

This feature directly supports the core product principles outlined in product.md:

1. **Visual Motivation**: Uses colors and patterns to celebrate progress - displaying statistics and visualizations makes progress tangible
2. **Simplicity First**: Quick commands to view progress without complex navigation
3. **Encouraging**: Focuses on positive metrics (days tracked, streaks) rather than failures
4. **Regular Usage**: Weekly and monthly reviews encourage consistent engagement

This feature implements the second MVP feature listed in product.md: **Progress Statistics** - showing summary stats for last 30/60/90 days with percentage calculations.

## Requirements

### Requirement 1: View All Dry Days (List View)

**User Story:** As a user tracking my dry days, I want to see a complete list of all my recorded dry days, so that I can review my entire history at a glance.

#### Acceptance Criteria

1. **AC-1.1**: WHEN the user runs the view command without parameters THEN the system SHALL display all dry days in reverse chronological order (most recent first)
2. **AC-1.2**: WHEN displaying dry days THEN the system SHALL show the date, note (if present), and whether it's a planned future day in a formatted table
3. **AC-1.3**: WHEN there are no dry days recorded THEN the system SHALL display a friendly message encouraging the user to add their first dry day
4. **AC-1.4**: WHEN displaying the list THEN the system SHALL show the total count of dry days and current streak at the top
5. **AC-1.5**: WHEN the list is long (>50 entries) THEN the system let's goSHALL display 50 entries per page with prompt "[Press ENTER for more]" or show all with scrolling enabled

### Requirement 2: View Week Summary

**User Story:** As a user tracking my dry days, I want to see a summary of the current week, so that I can understand my recent progress patterns.

#### Acceptance Criteria

1. **AC-2.1**: WHEN the user runs `view --week` THEN the system SHALL display dry days for the current week (Monday-Sunday) starting from the most recent Monday
2. **AC-2.2**: WHEN displaying the week THEN the system SHALL show a table with columns: Day (Mon-Sun), Date (YYYY-MM-DD), Status (✓ for dry, - for not dry), and any notes
3. **AC-2.3**: WHEN displaying the week THEN the system SHALL calculate and show the percentage of dry days in the week with a visual progress bar
4. **AC-2.4**: WHEN displaying the week THEN the system SHALL show the count in format "X out of 7 days" where X is dry days
5. **AC-2.5**: WHEN the week has no dry days THEN the system SHALL display an encouraging message like "Start your week strong! Add your first dry day."

### Requirement 3: View Month Summary

**User Story:** As a user tracking my dry days, I want to see a summary of the current month, so that I can track my monthly progress toward my goals.

#### Acceptance Criteria

1. **AC-3.1**: WHEN the user runs `view --month` THEN the system SHALL display dry days for the current calendar month (1st to last day)
2. **AC-3.2**: WHEN displaying the month THEN the system SHALL show a calendar grid (7 columns for days of week) with day numbers and ✓ for dry days
3. **AC-3.3**: WHEN displaying the month THEN the system SHALL calculate and show the percentage of dry days with a visual progress bar
4. **AC-3.4**: WHEN displaying the month THEN the system SHALL show the count in format "X out of Y days" where X is dry days and Y is total days in month
5. **AC-3.5**: WHEN displaying the month THEN the system SHALL highlight the current day with a different color/indicator and show streak counts
6. **AC-3.6**: WHEN the month has no dry days THEN the system SHALL display an encouraging message like "Your journey starts now! Add today as your first dry day."

### Requirement 4: View Statistics (30/60/90 Days)

**User Story:** As a user tracking my dry days, I want to see statistics for different time periods, so that I can understand my long-term trends and progress.

#### Acceptance Criteria

1. **AC-4.1**: WHEN the user runs `view --stats` THEN the system SHALL display statistics in a table with rows for 30, 60, and 90 day periods
2. **AC-4.2**: WHEN displaying statistics THEN the system SHALL show columns: Period, Dry Days, Total Days, Percentage, Longest Streak
3. **AC-4.3**: WHEN displaying statistics THEN the system SHALL calculate percentage as (dry days / total days) × 100
4. **AC-4.4**: WHEN displaying statistics THEN the system SHALL show the longest consecutive streak in each period
5. **AC-4.5**: WHEN displaying statistics THEN the system SHALL show the current active streak at the top of the table
6. **AC-4.6**: WHEN displaying statistics THEN the system SHALL use visual progress bars showing percentage completion for each period
7. **AC-4.7**: WHEN there is insufficient data for a period (e.g., only 20 days recorded for 90-day view) THEN the system SHALL calculate based on available data and show "(limited data: 20/90 days)" indicator

### Requirement 5: View Custom Date Range

**User Story:** As a user tracking my dry days, I want to view statistics for a custom date range, so that I can analyze specific periods of interest.

#### Acceptance Criteria

1. **AC-5.1**: WHEN the user runs `view --range START END` THEN the system SHALL display dry days and statistics for the specified date range (inclusive)
2. **AC-5.2**: WHEN the range is valid THEN the system SHALL show a table with: Date, Status (✓/-), Notes, and a summary with count, percentage, longest streak
3. **AC-5.3**: WHEN the range is invalid (end before start) THEN the system SHALL display error "Invalid range: end date must be after start date" with format examples
4. **AC-5.4**: WHEN the range includes future dates THEN the system SHALL show planned days with (P) indicator and different color
5. **AC-5.5**: IF the range is empty (no dry days) THEN the system SHALL display "No dry days in this period. Add your first dry day to start tracking!"

### Requirement 6: Rich Formatting and Visual Appeal

**User Story:** As a user tracking my dry days, I want the view output to be visually appealing and easy to read, so that I feel motivated and engaged.

#### Acceptance Criteria

1. **AC-6.1**: WHEN displaying any view THEN the system SHALL use the Rich library Panel/Table widgets for structured, colorful output
2. **AC-6.2**: WHEN showing dry days THEN the system SHALL use green color (#00FF00) for positive metrics (percentages >50%, streaks)
3. **AC-6.3**: WHEN showing streaks THEN the system SHALL use fire emoji (🔥) prefix and yellow color (#FFFF00) for streak counts
4. **AC-6.4**: WHEN showing percentages THEN the system SHALL use Rich progress bars with gradient colors (red <50%, yellow 50-75%, green >75%)
5. **AC-6.5**: WHEN showing dates THEN the system SHALL use consistent ISO 8601 date formatting (YYYY-MM-DD)
6. **AC-6.6**: WHEN displaying tables THEN the system SHALL use Rich Table with center alignment for numbers, left alignment for text, and box borders
7. **AC-6.7**: WHEN showing status indicators THEN the system SHALL use both color AND symbols (✓, -, P) for accessibility

### Requirement 7: Performance and Responsiveness

**User Story:** As a user tracking my dry days, I want the view command to respond quickly, so that checking my progress feels instant and effortless.

#### Acceptance Criteria

1. **AC-7.1**: WHEN the user runs any view command with <1000 entries THEN the system SHALL display results within 200ms (measured from command execution to first output)
2. **AC-7.2**: WHEN displaying large datasets (>1000 entries) THEN the system SHALL use efficient data structures (list comprehensions, generators) to avoid memory bloat
3. **AC-7.3**: WHEN calculating statistics THEN the system SHALL compute on-demand without persistent caching (calculations are fast enough)
4. **AC-7.4**: WHEN the data file is large (>5MB, ~10k entries) THEN the system SHALL maintain fast startup time (< 1 second) using lazy loading

### Requirement 8: Sorting and Filtering Options

**User Story:** As a user tracking my dry days, I want to sort and filter my view results, so that I can focus on specific aspects of my progress.

#### Acceptance Criteria

1. **AC-8.1**: WHEN the user runs `view --sort desc` THEN the system SHALL display dry days in reverse chronological order (most recent first, default)
2. **AC-8.2**: WHEN the user runs `view --sort asc` THEN the system SHALL display dry days in chronological order (oldest first)
3. **AC-8.3**: WHEN the user runs `view --filter planned` THEN the system SHALL display only planned (future) dry days
4. **AC-8.4**: WHEN the user runs `view --filter actual` THEN the system SHALL display only completed (past/today) dry days
5. **AC-8.5**: WHEN using both sort and filter THEN the system SHALL apply filter first, then sort the results

### Requirement 9: Accessibility

**User Story:** As a user with accessibility needs, I want the view output to be accessible, so that I can use the application regardless of my visual abilities.

#### Acceptance Criteria

1. **AC-9.1**: WHEN displaying status indicators THEN the system SHALL use both color AND text/symbols (e.g., ✓ for dry, not just green color)
2. **AC-9.2**: WHEN showing progress bars THEN the system SHALL include percentage text alongside the visual bar
3. **AC-9.3**: WHEN using color coding THEN the system SHALL ensure sufficient contrast ratios (WCAG 2.1 AA standard: 4.5:1 for text)
4. **AC-9.4**: WHEN displaying information THEN the system SHALL not rely solely on color to convey meaning (use symbols, text, or patterns)
5. **AC-9.5**: WHEN formatting output THEN the system SHALL support standard terminal screen readers by using plain text alternatives

### Requirement 10: Error Handling and Edge Cases

**User Story:** As a user tracking my dry days, I want clear error messages if something goes wrong, so that I understand what happened and how to fix it.

#### Acceptance Criteria

1. **AC-10.1**: WHEN the data file doesn't exist THEN the system SHALL display "No dry days yet! Start your journey with: sdd add"
2. **AC-10.2**: WHEN the data file is corrupted THEN the system SHALL display "Data file error. Try adding a new dry day: sdd add"
3. **AC-10.3**: WHEN a date range is invalid THEN the system SHALL display error with format examples: "Try: sdd view --range 2026-03-01 2026-03-31"
4. **AC-10.4**: WHEN storage is unavailable (permissions error) THEN the system SHALL display "Cannot access data file at ~/.sdd_dry_days/data.json. Check permissions."
5. **AC-10.5**: IF an unexpected error occurs THEN the system SHALL display user-friendly error in a red panel (not a stack trace) with error code for debugging

## Example Output Formats

### List View (sdd view)
```
╭────────────────────────────────────────────╮
│ 📊 Dry Days Summary                        │
│ Total: 45 days | Current Streak: 🔥 7 days │
╰────────────────────────────────────────────╯

┌────────────┬────────┬───────────────────┐
│ Date       │ Status │ Notes             │
├────────────┼────────┼───────────────────┤
│ 2026-03-07 │   ✓    │ Feeling great!    │
│ 2026-03-06 │   ✓    │ First dry day     │
│ 2026-03-05 │   ✓    │                   │
│ 2026-03-03 │   ✓    │ Weekend success   │
│ 2026-03-02 │   ✓(P) │ Planning ahead    │
└────────────┴────────┴───────────────────┘
```

### Week View (sdd view --week)
```
╭──────────────────────────────╮
│ 📅 Week of March 3-9, 2026   │
│ Progress: 5/7 days (71%)     │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░         │
╰──────────────────────────────╯

┌────────┬────────────┬────────┬──────────────┐
│ Day    │ Date       │ Status │ Notes        │
├────────┼────────────┼────────┼──────────────┤
│ Mon    │ 2026-03-03 │   ✓    │              │
│ Tue    │ 2026-03-04 │   -    │              │
│ Wed    │ 2026-03-05 │   ✓    │              │
│ Thu    │ 2026-03-06 │   ✓    │ First day    │
│ Fri    │ 2026-03-07 │   ✓    │ Feeling gr...│
│ Sat    │ 2026-03-08 │   -    │              │
│ Sun    │ 2026-03-09 │   ✓    │              │
└────────┴────────────┴────────┴──────────────┘
```

### Month View (sdd view --month)
```
╭──────────────────────────────╮
│ 📅 March 2026                │
│ Progress: 18/31 days (58%)   │
│ ▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░         │
╰──────────────────────────────╯

    Mon  Tue  Wed  Thu  Fri  Sat  Sun
     -    -    1✓   2✓   3✓   4-   5✓
     6✓   7✓*  8-   9✓  10✓  11-  12✓
    13✓  14✓  15-  16✓  17✓  18-  19✓
    20✓  21-  22✓  23✓  24-  25✓  26✓
    27-  28✓  29✓  30-  31✓

Legend: ✓=Dry  -=Not Dry  *=Today
Current Streak: 🔥 3 days
```

### Statistics View (sdd view --stats)
```
╭────────────────────────────────────────────╮
│ 📈 Statistics Overview                     │
│ Current Streak: 🔥 7 days                  │
╰────────────────────────────────────────────╯

┌────────┬──────────┬────────────┬────────────┬────────────────┐
│ Period │ Dry Days │ Total Days │ Percentage │ Longest Streak │
├────────┼──────────┼────────────┼────────────┼────────────────┤
│ 30d    │    22    │     30     │    73%     │    🔥 10 days  │
│        │          │            │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░      │
│ 60d    │    40    │     60     │    67%     │    🔥 10 days  │
│        │          │            │ ▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░      │
│ 90d    │    55    │     90     │    61%     │    🔥 12 days  │
│        │          │            │ ▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░      │
└────────┴──────────┴────────────┴────────────┴────────────────┘
```

### Custom Range View (sdd view --range 2026-03-01 2026-03-10)
```
╭────────────────────────────────────────────╮
│ 📊 Range: March 1-10, 2026                 │
│ Progress: 7/10 days (70%)                  │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░                      │
│ Longest Streak: 🔥 5 days                  │
╰────────────────────────────────────────────╯

┌────────────┬────────┬──────────────┐
│ Date       │ Status │ Notes        │
├────────────┼────────┼──────────────┤
│ 2026-03-01 │   ✓    │              │
│ 2026-03-02 │   ✓    │              │
│ 2026-03-03 │   -    │              │
│ 2026-03-04 │   ✓    │              │
│ 2026-03-05 │   ✓    │              │
│ 2026-03-06 │   ✓    │ First day    │
│ 2026-03-07 │   ✓    │ Feeling gr...│
│ 2026-03-08 │   -    │              │
│ 2026-03-09 │   -    │              │
│ 2026-03-10 │   ✓    │              │
└────────────┴────────┴──────────────┘
```

## Non-Functional Requirements

### Performance
- View commands must respond within 200ms for datasets up to 1000 entries
- Startup time must remain < 1 second even with large datasets
- Efficient memory usage (avoid loading all data into memory at once for very large datasets)

### Security
- No sensitive data displayed in error messages
- File permissions maintained (700 for directory, 600 for data file)
- No external network calls (all data local)

### Reliability
- Graceful handling of corrupted data files
- Consistent results across multiple invocations
- No data modification during view operations (read-only)

### Usability
- Clear, colorful visual feedback using Rich library
- Consistent date formatting across all views
- Helpful messages when no data is available
- Intuitive command structure (--week, --month, --stats, --range)
- Progress indicators (percentages, progress bars) for motivation

## Technical Constraints

1. **Rich Library**: All visualizations must use the Rich library for consistency
2. **Read-Only**: View operations must never modify data (pure read operations)
3. **Storage Abstraction**: Must work through the existing Storage interface
4. **CLI Integration**: Must integrate with existing argparse-based CLI
5. **Date Handling**: Must use existing DateParser utilities
6. **Performance**: Must maintain < 200ms response time for typical datasets
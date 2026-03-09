# Bug Report

## Bug Summary
The `OutputFormatter` class does not have an `info()` method, but the CLI code attempts to call `self.formatter.info()` in three locations, causing an `AttributeError` when displaying empty week, month, or range views.

## Bug Details

### Expected Behavior
When viewing a week, month, or range with no dry days, the application should display an encouraging informational message to the user, such as "Start your week strong! Add your first dry day."

### Actual Behavior
When attempting to view a week, month, or range with no dry days, the application crashes with an `AttributeError` because the `OutputFormatter` class does not have an `info()` method.

### Steps to Reproduce
1. Start with an empty database (no dry days added)
2. Run `sdd view --week` command
3. Observe the error: `AttributeError: 'OutputFormatter' object has no attribute 'info'`

Alternative reproduction:
1. Start with an empty database (no dry days added)
2. Run `sdd view --month` command
3. Observe the same error

Or:
1. Run `sdd view --range 2026-01-01 2026-01-31` for a range with no dry days
2. Observe the same error

### Environment
- **Version**: Current development version (after emoji removal fix)
- **Platform**: macOS Darwin 25.3.0
- **Python**: 3.12.2
- **Configuration**: Standard development environment

## Impact Assessment

### Severity
- [ ] Critical - System unusable
- [x] High - Major functionality broken
- [ ] Medium - Feature impaired but workaround exists
- [ ] Low - Minor issue or cosmetic

### Affected Users
All users attempting to view week, month, or range statistics when no dry days exist in that period.

### Affected Features
- Week view (`sdd view --week`)
- Month view (`sdd view --month`)
- Range view (`sdd view --range`)

All three views fail when displaying empty data sets.

## Additional Context

### Error Messages
```python
AttributeError: 'OutputFormatter' object has no attribute 'info'
```

### Code Locations
**File**: `src/sdd_dry_days/cli.py`

**Line 502** (Week view):
```python
self.formatter.info("Start your week strong! Add your first dry day.")
```

**Line 543** (Month view):
```python
self.formatter.info("Your journey starts now! Add today as your first dry day.")
```

**Line 679** (Range view):
```python
self.formatter.info(
    "No dry days in this period. Add your first dry day to start tracking!"
)
```

### Related Issues
This bug was discovered during the verification phase of the view-stats-panel-not-aligned bug fix. The week view was mentioned as having a pre-existing bug in that verification document.

## Initial Analysis

### Suspected Root Cause
The `OutputFormatter` class (`src/sdd_dry_days/ui/formatters.py`) was designed with methods for different message types:
- `success()` - for successful operations
- `error()` - for error messages
- `already_exists()` - for duplicate dry days
- `range_summary()` - for range addition summaries
- `confirm()` - for user confirmations
- `display_import_summary()` - for import results

However, no `info()` method was implemented for general informational messages.

The CLI code was written assuming an `info()` method exists, but it was never created.

### Affected Components
- `src/sdd_dry_days/ui/formatters.py` - Missing `info()` method in `OutputFormatter` class
- `src/sdd_dry_days/cli.py` - Three method calls attempting to use non-existent `info()` method:
  - `_view_week()` method (line 502)
  - `_view_month()` method (line 543)
  - `_view_range()` method (line 679)

### Potential Solutions
1. **Add `info()` method to `OutputFormatter`**: Create a new method that displays informational messages with appropriate styling (e.g., blue panel with info icon)
2. **Use existing methods**: Adapt the code to use `error()` or another existing method (not ideal as the semantic meaning would be wrong)
3. **Create panel directly in CLI**: Display the info panel directly in the CLI code without using the formatter (less maintainable)

**Recommended solution**: Option 1 - Add `info()` method to maintain consistency and follow the single responsibility principle.
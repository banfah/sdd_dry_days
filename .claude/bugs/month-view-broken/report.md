# Bug Report

## Bug Summary
The `display_month_view()` method attempts to access `stats.current_streak` attribute on a `PeriodStats` object, but this attribute doesn't exist. Current streak is not part of PeriodStats and must be calculated separately.

## Bug Details

### Expected Behavior
When viewing a month with dry days, the application should display a month view with:
- Month header with progress information
- Calendar grid showing dry days
- Legend explaining the markers
- (Optionally) Current streak information

### Actual Behavior
When attempting to view a month that contains dry days, the application displays the month header and calendar correctly, but then crashes when trying to display the streak information with:

```python
AttributeError: 'PeriodStats' object has no attribute 'current_streak'
```

### Steps to Reproduce
1. Add some dry days to the database (e.g., `sdd add` for today and a few past days)
2. Run `sdd view --month` command
3. Observe that the month header and calendar display correctly
4. Then see the error: `AttributeError: 'PeriodStats' object has no attribute 'current_streak'`

### Environment
- **Version**: Current development version (after dry_days_count fix)
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
All users attempting to view month statistics when dry days exist in that month.

### Affected Features
- Month view (`sdd view --month`) - partially works but crashes after displaying calendar

**Note**: The month view successfully displays the header panel and calendar grid, but crashes when trying to display the streak panel at the end.

## Additional Context

### Error Messages
```python
AttributeError: 'PeriodStats' object has no attribute 'current_streak'
```

Full error output:
```
╭─────────────────────────────── 📅 Month View ────────────────────────────────╮
│  March 2026                                                                  │
│  Progress: 5/31 days (16.129032258064516%)                                   │
│  ▓▓▓░░░░░░░░░░░░░░░░░ 16%                                                    │
╰──────────────────────────────────────────────────────────────────────────────╯

[Calendar grid displays correctly here]

╭────────────────────────────────────────────────────────╮
│ ✗ Error displaying view                                │
│ 'PeriodStats' object has no attribute 'current_streak' │
╰────────────────────────────────────────────────────────╯
```

### Code Locations

**File**: `src/sdd_dry_days/ui/view_formatters.py`

**Line 373** (Month view streak display):
```python
streak_text = f"Current Streak: 🔥 [green bold]{stats.current_streak}[/green bold] days"
```
**Issue**: Accesses `stats.current_streak` which doesn't exist on PeriodStats

**Line 317** (Method signature):
```python
def display_month_view(self, stats: PeriodStats):
```
**Issue**: Method only receives `stats` parameter, no `current_streak` parameter

**File**: `src/sdd_dry_days/cli.py`

**Line 546** (Method call):
```python
self.view_formatter.display_month_view(stats)
```
**Issue**: Only passes `stats`, doesn't pass `current_streak`

### PeriodStats Definition

**File**: `src/sdd_dry_days/core/stats.py`
**Lines 20-54** (PeriodStats dataclass):

PeriodStats has these attributes:
- `start_date`
- `end_date`
- `total_days`
- `dry_days_count`
- `percentage`
- `longest_streak` ← Has this
- `dry_day_dates`
- `available_days`
- `requested_days`

But does NOT have:
- `current_streak` ← Missing this

### Correct Pattern (Stats View)

The stats view correctly handles current streak as a separate parameter:

**Line 393** (Method signature):
```python
def display_stats_view(
    self,
    stats_30: PeriodStats,
    stats_60: PeriodStats,
    stats_90: PeriodStats,
    stats_120: PeriodStats,
    stats_150: PeriodStats,
    stats_180: PeriodStats,
    current_streak: int  # ← Separate parameter
):
```

**Line 411** (Usage):
```python
header_text = f"Current Streak: [green bold]{current_streak}[/green bold] days"
```

### Related Issues
- Week view doesn't display current streak (simpler, no streak panel)
- Range view doesn't display current streak (simpler, no streak panel)
- Only month view and stats view display current streak
- Stats view correctly receives current_streak as a parameter

## Initial Analysis

### Suspected Root Cause
The `display_month_view()` method was designed to display current streak information (lines 372-383) but was never updated to receive `current_streak` as a parameter. The code assumes `current_streak` is an attribute of `PeriodStats`, but it's not.

Current streak is calculated separately by `StreakCalculator` and must be passed as a parameter, as demonstrated by the `display_stats_view()` method.

### Affected Components
- `src/sdd_dry_days/ui/view_formatters.py`:
  - Line 317: `display_month_view()` method signature (missing parameter)
  - Line 373: Incorrect attribute access `stats.current_streak`

- `src/sdd_dry_days/cli.py`:
  - Line 546: Method call doesn't pass `current_streak`
  - Lines 507-546: `_view_month()` method doesn't calculate current streak

### Potential Solutions
1. **Add current_streak parameter** (like stats view):
   - Update `display_month_view()` signature to accept `current_streak: int`
   - Calculate current streak in CLI's `_view_month()` method
   - Pass current streak when calling `display_month_view()`
   - Use parameter instead of `stats.current_streak`

2. **Remove current streak display** (simpler):
   - Delete the streak panel code (lines 372-383)
   - Keep month view focused on calendar display
   - Users can use stats view for streak information

3. **Calculate within method** (not recommended):
   - Pass all dry days to `display_month_view()`
   - Calculate current streak within the method
   - Violates single responsibility principle

**Recommended solution**: Option 1 - Add current_streak parameter to match the pattern established by stats view, providing comprehensive information in month view.
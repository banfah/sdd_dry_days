# Bug Report

## Bug Summary
The `ViewFormatter` class attempts to access a `dry_days` attribute on `PeriodStats` objects, but the attribute is actually named `dry_days_count`. This causes an `AttributeError` when displaying week and month views with data.

## Bug Details

### Expected Behavior
When viewing a week or month with dry days, the application should display a header panel showing progress information (e.g., "Progress: 3/7 days (42.86%)") followed by a table of the days.

### Actual Behavior
When attempting to view a week or month that contains dry days, the application crashes with an `AttributeError` because `PeriodStats` objects do not have a `dry_days` attribute.

```python
AttributeError: 'PeriodStats' object has no attribute 'dry_days'
```

### Steps to Reproduce
1. Add some dry days to the database (e.g., `sdd add` for today and a few past days)
2. Run `sdd view --week` command
3. Observe the error: `AttributeError: 'PeriodStats' object has no attribute 'dry_days'`

Alternative reproduction:
1. Add some dry days to the database
2. Run `sdd view --month` command
3. Observe the same error

### Environment
- **Version**: Current development version (after info() method fix)
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
All users attempting to view week or month statistics when dry days exist in that period.

### Affected Features
- Week view (`sdd view --week`) - crashes when week has dry days
- Month view (`sdd view --month`) - crashes when month has dry days

**Note**: These views work correctly when there are NO dry days (they display the info message). They only crash when data exists.

## Additional Context

### Error Messages
```python
AttributeError: 'PeriodStats' object has no attribute 'dry_days'
```

Full error context from test:
```
╭──────────────────────────────────────────────────╮
│ ✗ Error displaying view                          │
│ 'PeriodStats' object has no attribute 'dry_days' │
╰──────────────────────────────────────────────────╯
```

### Code Locations
**File**: `src/sdd_dry_days/ui/view_formatters.py`

**Line 205** (Week view):
```python
header_text += f"Progress: [green bold]{stats.dry_days}/7 days ({stats.percentage}%)[/green bold]\n"
```
**Issue**: Accesses `stats.dry_days` which doesn't exist

**Line 335** (Month view):
```python
header_text += f"Progress: [green bold]{stats.dry_days}/{total_days} days ({stats.percentage}%)[/green bold]\n"
```
**Issue**: Accesses `stats.dry_days` which doesn't exist

### Correct Attribute Name
**File**: `src/sdd_dry_days/core/stats.py`
**Line 36** (PeriodStats dataclass):
```python
@dataclass
class PeriodStats:
    """Statistics for dry days over a specific time period.

    Attributes:
        start_date: Start of the period (inclusive).
        end_date: End of the period (inclusive).
        total_days: Total number of days in the period.
        dry_days_count: Number of days marked as dry in the period.  # ← Correct name
        ...
```

The attribute is named `dry_days_count`, not `dry_days`.

### Related Issues
- The empty view case (when `stats.dry_days_count == 0`) works correctly because it checks the correct attribute name
- The range view (`display_range_view`) correctly uses `stats.dry_days_count` on line 532
- Only week and month views have this bug

## Initial Analysis

### Suspected Root Cause
Inconsistent attribute naming between the `PeriodStats` dataclass and the `ViewFormatter` code. The dataclass uses `dry_days_count` throughout, but two locations in `view_formatters.py` mistakenly use `dry_days`.

This appears to be a simple typo or naming inconsistency introduced during development. The code that checks for empty views (`if stats.dry_days_count == 0:`) uses the correct attribute name, but the display code uses the wrong name.

### Affected Components
- `src/sdd_dry_days/ui/view_formatters.py` - Two instances of incorrect attribute access
  - Line 205: `display_week_view()` method
  - Line 335: `display_month_view()` method
- `src/sdd_dry_days/core/stats.py` - PeriodStats dataclass (defines the correct attribute)

### Potential Solutions
1. **Rename attribute references**: Change `stats.dry_days` to `stats.dry_days_count` in both locations (recommended)
2. **Add alias property**: Add a `dry_days` property to PeriodStats that returns `dry_days_count` (not recommended - adds unnecessary complexity)
3. **Rename dataclass attribute**: Change `dry_days_count` to `dry_days` everywhere (not recommended - would break existing code)

**Recommended solution**: Option 1 - Simple rename of two incorrect attribute accesses to match the dataclass.
# Bug Analysis

## Root Cause Analysis

### Investigation Summary
Code investigation revealed an attribute naming inconsistency in the `ViewFormatter` class. The `PeriodStats` dataclass consistently uses `dry_days_count` as the attribute name throughout the codebase, but two methods in `view_formatters.py` incorrectly reference `stats.dry_days` (without the `_count` suffix).

The investigation examined:
1. PeriodStats dataclass definition and attribute names
2. All usages of PeriodStats attributes in view_formatters.py
3. Pattern comparison between working and broken code
4. CLI code that checks for empty views (uses correct attribute)

### Root Cause
The `display_week_view()` and `display_month_view()` methods in `ViewFormatter` reference a non-existent attribute `stats.dry_days`. The correct attribute name defined in the `PeriodStats` dataclass is `stats.dry_days_count`.

**Evidence:**
- `PeriodStats` dataclass (line 36 of `stats.py`): defines `dry_days_count`
- Range view (line 532): correctly uses `stats.dry_days_count` ✓
- Week view (line 205): incorrectly uses `stats.dry_days` ✗
- Month view (line 335): incorrectly uses `stats.dry_days` ✗

### Contributing Factors
1. **Inconsistent naming during development**: Likely copy-paste error or naming change that wasn't updated everywhere
2. **No test coverage**: No integration tests verify that week/month views work with actual data
3. **Code pattern mismatch**: The range view (which works) uses the correct attribute, but week/month views don't follow the same pattern
4. **Ironic bug location**: Empty view checks use correct attribute (`if stats.dry_days_count == 0`), but display code uses wrong attribute

## Technical Details

### Affected Code Locations

**File**: `src/sdd_dry_days/ui/view_formatters.py`

1. **Method**: `display_week_view()`
   - **Line**: 205
   - **Current Code**: `header_text += f"Progress: [green bold]{stats.dry_days}/7 days ({stats.percentage}%)[/green bold]\n"`
   - **Issue**: References `stats.dry_days` which doesn't exist
   - **Should Be**: `stats.dry_days_count`

2. **Method**: `display_month_view()`
   - **Line**: 335
   - **Current Code**: `header_text += f"Progress: [green bold]{stats.dry_days}/{total_days} days ({stats.percentage}%)[/green bold]\n"`
   - **Issue**: References `stats.dry_days` which doesn't exist
   - **Should Be**: `stats.dry_days_count`

**File**: `src/sdd_dry_days/core/stats.py`

- **PeriodStats dataclass** (line 21-51)
  - **Attribute definition** (line 36): `dry_days_count: int`
  - **Docstring confirms**: "dry_days_count: Number of days marked as dry in the period."

**Correct Usage Example** (for comparison):

**File**: `src/sdd_dry_days/ui/view_formatters.py`
- **Method**: `display_range_view()`
  - **Line**: 532
  - **Correct Code**: `header_text += f"Progress: [green bold]{stats.dry_days_count}/{total_days} days ({stats.percentage}%)[/green bold]\n"`
  - **Uses**: Correct attribute name `stats.dry_days_count` ✓

### Data Flow Analysis
1. User runs `sdd view --week` or `sdd view --month` with dry days in database
2. CLI calculates `PeriodStats` object with correct attribute names
3. CLI checks `if stats.dry_days_count == 0:` (works - uses correct attribute)
4. Since count > 0, calls `self.view_formatter.display_week_view(stats, week_days)`
5. `display_week_view()` tries to access `stats.dry_days` on line 205
6. Python raises `AttributeError: 'PeriodStats' object has no attribute 'dry_days'`
7. CLI catches exception and displays error panel

### Dependencies
- **PeriodStats dataclass**: Defines the correct attribute structure
- **No external dependencies**: Pure internal naming inconsistency

## Impact Analysis

### Direct Impact
- Week view completely broken when week contains dry days
- Month view completely broken when month contains dry days
- Users cannot view their progress for current/recent periods with data
- New users who add days immediately encounter crashes

### Indirect Impact
- Poor user experience - crashes when trying to see progress
- Reduced confidence in application quality
- May discourage users from continuing to use the app
- Makes it appear the app doesn't work (even though stats view works fine)

### Risk Assessment
**If not fixed:**
- High severity: Core view functionality broken for common use cases
- Affects all users who have added dry days
- No workaround except using `sdd view --stats` or `sdd view --range`
- Week and month views are completely unusable when data exists

## Solution Approach

### Fix Strategy
**Rename two attribute references from `stats.dry_days` to `stats.dry_days_count`** to match the PeriodStats dataclass definition and align with the correct usage pattern established by the range view.

This approach:
- ✅ Minimal code change (two attribute name fixes)
- ✅ Aligns with existing dataclass definition
- ✅ Matches the pattern used by range view (already working)
- ✅ No breaking changes to any interfaces
- ✅ Fixes both week and month views simultaneously
- ✅ No changes needed to PeriodStats or CLI code

### Implementation Pattern
Simple find-and-replace in two locations:

**Location 1 - Week View (line 205):**
```python
# BEFORE:
header_text += f"Progress: [green bold]{stats.dry_days}/7 days ({stats.percentage}%)[/green bold]\n"

# AFTER:
header_text += f"Progress: [green bold]{stats.dry_days_count}/7 days ({stats.percentage}%)[/green bold]\n"
```

**Location 2 - Month View (line 335):**
```python
# BEFORE:
header_text += f"Progress: [green bold]{stats.dry_days}/{total_days} days ({stats.percentage}%)[/green bold]\n"

# AFTER:
header_text += f"Progress: [green bold]{stats.dry_days_count}/{total_days} days ({stats.percentage}%)[/green bold]\n"
```

### Alternative Solutions

1. **Add `dry_days` property to PeriodStats**
   - ❌ Adds unnecessary complexity
   - ❌ Maintains confusing dual naming
   - ❌ Creates inconsistency with documented attribute name
   - ❌ Future maintenance burden

2. **Rename `dry_days_count` to `dry_days` everywhere**
   - ❌ Would require changes to dataclass definition
   - ❌ Would break all other correct usages (stats view, range view, CLI checks)
   - ❌ Much larger refactor with higher risk
   - ❌ Changes would ripple through multiple files

3. **Use getattr() with fallback**
   - ❌ Masks the real problem
   - ❌ Adds runtime overhead
   - ❌ Makes code harder to understand
   - ❌ Doesn't fix the underlying inconsistency

### Risks and Trade-offs

**Chosen Solution (rename attribute references):**
- ✅ Extremely low risk - simple find-replace
- ✅ No breaking changes
- ✅ Aligns with established naming convention
- ✅ Matches working code pattern (range view)
- ⚠️ None - this is the obvious correct fix

**Testing considerations:**
- Test week view with dry days (should show progress)
- Test month view with dry days (should show progress)
- Verify empty views still work (already use correct attribute)
- Ensure range view still works (already correct, no changes)

## Implementation Plan

### Changes Required

1. **Change 1: Fix Week View attribute reference**
   - **File**: `src/sdd_dry_days/ui/view_formatters.py`
   - **Line**: 205
   - **Modification**: Change `stats.dry_days` to `stats.dry_days_count`
   ```python
   # CHANGE FROM:
   header_text += f"Progress: [green bold]{stats.dry_days}/7 days ({stats.percentage}%)[/green bold]\n"

   # CHANGE TO:
   header_text += f"Progress: [green bold]{stats.dry_days_count}/7 days ({stats.percentage}%)[/green bold]\n"
   ```

2. **Change 2: Fix Month View attribute reference**
   - **File**: `src/sdd_dry_days/ui/view_formatters.py`
   - **Line**: 335
   - **Modification**: Change `stats.dry_days` to `stats.dry_days_count`
   ```python
   # CHANGE FROM:
   header_text += f"Progress: [green bold]{stats.dry_days}/{total_days} days ({stats.percentage}%)[/green bold]\n"

   # CHANGE TO:
   header_text += f"Progress: [green bold]{stats.dry_days_count}/{total_days} days ({stats.percentage}%)[/green bold]\n"
   ```

### Testing Strategy

**Manual Testing:**
1. Add dry days to database: `sdd add` for today and a few past days
2. Test week view: `sdd view --week` - should show progress panel and table
3. Test month view: `sdd view --month` - should show progress panel and calendar
4. Test empty week view: Use fresh database, verify info message still appears
5. Test empty month view: Use fresh database, verify info message still appears
6. Test range view: `sdd view --range 2026-03-01 2026-03-09` - verify still works

**Automated Testing:**
- Existing view formatter tests should continue to pass
- No new tests required (visual output is hard to test programmatically)
- Integration tests may catch this if they test non-empty views

**Visual Verification:**
Expected output for week view with data:
```
╭────────────────────────────────────────────────────╮
│ Week of March 3-9, 2026                            │
│ Progress: 3/7 days (42.86%)                        │
│ ▓▓▓▓▓▓▓▓░░░░░░░░░░░░ 42.86%                        │
╰────────────────────────────────────────────────────╯

[Table with daily breakdown]
```

### Rollback Plan
If the fix causes issues:
1. **Immediate rollback**: Revert the two attribute name changes
2. **Alternative**: Investigate if there's a deeper issue with PeriodStats
3. **Risk is minimal**: This is a simple attribute name fix with clear correctness

## Code Reuse Opportunities

### Existing Patterns
- **Range view**: Already uses correct attribute `stats.dry_days_count` on line 532
- **Empty view checks**: Already use correct attribute `stats.dry_days_count` in if statements
- **Stats view**: Uses correct attribute `stats.dry_days_count` on line 439

The fix simply aligns week and month views with the pattern already established by these working implementations.

### Integration Points
- **No integration changes needed**: Pure view layer fix
- **PeriodStats dataclass**: No changes needed (already correct)
- **CLI code**: No changes needed (already correct)
- **No API changes**: Only internal display code affected

### Future Prevention
- **Pattern documentation**: Document that PeriodStats uses `dry_days_count` not `dry_days`
- **Code review guideline**: Check attribute names match dataclass definitions
- **Integration tests**: Add tests that verify views work with actual data, not just empty states
- **Consistency check**: When adding new views, verify attribute names match PeriodStats
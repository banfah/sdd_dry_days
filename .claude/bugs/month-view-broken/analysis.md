# Bug Analysis

## Root Cause Analysis

### Investigation Summary
Comprehensive code investigation revealed that the `display_month_view()` method was designed to display current streak information but was never properly integrated with the current streak calculation logic. The method assumes `current_streak` is an attribute of `PeriodStats`, but it's not - current streak must be calculated separately using `StreakCalculator` and passed as a parameter.

The investigation examined:
1. PeriodStats dataclass definition and attributes
2. display_month_view() implementation and method signature
3. CLI _view_month() method and what it passes
4. Comparison with working pattern in _view_stats() and display_stats_view()
5. StreakCalculator usage patterns

### Root Cause
The `display_month_view()` method attempts to access `stats.current_streak` on line 374, but `PeriodStats` objects don't have a `current_streak` attribute. The PeriodStats dataclass only contains:
- Period-specific statistics (count, percentage, longest streak in that period)
- Date range information
- Data availability metadata

Current streak is a **global metric** (across all dry days, not period-specific) and must be calculated separately using `StreakCalculator.calculate_current_streak(all_dry_days)`.

### Contributing Factors
1. **Incomplete implementation**: Streak panel code was added to display_month_view() but parameter was never added
2. **Missing calculation in CLI**: _view_month() doesn't calculate current_streak before calling display_month_view()
3. **Pattern inconsistency**: Stats view correctly uses current_streak as a parameter, but month view doesn't follow this pattern
4. **No test coverage**: No integration tests verify month view with data, so the missing parameter wasn't caught

## Technical Details

### Affected Code Locations

**File**: `src/sdd_dry_days/ui/view_formatters.py`

1. **Method signature** (Line 317):
   ```python
   def display_month_view(self, stats: PeriodStats):
   ```
   **Issue**: Missing `current_streak: int` parameter

2. **Incorrect attribute access** (Line 374):
   ```python
   streak_text = f"Current Streak: 🔥 [green bold]{stats.current_streak}[/green bold] days"
   ```
   **Issue**: `stats.current_streak` doesn't exist

3. **Streak panel display** (Lines 373-384):
   ```python
   # Display current streak with fire emoji
   streak_text = f"Current Streak: 🔥 [green bold]{stats.current_streak}[/green bold] days"
   if stats.longest_streak > 0:
       streak_text += f"\nLongest Streak: 🔥 [green bold]{stats.longest_streak}[/green bold] days"

   streak_panel = Panel(
       streak_text,
       title="Streaks",
       border_style="yellow",
       padding=(1, 2)
   )
   self.console.print(streak_panel)
   ```
   **Issue**: Entire panel fails because of line 374

**File**: `src/sdd_dry_days/cli.py`

1. **Missing calculation** (_view_month method, lines 507-546):
   - Gets month dates (line 532)
   - Fetches dry days for month (line 535)
   - Calculates period stats (line 538)
   - **Missing**: Never calculates current_streak
   - Calls display_month_view with only stats (line 546)

**Correct Pattern for Comparison**:

**File**: `src/sdd_dry_days/cli.py` (_view_stats method)

**Line 607** (Calculates current streak):
```python
current_streak = self.streak_calculator.calculate_current_streak(all_dry_days)
```

**Line 610** (Passes as parameter):
```python
self.view_formatter.display_stats_view(stats_30, stats_60, stats_90, stats_120, stats_150, stats_180, current_streak)
```

**File**: `src/sdd_dry_days/ui/view_formatters.py` (display_stats_view method)

**Line 386-393** (Method signature):
```python
def display_stats_view(
    self,
    stats_30: PeriodStats,
    stats_60: PeriodStats,
    stats_90: PeriodStats,
    stats_120: PeriodStats,
    stats_150: PeriodStats,
    stats_180: PeriodStats,
    current_streak: int  # ← Correct: separate parameter
):
```

**Line 411** (Usage):
```python
header_text = f"Current Streak: [green bold]{current_streak}[/green bold] days"
```

### Data Flow Analysis

**Current (Broken) Flow:**
1. User runs `sdd view --month`
2. CLI's `_view_month()` method executes
3. Gets month dates and fetches dry days for that month only
4. Calculates PeriodStats for the month
5. Calls `display_month_view(stats)` with only stats parameter
6. display_month_view() displays header, calendar, and legend successfully
7. display_month_view() tries to access `stats.current_streak` on line 374
8. Python raises `AttributeError`

**Correct (Stats View) Flow:**
1. User runs `sdd view --stats`
2. CLI's `_view_stats()` method executes
3. Fetches ALL dry days from storage
4. Calculates PeriodStats for each period (30/60/90/120/150/180 days)
5. Calculates current_streak using StreakCalculator with ALL dry days
6. Calls `display_stats_view(...)` with all stats AND current_streak
7. display_stats_view() uses current_streak parameter successfully

### Dependencies
- **StreakCalculator**: Required to calculate current streak from all dry days
- **PeriodStats**: Contains period-specific stats but not current streak
- **Storage**: Needed to get all dry days for current streak calculation

## Impact Analysis

### Direct Impact
- Month view crashes after successfully displaying calendar
- Users cannot see current streak in month view
- Partial functionality - header and calendar work, but streak panel fails
- Poor user experience - view appears to work then crashes

### Indirect Impact
- Reduced confidence in application quality
- Users may think month view is completely broken
- May discourage users from using calendar visualization
- Streak information unavailable in calendar context

### Risk Assessment
**If not fixed:**
- High severity: Month view partially broken for users with data
- Affects visualization of progress in calendar format
- Workaround exists: Use stats view for streak information
- Month view still provides value (calendar grid) but incomplete

## Solution Approach

### Fix Strategy
**Add `current_streak` parameter to `display_month_view()`** following the pattern established by `display_stats_view()`:

1. Update method signature to accept `current_streak: int` parameter
2. Calculate current streak in CLI's `_view_month()` method
3. Pass current streak when calling `display_month_view()`
4. Use parameter instead of `stats.current_streak` attribute

This approach:
- ✅ Follows established pattern from stats view
- ✅ Minimal code changes (3 locations)
- ✅ Fixes the crash and provides complete functionality
- ✅ Maintains month view's comprehensive information display
- ✅ No breaking changes to PeriodStats dataclass

### Alternative Solutions

1. **Remove streak panel entirely**
   - ✅ Simpler fix (delete lines 373-384)
   - ✅ No parameter changes needed
   - ❌ Loses valuable information from month view
   - ❌ Inconsistent with documented behavior (docstring mentions streaks)
   - ❌ Less comprehensive than intended design

2. **Calculate current_streak within display_month_view()**
   - ❌ Requires passing all dry days to method
   - ❌ Violates single responsibility principle
   - ❌ Display method shouldn't do business logic
   - ❌ Inconsistent with stats view pattern

3. **Add current_streak to PeriodStats**
   - ❌ Conceptually wrong (current streak is global, not period-specific)
   - ❌ Would require calculation in StatisticsCalculator
   - ❌ Breaks the separation between period stats and global streaks
   - ❌ Larger refactor with higher risk

### Risks and Trade-offs

**Chosen Solution (add parameter):**
- ✅ Very low risk - follows proven pattern
- ✅ No breaking changes to existing code
- ✅ Provides complete functionality as intended
- ✅ Consistent with stats view implementation
- ⚠️ Requires changes in 3 locations (method signature, CLI calculation, method call)

**Testing considerations:**
- Test month view with dry days (should show streak panel)
- Test month view with no current streak (should handle gracefully)
- Verify empty month view still works (info message)
- Ensure week view still works (doesn't have streak panel)

## Implementation Plan

### Changes Required

1. **Change 1: Add current_streak parameter to display_month_view()**
   - **File**: `src/sdd_dry_days/ui/view_formatters.py`
   - **Line**: 317
   - **Modification**: Add `current_streak: int` parameter to method signature
   ```python
   # CHANGE FROM:
   def display_month_view(self, stats: PeriodStats):

   # CHANGE TO:
   def display_month_view(self, stats: PeriodStats, current_streak: int):
       """Display month view with calendar-style layout.

       Args:
           stats: PeriodStats instance for the month period.
           current_streak: Current consecutive dry day streak.
       """
   ```

2. **Change 2: Use parameter instead of attribute**
   - **File**: `src/sdd_dry_days/ui/view_formatters.py`
   - **Line**: 374
   - **Modification**: Change `stats.current_streak` to `current_streak`
   ```python
   # CHANGE FROM:
   streak_text = f"Current Streak: 🔥 [green bold]{stats.current_streak}[/green bold] days"

   # CHANGE TO:
   streak_text = f"Current Streak: 🔥 [green bold]{current_streak}[/green bold] days"
   ```

3. **Change 3: Calculate current streak in CLI**
   - **File**: `src/sdd_dry_days/cli.py`
   - **Location**: After line 538 (after calculating stats)
   - **Modification**: Add current streak calculation
   ```python
   # ADD AFTER LINE 538:
   # Calculate statistics for the month
   stats = StatisticsCalculator.calculate_period_stats(dry_days, start, end)

   # Calculate current streak (across all dry days, not just this month)
   all_dry_days = self.storage.get_all_dry_days()
   current_streak = self.streak_calculator.calculate_current_streak(all_dry_days)
   ```

4. **Change 4: Pass current_streak to display method**
   - **File**: `src/sdd_dry_days/cli.py`
   - **Line**: 546
   - **Modification**: Pass current_streak as parameter
   ```python
   # CHANGE FROM:
   self.view_formatter.display_month_view(stats)

   # CHANGE TO:
   self.view_formatter.display_month_view(stats, current_streak)
   ```

### Testing Strategy

**Manual Testing:**
1. Add dry days: `sdd add` for today and several past days
2. Test month view: `sdd view --month` - should show streak panel
3. Test with zero current streak: Add days with gap before today
4. Test empty month: Fresh database - should show info message
5. Verify visual formatting of streak panel

**Automated Testing:**
- Existing view formatter tests should continue to pass
- Update test mocks to include current_streak parameter
- Integration tests may need updates to pass current_streak

**Visual Verification:**
Expected output with streaks:
```
╭─────────────────────── 📅 Month View ────────────────────────╮
│  March 2026                                                  │
│  Progress: 5/31 days (16.13%)                                │
│  ▓▓▓░░░░░░░░░░░░░░░░░ 16%                                    │
╰──────────────────────────────────────────────────────────────╯

[Calendar grid]

╭─────────────────────── Streaks ──────────────────────────────╮
│  Current Streak: 🔥 3 days                                   │
│  Longest Streak: 🔥 6 days                                   │
╰──────────────────────────────────────────────────────────────╯
```

### Rollback Plan
If the fix causes issues:
1. **Immediate rollback**: Remove current_streak parameter, delete streak panel code
2. **Alternative**: Use simplified version without streak display
3. **Risk is minimal**: Following proven pattern from stats view

## Code Reuse Opportunities

### Existing Patterns
- **Stats view pattern**: Established template for passing current_streak as parameter
- **StreakCalculator usage**: Already used correctly in stats view (line 607)
- **Method signature pattern**: Consistent with how other comprehensive views receive data

### Integration Points
- **StreakCalculator**: Reuse existing calculate_current_streak() method
- **Storage**: Reuse existing get_all_dry_days() method
- **Display pattern**: Follow stats view's parameter passing approach
- **No new components needed**: All required utilities already exist

### Future Prevention
- **Pattern documentation**: Document that current_streak is always a parameter, never an attribute
- **Code review guideline**: Check that methods displaying current_streak receive it as a parameter
- **Consistency check**: When adding new views, verify parameter patterns match existing views
- **Integration tests**: Add tests that verify views with actual data display correctly
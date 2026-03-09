# Bug Report

## Bug Summary
The right borders of both the Statistics Overview panel and the statistics table are misaligned, creating a jagged vertical line instead of a clean straight edge in the `sdd view --stats` output.

## Bug Details

### Expected Behavior
Both the Statistics Overview panel and the statistics table should have their right borders aligned in a straight vertical line, creating a cohesive and professional visual display.

### Actual Behavior
The right borders of the panel and table are at different horizontal positions, creating a misaligned, jagged appearance. Neither component is using consistent width settings, causing them to render at different widths based on their individual content.

### Steps to Reproduce
1. Run `sdd view --stats` command
2. Observe the output display
3. Compare the right border of the top panel with the right border of the bottom table
4. Notice the misalignment

### Environment
- **Version**: Current development version (after import feature completion)
- **Platform**: macOS Darwin 25.3.0
- **Terminal**: Standard terminal with Rich library rendering
- **Python**: 3.12.2

## Impact Assessment

### Severity
- [ ] Critical - System unusable
- [ ] High - Major functionality broken
- [x] Medium - Feature impaired but workaround exists
- [ ] Low - Minor issue or cosmetic

### Affected Users
All users who view statistics using `sdd view --stats` command.

### Affected Features
- Statistics display visualization
- Visual consistency and polish of the CLI output

## Additional Context

### Visual Evidence
Current output shows misaligned right borders:
```
╭─────────────────────────── 📈 Statistics Overview ───────────────────────────╮
│                                                                              │
│  Current Streak: 🔥 0 days                                                   │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯
                                                                               ↑ Panel right border
┏━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Period ┃ Dry Days ┃ Total Days ┃ Progress                 ┃ Longest Streak ┃
┡━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
...                                                                            ↑ Table right border
```

**Issue**: The panel's right border (╯) and the table's right border (┓) are at different horizontal positions, creating a jagged vertical line instead of a clean, aligned edge.

### Code Location
- **File**: `src/sdd_dry_days/ui/view_formatters.py`
- **Method**: `display_stats()`
- **Lines**: 411-417 (Panel creation)

### Current Implementation
```python
header_panel = Panel(
    header_text,
    title="📈 Statistics Overview",
    border_style="green",
    padding=(1, 2)
)
```

The Panel lacks an `expand` parameter, causing it to auto-size to its content width rather than matching the table below.

## Initial Analysis

### Suspected Root Cause
Both the Rich `Panel` and `Table` components are using different width strategies:
- The `Panel` auto-sizes to its content without an explicit `expand` parameter
- The `Table` auto-sizes to fit its columns without width constraints
- Neither component is configured to use consistent width, causing them to render at different widths

The lack of width coordination between these two components results in misaligned right borders.

### Affected Components
- `src/sdd_dry_days/ui/view_formatters.py` - `display_stats()` method
  - Lines 411-417: Panel creation (no expand parameter)
  - Lines 421-458: Table creation (no width constraints)

### Potential Solutions
1. **Add `expand=True` to both components**: Make both fill the full console width consistently
2. **Use a Box container**: Wrap both in a Rich Box or Group with consistent width
3. **Set explicit widths**: Calculate and set matching widths for both components
4. **Use Rich Layout**: Use Rich's layout system to ensure consistent alignment

### Related Code Patterns
- The import summary formatter uses `expand=False` for compact display
- Other formatters typically use either full expansion or content-fitting consistently
- Statistics display requires both components to use the same width strategy for visual alignment
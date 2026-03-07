# Requirements Document: Add Dry Days

## Introduction

The "Add Dry Days" feature is the foundational capability of SDD Dry Days, enabling users to record alcohol-free days (dry days) with minimal effort. This feature supports quick logging of today's date by default, with flexibility to add specific dates or date ranges when needed. The goal is to create a frictionless experience that encourages consistent usage and makes tracking dry days as simple as possible.

## Alignment with Product Vision

This feature directly supports the core product principles outlined in product.md:

1. **Simplicity First**: Adding a dry day should be effortless - ideally a single command with no required parameters
2. **Low Friction**: Minimal keystrokes to log a dry day (< 30 seconds total interaction time)
3. **Privacy Focused**: Data stored locally on user's machine in simple JSON format
4. **Encouraging**: Provide immediate positive feedback when a dry day is added

This feature is the **first MVP feature** listed in product.md and is essential for all other functionality (calendar view, goals, statistics) to work.

## Requirements

### Requirement 1: Add Today as Dry Day (Default Behavior)

**User Story:** As a user tracking my dry days, I want to quickly mark today as a dry day with a single command, so that I can log my progress with minimal effort.

#### Acceptance Criteria

1. WHEN the user runs the add command without any date parameter THEN the system SHALL record today's date as a dry day
2. WHEN a dry day is successfully added THEN the system SHALL display a confirmation message with the date added
3. WHEN a dry day is successfully added THEN the system SHALL show the current streak count (consecutive dry days)
4. WHEN the user tries to add today as a dry day and it already exists THEN the system SHALL display a friendly message indicating the date is already recorded
5. WHEN today is added as a dry day THEN the system SHALL persist the data to the JSON storage file immediately

### Requirement 2: Add Specific Date as Dry Day

**User Story:** As a user, I want to add a dry day for a specific date in the past or future, so that I can backfill my tracking history or plan ahead.

#### Acceptance Criteria

1. WHEN the user provides a date in ISO format (YYYY-MM-DD) THEN the system SHALL record that specific date as a dry day
2. WHEN the user provides a date in common formats (MM/DD/YYYY, DD-MM-YYYY) THEN the system SHALL parse and accept the date
3. IF the provided date format is invalid THEN the system SHALL display an error message with examples of valid formats
4. WHEN a specific date is successfully added THEN the system SHALL display confirmation with the date that was added
5. IF the specific date already exists as a dry day THEN the system SHALL display a message indicating it's already recorded
6. WHEN a past date is added THEN the system SHALL accept it without restriction
7. WHEN a future date is added THEN the system SHALL accept it and mark it as planned

### Requirement 3: Add Multiple Dates (Date Rang

**User Story:** As a user, I want to add multiple consecutive dates as dry days at once, so that I can quickly backfill a range of dates without repeating the command.

#### Acceptance Criteria

1. WHEN the user provides a date range with start and end dates THEN the system SHALL record all dates in that range (inclusive) as dry days
2. WHEN a date range is provided THEN the system SHALL display the count of dates added
3. IF any date in the range already exists THEN the system SHALL skip those dates and only add new ones
4. WHEN adding a date range THEN the system SHALL display a summary showing how many dates were added vs. already existed
5. IF the end date is before the start date THEN the system SHALL display an error message
6. WHEN a large date range is provided (>90 days) THEN the system SHALL ask for confirmation before proceeding

### Requirement 4: Data Persistence

**User Story:** As a user, I want my dry day records to be saved reliably, so that I don't lose my progress if the application closes.

#### Acceptance Criteria

1. WHEN a dry day is added THEN the system SHALL save the data to a JSON file at `~/.sdd_dry_days/data.json`
2. IF the data directory doesn't exist THEN the system SHALL create it automatically with appropriate permissions
3. IF the data file doesn't exist THEN the system SHALL create it with an empty dry days list
4. WHEN writing to the data file THEN the system SHALL use atomic writes to prevent data corruption
5. IF the data file cannot be written THEN the system SHALL display an error message with the reason
6. WHEN reading existing data THEN the system SHALL validate the JSON structure and handle corrupted files gracefully

### Requirement 5: Optional Notes/Tags

**User Story:** As a user, I want to optionally add a note to a dry day entry, so that I can remember context or significant events associated with that day.

#### Acceptance Criteria

1. WHEN the user provides a note with the add command THEN the system SHALL store the note with the dry day entry
2. IF no note is provided THEN the system SHALL store the dry day with an empty note field
3. WHEN a note is added THEN the system SHALL display it in the confirmation message
4. WHEN the user adds a note to an existing dry day THEN the system SHALL update the note without duplicating the date

## Non-Functional Requirements

### Performance

- **Startup Time**: Command execution SHALL complete in < 1 second on modern hardware
- **Response Time**: User SHALL see confirmation feedback immediately (< 200ms after data is saved)
- **Data Size**: System SHALL efficiently handle at least 5 years of daily entries (1,825 dates) without performance degradation

### Security

- **File Permissions**: Data directory SHALL be created with user-only read/write permissions (700)
- **Data File Permissions**: Data file SHALL be created with user-only read/write permissions (600)
- **Input Validation**: All date inputs SHALL be validated to prevent injection attacks
- **No External Communication**: System SHALL NOT transmit any data outside the local machine

### Reliability

- **Atomic Writes**: Data writes SHALL be atomic to prevent partial writes during system crashes
- **Data Validation**: System SHALL validate data structure on read and handle corrupted files gracefully
- **Error Recovery**: IF data file is corrupted, system SHALL create a backup and initialize a new file
- **Idempotent Operations**: Adding the same date multiple times SHALL NOT create duplicate entries

### Usability

- **Clear Feedback**: User SHALL receive clear confirmation or error messages for all operations
- **Helpful Errors**: Error messages SHALL include examples or suggestions for fixing the issue
- **No Required Parameters**: Default behavior (add today) SHALL work without any parameters
- **Date Format Flexibility**: System SHALL accept multiple common date formats for user convenience
- **Colorful Output**: Confirmation messages SHALL use colors (via Rich library) to provide visual feedback and encouragement

## Technical Constraints

### Technology Stack (from tech.md)
- **Language**: Python 3.8+
- **Core Libraries**: datetime, json, pathlib (standard library)
- **UI Library**: Rich (for colorful console output)
- **Storage**: JSON file at `~/.sdd_dry_days/data.json`

### Data Format
```json
{
  "dry_days": [
    {
      "date": "2026-03-06",
      "note": "First dry day!",
      "added_at": "2026-03-06T14:30:00",
      "is_planned": false
    }
  ],
  "version": "1.0"
}
```

### CLI Interface Design
```bash
# Add today (default)
sdd add

# Add specific date
sdd add 2026-03-06
sdd add 03/06/2026

# Add date with note
sdd add --note "Feeling great today!"
sdd add 2026-03-06 --note "Birthday celebration"

# Add date range
sdd add --range 2026-03-01 2026-03-05
sdd add -r 2026-03-01 2026-03-05

# Future: List recent dry days to verify
sdd add --list
```

## Edge Cases and Special Scenarios

### Edge Case 1: Leap Year Dates
- System SHALL correctly handle February 29 in leap years
- System SHALL reject February 29 in non-leap years with clear error message

### Edge Case 2: Timezone Considerations
- System SHALL use the local system timezone for "today"
- System SHALL store dates in ISO format (YYYY-MM-DD) without time information
- System SHALL handle daylight saving time transitions correctly

### Edge Case 3: System Clock Changes
- IF system clock is changed backward THEN existing future dates SHALL remain valid
- IF system clock is changed forward THEN past dates SHALL remain valid

### Edge Case 4: Concurrent Access
- IF multiple instances try to write simultaneously THEN the last write SHALL win (acceptable for single-user MVP)
- System SHALL use file locking if available on the platform

### Edge Case 5: Disk Space
- IF disk is full THEN system SHALL display a clear error message
- System SHALL check available disk space before attempting writes (optional, nice-to-have)

## Success Metrics

### Functional Success
- User can add today as a dry day with a single command
- User can add any specific date without errors
- User can add date ranges efficiently
- Data persists correctly between sessions

### User Experience Success
- Average interaction time < 30 seconds
- Clear, colorful, encouraging feedback
- Zero data loss incidents
- Intuitive CLI commands that don't require documentation for basic usage

## Future Considerations

These are NOT part of this specification but should be considered in the design for future extensibility:

1. **Undo Feature**: Ability to remove accidentally added dry days
2. **Import/Export**: Ability to import dry days from other sources or export for backup
3. **Bulk Operations**: Ability to add dry days from a file
4. **Calendar Integration**: Sync with calendar applications
5. **Reminders**: Optional reminders to log dry days
6. **MongoDB Migration**: Easy migration path when moving from JSON to MongoDB storage

## Dependencies

### Depends On (Blocking)
- None (this is the first feature to be implemented)

### Depended On By (Enabling)
- **Calendar View Feature**: Requires dry days data to display
- **Goal Tracking Feature**: Requires dry days data to calculate progress
- **Statistics Feature**: Requires dry days data to compute metrics
- **Streak Calculation**: Requires dry days data to determine consecutive days

## Validation and Testing Requirements

### Unit Testing Requirements
- Test date parsing for various formats
- Test duplicate detection logic
- Test date range generation
- Test data validation and error handling
- Test file I/O operations with mocked filesystem

### Integration Testing Requirements
- Test complete add workflow from command to storage
- Test with actual file system operations
- Test with corrupted data files
- Test with missing directories

### Manual Testing Scenarios
1. Fresh install (no data directory exists)
2. Adding multiple dates in various formats
3. Attempting to add duplicates
4. Adding very large date ranges
5. Testing with system clock at different dates
6. Testing with full disk (if possible)
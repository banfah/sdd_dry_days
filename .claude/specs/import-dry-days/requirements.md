# Requirements Document: Import Dry Days

## Introduction

The "Import Dry Days" feature enables users to batch import multiple dry day dates from a simple text file. This feature provides a convenient way to backfill historical data or migrate from other tracking systems, eliminating the need to manually enter each date individually.

This feature builds upon the existing "Add Dry Days" functionality, leveraging the existing DateParser and Storage components to maintain consistency with manual entry methods.

## Alignment with Product Vision

This feature directly supports the core product principles outlined in product.md:

1. **Simplicity First**: Simple text file format (one date per line) makes importing effortless
2. **Privacy Focused**: Local file import with no external transmission maintains data privacy
3. **Non-Judgmental**: Focuses on importing dry days to build positive tracking history
4. **Encouraging**: Enables users to quickly populate their tracking history and see progress

This feature enhances the first MVP feature listed in product.md: **Add Dry Days** - by providing a bulk import option that complements the existing manual entry methods.

## Requirements

### Requirement 1: Import from Text File

**User Story:** As a user tracking my dry days, I want to import multiple dates from a text file, so that I can quickly populate my history without manually entering each date.

#### Acceptance Criteria

1. **AC-1.1**: WHEN the user runs `sdd import <filepath>` THEN the system SHALL read the text file and parse each line as a date
2. **AC-1.2**: WHEN reading the file THEN the system SHALL skip empty lines and lines containing only whitespace
3. **AC-1.3**: WHEN parsing dates THEN the system SHALL use the existing DateParser to support all standard formats (ISO, US, EU, compact)
4. **AC-1.4**: WHEN a line cannot be parsed as a valid date THEN the system SHALL log the error but continue processing remaining dates
5. **AC-1.5**: WHEN all dates are processed THEN the system SHALL display a summary showing: total lines read, successful imports, duplicates skipped, and errors encountered

### Requirement 2: Duplicate Handling

**User Story:** As a user importing dry days, I want the system to handle duplicates gracefully, so that I can safely re-import files without creating duplicate entries.

#### Acceptance Criteria

1. **AC-2.1**: WHEN a date already exists in storage THEN the system SHALL skip it and count it as a duplicate (not an error)
2. **AC-2.2**: WHEN displaying the summary THEN the system SHALL show the count of duplicates skipped separately from errors
3. **AC-2.3**: WHEN all dates are duplicates THEN the system SHALL display a friendly message like "All dates already recorded. No new dry days added."

### Requirement 3: Error Handling

**User Story:** As a user importing dry days, I want clear error messages when something goes wrong, so that I can fix issues and retry the import.

#### Acceptance Criteria

1. **AC-3.1**: WHEN the file path does not exist THEN the system SHALL display error "File not found: <filepath>. Please check the path and try again."
2. **AC-3.2**: WHEN the file cannot be read (permissions error) THEN the system SHALL display error "Cannot read file: <filepath>. Check file permissions."
3. **AC-3.3**: WHEN the file is empty THEN the system SHALL display "File is empty. Add dates (one per line) and try again."
4. **AC-3.4**: WHEN a line has an invalid date format THEN the system SHALL log the line number and content: "Line X: Invalid date format 'content'. Skipped."
5. **AC-3.5**: WHEN errors occur THEN the system SHALL still import successfully parsed dates and show which lines failed

### Requirement 4: File Format

**User Story:** As a user preparing an import file, I want a simple, clear file format, so that I can easily create import files without complex formatting.

#### Acceptance Criteria

1. **AC-4.1**: WHEN creating an import file THEN the user SHALL use plain text format (.txt)
2. **AC-4.2**: WHEN writing dates THEN the user SHALL place one date per line
3. **AC-4.3**: WHEN a line starts with # THEN the system SHALL treat it as a comment and skip it
4. **AC-4.4**: WHEN mixing date formats THEN the system SHALL accept all supported formats in the same file (ISO, US, EU, compact)
5. **AC-4.5**: WHEN the file has a .txt, .csv, or no extension THEN the system SHALL process it (format-agnostic)

### Requirement 5: Import Summary Display

**User Story:** As a user who just completed an import, I want to see a clear summary of what was imported, so that I know the import was successful and understand any issues.

#### Acceptance Criteria

1. **AC-5.1**: WHEN the import completes THEN the system SHALL display a formatted summary panel
2. **AC-5.2**: WHEN displaying the summary THEN the system SHALL show:
   - Total lines processed
   - Successfully added dry days
   - Duplicates skipped
   - Errors encountered
3. **AC-5.3**: WHEN there are errors THEN the system SHALL list each error with line number and reason
4. **AC-5.4**: WHEN the import is successful THEN the system SHALL use green color (#00FF00) for positive metrics
5. **AC-5.5**: WHEN all imports succeed THEN the system SHALL display "✓ Import completed successfully!"

### Requirement 6: Performance

**User Story:** As a user importing a large history, I want the import to complete quickly, so that I can start using the application immediately.

#### Acceptance Criteria

1. **AC-6.1**: WHEN importing up to 1000 dates THEN the system SHALL complete within 5 seconds
2. **AC-6.2**: WHEN importing THEN the system SHALL process dates sequentially (no complex batch optimization needed)
3. **AC-6.3**: WHEN the import is in progress THEN the system SHALL provide feedback (e.g., "Processing..." message)

## Example File Format

```txt
# My dry days history - imported from old tracker
# Format: one date per line, any standard format works

2026-01-01
2026-01-02
2026-01-03

# Week 2
2026-01-08
2026-01-09

# Mixed formats work fine
01/15/2026
20/01/2026
20260121
```

## Example Output

```
┌─────────────────────────────────────────────┐
│ 📥 Import Summary                            │
├─────────────────────────────────────────────┤
│ Total lines processed: 12                   │
│ Successfully added: 8 dry days              │
│ Duplicates skipped: 2                       │
│ Errors: 2                                   │
│                                              │
│ ❌ Errors encountered:                       │
│   Line 7: Invalid date format '2026-13-45' │
│   Line 10: Invalid date format 'yesterday'  │
│                                              │
│ ✓ Import completed successfully!            │
└─────────────────────────────────────────────┘
```

## Non-Functional Requirements

### Performance
- Import up to 1000 dates within 5 seconds
- Sequential processing (no complex batching required)
- Simple line-by-line reading (no streaming for small files)

### Security
- No external file access (user provides explicit local path)
- File permissions validation before reading
- No code execution or dynamic evaluation of file contents

### Reliability
- Continue processing on individual date parse errors
- Atomic storage operations (each dry day saved independently)
- No partial state if file reading fails

### Usability
- Clear error messages with line numbers for debugging
- Simple file format (plain text, one date per line)
- Helpful summary showing exactly what was imported
- Support for comments (lines starting with #)

## Technical Constraints

1. **DateParser Reuse**: Must use existing DateParser.parse() for consistency
2. **Storage Abstraction**: Must work through existing Storage interface
3. **CLI Integration**: Must integrate with existing argparse-based CLI
4. **File Handling**: Use Python's built-in file operations (no external libraries)
5. **Simplicity**: Keep implementation simple - no complex validation, progress bars, or advanced features
6. **Error Tolerance**: Process as many valid dates as possible even if some lines fail

# Year Field Updates Summary

## Overview
Updated all SQL scripts to use the current year (`strftime('%Y', 'now')`) when populating the year field for new records instead of hardcoding 2025.

## Files Modified

### 1. Schema File (`schema.sql`)
- Added `year INTEGER DEFAULT 2025` to:
  - `itineraries` table
  - `itinerary_camps` table  
  - `itinerary_programs` table
  - `camp_programs` table

### 2. Itinerary Update Script (`update_itineraries.sql`)
- Modified all 24 UPDATE statements to include:
  ```sql
  year = strftime('%Y', 'now'),
  ```
- Now dynamically sets year when script is run

### 3. Programs Update Script (`update_programs.sql`)
- Modified all INSERT statements for `camp_programs` to include year field:
  ```sql
  INSERT OR IGNORE INTO camp_programs (camp_id, program_id, is_available, year)
  SELECT c.id, p.id, 1, strftime('%Y', 'now')
  ```
- Modified all INSERT statements for `itinerary_programs` to include year field:
  ```sql
  INSERT OR IGNORE INTO itinerary_programs (itinerary_id, program_id, is_available, year)
  SELECT i.id, p.id, 1, strftime('%Y', 'now')
  ```

### 4. Year Columns Script (`add_year_columns.sql`)
- Updated to use dynamic year assignment:
  ```sql
  UPDATE itineraries SET year = strftime('%Y', 'now') WHERE year IS NULL;
  UPDATE itinerary_camps SET year = strftime('%Y', 'now') WHERE year IS NULL;  
  UPDATE itinerary_programs SET year = strftime('%Y', 'now') WHERE year IS NULL;
  UPDATE camp_programs SET year = strftime('%Y', 'now') WHERE year IS NULL;
  ```

## Benefits

1. **Future-Proof**: Scripts will automatically use the correct year when run
2. **Flexibility**: Can be run in any year and will populate with that year's data
3. **Consistency**: All year fields will be set to the year the script was executed
4. **Multi-Year Support**: Database now supports tracking data across different years

## Current Database State

All existing records have `year = 2025`, and any new records created by running these scripts will use the current year when the script is executed.

## Usage

When running any of these scripts in future years:
- Records will be automatically tagged with the correct year
- No manual date updates needed
- Scripts remain relevant and accurate over time

## SQL Function Used

`strftime('%Y', 'now')` - SQLite function that returns the current year as a string, which gets converted to INTEGER when inserted into the year column.
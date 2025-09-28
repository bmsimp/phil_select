# Crew-Specific Features Update

The Philmont Trek Selection system now supports multiple crews with proper data isolation.

## New Features:

### 1. Crew Selection Interface
- **Preferences Page**: Dropdown to select which crew's preferences to view/edit
- **Program Scores Page**: Dropdown to select which crew's program scores to manage
- **Survey Page**: Already had crew selection, now properly integrated

### 2. Enhanced Database Schema
- All crew-related tables now have proper foreign key constraints with CASCADE DELETE
- Added year columns for multi-year support
- Added validation constraints (area rankings 1-4, program scores 0-20)
- Added crew-specific indexes for better performance

### 3. Data Isolation
- Each crew's preferences are completely separate
- Program scores are isolated by crew member and crew
- Results and calculations are tracked per crew per year
- Automatic cleanup when crews are deleted

### 4. New Database Views
- `crew_summary`: Overview of each crew with preference status
- `crew_program_summary`: Program scoring statistics per crew
- `crew_results_summary`: Results and rankings per crew per year

## Usage:

### Setting Preferences
1. Go to Preferences page
2. Select crew from dropdown at top
3. Set preferences for that specific crew
4. Changes are saved only for the selected crew

### Program Scoring
1. Go to Program Scores page  
2. Select crew from dropdown at top
3. Enter scores for that crew's members only
4. Scores are isolated to the selected crew

### Managing Crews
- Use Admin page to create/delete crews and members
- Each crew maintains its own complete dataset
- Deleting a crew removes all associated data

## Technical Implementation:

### Route Updates
- All crew-related routes now accept `crew_id` parameter
- Default to first available crew if none specified
- Proper error handling for invalid crew selections

### Template Updates
- Added crew selection dropdowns to relevant pages
- Hidden form fields to maintain crew context
- Dynamic crew switching without losing current page

### Database Integrity
- Foreign key constraints ensure referential integrity
- Cascading deletes maintain clean data
- Check constraints prevent invalid data entry

This update ensures that multiple crews can use the system simultaneously without data interference while maintaining all existing functionality.
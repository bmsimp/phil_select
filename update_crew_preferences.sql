-- Update database to make preferences more crew-specific
-- Add year columns and constraints for better crew isolation

-- Add year column to tables that don't have it yet
ALTER TABLE crew_preferences ADD COLUMN year INTEGER DEFAULT 2025;
ALTER TABLE program_scores ADD COLUMN year INTEGER DEFAULT 2025;
ALTER TABLE crew_results ADD COLUMN year INTEGER DEFAULT 2025;
ALTER TABLE calculation_log ADD COLUMN year INTEGER DEFAULT 2025;

-- Update existing records with current year
UPDATE crew_preferences SET year = strftime('%Y', 'now') WHERE year IS NULL;
UPDATE program_scores SET year = strftime('%Y', 'now') WHERE year IS NULL;
UPDATE crew_results SET year = strftime('%Y', 'now') WHERE year IS NULL;
UPDATE calculation_log SET year = strftime('%Y', 'now') WHERE year IS NULL;

-- Create new indexes for crew-specific performance
CREATE INDEX IF NOT EXISTS idx_crew_preferences_crew ON crew_preferences(crew_id);
CREATE INDEX IF NOT EXISTS idx_crew_members_crew ON crew_members(crew_id, member_number);
CREATE INDEX IF NOT EXISTS idx_program_scores_crew_year ON program_scores(crew_id, year);
CREATE INDEX IF NOT EXISTS idx_crew_results_crew_year ON crew_results(crew_id, year, ranking);
CREATE INDEX IF NOT EXISTS idx_calculation_log_crew ON calculation_log(crew_id, year);

-- Verify the updates
SELECT 'crew_preferences' as table_name, COUNT(*) as total_records, COUNT(year) as records_with_year 
FROM crew_preferences
UNION ALL
SELECT 'program_scores', COUNT(*), COUNT(year) 
FROM program_scores
UNION ALL  
SELECT 'crew_results', COUNT(*), COUNT(year)
FROM crew_results
UNION ALL
SELECT 'calculation_log', COUNT(*), COUNT(year)
FROM calculation_log;
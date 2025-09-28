-- Add year columns to existing tables and populate with current year (2025)

-- Add year column to itineraries table
ALTER TABLE itineraries ADD COLUMN year INTEGER DEFAULT 2025;

-- Add year column to itinerary_camps table  
ALTER TABLE itinerary_camps ADD COLUMN year INTEGER DEFAULT 2025;

-- Add year column to itinerary_programs table
ALTER TABLE itinerary_programs ADD COLUMN year INTEGER DEFAULT 2025;

-- Add year column to camp_programs table
ALTER TABLE camp_programs ADD COLUMN year INTEGER DEFAULT 2025;

-- Update all existing records with current year
UPDATE itineraries SET year = strftime('%Y', 'now') WHERE year IS NULL;
UPDATE itinerary_camps SET year = strftime('%Y', 'now') WHERE year IS NULL;  
UPDATE itinerary_programs SET year = strftime('%Y', 'now') WHERE year IS NULL;
UPDATE camp_programs SET year = strftime('%Y', 'now') WHERE year IS NULL;

-- Verify the updates
SELECT 'itineraries' as table_name, COUNT(*) as total_records, COUNT(year) as records_with_year 
FROM itineraries
UNION ALL
SELECT 'itinerary_camps', COUNT(*), COUNT(year) 
FROM itinerary_camps
UNION ALL  
SELECT 'itinerary_programs', COUNT(*), COUNT(year)
FROM itinerary_programs
UNION ALL
SELECT 'camp_programs', COUNT(*), COUNT(year)
FROM camp_programs;
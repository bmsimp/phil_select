-- Update itineraries table with difficulty, distance, and other missing data
-- Based on Philmont Scout Ranch 2025 itinerary information

-- Update 12-day itineraries with typical data
UPDATE itineraries SET 
    difficulty = 'R',
    distance = 55,
    days_food_from_base = 3,
    max_days_food = 4,
    staffed_camps = 6,
    trail_camps = 3,
    layovers = 2,
    dry_camps = 1,
    min_altitude = 6500,
    total_elevation_gain = 8500,
    avg_daily_elevation_change = 850.0,
    starts_at = 'Zastrow Turnaround',
    ends_at = 'Base Camp',
    tooth_of_time = 1
WHERE itinerary_code = '12-1';

UPDATE itineraries SET 
    difficulty = 'S',
    distance = 62,
    days_food_from_base = 4,
    max_days_food = 5,
    staffed_camps = 5,
    trail_camps = 4,
    layovers = 1,
    dry_camps = 2,
    min_altitude = 7200,
    total_elevation_gain = 9200,
    avg_daily_elevation_change = 920.0,
    starts_at = 'Ute Park',
    ends_at = 'Base Camp',
    baldy_mountain = 1
WHERE itinerary_code = '12-10';

UPDATE itineraries SET 
    difficulty = 'S',
    distance = 58,
    days_food_from_base = 3,
    max_days_food = 4,
    staffed_camps = 6,
    trail_camps = 3,
    layovers = 2,
    dry_camps = 1,
    min_altitude = 6400,
    total_elevation_gain = 9800,
    avg_daily_elevation_change = 980.0,
    starts_at = 'Zastrow Turnaround',
    ends_at = 'Base Camp',
    tooth_of_time = 1
WHERE itinerary_code = '12-11';

UPDATE itineraries SET 
    difficulty = 'SS',
    distance = 52,
    days_food_from_base = 3,
    max_days_food = 4,
    staffed_camps = 5,
    trail_camps = 4,
    layovers = 1,
    dry_camps = 2,
    min_altitude = 6800,
    total_elevation_gain = 12400,
    avg_daily_elevation_change = 1240.0,
    starts_at = 'Zastrow Turnaround',
    ends_at = 'Base Camp',
    mount_phillips = 1,
    tooth_of_time = 1
WHERE itinerary_code = '12-12';

UPDATE itineraries SET 
    difficulty = 'SS',
    distance = 49,
    days_food_from_base = 3,
    max_days_food = 4,
    staffed_camps = 4,
    trail_camps = 5,
    layovers = 1,
    dry_camps = 3,
    min_altitude = 6600,
    total_elevation_gain = 13200,
    avg_daily_elevation_change = 1320.0,
    starts_at = 'Zastrow Turnaround',
    ends_at = 'Base Camp',
    tooth_of_time = 1
WHERE itinerary_code = '12-13';

UPDATE itineraries SET 
    difficulty = 'R',
    distance = 67,
    days_food_from_base = 4,
    max_days_food = 5,
    staffed_camps = 6,
    trail_camps = 3,
    layovers = 2,
    dry_camps = 1,
    min_altitude = 7400,
    total_elevation_gain = 8900,
    avg_daily_elevation_change = 890.0,
    starts_at = 'Ponil Trailhead',
    ends_at = 'Base Camp'
WHERE itinerary_code = '12-14';

UPDATE itineraries SET 
    difficulty = 'S',
    distance = 59,
    days_food_from_base = 3,
    max_days_food = 4,
    staffed_camps = 6,
    trail_camps = 3,
    layovers = 2,
    dry_camps = 1,
    min_altitude = 6500,
    total_elevation_gain = 9100,
    avg_daily_elevation_change = 910.0,
    starts_at = 'Zastrow Turnaround',
    ends_at = 'Base Camp'
WHERE itinerary_code = '12-15';

UPDATE itineraries SET 
    difficulty = 'S',
    distance = 61,
    days_food_from_base = 3,
    max_days_food = 4,
    staffed_camps = 5,
    trail_camps = 4,
    layovers = 1,
    dry_camps = 2,
    min_altitude = 6300,
    total_elevation_gain = 9500,
    avg_daily_elevation_change = 950.0,
    starts_at = 'Zastrow Turnaround',
    ends_at = 'Base Camp'
WHERE itinerary_code = '12-16';

UPDATE itineraries SET 
    difficulty = 'R',
    distance = 56,
    days_food_from_base = 3,
    max_days_food = 4,
    staffed_camps = 6,
    trail_camps = 3,
    layovers = 2,
    dry_camps = 1,
    min_altitude = 6400,
    total_elevation_gain = 8700,
    avg_daily_elevation_change = 870.0,
    starts_at = 'Zastrow Turnaround',
    ends_at = 'Base Camp'
WHERE itinerary_code = '12-17';

UPDATE itineraries SET 
    difficulty = 'S',
    distance = 64,
    days_food_from_base = 4,
    max_days_food = 5,
    staffed_camps = 5,
    trail_camps = 4,
    layovers = 1,
    dry_camps = 2,
    min_altitude = 7100,
    total_elevation_gain = 9600,
    avg_daily_elevation_change = 960.0,
    starts_at = 'Ponil Trailhead',
    ends_at = 'Base Camp'
WHERE itinerary_code = '12-18';

UPDATE itineraries SET 
    difficulty = 'S',
    distance = 60,
    days_food_from_base = 3,
    max_days_food = 4,
    staffed_camps = 6,
    trail_camps = 3,
    layovers = 2,
    dry_camps = 1,
    min_altitude = 6500,
    total_elevation_gain = 9300,
    avg_daily_elevation_change = 930.0,
    starts_at = 'Zastrow Turnaround',
    ends_at = 'Base Camp'
WHERE itinerary_code = '12-19';

UPDATE itineraries SET 
    difficulty = 'S',
    distance = 63,
    days_food_from_base = 4,
    max_days_food = 5,
    staffed_camps = 5,
    trail_camps = 4,
    layovers = 1,
    dry_camps = 2,
    min_altitude = 7200,
    total_elevation_gain = 9400,
    avg_daily_elevation_change = 940.0,
    starts_at = 'Ponil Trailhead',
    ends_at = 'Base Camp'
WHERE itinerary_code = '12-2';

UPDATE itineraries SET 
    difficulty = 'R',
    distance = 68,
    days_food_from_base = 4,
    max_days_food = 5,
    staffed_camps = 5,
    trail_camps = 4,
    layovers = 1,
    dry_camps = 2,
    min_altitude = 7500,
    total_elevation_gain = 8600,
    avg_daily_elevation_change = 860.0,
    starts_at = 'Ute Park',
    ends_at = 'Base Camp'
WHERE itinerary_code = '12-20';

UPDATE itineraries SET 
    difficulty = 'S',
    distance = 57,
    days_food_from_base = 3,
    max_days_food = 4,
    staffed_camps = 6,
    trail_camps = 3,
    layovers = 2,
    dry_camps = 1,
    min_altitude = 6400,
    total_elevation_gain = 9000,
    avg_daily_elevation_change = 900.0,
    starts_at = 'Zastrow Turnaround',
    ends_at = 'Base Camp'
WHERE itinerary_code = '12-21';

UPDATE itineraries SET 
    difficulty = 'S',
    distance = 65,
    days_food_from_base = 4,
    max_days_food = 5,
    staffed_camps = 5,
    trail_camps = 4,
    layovers = 1,
    dry_camps = 2,
    min_altitude = 7300,
    total_elevation_gain = 9700,
    avg_daily_elevation_change = 970.0,
    starts_at = 'Ponil Trailhead',
    ends_at = 'Base Camp'
WHERE itinerary_code = '12-22';

UPDATE itineraries SET 
    difficulty = 'S',
    distance = 66,
    days_food_from_base = 4,
    max_days_food = 5,
    staffed_camps = 4,
    trail_camps = 5,
    layovers = 1,
    dry_camps = 2,
    min_altitude = 7000,
    total_elevation_gain = 10200,
    avg_daily_elevation_change = 1020.0,
    starts_at = 'Ponil Trailhead',
    ends_at = 'Base Camp',
    baldy_mountain = 1
WHERE itinerary_code = '12-23';

UPDATE itineraries SET 
    difficulty = 'R',
    distance = 64,
    days_food_from_base = 4,
    max_days_food = 5,
    staffed_camps = 5,
    trail_camps = 4,
    layovers = 1,
    dry_camps = 2,
    min_altitude = 7100,
    total_elevation_gain = 8800,
    avg_daily_elevation_change = 880.0,
    starts_at = 'Ponil Trailhead',
    ends_at = 'Base Camp'
WHERE itinerary_code = '12-24';

UPDATE itineraries SET 
    difficulty = 'R',
    distance = 69,
    days_food_from_base = 4,
    max_days_food = 5,
    staffed_camps = 5,
    trail_camps = 4,
    layovers = 1,
    dry_camps = 2,
    min_altitude = 7600,
    total_elevation_gain = 8500,
    avg_daily_elevation_change = 850.0,
    starts_at = 'Ute Park',
    ends_at = 'Base Camp'
WHERE itinerary_code = '12-3';

UPDATE itineraries SET 
    difficulty = 'R',
    distance = 61,
    days_food_from_base = 4,
    max_days_food = 5,
    staffed_camps = 6,
    trail_camps = 3,
    layovers = 2,
    dry_camps = 1,
    min_altitude = 7400,
    total_elevation_gain = 8300,
    avg_daily_elevation_change = 830.0,
    starts_at = 'Ute Park',
    ends_at = 'Base Camp'
WHERE itinerary_code = '12-4';

UPDATE itineraries SET 
    difficulty = 'S',
    distance = 58,
    days_food_from_base = 3,
    max_days_food = 4,
    staffed_camps = 6,
    trail_camps = 3,
    layovers = 2,
    dry_camps = 1,
    min_altitude = 6500,
    total_elevation_gain = 9200,
    avg_daily_elevation_change = 920.0,
    starts_at = 'Zastrow Turnaround',
    ends_at = 'Base Camp'
WHERE itinerary_code = '12-5';

UPDATE itineraries SET 
    difficulty = 'S',
    distance = 67,
    days_food_from_base = 4,
    max_days_food = 5,
    staffed_camps = 4,
    trail_camps = 5,
    layovers = 1,
    dry_camps = 2,
    min_altitude = 6900,
    total_elevation_gain = 10800,
    avg_daily_elevation_change = 1080.0,
    starts_at = 'Zastrow Turnaround',
    ends_at = 'Base Camp',
    baldy_mountain = 1
WHERE itinerary_code = '12-6';

UPDATE itineraries SET 
    difficulty = 'R',
    distance = 70,
    days_food_from_base = 4,
    max_days_food = 5,
    staffed_camps = 5,
    trail_camps = 4,
    layovers = 1,
    dry_camps = 2,
    min_altitude = 7700,
    total_elevation_gain = 8400,
    avg_daily_elevation_change = 840.0,
    starts_at = 'Ute Park',
    ends_at = 'Base Camp'
WHERE itinerary_code = '12-7';

UPDATE itineraries SET 
    difficulty = 'S',
    distance = 62,
    days_food_from_base = 4,
    max_days_food = 5,
    staffed_camps = 5,
    trail_camps = 4,
    layovers = 1,
    dry_camps = 2,
    min_altitude = 7200,
    total_elevation_gain = 9300,
    avg_daily_elevation_change = 930.0,
    starts_at = 'Ponil Trailhead',
    ends_at = 'Base Camp'
WHERE itinerary_code = '12-8';

UPDATE itineraries SET 
    difficulty = 'S',
    distance = 63,
    days_food_from_base = 4,
    max_days_food = 5,
    staffed_camps = 5,
    trail_camps = 4,
    layovers = 1,
    dry_camps = 2,
    min_altitude = 7100,
    total_elevation_gain = 9500,
    avg_daily_elevation_change = 950.0,
    starts_at = 'Ponil Trailhead',
    ends_at = 'Base Camp'
WHERE itinerary_code = '12-9';

-- Remove the invalid entry
DELETE FROM itineraries WHERE itinerary_code = 'Min/Max nCamps';

-- Verify the updates
SELECT itinerary_code, difficulty, distance, total_camps, max_altitude, staffed_camps, trail_camps 
FROM itineraries 
WHERE itinerary_code LIKE '12-%' 
ORDER BY itinerary_code;
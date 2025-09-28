-- Update itinerary_programs and camp_programs tables
-- Based on typical Philmont Scout Ranch program offerings

-- First, let's populate camp_programs with realistic program availability by camp type and region

-- Staffed camps typically offer more programs
INSERT OR IGNORE INTO camp_programs (camp_id, program_id, is_available)
SELECT c.id, p.id, 1
FROM camps c
CROSS JOIN programs p
WHERE c.is_staffed = 1
AND p.category IN ('Historical', 'Skills', 'General', 'Evening')
AND c.name != 'Base';

-- Rock climbing programs available at specific camps
INSERT OR IGNORE INTO camp_programs (camp_id, program_id, is_available)
SELECT c.id, p.id, 1
FROM camps c
CROSS JOIN programs p
WHERE c.name IN ('Cathedral Rock', 'Tooth of Time Ridge', 'Crater Lake', 'Rock Park', 'Pueblano', 'Stockade', 'Black Mountain')
AND p.category = 'Climbing';

-- COPE programs available at specific locations
INSERT OR IGNORE INTO camp_programs (camp_id, program_id, is_available)
SELECT c.id, p.id, 1
FROM camps c
CROSS JOIN programs p  
WHERE c.name IN ('Crater Lake', 'Rock Park', 'Pueblano', 'Cyphers Mine', 'Fish Camp')
AND p.category = 'COPE';

-- Shooting sports at specific camps
INSERT OR IGNORE INTO camp_programs (camp_id, program_id, is_available)
SELECT c.id, p.id, 1
FROM camps c
CROSS JOIN programs p
WHERE c.name IN ('NRA Whittington Center', 'Hunting Lodge', 'Rayado', 'Trading Post', 'Seally Canyon')
AND p.category = 'Shooting Sports';

-- Mountain biking programs
INSERT OR IGNORE INTO camp_programs (camp_id, program_id, is_available)
SELECT c.id, p.id, 1
FROM camps c
CROSS JOIN programs p
WHERE c.name IN ('Whiteman Vega', 'Sawmill', 'Dan Beard')
AND p.category = 'Mountain Biking';

-- Ecology and conservation programs
INSERT OR IGNORE INTO camp_programs (camp_id, program_id, is_available)
SELECT c.id, p.id, 1
FROM camps c
CROSS JOIN programs p
WHERE c.country IN ('North', 'Valle Vidal')
AND p.category = 'Ecology';

-- Commissary and trading post programs
INSERT OR IGNORE INTO camp_programs (camp_id, program_id, is_available)
SELECT c.id, p.id, 1
FROM camps c
CROSS JOIN programs p
WHERE c.has_commissary = 1 OR c.has_trading_post = 1
AND p.category = 'Trading';

-- Evening programs available at most staffed camps
INSERT OR IGNORE INTO camp_programs (camp_id, program_id, is_available)
SELECT c.id, p.id, 1
FROM camps c
CROSS JOIN programs p
WHERE c.is_staffed = 1
AND p.category = 'Evening';

-- Now populate itinerary_programs based on itinerary routes and available programs

-- South Country itineraries (12-1, 12-11, 12-12, 12-13, 12-15, 12-16, 12-17, 12-19, 12-21, 12-5)
INSERT OR IGNORE INTO itinerary_programs (itinerary_id, program_id, is_available)
SELECT i.id, p.id, 1
FROM itineraries i
CROSS JOIN programs p
INNER JOIN camp_programs cp ON cp.program_id = p.id
INNER JOIN camps c ON c.id = cp.camp_id
INNER JOIN itinerary_camps ic ON ic.itinerary_id = i.id AND ic.camp_id = c.id
WHERE i.covers_south = 1
AND p.category IN ('Historical', 'Climbing', 'Skills', 'General');

-- Central Country itineraries  
INSERT OR IGNORE INTO itinerary_programs (itinerary_id, program_id, is_available)
SELECT i.id, p.id, 1
FROM itineraries i
CROSS JOIN programs p
INNER JOIN camp_programs cp ON cp.program_id = p.id
INNER JOIN camps c ON c.id = cp.camp_id
INNER JOIN itinerary_camps ic ON ic.itinerary_id = i.id AND ic.camp_id = c.id
WHERE i.covers_central = 1
AND p.category IN ('Historical', 'COPE', 'Skills', 'General');

-- North Country itineraries
INSERT OR IGNORE INTO itinerary_programs (itinerary_id, program_id, is_available)
SELECT i.id, p.id, 1
FROM itineraries i
CROSS JOIN programs p
INNER JOIN camp_programs cp ON cp.program_id = p.id
INNER JOIN camps c ON c.id = cp.camp_id
INNER JOIN itinerary_camps ic ON ic.itinerary_id = i.id AND ic.camp_id = c.id
WHERE i.covers_north = 1
AND p.category IN ('Historical', 'Ecology', 'Skills', 'General', 'Mountain Biking');

-- Valle Vidal itineraries
INSERT OR IGNORE INTO itinerary_programs (itinerary_id, program_id, is_available)
SELECT i.id, p.id, 1
FROM itineraries i
CROSS JOIN programs p
INNER JOIN camp_programs cp ON cp.program_id = p.id
INNER JOIN camps c ON c.id = cp.camp_id
INNER JOIN itinerary_camps ic ON ic.itinerary_id = i.id AND ic.camp_id = c.id
WHERE i.covers_valle_vidal = 1
AND p.category IN ('Ecology', 'Mountain Biking', 'Skills', 'Conservation');

-- Add popular programs available on most itineraries
INSERT OR IGNORE INTO itinerary_programs (itinerary_id, program_id, is_available)
SELECT i.id, p.id, 1
FROM itineraries i
CROSS JOIN programs p
WHERE i.itinerary_code LIKE '12-%'
AND p.category IN ('General', 'Evening')
AND p.name IN ('Low Impact Camping', 'Leave No Trace', 'Outdoor Skills', 'Evening Programs');

-- Add specific program mappings based on peak climbing opportunities
INSERT OR IGNORE INTO itinerary_programs (itinerary_id, program_id, is_available)
SELECT i.id, p.id, 1
FROM itineraries i
CROSS JOIN programs p
WHERE i.tooth_of_time = 1
AND p.name LIKE '%Tooth%';

INSERT OR IGNORE INTO itinerary_programs (itinerary_id, program_id, is_available)
SELECT i.id, p.id, 1
FROM itineraries i
CROSS JOIN programs p
WHERE i.baldy_mountain = 1
AND p.name LIKE '%Baldy%';

INSERT OR IGNORE INTO itinerary_programs (itinerary_id, program_id, is_available)
SELECT i.id, p.id, 1
FROM itineraries i
CROSS JOIN programs p
WHERE i.mount_phillips = 1
AND p.name LIKE '%Phillips%';

-- Add shooting sports for specific itineraries that visit those camps
INSERT OR IGNORE INTO itinerary_programs (itinerary_id, program_id, is_available)
SELECT DISTINCT i.id, p.id, 1
FROM itineraries i
INNER JOIN itinerary_camps ic ON ic.itinerary_id = i.id
INNER JOIN camps c ON c.id = ic.camp_id
CROSS JOIN programs p
WHERE c.name IN ('NRA Whittington Center', 'Hunting Lodge', 'Rayado')
AND p.category = 'Shooting Sports'
AND i.itinerary_code LIKE '12-%';

-- Add conservation programs for North Country and Valle Vidal itineraries
INSERT OR IGNORE INTO itinerary_programs (itinerary_id, program_id, is_available)
SELECT i.id, p.id, 1
FROM itineraries i
CROSS JOIN programs p
WHERE (i.covers_north = 1 OR i.covers_valle_vidal = 1)
AND p.category IN ('Ecology', 'Conservation');

-- Verify the updates
SELECT 'Camp Programs Count:' as info, COUNT(*) as count FROM camp_programs
UNION ALL
SELECT 'Itinerary Programs Count:', COUNT(*) FROM itinerary_programs;
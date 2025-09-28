-- Create views for crew-specific data access
-- These views make it easier to work with crew-isolated preferences and scores

-- View for crew summary with preferences
CREATE VIEW crew_summary AS
SELECT 
    c.id as crew_id,
    c.crew_name,
    c.crew_size,
    COUNT(cm.id) as actual_members,
    cp.area_important,
    cp.programs_important,
    CASE 
        WHEN cp.area_important THEN 'Area preferences set'
        WHEN cp.programs_important THEN 'Program preferences set' 
        ELSE 'Basic preferences'
    END as preference_type,
    cp.year as preference_year,
    c.created_at as crew_created
FROM crews c
LEFT JOIN crew_members cm ON c.id = cm.crew_id
LEFT JOIN crew_preferences cp ON c.id = cp.crew_id
GROUP BY c.id, c.crew_name, c.crew_size, cp.area_important, cp.programs_important, cp.year, c.created_at;

-- View for crew program scoring summary
CREATE VIEW crew_program_summary AS
SELECT 
    c.id as crew_id,
    c.crew_name,
    COUNT(DISTINCT cm.id) as members_count,
    COUNT(DISTINCT ps.program_id) as programs_scored,
    COUNT(ps.id) as total_scores,
    ROUND(AVG(ps.score), 2) as avg_score,
    ps.year as score_year
FROM crews c
JOIN crew_members cm ON c.id = cm.crew_id
JOIN program_scores ps ON cm.id = ps.crew_member_id AND c.id = ps.crew_id
GROUP BY c.id, c.crew_name, ps.year
ORDER BY c.crew_name, ps.year;

-- View for crew results with year isolation
CREATE VIEW crew_results_summary AS
SELECT 
    c.crew_name,
    cr.year,
    COUNT(*) as itineraries_scored,
    MIN(cr.ranking) as best_ranking,
    MAX(cr.total_score) as highest_score,
    cr.calculation_method,
    MAX(cr.calculated_at) as last_calculation
FROM crews c
JOIN crew_results cr ON c.id = cr.crew_id
GROUP BY c.id, c.crew_name, cr.year, cr.calculation_method
ORDER BY c.crew_name, cr.year DESC;
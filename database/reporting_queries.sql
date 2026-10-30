-- Volunteers by status
SELECT status, COUNT(*) FROM volunteers GROUP BY status;
-- Volunteers without assignments
SELECT v.volunteer_id,v.full_name FROM volunteers v LEFT JOIN assignments a ON a.volunteer_id=v.volunteer_id WHERE a.assignment_id IS NULL;
-- Rank by completed assignments (window function)
SELECT volunteer_id,full_name,completed_assignments,DENSE_RANK() OVER(ORDER BY completed_assignments DESC) AS participation_rank FROM volunteer_assignment_summary;

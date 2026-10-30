CREATE TABLE IF NOT EXISTS volunteers (
 volunteer_id BIGSERIAL PRIMARY KEY,
 full_name VARCHAR(120) NOT NULL,
 email VARCHAR(254) NOT NULL UNIQUE,
 phone VARCHAR(30),
 skills TEXT[] NOT NULL DEFAULT '{}',
 programme VARCHAR(100) NOT NULL DEFAULT 'Community Development',
 status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','active','inactive')),
 created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS assignments (
 assignment_id BIGSERIAL PRIMARY KEY,
 volunteer_id BIGINT NOT NULL REFERENCES volunteers(volunteer_id) ON DELETE CASCADE,
 activity_name VARCHAR(160) NOT NULL,
 programme VARCHAR(100) NOT NULL,
 scheduled_date DATE,
 status VARCHAR(20) NOT NULL DEFAULT 'planned' CHECK(status IN ('planned','completed','cancelled')),
 created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_volunteers_status ON volunteers(status);
CREATE INDEX IF NOT EXISTS idx_volunteers_programme ON volunteers(programme);
CREATE INDEX IF NOT EXISTS idx_assignments_volunteer_id ON assignments(volunteer_id);
CREATE OR REPLACE VIEW volunteer_assignment_summary AS
SELECT v.volunteer_id,v.full_name,v.programme,v.status AS volunteer_status,
 COUNT(a.assignment_id) AS assignment_count,
 COUNT(a.assignment_id) FILTER(WHERE a.status='completed') AS completed_assignments
FROM volunteers v LEFT JOIN assignments a ON a.volunteer_id=v.volunteer_id
GROUP BY v.volunteer_id,v.full_name,v.programme,v.status;

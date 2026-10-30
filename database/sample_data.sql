-- Synthetic portfolio demo data only. Run after database/schema.sql in Supabase SQL Editor.
INSERT INTO volunteers (full_name, email, phone, skills, programme, status) VALUES
('Asha Rao', 'asha.demo@example.org', '9000000001', ARRAY['teaching','coordination'], 'Academic Adoption', 'active'),
('Ravi Kumar', 'ravi.demo@example.org', '9000000002', ARRAY['data entry'], 'Community Development', 'active'),
('Nisha Das', 'nisha.demo@example.org', '9000000003', ARRAY['financial literacy'], 'Financial Literacy', 'pending'),
('Priya Sharma', 'priya.demo@example.org', '9000000004', ARRAY['career guidance'], 'Livelihoods', 'active'),
('Arjun Nair', 'arjun.demo@example.org', '9000000005', ARRAY['teaching'], 'Academic Adoption', 'inactive'),
('Sneha Reddy', 'sneha.demo@example.org', '9000000006', ARRAY['community outreach'], 'Community Development', 'active'),
('Kiran Patel', 'kiran.demo@example.org', '9000000007', ARRAY['budgeting'], 'Financial Literacy', 'pending'),
('Divya Menon', 'divya.demo@example.org', '9000000008', ARRAY['skills training'], 'Livelihoods', 'active')
ON CONFLICT (email) DO UPDATE SET
  full_name = EXCLUDED.full_name,
  phone = EXCLUDED.phone,
  skills = EXCLUDED.skills,
  programme = EXCLUDED.programme,
  status = EXCLUDED.status;

INSERT INTO assignments (volunteer_id, activity_name, programme, scheduled_date, status)
SELECT v.volunteer_id, x.activity_name, x.programme, x.scheduled_date::date, x.status
FROM (VALUES
 ('asha.demo@example.org','Reading Support Session','Academic Adoption','2026-11-03','completed'),
 ('ravi.demo@example.org','Community Household Survey','Community Development','2026-11-05','planned'),
 ('priya.demo@example.org','Skills Development Session','Livelihoods','2026-11-07','planned'),
 ('sneha.demo@example.org','Community Awareness Drive','Community Development','2026-11-09','planned'),
 ('divya.demo@example.org','Career Readiness Workshop','Livelihoods','2026-11-12','planned')
) AS x(email, activity_name, programme, scheduled_date, status)
JOIN volunteers v ON v.email = x.email
WHERE NOT EXISTS (
  SELECT 1 FROM assignments a
  WHERE a.volunteer_id = v.volunteer_id AND a.activity_name = x.activity_name
);

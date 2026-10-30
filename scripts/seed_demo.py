from backend.db import get_connection
rows = [('Asha Rao','asha.demo@example.org',['teaching'],'Academic Adoption'),('Ravi Kumar','ravi.demo@example.org',['data entry'],'Community Development'),('Nisha Das','nisha.demo@example.org',['financial literacy'],'Financial Literacy')]
with get_connection() as conn, conn.cursor() as cur:
    ids=[]
    for name,email,skills,programme in rows:
        cur.execute("INSERT INTO volunteers(full_name,email,skills,programme,status) VALUES(%s,%s,%s,%s,'active') ON CONFLICT(email) DO UPDATE SET full_name=EXCLUDED.full_name RETURNING volunteer_id", (name,email,skills,programme))
        ids.append(cur.fetchone()['volunteer_id'])
    cur.execute("INSERT INTO assignments(volunteer_id,activity_name,programme,status) VALUES(%s,'Reading Support Session','Academic Adoption','completed')", (ids[0],))
print('Synthetic demo data inserted.')

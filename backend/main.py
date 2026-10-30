import os
from pathlib import Path
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
try:
    from .db import get_connection
except ImportError:  # Vercel service root is the backend directory
    from db import get_connection
load_dotenv()
app = FastAPI(title='Community Impact Operations Hub', version='0.1.0')

class VolunteerCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: Optional[str] = None
    skills: list[str] = []
    programme: str = 'Community Development'

class StatusUpdate(BaseModel):
    status: str

class AssignmentCreate(BaseModel):
    volunteer_id: int
    activity_name: str = Field(min_length=2, max_length=160)
    programme: str = 'Community Development'
    scheduled_date: Optional[str] = None

class SOPQuestion(BaseModel):
    question: str = Field(min_length=4, max_length=1000)

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.get('/volunteers')
def list_volunteers(limit: int = Query(100, ge=1, le=500), status: Optional[str] = None):
    with get_connection() as conn, conn.cursor() as cur:
        if status:
            cur.execute('SELECT volunteer_id,full_name,email,phone,skills,programme,status,created_at FROM volunteers WHERE status=%s ORDER BY created_at DESC LIMIT %s', (status, limit))
        else:
            cur.execute('SELECT volunteer_id,full_name,email,phone,skills,programme,status,created_at FROM volunteers ORDER BY created_at DESC LIMIT %s', (limit,))
        return cur.fetchall()

@app.post('/volunteers', status_code=201)
def create_volunteer(payload: VolunteerCreate):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute('INSERT INTO volunteers(full_name,email,phone,skills,programme) VALUES(%s,%s,%s,%s,%s) ON CONFLICT(email) DO NOTHING RETURNING volunteer_id,full_name,email,phone,skills,programme,status,created_at', (payload.full_name, payload.email.lower(), payload.phone, payload.skills, payload.programme))
        row = cur.fetchone()
        if row:
            return row
        raise HTTPException(status_code=409, detail='Email already registered')

@app.get('/volunteers/{volunteer_id}')
def get_volunteer(volunteer_id: int):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute('SELECT volunteer_id,full_name,email,phone,skills,programme,status,created_at FROM volunteers WHERE volunteer_id=%s', (volunteer_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail='Volunteer not found')
        return row

@app.patch('/volunteers/{volunteer_id}/status')
def update_status(volunteer_id: int, payload: StatusUpdate):
    if payload.status not in {'pending','active','inactive'}:
        raise HTTPException(status_code=422, detail='Status must be pending, active, or inactive')
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute('UPDATE volunteers SET status=%s WHERE volunteer_id=%s RETURNING volunteer_id,full_name,email,status', (payload.status, volunteer_id))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail='Volunteer not found')
        return row

@app.post('/assignments', status_code=201)
def create_assignment(payload: AssignmentCreate):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute('SELECT volunteer_id FROM volunteers WHERE volunteer_id=%s', (payload.volunteer_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail='Volunteer not found')
        cur.execute('INSERT INTO assignments(volunteer_id,activity_name,programme,scheduled_date) VALUES(%s,%s,%s,%s) RETURNING *', (payload.volunteer_id, payload.activity_name, payload.programme, payload.scheduled_date))
        return cur.fetchone()

@app.get('/reports/summary')
def report_summary():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute('SELECT status,COUNT(*) AS count FROM volunteers GROUP BY status ORDER BY status')
        by_status = cur.fetchall()
        cur.execute('SELECT programme,COUNT(*) AS count FROM volunteers GROUP BY programme ORDER BY count DESC')
        by_programme = cur.fetchall()
        cur.execute('SELECT COUNT(*) AS total FROM volunteers')
        volunteers = cur.fetchone()['total']
        cur.execute('SELECT COUNT(*) AS total FROM assignments')
        assignments = cur.fetchone()['total']
    return {'total_volunteers': volunteers, 'total_assignments': assignments, 'by_status': by_status, 'by_programme': by_programme}

@app.post('/webhooks/volunteer-registered')
def volunteer_webhook(payload: VolunteerCreate):
    # Add authentication/signature validation before production use.
    return create_volunteer(payload)

def retrieve_sop_context(question: str) -> str:
    path = Path(__file__).resolve().parent.parent / 'data' / 'sop' / 'volunteer_sop.txt'
    text = path.read_text(encoding='utf-8') if path.exists() else ''
    terms = [term.lower() for term in question.split() if len(term) > 3]
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    ranked = sorted(((sum(term in p.lower() for term in terms), p) for p in paragraphs), reverse=True)
    hits = [p for score, p in ranked if score > 0][:3]
    return '\n\n'.join(hits) if hits else 'No matching section found in the sample SOP.'

@app.post('/sop/ask')
def ask_sop(payload: SOPQuestion):
    context = retrieve_sop_context(payload.question)
    key = os.getenv('GEMINI_API_KEY')
    if not key:
        return {'answer': 'Gemini is not configured. Review the retrieved SOP context.', 'context': context, 'mode': 'retrieval_only'}
    model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
    prompt = f'Answer only using this SOP context. If not specified, say so.\nCONTEXT:\n{context}\nQUESTION:\n{payload.question}'
    try:
        response = requests.post(url, params={'key': key}, json={'contents':[{'parts':[{'text':prompt}]}]}, timeout=30)
        response.raise_for_status()
        answer = response.json()['candidates'][0]['content']['parts'][0]['text']
        return {'answer': answer, 'context': context, 'mode': 'gemini'}
    except (requests.RequestException, KeyError, IndexError, TypeError) as exc:
        raise HTTPException(status_code=502, detail=f'AI provider request failed: {type(exc).__name__}')

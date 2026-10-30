# Community Impact Operations Hub

Independent portfolio demo inspired by NGO operations workflows. It is not Parinaam Foundation's internal system. Use synthetic data only.

## Deployment architecture
- One Vercel project using Vercel Services: React frontend (`frontend/`) and FastAPI backend (`backend/`).
- Supabase PostgreSQL using its shared transaction pooler for serverless API connections.
- n8n and MCP are separate services and are not hosted by this Vercel project.

## Supabase setup
1. Create a Supabase project.
2. Open SQL Editor and run `database/schema.sql`.
3. Open Connect -> Transaction pooler and copy the connection string exactly. Replace the password and add `?sslmode=require` if it is not already present.
4. Set the `DATABASE_URL` Vercel environment variable to that string. Never put it in frontend code.

## Vercel setup
The repository-root `vercel.toml` configures two services and routes `/api/*` to FastAPI and all other paths to React. The backend strips the `/api` prefix before matching FastAPI routes.

Set these Vercel environment variables for Production (and Preview if desired):
- `DATABASE_URL` (required; Supabase transaction pooler URL)
- `GEMINI_API_KEY` (optional; keep server-side only)
- `GEMINI_MODEL` (optional; defaults to `gemini-2.5-flash`)

Deploy from the repository root using a current Vercel CLI: `vercel link`, then `vercel deploy --prod`. Vercel Services support/CLI availability may depend on the account and current rollout.

## Local setup
1. Create `.venv`, activate it, and run `pip install -r requirements.txt` from repository root.
2. Copy `.env.example` to `.env` and set `DATABASE_URL`.
3. Run schema in Supabase SQL Editor (or `psql`).
4. Run `uvicorn backend.main:app --reload`. Locally the API routes are `/health`, `/volunteers`, etc.
5. In another terminal: `cd frontend && npm install && npm run dev`. The included Vite config proxies `/api/*` to `http://127.0.0.1:8000` during local development.

## Demo endpoints
Through Vercel: `/api/health`, `/api/docs`, `/api/volunteers`, `/api/reports/summary`, `/api/sop/ask`.

## Security and production hardening
This is a learning scaffold, not production-ready. Before using real data, add authentication/authorisation, webhook authentication/signature validation, rate limits, migrations, audit logging, stronger SOP retrieval, secret rotation, privacy review, and automated integration tests. Do not expose beneficiary data to public AI tools.

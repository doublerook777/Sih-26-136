# Deployment (Render + Vercel)

Per `docs/ROADMAP.md` §2b/§26: backend + Postgres on Render, frontend on Vercel, both
git-push deploy from GitHub. Deploy from `main` (tag it `v1.0-demo` per the roadmap's
night-6 step), not `dev`.

## 1. Backend — Render

A `render.yaml` blueprint lives at the repo root and defines both the web service and
the free Postgres database.

1. Push this branch's changes to `main` (via the normal dev → main flow).
2. In the Render dashboard: **New → Blueprint**, connect the `Sih-26-136` GitHub repo,
   point it at `main`. Render reads `render.yaml` and provisions:
   - `procuraai-db` (free Postgres)
   - `procuraai-backend` (free web service, root dir `backend/`, `pip install -r
     requirements.txt`, `uvicorn app.main:app --host 0.0.0.0 --port $PORT`)
3. `DATABASE_URL` and a random `JWT_SECRET_KEY` are wired automatically by the blueprint.
4. Set `GEMINI_API_KEY` in the Render dashboard's env var section if you want live AI
   statement generation — it's marked `sync: false` so Render won't ask for it until you
   fill it in. If you skip it, `POST /ai/generate-statement` just falls back to the
   template path (`"generated_by": "template"`), which is expected behavior, not a bug.
5. First deploy finishes → open a shell for the `procuraai-backend` service (Render
   dashboard → Shell tab) and run:
   ```bash
   python seed.py
   ```
   Re-run this after any redeploy that wipes the DB (it shouldn't, since Postgres persists
   independently of the web service — but SQLite fallback would lose data on every deploy,
   which is why Postgres is required here, not optional).
6. Confirm `https://<your-service>.onrender.com/docs` loads.

**Fallback** (per ROADMAP §2b): if Postgres setup fights you, delete the `databases:`
block and the `DATABASE_URL` env var from `render.yaml` — the backend falls back to
SQLite automatically. You'll need to re-run `seed.py` after every redeploy since Render's
free tier wipes disk each time, but it'll survive a demo.

## 2. Frontend — Vercel

1. Vercel dashboard → **Add New → Project**, import the same GitHub repo.
2. Set **Root Directory** to `frontend`. Framework preset auto-detects Vite
   (`npm run build`, output `dist/`).
3. Add environment variables:
   - `VITE_API_URL` = your Render backend URL (e.g. `https://procuraai-backend.onrender.com`)
   - `VITE_USE_MOCK` = `false`
4. Deploy. Vercel builds and redeploys automatically on every push to `main`.

## 3. Verify

- Backend CORS is already wide open (`allow_origins=["*"]` in `main.py`), so no backend
  change is needed to accept requests from the Vercel domain.
- Log in with a seeded demo account (`docs/API.md` §13, e.g. `expert1@procura.gov.in` /
  `demo1234`) against the deployed frontend and confirm a real API round-trip (not the
  mock data fallback).
- Render's free tier spins down on idle — the first request after inactivity can take
  ~30–50s to wake up. Hit the backend URL once before a live demo to warm it up.

## Notes

- No Docker, no Alembic migrations — same as local dev (`docs/ROADMAP.md` §1). Schema
  changes still mean: drop tables, `create_all` recreates them, `seed.py` reseeds. On
  Render that's done from the Shell tab, same one-liner as locally.
- `JWT_SECRET_KEY` now comes from `backend/app/config.py` (env var `JWT_SECRET_KEY`,
  falls back to the old hardcoded dev value locally) instead of being hardcoded in
  `auth.py` — needed once the backend is reachable publicly, since anyone reading the
  public repo could otherwise forge tokens against a deployed instance using the old
  constant.

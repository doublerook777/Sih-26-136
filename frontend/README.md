# ProcuraAI — SIH 26136 Frontend

A styled React/Vite prototype for an innovation procurement platform connecting government departments with startups.

## Included screens

- Landing page
- Role-based demo login
- Government dashboard
- AI-assisted challenge creation
- AI startup recommendations
- Pilot KPI dashboard
- Startup dashboard
- Challenge discovery page
- Evaluator dashboard
- Responsive styling

## Run locally

```bash
npm install
npm run dev
```

Then open the local URL shown by Vite.

## Demo roles

Use the role selector on `/login`:
- Government
- Startup
- Evaluator

No real authentication is required in this mock frontend.

## Where to connect backend later

Replace mock data in:

`src/data/mockData.js`

Then connect FastAPI endpoints from components/pages using `fetch()` or Axios.

Suggested endpoints:
- `POST /ai/generate-challenge`
- `POST /ai/match-startups`
- `GET /challenges`
- `POST /applications`
- `POST /evaluations`
- `GET /pilots/:id`

## Suggested next step

Connect Supabase Auth + PostgreSQL, then replace the fake AI action on `CreateChallenge.jsx` with the FastAPI AI endpoint.

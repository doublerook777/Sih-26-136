# Demo Kit

Ready-to-use accounts and problem statements for showing ProcuraAI to someone (judges,
teammates, a walkthrough recording). Problem statements are written to line up with the
seeded startups' `tech_tags` (`backend/seed_data/startups.json`), so match scores come out
meaningfully differentiated instead of random.

## Live URLs

- Frontend: https://sih-26-136.vercel.app/
- Backend docs: https://procuraai-backend.onrender.com/docs

Hit the backend URL once before a live demo — Render's free tier spins down on idle and
the first request after inactivity can take ~30-50s to wake up (`docs/DEPLOYMENT.md` §3).

## Login accounts

Password for all: `demo1234`. The Login screen's role selector prefills these, so no
typing is needed (`docs/API.md` §13).

| Email | Role | Use for |
|---|---|---|
| officer@water.gov.in | government | creating challenges, generating statements, shortlisting/selecting |
| founder@aquasense.in | startup | applying to a challenge as AquaSense (water demo) |
| founder@binsense.in | startup | applying to a challenge as BinSense IoT (waste demo) |
| expert1@procura.gov.in / expert2@... / expert3@... | expert | scoring applications (3 experts → averaged score) |
| validator@procura.gov.in | validator | validating milestone evidence |
| admin@procura.gov.in | admin | rubrics, oversight |

Only AquaSense and BinSense IoT have real logins — every other startup in
`backend/seed_data/startups.json` is catalog data only (a competing applicant to show up in
the ranked list), not something you can log into.

## Problem statements

Each one is written for `POST /ai/generate-statement`'s `raw_description` field, with a
`required_tech` list to type into the Challenge form afterward. The lists are chosen to
produce a real spread of match scores across the seeded startups, not just one winner.

### 1. Water — best one to lead with

- **Title:** Reducing non-revenue water loss in urban distribution networks
- **Description:** "Our municipal water distribution pipelines are losing an estimated
  30% of treated water to undetected leaks. We need a solution using IoT sensors and
  AI-based anomaly detection to identify pipe leakage in real time, mapped against our
  GIS network, so field teams can be dispatched faster."
- **required_tech:** `["iot", "sensors", "ai", "gis"]`

| Startup | Match |
|---|---|
| AquaSense Systems | 4/4 — full match |
| PipeAI Technologies | 3/4 (no sensors) |
| JalShuddh AI | 3/4 (no gis) |
| HydroTrack Telemetry | 2/4 (no ai, gis) |

### 2. Waste

- **Title:** Smart bin monitoring to cut overflow complaints
- **Description:** "Citizens are reporting overflowing garbage bins faster than
  sanitation crews can respond. We want IoT sensor-based bin-fill monitoring with a
  mobile app for crew dispatch and GIS-based route optimization."
- **required_tech:** `["iot", "sensors", "mobile-app", "gis"]`

| Startup | Match |
|---|---|
| BinSense IoT | 4/4 |
| CleanHazard Systems | 4/4 |
| EcoFleet Routing | 2/4 |
| BioGasGen Decentralized | 2/4 |
| TrashBotics Automation | 0/4 |

Two full matches here is deliberate — good for showing the rubric break a tie on domain
experience/past projects/cost, not just tech overlap.

### 3. Transport — clearest "one obvious winner" story

- **Title:** Automated traffic signal optimization at high-congestion intersections
- **Description:** "Peak-hour congestion at key intersections is worsening. We want a
  computer vision and AI-based traffic signal system with automated real-time signal
  adjustment and analytics dashboards for traffic planners."
- **required_tech:** `["computer-vision", "ai", "automation", "analytics"]`

| Startup | Match |
|---|---|
| UrbanFlow Traffic AI | 4/4 — clear winner |
| SafeStreet Vision | 2/4 |
| EvGrid Dynamics | 2/4 |
| TransitPulse Mobility | 1/4 |
| LastMile Micro | 0/4 |

### 4. Healthcare

- **Title:** Reducing OPD wait times via predictive triage
- **Description:** "Hospital OPD queues are unpredictable, causing patient overcrowding.
  We want an AI-based triage and patient flow prediction system with a mobile app for
  token/queue management."
- **required_tech:** `["ai", "mobile-app"]`

| Startup | Match |
|---|---|
| MedQueue Technologies | 2/2 |
| VitalsEdge Diagnostics | 2/2 |
| ArogyaScan AI | 1/2 |
| PharmChain Logistics | 1/2 |
| NeuroBed Systems | 0/2 |

Same tie situation as waste — two full-tech matches, good for showing eligibility/cost
differentiation.

**Note:** `POST /ai/generate-statement`'s own `suggested_required_tech` (from
`backend/app/ai/classify.py`) is derived from the raw description text and will usually be
close to, but not always identical to, the `required_tech` lists above. For the demo,
either copy the AI's suggested tags straight into the `required_tech` field after clicking
"Generate Statement" (shows the AI-assist actually being used), or type the lists above
directly if guaranteed match numbers matter more.

## Suggested demo flow (~8-10 min)

1. **Government officer** logs in → New Challenge → paste problem statement #1's raw
   description → click Generate Statement → point out `generated_by: "template"` (LLM
   fallback working) and the `suggested_sector` / `suggested_required_tech` fields
   auto-filling the form.
2. Publish the challenge.
3. **Startup (AquaSense)** logs in → applies with a quote + pitch.
4. Back as **officer** → view ranked applications → show `match_score` with its
   per-factor breakdown (never a bare number) → shortlist → select.
5. **3 expert accounts** each submit an evaluation with different scores → show
   `GET /evaluations` returning the averaged total, not just a list.
6. Officer creates a pilot from the selected application with 2-3 milestones + KPIs.
7. Startup submits milestone evidence → **validator** verifies claimed vs. verified
   value → payment released (mock).
8. Officer finalizes the pilot → show the weighted final score and scale-up decision
   threshold logic.
9. Optional closer: open `/documents/{doc_type}/{entity_id}` to show the auto-generated
   HTML challenge document / print view.

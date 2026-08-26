# SIH 26136 — Team Execution Roadmap

**Project:** Startup-Friendly Public Procurement Platform ("ProcuraAI")
**Team:** 6 members, 3 pairs
**Duration:** Day 0 setup + 6 build days
**Repo model:** monorepo, `main` / `dev` / feature branches

---

## 1. Tech Stack (Final)

| Layer | Choice | Why |
|---|---|---|
| Frontend | React 19 + Vite + react-router 7 | Already built, keep it |
| Styling | The existing `styles.css` (1487 lines) | Do NOT migrate to Tailwind |
| Charts | Recharts | One import, works with React 19 |
| FE state | React Context + plain `fetch` wrapper | No Redux, no TanStack Query |
| Backend | FastAPI (Python 3.11+) | Auto Swagger docs, same language as scoring engines |
| ORM | SQLModel | Pydantic + SQLAlchemy in one class, half the code |
| DB | SQLite (dev) → Postgres on Render (demo) | Same SQLModel code, one env var change |
| Auth | JWT via `python-jose` + `passlib[bcrypt]` | ~50 lines, one file |
| Matching | scikit-learn TF-IDF + weighted formula | Deterministic, explainable, offline |
| LLM | Gemini Flash or Groq free tier, ONE endpoint only | Problem statement drafting |
| Documents | Jinja2 → HTML → browser print | Zero PDF library pain |
| Payments | Mock table + status transitions | No Razorpay |
| Deploy | Render (backend) + Vercel (frontend) | Both free, both git-push deploy |
| Testing | pytest for the 4 scoring engines only | Nothing else gets tested |

### Not using, on purpose

Docker, Redis, Celery, Kubernetes, Kafka, Supabase, Tailwind, Redux, Alembic migrations,
LangChain, vector databases, a real payment gateway, microservices, GraphQL, blockchain.

Every one of these costs a day to learn and earns zero demo points.

---

## 2. Database Schema (13 tables)

The proposed solution lists 19. Several are attributes, not entities. Collapsed version,
plus one table (`rubrics`) that the proposed solution does not have but needs. See section 2c.

```
users            id, name, email, password_hash, role, department, district
                 role ∈ {government, startup, expert, validator, admin}

startups         id, user_id, name, sector, technologies[], dpiit_number,
                 incorporation_year, turnover, team_size, past_projects[],
                 certifications[], description

challenges       id, created_by, department, district, title, raw_description,
                 statement_json (the 15-section template), sector, required_tech[],
                 eligibility_rules_json, kpi_targets_json, budget, timeline,
                 deadline, status, match_rubric_id, evaluation_rubric_id

applications     id, challenge_id, startup_id, eligible (bool),
                 eligibility_report_json, match_score, match_breakdown_json,
                 rubric_snapshot_json, explanation, status
                 status ∈ {applied, screened, shortlisted, evaluated, selected, rejected}

evaluations      id, application_id, expert_id, scores_json (7 criteria),
                 weighted_total, rubric_snapshot_json, comments, submitted_at

rubrics          id, name, kind, weights_json, criteria_json, version,
                 is_default, active, created_by, created_at
                 kind ∈ {match, evaluation}

pilots           id, challenge_id, startup_id, location, duration_days, budget,
                 objectives, security_checklist_json, security_status,
                 risk_level, status

milestones       id, pilot_id, seq, title, deliverable, amount, due_date,
                 status, evidence_text, evidence_url, submitted_at
                 status ∈ {pending, in_progress, submitted, validated, rejected, paid}

validations      id, milestone_id, validator_id, claimed_value, verified_value,
                 verdict, evidence_notes, validated_at

payments         id, milestone_id, amount, status, released_at, mock_txn_ref

kpis             id, pilot_id, name, unit, baseline, target, achieved, met (bool),
                 category, direction
                 category ∈ {technical, cost, impact, scalability}
                 direction ∈ {higher_is_better, lower_is_better}

risks            id, pilot_id, description, probability (1-5), impact (1-5),
                 score, mitigation, owner

procurement      id, pilot_id, final_score, decision, pathway, justification,
                 replication_json (district → status)
```

`decision ∈ {scale, scale_with_modifications, extend_pilot, reject}`

Store the security checklist, risk score rollup, and IP/data clauses as JSON columns
instead of separate tables. Fewer joins, fewer bugs, same demo output.


---

## 2b. Why SQLite Locally and Postgres on Render

Two databases for two situations, one codebase driving both.

**While you build (all six, on your own laptops)**

SQLite is a single file. `procura.db` sits in `backend/`. No server, no username, no
password, no port. Run `uvicorn`, the file appears, you are working in five seconds.
Each person has a private copy, so C1 can wipe and reseed forty times an hour without
breaking anyone else.

**On demo day (one shared server)**

The deployed backend needs a real database because:

- Render's free tier wipes disk on every redeploy. A SQLite file would take your seeded
  demo data with it.
- Judges plus your team hitting it at once means concurrent writes. SQLite locks the whole
  file on write. Postgres does not.
- Render provisions free Postgres in two clicks.

**The entire code change**

```python
# backend/app/config.py
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./procura.db")
```

Locally the env var is unset, so you get SQLite. On Render you paste their Postgres URL
into the dashboard and the same code hits Postgres. No model changes, no query changes.

**Two rules that keep this painless**

1. **No engine-specific features.** Stick to int, str, float, bool, datetime, JSON. Do not
   use Postgres `ARRAY` columns. Store `technologies` and `required_tech` as JSON lists,
   which work identically in both. This is what `technologies[]` in the schema means.
2. **No migrations.** Do not touch Alembic. To change the schema: delete the DB, recreate
   tables, run `seed.py`. Three seconds locally, one shell command on Render. For a six-day
   prototype, migrations are pure overhead.

**Fallback:** if Render Postgres fights you on Day 5, deploy with SQLite and reseed after
each redeploy. It will survive a six-minute demo. Do not burn Day 6 debugging a database.
A2 owns this call.


---

## 2c. Configurable Scoring Rubrics

**The problem.** If the match weights (30/20/15/15/10/10) and the expert weights
(25/15/15/15/10/10/10) live inside Python, your system only really works for one kind of
challenge. A hospital software pilot should weight security higher than a village water
pilot does. The problem statement asks for *standard templates*, and a template that
cannot be reused for a different challenge type is just a hardcoded form. A judge will
notice.

**What a rubric is.** A named list of percentages that sums to 100, stored in a table
instead of in code.

```json
{
  "name": "Default (PS baseline)",
  "kind": "match",
  "weights": {
    "technology_match": 30, "domain_experience": 20, "past_projects": 15,
    "eligibility": 15, "cost_fit": 10, "scalability": 10
  }
}
```

For an `evaluation` rubric, `criteria_json` also carries the label and help text per
criterion, so `EvaluationForm.jsx` renders itself from the rubric instead of from
hardcoded JSX. Add a criterion to the rubric, the form grows a field. No frontend deploy.

### The audit problem, and the two fixes

This is the part teams skip and then cannot answer in Q&A.

AquaSense is scored in January under "Default" and gets 91. In March an admin edits
"Default", dropping technology from 30 to 20. That stored 91 is now unexplainable. It was
produced by rules that no longer exist anywhere.

**Fix 1: snapshot on write.** When you score, copy the weights into the row.

```
applications.rubric_snapshot_json = {"technology_match": 30, "domain_experience": 20, ...}
```

Combined with `match_breakdown_json`, which already holds the raw per-factor values, every
score can be recomputed and defended years later. One column, one line of code.

**Fix 2: edit means clone.** A rubric that has been used is immutable. "Edit" creates
v2 and leaves v1 untouched forever. One extra endpoint, and the whole class of
retroactive-tampering questions disappears.

### Engine change

Pair C's functions stay pure, they just take one more argument.

```python
# before
def score_match(challenge, startup):
    tech = tech_similarity(...) * 0.30          # hardcoded

# after
def score_match(challenge, startup, weights: dict) -> dict:
    tech = tech_similarity(...) * weights["technology_match"] / 100
```

One shared validator, used by both `seed.py` and the admin endpoint:

```python
def validate_rubric(weights: dict, kind: str):
    if abs(sum(weights.values()) - 100) > 0.01:
        raise ValueError(f"weights must sum to 100, got {sum(weights.values())}")
    if set(weights) != REQUIRED_KEYS[kind]:
        raise ValueError("unknown or missing criteria")
```

`test_matching.py` gets a case proving that shifting weight from technology to cost
reorders the ranking. Show that test to a judge.

### Seed four, not one

Configurability is a claim until the dropdown has options in it.

| Rubric | Kind | Shifted toward |
|---|---|---|
| Default (PS baseline) | match | 30/20/15/15/10/10 exactly as the PS specifies |
| Infrastructure / IoT | match | technology and scalability up, cost down |
| Healthcare | match | security posture and past projects up, cost down |
| Low-budget municipal | match | cost_fit up to 25, past_projects down |
| Default expert panel | evaluation | 25/15/15/15/10/10/10 as the PS specifies |
| Security-weighted panel | evaluation | security to 25, social impact down |

### Endpoints

```
GET    /rubrics?kind=match
GET    /rubrics/{id}
POST   /rubrics                    admin only, runs validate_rubric
POST   /rubrics/{id}/clone         the only way to "edit" a used rubric
```

### Where this lands in the roadmap

About 90 minutes total, spread across people already editing those exact files. Nothing
moves to a later day and nothing new lands on Day 5.

| Who | Day | Task |
|---|---|---|
| A2 | 1 | `rubrics` table, two FKs on `challenges`, two snapshot columns. Same sitting as the rest of `models.py`. |
| C2 | 1 | `seed_data/rubrics.json` with the six rubrics above |
| C1 | 2 | `score_match` and `score_evaluation` take `weights`. Add `validate_rubric`. ~20 min. |
| A1 | 3 | The four `/rubrics` endpoints. ~30 min. |
| B1 | 3 | Rubric dropdown on `CreateChallenge.jsx`, dynamic `EvaluationForm.jsx`. ~40 min. |

### What stays hardcoded, on purpose

Do not make everything configurable or Day 4 becomes an admin panel.

- **Final scale-up weights and the four decision thresholds.** One rubric applied uniformly
  is defensible as national policy.
- **Risk formula** (probability x impact). Standard, do not invent variants.
- **Eligibility gate structure.** Already per-challenge JSON, which is the right level.

**The line: scoring weights are configurable, decision thresholds are not.** Say this out
loud during the demo. If a department could tune both the weights and the pass mark, they
could engineer a preferred vendor into winning. Letting them choose weights is flexibility.
Letting them choose thresholds is corruption. That one sentence answers the hardest
question a judge can ask about the whole system.

---

## 3. Team Division (3 pairs)

### Pair A — Core Platform & Contracts (covers M1 + M3)
Owns the database, auth, the challenge lifecycle, the pilot lifecycle, and deployment.

| Member | Fixed tools to learn |
|---|---|
| **A1** | FastAPI (routers, dependencies), Pydantic schemas, Swagger/Thunder Client |
| **A2** | SQLModel + SQLite/Postgres, JWT auth (`python-jose`, `passlib`), Render deployment, `seed.py` |

**Files they own:** `backend/app/models.py`, `db.py`, `auth.py`, `deps.py`, `seed.py`,
`routers/{auth,challenges,startups,applications,pilots,milestones,payments}.py`

### Pair B — Frontend & Dashboards (covers M2)
Owns every screen. The member who already built the prototype should be B1.

| Member | Fixed tools to learn |
|---|---|
| **B1** | React components + react-router, forms, the existing `styles.css` system |
| **B2** | `fetch` API client layer, React Context (auth + role), Recharts, Vercel deployment |

**Files they own:** everything under `frontend/`

### Pair C — Intelligence & Governance (covers M4 + M5 + M6)
Owns every number the system produces and every document it generates.

| Member | Fixed tools to learn |
|---|---|
| **C1** | scikit-learn (TF-IDF, cosine similarity), the weighted scoring math, Gemini/Groq API client |
| **C2** | Jinja2 templates, risk/security/decision logic, pytest, seed dataset curation |

**Files they own:** `backend/app/engines/*`, `backend/app/ai/*`, `backend/app/templates/*`,
`routers/{evaluations,validation,governance,procurement}.py`, `tests/`, `seed_data/`

**C2 also owns the PPT and demo script.** Start it Day 3, not Day 6.

### Why this split works
Pair C writes **pure functions**. `score_match(challenge, startup) -> dict`.
`check_eligibility(challenge, startup) -> dict`. `decide(pilot) -> dict`.
Pair A imports and mounts them. Almost zero merge conflicts because the file boundaries
are hard.

---

## 4. Repository Structure

```
sih-26136/
├── README.md
├── docs/
│   ├── API.md              ← frozen Day 0, the single source of truth
│   ├── SCHEMA.md
│   └── DEMO_SCRIPT.md
│
├── backend/
│   ├── app/
│   │   ├── main.py                 # app + CORS + router mounting
│   │   ├── config.py               # env vars
│   │   ├── db.py                   # engine, session dependency
│   │   ├── models.py               # all 12 SQLModel tables
│   │   ├── schemas.py              # request/response models
│   │   ├── auth.py                 # hash, verify, JWT encode/decode
│   │   ├── deps.py                 # get_current_user, require_role
│   │   │
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── rubrics.py          # list, get, create, clone
│   │   │   ├── challenges.py
│   │   │   ├── startups.py
│   │   │   ├── applications.py     # apply, screen, match, shortlist
│   │   │   ├── evaluations.py
│   │   │   ├── pilots.py
│   │   │   ├── milestones.py
│   │   │   ├── validation.py
│   │   │   ├── payments.py
│   │   │   ├── governance.py       # risk, security, kpis
│   │   │   ├── procurement.py      # final score, decision, replication
│   │   │   └── documents.py        # renders Jinja templates
│   │   │
│   │   ├── engines/                # PURE FUNCTIONS, no DB imports
│   │   │   ├── rubric.py           # validate_rubric, REQUIRED_KEYS
│   │   │   ├── eligibility.py
│   │   │   ├── matching.py
│   │   │   ├── evaluation.py
│   │   │   ├── performance.py
│   │   │   ├── risk.py
│   │   │   └── decision.py
│   │   │
│   │   ├── ai/
│   │   │   ├── client.py           # LLM call + timeout + fallback
│   │   │   └── problem_statement.py
│   │   │
│   │   └── templates/
│   │       ├── base.html
│   │       ├── problem_statement.html
│   │       ├── eligibility_criteria.html
│   │       ├── evaluation_criteria.html
│   │       ├── pilot_agreement.html
│   │       ├── milestone_contract.html
│   │       ├── data_ip.html
│   │       ├── security_checklist.html
│   │       ├── risk_register.html
│   │       ├── kpi_report.html
│   │       ├── validation_report.html
│   │       ├── payment_approval.html
│   │       ├── procurement_recommendation.html
│   │       └── scale_up_decision.html
│   │
│   ├── seed_data/
│   │   ├── startups.json           # 20 startups, 4 sectors
│   │   ├── challenges.json
│   │   ├── rubrics.json            # 4 match + 2 evaluation rubrics
│   │   └── users.json
│   ├── seed.py
│   ├── tests/
│   │   ├── test_eligibility.py
│   │   ├── test_rubric.py
│   │   ├── test_matching.py
│   │   ├── test_evaluation.py
│   │   ├── test_performance.py
│   │   └── test_decision.py
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/                       # the existing zip, moved here as-is
    ├── src/
    │   ├── main.jsx
    │   ├── App.jsx                 # routes + role guards
    │   ├── styles.css              # KEEP AS IS
    │   │
    │   ├── api/
    │   │   ├── client.js           # fetch wrapper, JWT header, error handling
    │   │   └── endpoints.js        # one function per API call
    │   │
    │   ├── context/
    │   │   └── AuthContext.jsx     # user, token, role, login, logout
    │   │
    │   ├── components/
    │   │   ├── DashboardLayout.jsx     (exists, extend nav)
    │   │   ├── ChallengeCard.jsx       (exists)
    │   │   ├── StatCard.jsx            (exists)
    │   │   ├── Badge.jsx               (exists)
    │   │   ├── ProtectedRoute.jsx      (new)
    │   │   ├── ScoreBreakdown.jsx      (new, bar per criterion)
    │   │   ├── MilestoneTracker.jsx    (new)
    │   │   ├── KpiChart.jsx            (new, Recharts)
    │   │   ├── RiskMatrix.jsx          (new)
    │   │   ├── ChecklistPanel.jsx      (new)
    │   │   └── DocumentViewer.jsx      (new, iframe + print button)
    │   │
    │   ├── pages/
    │   │   ├── Landing.jsx             (exists)
    │   │   ├── Login.jsx               (exists, wire to real auth)
    │   │   ├── GovernmentDashboard.jsx (exists, wire to API)
    │   │   ├── CreateChallenge.jsx     (exists, wire to real AI)
    │   │   ├── Recommendations.jsx     (exists, wire to matching)
    │   │   ├── PilotDashboard.jsx      (exists, wire to API)
    │   │   ├── StartupDashboard.jsx    (exists, wire to API)
    │   │   ├── ExploreChallenges.jsx   (exists, wire to API)
    │   │   ├── EvaluatorDashboard.jsx  (exists, wire to API)
    │   │   ├── ChallengeDetail.jsx     (new, replaces Placeholder)
    │   │   ├── ChallengeList.jsx       (new, replaces Placeholder)
    │   │   ├── MyApplications.jsx      (new, replaces Placeholder)
    │   │   ├── EvaluationForm.jsx      (new)
    │   │   ├── CreatePilot.jsx         (new)
    │   │   ├── MilestoneSubmit.jsx     (new, startup side)
    │   │   ├── ValidatorDashboard.jsx  (new)
    │   │   ├── ScaleUpDecision.jsx     (new)
    │   │   ├── Replication.jsx         (new)
    │   │   └── TemplateLibrary.jsx     (new)
    │   │
    │   └── data/mockData.js        # KEEP as offline fallback
    ├── package.json
    └── .env.example                # VITE_API_URL
```

---

## 5. Git Workflow

**Branches**
```
main        protected, only merged from dev, tagged nightly as demo-dayN
dev         integration branch, everyone merges here
feat/a-*    Pair A features
feat/b-*    Pair B features
feat/c-*    Pair C features
```

**Rules**
1. Never commit to `main` or `dev` directly. PR only.
2. A PR is merged by someone from a **different pair**. Takes 3 minutes, catches 80% of breakage.
3. `git pull origin dev` every morning before you write a line of code.
4. One feature = one branch = one PR. Do not accumulate 400-line PRs.
5. Commit message format: `[pairA] add milestone status transitions`
6. Nightly at 9pm: everyone merges to `dev`, run the demo path once, tag `main`.
7. Never commit `.env`, `*.db`, `node_modules/`, `__pycache__/`. Write `.gitignore` on Day 0.

**Merge conflict prevention:** the file ownership table in section 3 is not a suggestion.
If you need a file another pair owns, message them. Do not edit it.

---

## 6. API Contract (freeze this on Day 0)

```
POST   /auth/register
POST   /auth/login                        → { token, user }
GET    /auth/me

GET    /rubrics                           ?kind=match|evaluation
GET    /rubrics/{id}
POST   /rubrics                           admin only, validate_rubric
POST   /rubrics/{id}/clone                the only way to edit a used rubric

GET    /challenges                        ?sector=&status=
POST   /challenges                        → creates + returns generated statement
                                          body includes match_rubric_id, evaluation_rubric_id
GET    /challenges/{id}
POST   /ai/generate-statement             { raw_description, department, sector, ... }
                                          → 15-section statement_json

GET    /startups                          ?sector=&tech=
GET    /startups/{id}
POST   /challenges/{id}/discover          → eligibility + match scores for all startups
GET    /challenges/{id}/applications

POST   /applications                      { challenge_id }  (startup applies)
POST   /applications/{id}/shortlist
GET    /applications/{id}

POST   /evaluations                       { application_id, scores{7} }
GET    /evaluations?application_id=
POST   /applications/{id}/select

POST   /pilots                            → creates pilot + milestones
GET    /pilots/{id}
GET    /pilots/{id}/kpis
POST   /pilots/{id}/kpis
GET    /pilots/{id}/risks
POST   /pilots/{id}/risks
POST   /pilots/{id}/security-check        → PASSED / NEEDS_REMEDIATION

POST   /milestones/{id}/submit            { evidence }
POST   /milestones/{id}/validate          { verified_value, verdict }
POST   /milestones/{id}/pay               → mock payment

POST   /pilots/{id}/finalize              → final score + decision
GET    /pilots/{id}/procurement           → pathway recommendation
POST   /pilots/{id}/replicate             { districts[] }

GET    /documents/{type}/{entity_id}      → rendered HTML (printable)
```

Write the exact JSON request/response body for each one into `docs/API.md` on Day 0.
Pair B builds against that file. Pair A builds to satisfy it.

---

## 7. Scoring Formulas (Pair C)

The percentages below are the **seeded defaults**, not constants in code. Match and expert
weights come from a `rubrics` row at call time (section 2c). Eligibility, risk, and the
final decision thresholds ARE hardcoded, on purpose.

**Eligibility (pass/fail gate, runs before matching)**
```
registered_startup, required_certification, min_experience_years,
technology_overlap >= 1, budget_within_range, security_baseline
→ ALL must pass, else NOT ELIGIBLE with reason list
```

**AI Match Score (0-100)** — weights from the challenge's `match_rubric_id`
```
technology_match      30%   TF-IDF cosine(required_tech, startup.technologies)
domain_experience     20%   sector exact match 1.0 / adjacent 0.6 / unrelated 0.2
past_projects         15%   min(count_relevant / 3, 1.0)
eligibility           15%   1.0 if eligible else 0
cost_fit              10%   1 - abs(quote - budget) / budget, clamped [0,1]
scalability           10%   team_size + deployment_count heuristic, normalised
```
Always return `match_breakdown_json` with each factor, `rubric_snapshot_json` with the
weights used, AND a generated one-sentence explanation. The explanation is what wins
judges, not the number.

**Expert Evaluation (0-100)** — weights from the challenge's `evaluation_rubric_id`
```
technical_feasibility 25%   innovation 15%   cost_effectiveness 15%
scalability 15%   security 10%   implementation_capability 10%   social_impact 10%
final = mean(all expert weighted_totals)
```
Snapshot the weights onto each `evaluations` row too. Different experts on the same
application must share one rubric, or the average is meaningless.

**Risk** — HARDCODED
```
score = probability × impact   (1-25)
pilot_risk_level = LOW <8, MEDIUM 8-15, HIGH >15   (using max risk score)
```

**Final Pilot Score → decision** — HARDCODED, never configurable
```
technical 30%  cost 20%  impact 20%  scalability 15%  security 15%

>= 85   SCALE
70-84   SCALE_WITH_MODIFICATIONS
55-69   EXTEND_PILOT
< 55    REJECT
```


---

## 7b. How KPIs Roll Up Into the Final Score

Two layers. Teams usually conflate them and end up with a final score that means nothing.

**Layer 1: one KPI at a time.** Each row stores baseline (before the pilot), target
(promised in the agreement), and achieved (the value the *validator* verified, never the
value the startup claimed).

```
achievement = |achieved - baseline| / |target - baseline|
```

Two traps:

- **Direction.** Wastage, cost, and detection time improve by going *down*. Uptime and
  satisfaction improve by going *up*. Without a `direction` field your uptime scores come
  out negative. If the value moved the wrong way, the gain is negative and clamps to 0.
- **Overachievement.** Cap at 1.2. One KPI that overshoots 400% will otherwise carry a
  failing pilot to a pass by itself.

```python
def achievement(kpi) -> float:
    span = abs(kpi.target - kpi.baseline)
    if span == 0:
        return 1.0 if kpi.achieved >= kpi.target else 0.0
    gain = abs(kpi.achieved - kpi.baseline)
    wrong_way = (kpi.direction == "lower_is_better" and kpi.achieved > kpi.baseline) or \
                (kpi.direction == "higher_is_better" and kpi.achieved < kpi.baseline)
    if wrong_way:
        gain = -gain
    return max(0.0, min(gain / span, 1.2))
```

**Layer 2: KPIs to categories to final score.** The five categories in section 7 are
buckets, not KPIs. Each KPI carries a `category`, and a category scores as the mean of its
KPIs.

| Category | Weight | Source |
|---|---|---|
| technical | 30% | mean of its KPIs |
| cost | 20% | mean of its KPIs |
| impact | 20% | mean of its KPIs |
| scalability | 15% | mean of its KPIs |
| security | 15% | the cybersecurity checklist, not KPIs (7 of 8 passed = 87.5) |

Security is the exception: it has no measurable KPI, so its score comes from the checklist.

Worked example:

```
technical    detection time 67, uptime 91          → 79  × 0.30 = 23.7
cost         cost per km 87                        → 87  × 0.20 = 17.4
impact       water wastage 120 (capped)            → 120 × 0.20 = 24.0
scalability  districts ready 92, install time 86   → 89  × 0.15 = 13.4
security     checklist score                       → 96  × 0.15 = 14.4
                                                              -------
                                                                92.9  → SCALE
```

`engines/performance.py` is therefore two functions: `achievement(kpi)` and
`final_score(kpis, security_score)`. About 40 lines.

**Seed 6 to 8 KPIs per pilot, spread across all four categories.** A pilot with one KPI
makes the entire final-score machinery look like theatre.

---

## 8. Six-Day Roadmap

### Day 0 — Setup and Contract Freeze (4 hours, all six together)

Do this before Day 1. It is the highest-value block of the whole week.

| Task | Who |
|---|---|
| Install Python 3.11+, Node 20+, Git, VS Code, Thunder Client | All |
| Create GitHub repo, `dev` branch, `.gitignore`, branch protection on `main` | A2 |
| Move existing frontend zip into `frontend/`, commit, verify `npm run dev` runs | B1 |
| Hello-world FastAPI running on `:8000` with CORS open to `:5173` | A1 |
| **Write `docs/API.md` together.** Every endpoint, every JSON body. 90 minutes. | All |
| Write `docs/SCHEMA.md` (paste section 2) | A2 |
| Curate `seed_data/startups.json`: 20 startups across water, health, waste, transport | C2 |
| Agree the rubric criteria key names so engines and frontend never drift | C1 + B2 |
| Get a Gemini or Groq API key, verify one test call works | C1 |
| Git drill: everyone creates a branch, commits, opens a PR, gets it merged | All |

**Done when:** frontend and backend both run locally on every machine, and `docs/API.md`
is merged to `dev`.

---

### Day 1 — Skeletons

| Pair | Deliverable |
|---|---|
| **A** | All 13 tables in `models.py` including `rubrics`, the two rubric FKs on `challenges`, and the `rubric_snapshot_json` columns on `applications` and `evaluations`. `db.py` + session dep. `auth.py`: register, login, JWT, `/auth/me`, `require_role`. `seed.py` loads users + startups + 3 challenges. `GET /challenges` and `GET /startups` returning real rows. |
| **B** | Frontend moved into monorepo. `api/client.js` (fetch wrapper, attaches JWT, handles 401). `AuthContext.jsx`. `ProtectedRoute.jsx`. Login page hits real `/auth/login` and stores the token. `GovernmentDashboard` and `ExploreChallenges` fetch real data. Install Recharts. Add a `USE_MOCK` env flag that falls back to `mockData.js`. |
| **C** | `engines/eligibility.py` as a pure function + `test_eligibility.py`. `seed_data/rubrics.json` with 4 match + 2 evaluation rubrics. `templates/base.html` + `problem_statement.html` (all 15 sections). `templates/eligibility_criteria.html`. `seed_data/challenges.json`. |

**Integration check (9pm):** Log in as government, land on the dashboard, see three real
challenges from the database.

---

### Day 2 — Challenge Creation and Startup Discovery

| Pair | Deliverable |
|---|---|
| **A** | `POST /challenges` (persists raw + generated statement). `GET /challenges/{id}`. `POST /applications`. `GET /challenges/{id}/applications`. Mount `documents.py` router that renders any Jinja template by type + id. |
| **B** | `RubricSelect.jsx` dropdown on the challenge form with a live weight preview. `CreateChallenge.jsx` wired to real `POST /ai/generate-statement`, showing a loading state and the real 15-section output. `ChallengeList.jsx` and `ChallengeDetail.jsx` (replaces the two Placeholder routes). Startup side: Apply button on `ExploreChallenges`. `DocumentViewer.jsx` with a print button. |
| **C** | `engines/rubric.py` with `validate_rubric` + `test_rubric.py`. `ai/client.py` with a 10-second timeout and a template-only fallback if the LLM fails. `ai/problem_statement.py` producing the 15-section JSON. `engines/matching.py` taking `weights` as an argument, returning breakdown + snapshot + explanation string. `test_matching.py`, including a case proving that reweighting reorders the ranking. |

**Integration check:** Officer types a raw problem, clicks generate, sees a real structured
15-section statement, publishes it, and it appears on the startup dashboard.

---

### Day 3 — Screening, Matching, Expert Evaluation

| Pair | Deliverable |
|---|---|
| **A** | The four `/rubrics` endpoints (list, get, create, clone). `POST /challenges/{id}/discover` running eligibility then matching over all startups with the challenge's rubric, persisting `applications` rows with scores and weight snapshots. `POST /applications/{id}/shortlist`. `POST /evaluations`. `GET /evaluations`. `POST /applications/{id}/select`. Expert assignment logic. |
| **B** | `Recommendations.jsx` showing the real ranked list with `ScoreBreakdown.jsx` (a bar per criterion), the eligibility checklist per startup, and the explanation text. `EvaluatorDashboard.jsx` wired to assigned applications. `EvaluationForm.jsx` rendering its fields from the rubric's `criteria_json` rather than hardcoded JSX. `RubricLibrary.jsx`. `MyApplications.jsx`. |
| **C** | `engines/evaluation.py` taking `weights` as an argument, multi-expert averaging under a shared rubric. `templates/evaluation_criteria.html`. `test_evaluation.py`. **Start the PPT.** Draft `docs/DEMO_SCRIPT.md`. |

**Integration check:** Government clicks Discover, sees 20 startups screened down to eligible
ones and ranked with visible reasoning, shortlists 3, three expert accounts each score them,
the average appears, and the top startup gets selected.

---

### Day 4 — Pilot, Agreement, Milestones, Governance

| Pair | Deliverable |
|---|---|
| **A** | `POST /pilots` (creates the pilot plus 4 milestones from a template, splitting the budget). `GET /pilots/{id}`. Milestone status state machine. `POST /pilots/{id}/security-check`. `GET/POST /pilots/{id}/risks` and `/kpis`. |
| **B** | `CreatePilot.jsx` form. `PilotDashboard.jsx` fully wired with `MilestoneTracker.jsx`. `RiskMatrix.jsx`. `ChecklistPanel.jsx` for the cybersecurity checklist. Agreement viewer rendering the real generated HTML. |
| **C** | `templates/pilot_agreement.html` with all 16 clauses populated from the pilot record. `templates/data_ip.html`, `security_checklist.html`, `risk_register.html`, `milestone_contract.html`. `engines/risk.py`. Security checklist scoring logic. Seed 6 to 8 KPIs per pilot across all four categories, each with `category` and `direction` set. |

**Integration check:** Selected startup becomes a pilot, a real pilot agreement document
renders and prints, 4 milestones exist with amounts, the risk register shows scores, and
security status reads PASSED.

---

### Day 5 — Execution, Validation, Payment, Scale-Up, Replication

This is the hard deadline. The full pipeline must run end to end tonight.

| Pair | Deliverable |
|---|---|
| **A** | `POST /milestones/{id}/submit`. `POST /milestones/{id}/validate`. `POST /milestones/{id}/pay` with mock txn ref. `POST /pilots/{id}/finalize`. `GET /pilots/{id}/procurement`. `POST /pilots/{id}/replicate`. **Deploy backend to Render + seed the production DB.** |
| **B** | `MilestoneSubmit.jsx` (startup uploads evidence). `ValidatorDashboard.jsx` (claimed vs verified, approve/reject). Payment status flow on the pilot dashboard. `KpiChart.jsx` (baseline / target / achieved). `ScaleUpDecision.jsx`. `Replication.jsx` (district status table). `TemplateLibrary.jsx` listing all 13 document templates plus the rubric library. **Deploy frontend to Vercel.** |
| **C** | `engines/performance.py`: `achievement(kpi)` respecting `direction` and capping at 1.2, then `final_score()` grouping KPIs by `category` and folding in the security checklist score (section 7b). `test_performance.py` with a lower-is-better case. `engines/decision.py` (the four-way decision). `templates/validation_report.html`, `payment_approval.html`, `procurement_recommendation.html`, `scale_up_decision.html`, `kpi_report.html`. `test_decision.py`. Seed a second and third district for the replication demo. |

**Integration check:** Run all 21 stages in one sitting, from creating a challenge to
replicating to District C. Time it. It must fit in 6 minutes.

---

### Day 6 — Freeze, Polish, Rehearse

| Time | Task | Who |
|---|---|---|
| Morning | Bug bash. Every pair runs the full demo path three times and logs breakages. Fix blockers only. | All |
| Morning | Seed the demo database into a clean, believable state. No "test test test" rows. | C2 + A2 |
| **2pm** | **Feature freeze.** No new features after this. Only bug fixes. | All |
| Afternoon | Empty states, loading spinners, error toasts, mobile check on the landing page | B1 + B2 |
| Afternoon | Record a full screen capture of the working demo as offline insurance | B2 |
| Afternoon | Finish the PPT, add architecture diagram and the 21-stage pipeline graphic | C2 |
| Evening | Three full rehearsals with a timer. Assign speaking parts. | All |
| Evening | Q&A prep: write answers to the 10 questions in section 10 below | All |
| Night | Tag `main` as `v1.0-demo`. Verify the deployed URLs work from a phone hotspot. | A2 |

**If you have a 7th day:** it is a buffer day, not a feature day. Use it entirely for
rehearsal and for whatever Day 5 slipped.

---

## 9. Integrating the Existing Frontend

The existing zip is in good shape. Do not rewrite it.

**Keep exactly as is:** `styles.css`, `Badge.jsx`, `StatCard.jsx`, `ChallengeCard.jsx`,
`Landing.jsx`, the visual language, the `ProcuraAI` branding.

**Modify:**
1. `DashboardLayout.jsx` — add `validator` to `roleNav`, extend the government and startup
   nav arrays with the new routes, and pull the footer user from `AuthContext` instead of
   the hardcoded "Demo User".
2. `Login.jsx` — replace `navigate(/${role})` with a real `POST /auth/login`, store the
   token, then navigate. Keep the role selector as a demo convenience that prefills
   credentials for seeded accounts.
3. `App.jsx` — wrap dashboard routes in `ProtectedRoute`, delete `Placeholder` routes as
   real pages land.
4. `CreateChallenge.jsx` — the `generate()` function currently just sets a boolean. Replace
   with a real API call. Everything else on that page already looks right.
5. `mockData.js` — do not delete. Convert it into the `USE_MOCK=true` fallback path so the
   demo still renders if the backend dies on stage.

**Add:** `api/`, `context/`, `.env` with `VITE_API_URL`, and the 10 new pages listed in the
file structure.

---

## 10. Judge Q&A Prep (write real answers by Day 6)

1. Why is your matching deterministic instead of an LLM?
2. How do you prevent a department from gaming the eligibility criteria or the scoring weights?
3. What stops the startup from inflating its own KPI results?
4. How does this comply with GFR 2017 / GeM procurement rules?
5. Who owns the IP developed during the pilot?
6. What happens if a pilot fails at milestone 2? Does the startup lose everything?
7. How would you integrate with the real Startup India and GeM databases?
8. What is your data retention and deletion policy?
9. How does a district reuse another district's validated pilot without re-tendering?
10. What does this cost to run at national scale?
11. A rubric was edited after scoring. How do you prove an old score was fair?

Question 4 is the one most teams cannot answer. Spend 30 minutes reading up on GeM and
GFR Rule 173 and have a real answer.

---

## 11. Rules That Save The Week

1. **No one works on an unmerged branch for more than one day.**
2. **If a feature is not in the demo script, it does not get built.**
3. **Pair C never imports the database.** Pure functions only.
4. **Pair B never waits on Pair A.** Build against `docs/API.md` with mocks, swap later.
5. **The LLM has a fallback.** Every AI call must work offline with a template.
6. **Seed data is a feature.** Believable startup names and realistic numbers do more for
   the demo than any extra screen.
7. **Record the demo video on Day 6.** Wifi fails at hackathons.
8. **Every score carries its own weights.** Snapshot on write, never recompute from the
   live rubric.
9. **Depth over breadth.** One flawless water-leakage flow beats four half-built sectors.

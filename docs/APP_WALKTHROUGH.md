# ProcuraAI — Full Walkthrough (Problem Statement → Scale-Up Decision)

This document walks through **every screen, click, and number** in ProcuraAI, from a
government officer posting a problem all the way to the final "should we scale this up
statewide?" decision. It's written so you can have the website open in one window and
this file open in the other, and follow along step by step.

Nothing in here is invented or rounded for effect — every score you'll see below was
computed by actually running the platform's scoring code with real seed data, so the
numbers match what you'll see on screen (small differences are possible if you type
different values, but the formulas are exact).

**Login page:** `http://localhost:5173/login`. Password for every account is `demo1234`.

| Role | Email | Who they are |
|---|---|---|
| Government officer | `officer@water.gov.in` | Posts problems, picks winners, runs pilots |
| Startup founder | `founder@aquasense.in` | Applies to challenges, submits milestone evidence |
| Expert (×3) | `expert1@procura.gov.in`, `expert2@...`, `expert3@...` | Score shortlisted applications |
| Validator | `validator@procura.gov.in` | Independently checks a startup's claims before payment |
| Admin | `admin@procura.gov.in` | Can see everything (not used in this walkthrough) |

---

## The big picture

A challenge moves through this pipeline, in this order:

```
Officer writes a problem
        │
        ▼
AI expands it into a 15-section spec, officer publishes it
        │
        ▼
Startups apply (or officer "discovers" every startup on the platform)
        │
        ▼
Two automatic engines run on every startup:
   1. Eligibility gate  (pass/fail — 6 yes/no checks)
   2. Match score       (0–100, six weighted factors)
        │
        ▼
Officer shortlists the top candidates
        │
        ▼
3 independent experts each score the shortlisted startups (0–100, seven weighted criteria)
their scores are averaged
        │
        ▼
Officer looks at the average and clicks "Select Winner"
   → winner becomes "selected", every other applicant becomes "rejected" automatically
        │
        ▼
Officer creates a Pilot for the winner
   → budget is auto-split into 4 milestones (20% / 30% / 30% / 20%)
   → the challenge's KPI targets are copied onto the pilot
        │
        ▼
For each of the 4 milestones, in order:
   startup submits evidence → validator independently checks it → officer pays
        │
        ▼
Along the way: officer logs risks (probability × impact) and
runs an 8-item cybersecurity checklist, and records each KPI's actual measured value
        │
        ▼
Officer clicks "Finalize pilot"
   → one composite 0–120 score is computed from 5 weighted categories
   → a fixed threshold table turns that score into one of 4 decisions:
     scale / scale with modifications / extend pilot / reject
        │
        ▼
If scaling: officer adds more districts to a replication plan
```

Two engines matter the most and are explained in full detail below:
the **match engine** (who looks like a good fit) and the **evaluation engine**
(what human experts actually think after reading the proposal). Everything after
"Select Winner" is about proving, with real numbers, whether the pilot actually worked.

---

## Stage 1 — Officer creates a challenge

**Login as officer** → left sidebar → **"Create Challenge"** (`/government/create`).

Fill in the left-hand form:

| Field | What it's for |
|---|---|
| Challenge Title | Headline of the problem |
| Department / District | Which office owns this, and where |
| Sector | One of `water`, `healthcare`, `waste`, `transport` — this matters a lot later (see Domain Experience below) |
| Pilot Budget (₹) | Hard ceiling. Startups that quote above this fail the "budget" eligibility gate |
| Pilot Duration (days) | How long the pilot runs once created |
| Required Technologies | **Must** be typed using only these 12 exact words: `iot, sensors, ai, computer-vision, analytics, cloud, mobile-app, gis, telematics, robotics, edge-computing, automation`. Typing a real-world phrase like "Acoustic Sensors" instead of `sensors` will not match anything — the matching engine only understands this fixed vocabulary, never free text. |
| Rough Problem Description | 2–3 plain sentences — this is what the AI expands |
| Match Scoring Rubric | Which weighting formula will be used to rank startups (see Stage 3) |

Click **"Generate structured challenge"**. The backend calls an AI model to turn your
rough paragraph into a 15-section formal specification (Problem Definition, Background,
Existing System, Identified Gap, Desired Solution, Target Users, Technical Requirements,
Constraints, Budget, Timeline, Expected Outcomes, KPIs, Eligibility Requirements, Data
Governance, Security Requirements). If the AI call fails or times out, the backend
silently falls back to a template version instead of showing an error — you'll see a small
banner saying "Generated via baseline procurement template" but you can still edit every
section and publish normally. **This fallback is intentional and always on** — publishing
a challenge can never be blocked by an AI outage.

Review/edit any of the 15 sections, then click **"Publish Challenge"**. You're redirected
to the challenges list; the new challenge is now `open` and visible to startups.

---

## Stage 2 — Startups apply (optional, but affects one number later)

Log out, log back in as the startup founder → sidebar → **"Explore Challenges"**
(`/startup/explore`). Open a challenge, click **Apply**, and fill in the modal:

- **Proposed Pilot Budget Quote (₹)** — defaults to the challenge's budget, but the
  startup can quote lower (or higher, which risks failing the budget gate)
- **Technical Approach & Pilot Pitch** — free text

This is the *only* way a "quote" number enters the system. If a startup never applies,
the officer's blanket "Discover Startups" step (next) still screens and scores them, but
their **cost fit** score defaults to a neutral 75/100 rather than being based on a real
number — you can't reward or penalize a quote that doesn't exist.

---

## Stage 3 — Discover, screen, and rank every startup

Back as the officer → sidebar → **"AI Recommendations"** (`/government/recommendations`).
Pick the challenge from the dropdown, click **"Discover startups"**.

This single click runs **every startup ever seeded on the platform** (20 by default)
through two pure, deterministic calculations — no AI, no randomness, same input always
gives the same output.

### 3a. The eligibility gate — 6 pass/fail checks

Every startup must pass all six of these, or it's marked ineligible and automatically
scores 0 on the "eligibility" factor below:

| # | Check | How it's decided |
|---|---|---|
| 1 | Registered startup | Does the startup have a non-empty DPIIT registration number? |
| 2 | Required certification | If the challenge names one (e.g. `ISO 9001:2015`), does the startup hold it? |
| 3 | Minimum experience years | `current_year − incorporation_year` must be ≥ the challenge's minimum |
| 4 | Technology overlap | At least N of the challenge's required tags must appear in the startup's tags (N is usually 1) |
| 5 | Budget within range | The startup's quote (from Stage 2) must be ≤ the challenge's budget |
| 6 | Security baseline | Startup must self-declare it meets a basic security baseline |

Any challenge rule that isn't set is treated as "waived" (auto-pass) — e.g. if a challenge
never sets `required_certification`, every startup passes that check by default.

**On screen:** only the *failed* checks are shown, as red tags under each ineligible
startup (e.g. "Missing required certification: ISO 27001"). Passing checks aren't listed
individually — you'll just see the green **"Eligible"** badge.

### 3b. The match score — six weighted factors, 0–100

For every startup, six raw sub-scores (each 0–100) are computed, then combined using the
percentage weights from the rubric you picked in Stage 1. The **default rubric** looks
like this:

| Factor | Default weight | What produces the 0–100 sub-score |
|---|---|---|
| Technology match | 30% | Overlap between required tags and the startup's tags |
| Domain experience | 20% | How closely the startup's sector matches the challenge's sector |
| Past projects | 15% | Number of the startup's past projects in this exact sector |
| Eligibility | 15% | 100 if it passed all 6 gates above, otherwise 0 |
| Cost fit | 10% | How close the quote is to the budget |
| Scalability | 10% | Team size + number of past deployments |

Four rubric variants exist (Default, Infrastructure/IoT, Healthcare, Low-budget
municipal) — same six factors every time, just different weights, because a hardware-heavy
IoT project should care more about technology match than a cash-strapped municipal one
should. You can browse all of them read-only at sidebar → **"Rubric Library"**.

Here's exactly how each of the six sub-scores is computed:

**Technology match.** If the startup's tag list is *exactly* the same set as the
challenge's required list, this is 100. Otherwise it's a text-similarity score between the
two lists (technically: TF-IDF cosine similarity — in plain terms, it rewards lists that
share more of the *same, less-common* words, and it can actually go a little *below* 100
even if every required tag is present, if the startup also lists extra tags that dilute the
match). If the startup has zero tags, this is 0.

**Domain experience.** Compares the challenge's sector to the startup's sector:
- Same sector → **100**
- "Adjacent" sector → **60** (the platform only treats `water ↔ waste` and
  `waste ↔ transport` as adjacent; `healthcare` has no adjacency to anything)
- Anything else → **20**

**Past projects.** Counts how many of the startup's listed past projects were in the
*same* sector as the challenge, divides by 3, and caps at 100%. So 3+ relevant past
projects = 100, 1 relevant project ≈ 33.3, 0 relevant projects = 0.

**Eligibility.** Simply 100 if the eligibility gate passed, 0 if it didn't. This is why a
single failed gate check (say, a missing certificate) can tank a startup's entire ranking
even if their tech is perfect — eligibility is worth double the "cost fit" weight in the
default rubric.

**Cost fit.** `(1 − |quote − budget| / budget) × 100`, clamped to [0, 100]. A quote exactly
at budget scores 100; a quote 20% under or over budget scores 80. If no quote was ever
submitted (Stage 2 was skipped), this defaults to a neutral **75**, not 0 and not 100 —
the system deliberately doesn't reward or punish a number that was never given.

**Scalability.** Two halves, each worth up to 50 points: `min(team_size / 20, 1) × 50` for
team size, plus `min(past_project_count / 3, 1) × 50` for prior deployments. A team of 20+
people with 3+ past deployments scores the full 100.

### A real worked example

Using the seeded "Reduce Municipal Water Leakage" challenge (required tech
`iot, sensors, analytics, gis`, budget ₹10,00,000, default rubric) against the seeded
startup **AquaSense Systems** (tags `iot, sensors, ai, analytics, gis`, water sector, 3
past water-sector projects, team of 18, incorporated 2021), with a quote of ₹9,50,000:

| Factor | Sub-score | Weight | Contribution |
|---|---|---|---|
| Technology match | 81.8 | 30% | 24.5 |
| Domain experience | 100.0 (exact sector match) | 20% | 20.0 |
| Past projects | 100.0 (3 of 3 relevant) | 15% | 15.0 |
| Eligibility | 100.0 (passed all 6 gates) | 15% | 15.0 |
| Cost fit | 95.0 (quote is 5% under budget) | 10% | 9.5 |
| Scalability | 95.0 (team 18/20 + 3/3 deployments) | 10% | 9.5 |
| **Total** | | | **93.5 / 100** |

Notice technology match landed at 81.8, not 100 — AquaSense lists `ai` as a tag, which the
challenge never asked for. Listing every required tag plus one extra still isn't treated
as a perfect set match. If AquaSense had never submitted a quote at all, cost fit would
have been the neutral 75 instead of 95, and the total would have been **91.5** instead of
93.5 — a good illustration of why applying with a real quote (Stage 2) is worth doing.

Every ranked card also shows a plain-English **explanation** built from the same numbers,
e.g. *"Recommended because the startup has capabilities matching 4 of 4 required
technologies, 3 prior water-sector deployments, a quote 5% under budget."* — nothing in
that sentence is generated freely; it's assembled from the real counts above.

The result list is sorted eligible-first, then by match score, highest first.

---

## Stage 4 — Shortlist

On the same Recommendations page, click **"Shortlist"** on any eligible applicant you
want an expert panel to look at. Their status flips from `screened` to `shortlisted`, and
they now appear in the expert queue.

---

## Stage 5 — Expert evaluation

Log out, log in as an expert (`expert1@procura.gov.in`) → sidebar → **"Pending Reviews"**
(`/evaluator/reviews`) → click a shortlisted application → **Evaluate**.

You'll see a slider (0–100) for each of the 7 criteria in the challenge's **evaluation
rubric** (the default one, weights shown):

| Criterion | Default weight |
|---|---|
| Technical feasibility | 25% |
| Innovation | 15% |
| Cost effectiveness | 15% |
| Scalability | 15% |
| Security | 10% |
| Implementation capability | 10% |
| Social impact | 10% |

Every slider starts at 50, and a **live "weighted preview"** at the bottom recalculates as
you drag any slider — you see your own weighted total before you even submit. Click
**"Submit evaluation"** and the same formula is recomputed and frozen server-side.

**The math is a straight weighted average:** each score × its criterion's weight ÷ 100,
summed. Example — one expert enters 92/88/85/90/95/90/88 in that order:

```
92×0.25 + 88×0.15 + 85×0.15 + 90×0.15 + 95×0.10 + 90×0.10 + 88×0.10
= 23.0 + 13.2 + 12.75 + 13.5 + 9.5 + 9.0 + 8.8
= 89.8 / 100
```

A second expert scoring more conservatively (85/80/88/82/90/85/80) would land at **84.2**.
The two are simply averaged: **(89.8 + 84.2) / 2 = 87.0**, shown as the "Expert average"
with a count of how many experts have scored so far. There's no weighting by seniority or
confidence — every submitted evaluation counts equally in the average.

Each expert's rubric weights are **frozen onto their evaluation at submit time**
("rubric snapshot"). If someone edits the rubric later, every evaluation already submitted
still shows the weights that were actually used when it was scored — this is deliberate,
so a past score can always be explained and never silently changes.

---

## Stage 6 — Officer selects the winner

Log back in as the officer → **"AI Recommendations"** → pick the same challenge. Any
application that's been shortlisted or evaluated now shows an **"Expert average"** box
right on its card:

- If no expert has scored it yet: *"Loading expert scores…"* then *"No expert evaluations
  submitted yet."*
- Once at least one has: **"Expert average: 87.0/100"** plus *"2 evaluations · Dr S Rao,
  Prof M Iyer"* (the named experts who scored it).

Click **"Select winner"** on your chosen startup. Two things happen in one action:
1. That application's status becomes `selected`.
2. **Every other application on that challenge is automatically set to `rejected`** — you
   never manually reject the runners-up, it's a side effect of picking a winner.

A **"Create pilot"** button now appears on the winning card.

---

## Stage 7 — Create the pilot

Click **"Create pilot"** → fills a form pre-populated from the challenge (location,
duration, budget, objectives). The budget is **automatically split into exactly 4
milestones**, always in this fixed 20/30/30/20 ratio, at fixed intervals:

| # | Milestone | % of budget | Due |
|---|---|---|---|
| 1 | Prototype | 20% | +20 days |
| 2 | Field trial | 30% | +45 days |
| 3 | Deployment | 30% | +70 days |
| 4 | Final results | remainder (≈20%) | pilot's end date |

(The 4th milestone gets whatever is left over after rounding down the first three, so the
four always add up to exactly the total budget — the "Create pilot" button is disabled
until that check passes.) The challenge's KPI targets (baseline/target/unit/direction) are
copied onto the pilot unchanged. Click **"Create pilot"** and you land on the pilot
dashboard — the hub for everything that follows.

---

## Stage 8 — Running the pilot: the milestone lifecycle

Each milestone moves through a fixed sequence of statuses:

```
pending/in_progress → submitted → validated → paid
                    ↘ rejected (validator sends it back)
```

**Startup's turn:** log in as the founder → **"My Pilot"** → open a `pending` milestone →
**"Submit Milestone Evidence"**. They write an evidence summary, an optional evidence URL,
and a **claimed value** (their own unverified number, e.g. "we measured 22% water
wastage"). This flips the milestone to `submitted`.

**Validator's turn:** log in as `validator@procura.gov.in` → **Validation Queue**
(`/validator`) — this page pulls every `submitted` (or previously `rejected`) milestone
across *all* pilots. The validator sees the startup's claimed value side-by-side with an
input box for the **independently verified value**, plus notes, then clicks **Approve** or
**Reject**. Approving sets the milestone to `validated`; rejecting sends it back to
`rejected` so the startup can resubmit. This claimed-vs-verified split exists specifically
so no one can self-certify their own pilot's success.

**Officer's turn:** back on the pilot dashboard, the milestone tracker shows a **"Pay
milestone"** button that is only clickable once a milestone is `validated`. There's no
extra confirmation dialog — one click calls the payment endpoint and the milestone becomes
`paid` immediately. This is the "auto-advances to paid" step people describe when
demoing it: it isn't automatic in the sense of happening without a click, it's automatic
in the sense that once validated, paying it is a single deliberate action rather than a
multi-step approval chain.

The pilot dashboard's **"Paid to date"** figure is just the sum of every `paid` milestone's
amount, shown against the total budget.

---

## Stage 9 — Risk register and security checklist

Still on the pilot dashboard, as the officer:

**Risk register.** Add a risk with a free-text description, a **Probability** (1–5) and
**Impact** (1–5) dropdown, mitigation notes, and an owner. The risk's score is simply:

```
risk score = probability × impact        (so it ranges 1–25)
```

Example: probability 3, impact 4 → **score 12**. The *pilot's* overall risk level is driven
by whichever single risk currently has the **highest** score, not an average:

| Highest score in the list | Overall pilot risk |
|---|---|
| < 8 | low |
| 8 – 15 | medium |
| > 15 | high |

So a pilot with risks scoring [6, 12, 20] is rated **high** overall — one bad risk is
enough to flip the whole pilot's badge, on purpose, because averaging away a genuinely
severe risk would hide it.

**Cybersecurity checklist.** 8 fixed yes/no controls — authentication, authorization, data
encryption, secure API, data backup, vulnerability assessment, access logging, incident
response plan. Click **"Run security check"**. The score is just:

```
security score = (number of boxes checked / 8) × 100
```

All 8 checked → `passed`. Anything less → `needs_remediation`, and the UI lists exactly
which controls are still missing (e.g. 7 of 8 checked, missing "incident response plan" →
**87.5%**, `needs_remediation`). This score feeds straight into the final decision math in
Stage 11, worth 15% of the total.

---

## Stage 10 — Recording KPIs

Each KPI card shows three bars: **Baseline**, **Target**, and **Achieved** (blank until
measured). As the officer, type a measured value into the box under the chart and click
**"Record achieved value"**. The backend then computes an **achievement percentage**:

```
span = |target − baseline|
gain  = |achieved − baseline|,  but flipped negative if you moved the wrong direction
achievement = clamp(gain / span, 0%, 120%)
```

In plain terms: it measures **how far you actually moved, as a fraction of how far you
were asked to move** — hitting the target exactly is 100%; overshooting it is rewarded up
to a hard ceiling of **120%** (so one spectacular KPI can't single-handedly rescue an
otherwise-failing pilot in the final score); moving the wrong direction, or not moving at
all, scores toward 0%.

Worked examples from the seeded "water wastage" KPI (baseline 30%, target 20%,
`lower_is_better`):

| Achieved | Reasoning | Achievement |
|---|---|---|
| 18% | Moved 12 of the required 10 points, in the right direction, past the target | **120%** (capped) |
| 25% | Moved 5 of the required 10 points | 50% |
| 30% | Didn't move at all | 0% |
| 35% | Moved backwards (wrong direction) | 0% (clamped, never negative on screen) |

And for a `higher_is_better` KPI like system uptime (baseline 0%, target 95%, achieved
97%): `gain = 97, span = 95, achievement = 97/95 = 102.1%`.

---

## Stage 11 — The final scale-up decision

Once every milestone is validated, the security checklist has been run, and KPIs are
recorded, go to **"Scale-up decision"** on the pilot dashboard and click **"Finalize
pilot"**. This is a single button — no manual score entry, everything below is computed
from what you already recorded.

**Step 1 — roll KPIs up into 4 categories.** Every KPI on the pilot is tagged
`technical`, `cost`, `impact`, or `scalability`. Each category's score is just the average
achievement percentage of every KPI in it (a category with no KPIs defaults to 100 —
"unconstrained", not "failed"). The 5th category, `security`, is simply the checklist score
from Stage 9 — it isn't derived from any KPI.

**Step 2 — combine the 5 categories into one final score**, using fixed weights that are
**not configurable by design** (see note at the end of this document for why):

| Category | Weight |
|---|---|
| Technical | 30% |
| Cost | 20% |
| Impact | 20% |
| Scalability | 15% |
| Security | 15% |

**Step 3 — a fixed threshold table turns that score into a decision:**

| Final score | Decision |
|---|---|
| ≥ 85 | **Scale** — approved for statewide/district replication |
| ≥ 70 | **Scale with modifications** — approved with corrective refinements |
| ≥ 55 | **Extend pilot** — needs another validation period |
| < 55 | **Reject** — did not meet minimum thresholds |

### A real worked example

Suppose the water-leakage pilot ends with: uptime achievement 102.1%, leak-detection
achievement 101.5% (both `technical`), cost achievement 113.3%, water-wastage achievement
120% (`impact`, capped), telemetry-coverage achievement 107.1% (`scalability`), and a
security score of 87.5% (7 of 8 checklist items):

```
technical    = (102.1 + 101.5) / 2 = 101.8
cost         = 113.3
impact       = 120.0
scalability  = 107.1
security     = 87.5

final_score = 101.8×0.30 + 113.3×0.20 + 120.0×0.20 + 107.1×0.15 + 87.5×0.15
            = 30.5 + 22.7 + 24.0 + 16.1 + 13.1
            = 106.4
```

**106.4 ≥ 85 → decision: "Scale."** Notice the final score can legitimately go *above*
100 — each individual KPI is capped at 120%, but nothing caps the *composite*, so a pilot
that overshoots several targets at once can score above 100 overall. That's expected
behavior, not a bug.

A plain-language justification is generated from these same real numbers — never invented
text — e.g. *"Exceeded impact target with score 120.0%, achieved technical reliability of
101.8%... All 4/4 milestones verified and cybersecurity audit needs_remediation (87.5%).
Recommended for accelerated statewide procurement scale."*

Below the decision, a **"Procurement readiness"** panel shows 4 independent yes/no checks
(all recomputed live from real data every time you open the page, not stored guesses):

| Check | True when… |
|---|---|
| `pilot_validated` | every milestone on the pilot is `validated` or `paid` |
| `performance_threshold_met` | final score ≥ 85 |
| `security_approved` | the checklist status is `passed` (not `needs_remediation`) |
| `budget_available` | total paid so far hasn't exceeded the pilot's budget |

---

## Stage 12 — Replication plan

Click **"Replication plan"** from the pilot dashboard. The pilot's own district is already
listed as `completed`. Type more district names, comma-separated (e.g. `District B,
District C`), click **"Add to plan"** — each new row starts as `planned`. There's no scoring
here; it's a simple tracking table of where a validated solution is being rolled out next.

Close on the idea the platform is built around: **a validated pilot becomes a reusable
template other districts can adopt without re-running procurement from scratch** — the
same rubric, the same milestone structure, the same KPI targets, just pointed at a new
location.

---

## Stage 13 — The paper trail

Every stage above produces a formal, printable HTML document (sidebar → **"Template
Library"**, or the document links on the Challenge/Pilot pages), all rendered from the same
underlying data — nothing in a document is typed by hand separately:

| Document | What it shows |
|---|---|
| Problem Statement | The 15-section spec from Stage 1 |
| Eligibility Criteria | The 6 gate rules for the challenge |
| Evaluation Criteria | The 7 expert-rubric weights |
| Pilot Agreement | Scope, milestone payment schedule, data & validation terms |
| Milestone Contract | Deliverables and release conditions per milestone |
| Data and IP Agreement | Data governance / IP clauses |
| Security Checklist | The 8-item cybersecurity result |
| Risk Register | Every logged risk, score, and mitigation |
| KPI Report | Baseline/target/achieved and attainment evidence |
| Validation Report | The validator's independent record per milestone |
| Payment Approval | Authorization tied to a validated milestone |
| Procurement Recommendation | The evidence-backed pathway |
| Scale-up Decision | Final score and outcome |

---

## Appendix — what's configurable vs. what's fixed on purpose

- **Configurable, per challenge:** which match rubric and which evaluation rubric to use
  (their weights can differ challenge to challenge, but the six/seven criteria names
  themselves are fixed). Once a rubric has been used for real scoring, you can't edit it in
  place — you clone it into a new version instead, so every historical score stays
  explainable via the exact weights it was scored with.
- **Fixed, not configurable, anywhere in the platform:**
  - The final scale-up score's 5 category weights (30/20/20/15/15)
  - The 85 / 70 / 55 decision thresholds
  - The risk formula (`probability × impact`) and its low/medium/high bands
  - The KPI achievement cap of 120%

  These are deliberately hardcoded policy rather than settings, because a department that
  could tune *both* the scoring weights *and* the passing bar could quietly engineer a
  favored vendor into a "scale" decision. Keeping the final gate fixed is what makes the
  whole audit trail meaningful — every number a citizen or auditor sees traces back to a
  formula nobody on the department side can adjust after the fact.

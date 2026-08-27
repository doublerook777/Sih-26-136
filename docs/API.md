# API Contract

**Status: FROZEN as of Day 0.** Pair A builds to satisfy this. Pair B builds against it
with mock data. Neither waits for the other.

If something here turns out to be wrong, change **this file first** in a PR, tell the other
pairs in the group chat, then change the code. Never change the code and leave this stale.

---

## 0. Conventions (decided, do not re-litigate)

| Decision | Value |
|---|---|
| Base URL (dev) | `http://localhost:8000` |
| Base URL (prod) | set in frontend `.env` as `VITE_API_URL` |
| Field naming | `snake_case` everywhere, in requests, responses, and the database |
| IDs | integers, auto-increment |
| Money | integers, whole rupees, no paise, no decimals, no strings |
| Percentages / scores | floats, 0 to 100, one decimal place (`91.2`) |
| Dates and times | ISO 8601 UTC strings, `"2026-08-27T14:30:00Z"` |
| Dates only | `"2026-08-27"` |
| Booleans | real JSON `true` / `false`, never `"yes"` / `1` |
| List endpoints | return a bare JSON array, not wrapped in an object |
| Auth | JWT in the header: `Authorization: Bearer <token>` |
| Missing values | `null`, never `""` or `"N/A"` |

### Error shape (all errors, every endpoint)

FastAPI's default. Do not invent a second shape.

```json
{ "detail": "human readable message" }
```

| Code | Means |
|---|---|
| 200 | success |
| 201 | created |
| 400 | bad input the server understood but rejected |
| 401 | not logged in, or token expired |
| 403 | logged in but wrong role |
| 404 | not found |
| 422 | FastAPI validation error (wrong types, missing fields) |

Pair B writes **one** error handler for all of this, not one per screen.

### Roles

```
government   startup   expert   validator   admin
```

Every protected endpoint below lists which roles may call it.

---

## 1. Auth

### POST /auth/register
Roles: public

```json
// request
{
  "name": "R Kumar",
  "email": "officer@water.gov.in",
  "password": "secret123",
  "role": "government",
  "department": "Urban Water Supply",
  "district": "District A"
}
```
```json
// 201
{
  "id": 1,
  "name": "R Kumar",
  "email": "officer@water.gov.in",
  "role": "government",
  "department": "Urban Water Supply",
  "district": "District A"
}
```
`department` and `district` are `null` for startup, expert, validator, admin.

### POST /auth/login
Roles: public

```json
// request
{ "email": "officer@water.gov.in", "password": "secret123" }
```
```json
// 200
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "name": "R Kumar",
    "email": "officer@water.gov.in",
    "role": "government",
    "department": "Urban Water Supply",
    "district": "District A"
  }
}
```
```json
// 401
{ "detail": "invalid email or password" }
```

### GET /auth/me
Roles: any logged in

Returns the same `user` object as above. Pair B calls this on page load to restore the
session from a stored token.

---

## 2. Rubrics

Criteria keys are **frozen**. See section 9.

### GET /rubrics?kind=match
Roles: any logged in. `kind` is `match` or `evaluation`.

```json
// 200
[
  {
    "id": 1,
    "name": "Default (PS baseline)",
    "kind": "match",
    "version": 1,
    "is_default": true,
    "active": true,
    "weights": {
      "technology_match": 30,
      "domain_experience": 20,
      "past_projects": 15,
      "eligibility": 15,
      "cost_fit": 10,
      "scalability": 10
    },
    "criteria": [
      { "key": "technology_match", "label": "Technology match", "weight": 30,
        "help": "Overlap between required tech and startup capability" }
    ]
  }
]
```

`criteria` carries the display labels. **Pair B never hardcodes a label**, it renders from
this array.

### GET /rubrics/{id}
Roles: any logged in. Returns one rubric, same shape.

### POST /rubrics
Roles: admin

```json
// request
{
  "name": "Healthcare weighted",
  "kind": "match",
  "criteria": [
    { "key": "technology_match", "label": "Technology match", "weight": 25, "help": "..." },
    { "key": "domain_experience", "label": "Domain experience", "weight": 20, "help": "..." },
    { "key": "past_projects", "label": "Past projects", "weight": 20, "help": "..." },
    { "key": "eligibility", "label": "Eligibility", "weight": 15, "help": "..." },
    { "key": "cost_fit", "label": "Cost fit", "weight": 5, "help": "..." },
    { "key": "scalability", "label": "Scalability", "weight": 15, "help": "..." }
  ]
}
```
```json
// 201 — same shape as GET /rubrics/{id}
```
```json
// 400
{ "detail": "weights must sum to 100, got 95" }
```

### POST /rubrics/{id}/clone
Roles: admin. The only way to "edit" a rubric that has been used.

```json
// request
{ "name": "Healthcare weighted v2", "criteria": [ ...same shape as POST... ] }
```
Returns the new rubric with `version` incremented. The original is untouched.

---

## 3. Challenges

### GET /challenges?sector=water&status=open
Roles: any logged in. Both query params optional.

```json
// 200
[
  {
    "id": 1,
    "title": "Reduce municipal water leakage",
    "department": "Urban Water Supply",
    "district": "District A",
    "sector": "water",
    "budget": 1000000,
    "timeline_days": 90,
    "deadline": "2026-09-15",
    "status": "open",
    "required_tech": ["iot", "sensors", "analytics"],
    "application_count": 12,
    "created_at": "2026-08-27T09:00:00Z"
  }
]
```
`status` is one of `draft`, `open`, `screening`, `evaluating`, `selected`, `piloting`, `closed`.

### POST /challenges
Roles: government

```json
// request
{
  "title": "Reduce municipal water leakage",
  "raw_description": "Our pipes leak and we only find out when a road floods.",
  "department": "Urban Water Supply",
  "district": "District A",
  "sector": "water",
  "budget": 1000000,
  "timeline_days": 90,
  "deadline": "2026-09-15",
  "required_tech": ["iot", "sensors", "analytics"],
  "match_rubric_id": 1,
  "evaluation_rubric_id": 5,
  "eligibility_rules": {
    "registered_startup": true,
    "required_certification": "ISO 27001",
    "min_experience_years": 2,
    "min_technology_overlap": 1,
    "max_quote": 1000000,
    "security_baseline": true
  },
  "kpi_targets": [
    { "name": "Water wastage", "unit": "%", "baseline": 30, "target": 20,
      "category": "impact", "direction": "lower_is_better" }
  ]
}
```
```json
// 201 — full challenge object including the generated statement
{
  "id": 1,
  "title": "Reduce municipal water leakage",
  "status": "draft",
  "statement": { ...see POST /ai/generate-statement... },
  "...": "all fields from GET /challenges plus the above"
}
```

### GET /challenges/{id}
Roles: any logged in. Full object including `statement`, `eligibility_rules`,
`kpi_targets`, and both rubric ids.

### POST /ai/generate-statement
Roles: government. Called by the Create Challenge screen **before** saving, so the officer
can review the generated statement.

```json
// request
{
  "raw_description": "Our pipes leak and we only find out when a road floods.",
  "title": "Reduce municipal water leakage",
  "department": "Urban Water Supply",
  "district": "District A",
  "sector": "water",
  "budget": 1000000,
  "timeline_days": 90
}
```
```json
// 200 — exactly these 15 keys, always all 15, never a subset
{
  "problem": "...",
  "background": "...",
  "existing_system": "...",
  "identified_gap": "...",
  "desired_solution": "...",
  "target_users": "...",
  "technical_requirements": "...",
  "constraints": "...",
  "budget": "...",
  "timeline": "...",
  "expected_outcomes": "...",
  "kpis": "...",
  "eligibility_requirements": "...",
  "data_requirements": "...",
  "security_requirements": "...",
  "generated_by": "llm"
}
```
`generated_by` is `"llm"` or `"template"`. **If the LLM fails or times out at 10 seconds,
return the template version with `"template"` and a 200, never a 500.** The demo must not
depend on an API key working.

---

## 4. Startups

### GET /startups?sector=water&tech=iot
Roles: any logged in. Both params optional.

```json
// 200
[
  {
    "id": 3,
    "name": "AquaSense",
    "sector": "water",
    "technologies": ["iot", "sensors", "analytics"],
    "dpiit_number": "DIPP12345",
    "incorporation_year": 2022,
    "team_size": 8,
    "certifications": ["ISO 27001"],
    "description": "Real-time pipeline leak detection using acoustic sensors.",
    "past_projects": [
      { "name": "Nashik pipeline audit", "sector": "water", "year": 2024 }
    ]
  }
]
```

### GET /startups/{id}
Roles: any logged in. Same object, single.

---

## 5. Discovery, Screening, Matching

### POST /challenges/{id}/discover
Roles: government. No request body. Runs eligibility then matching over every startup,
persists `applications` rows, returns the ranked list.

```json
// 200 — sorted by match_score descending, ineligible last
[
  {
    "application_id": 14,
    "startup_id": 3,
    "startup_name": "AquaSense",
    "eligible": true,
    "eligibility_report": {
      "registered_startup":     { "passed": true,  "note": "DIPP12345" },
      "required_certification": { "passed": true,  "note": "ISO 27001 present" },
      "min_experience_years":   { "passed": true,  "note": "4 years, needs 2" },
      "technology_overlap":     { "passed": true,  "note": "3 of 3 matched" },
      "budget_within_range":    { "passed": true,  "note": "quote 8.5L of 10L" },
      "security_baseline":      { "passed": true,  "note": "self-declared" }
    },
    "match_score": 91.2,
    "match_breakdown": {
      "technology_match": 94.0,
      "domain_experience": 90.0,
      "past_projects": 85.0,
      "eligibility": 100.0,
      "cost_fit": 80.0,
      "scalability": 92.0
    },
    "rubric_snapshot": {
      "technology_match": 30, "domain_experience": 20, "past_projects": 15,
      "eligibility": 15, "cost_fit": 10, "scalability": 10
    },
    "explanation": "Recommended because the startup has IoT expertise, municipal infrastructure experience and two previous water-management deployments.",
    "status": "screened"
  }
]
```

**Ineligible startups are still returned**, with `eligible: false`, `match_score: 0`, and
`eligibility_report` showing which checks failed. The UI shows them greyed out with the
reason. Do not silently drop them, the transparency is the point.

### GET /challenges/{id}/applications
Roles: government, expert. Same array shape as above, read-only, no recomputation.

### POST /applications
Roles: startup. A startup applying to a challenge itself.

```json
// request
{ "challenge_id": 1, "quote": 850000, "pitch": "We propose acoustic sensors at 40 nodes." }
```
```json
// 201 — same object shape as one entry in /discover
```

### GET /applications/{id}
Roles: government, expert, and the owning startup. Same single-object shape.

### POST /applications/{id}/shortlist
Roles: government. No body. Sets `status` to `shortlisted` and makes it visible to experts.

```json
// 200
{ "application_id": 14, "status": "shortlisted" }
```

### POST /applications/{id}/select
Roles: government. No body. Marks the winner, sets every other application on that
challenge to `rejected`, sets the challenge to `selected`.

```json
// 200
{ "application_id": 14, "status": "selected", "challenge_status": "selected" }
```

---

## 6. Expert Evaluation

### POST /evaluations
Roles: expert. Weights come from the challenge's `evaluation_rubric_id`.

```json
// request — every key from the rubric, each 0 to 100
{
  "application_id": 14,
  "scores": {
    "technical_feasibility": 88,
    "innovation": 82,
    "cost_effectiveness": 90,
    "scalability": 85,
    "security": 92,
    "implementation_capability": 87,
    "social_impact": 94
  },
  "comments": "Strong municipal track record. Sensor calibration plan is thin."
}
```
```json
// 201
{
  "id": 7,
  "application_id": 14,
  "expert_id": 4,
  "expert_name": "Dr S Rao",
  "scores": { "...as sent..." },
  "weighted_total": 87.6,
  "rubric_snapshot": {
    "technical_feasibility": 25, "innovation": 15, "cost_effectiveness": 15,
    "scalability": 15, "security": 10, "implementation_capability": 10,
    "social_impact": 10
  },
  "comments": "...",
  "submitted_at": "2026-08-28T11:00:00Z"
}
```

### GET /evaluations?application_id=14
Roles: government, expert

```json
// 200
{
  "application_id": 14,
  "average_total": 88.0,
  "evaluation_count": 3,
  "evaluations": [ { ...one object as above... } ]
}
```
This is the one list endpoint that returns an object instead of a bare array, because the
average is the point.

---

## 7. Pilots

### POST /pilots
Roles: government. Creates the pilot and its milestones in one call.

```json
// request
{
  "challenge_id": 1,
  "startup_id": 3,
  "location": "District A",
  "duration_days": 90,
  "budget": 1000000,
  "objectives": "Reduce measured water loss by at least 10 percentage points.",
  "milestones": [
    { "seq": 1, "title": "Prototype",     "deliverable": "40-node sensor prototype", "amount": 200000, "due_date": "2026-09-20" },
    { "seq": 2, "title": "Field trial",   "deliverable": "Live data for 2 weeks",    "amount": 300000, "due_date": "2026-10-10" },
    { "seq": 3, "title": "Deployment",    "deliverable": "Full district coverage",   "amount": 300000, "due_date": "2026-11-01" },
    { "seq": 4, "title": "Final results", "deliverable": "Verified KPI report",      "amount": 200000, "due_date": "2026-11-25" }
  ],
  "kpis": [
    { "name": "Water wastage", "unit": "%", "baseline": 30, "target": 20,
      "category": "impact", "direction": "lower_is_better" },
    { "name": "Leak detection time", "unit": "hours", "baseline": 72, "target": 6,
      "category": "technical", "direction": "lower_is_better" },
    { "name": "System uptime", "unit": "%", "baseline": 0, "target": 95,
      "category": "technical", "direction": "higher_is_better" },
    { "name": "Cost per km monitored", "unit": "INR", "baseline": 40000, "target": 25000,
      "category": "cost", "direction": "lower_is_better" }
  ]
}
```
Milestone amounts must sum to `budget`, else `400`.

```json
// 201
{
  "id": 1,
  "challenge_id": 1,
  "startup_id": 3,
  "startup_name": "AquaSense",
  "location": "District A",
  "duration_days": 90,
  "budget": 1000000,
  "objectives": "...",
  "status": "created",
  "security_status": "pending",
  "risk_level": null,
  "milestones": [ ...see GET /pilots/{id}... ],
  "kpis": [ ...see GET /pilots/{id}/kpis... ],
  "created_at": "2026-08-28T12:00:00Z"
}
```
`status` is one of `created`, `active`, `completed`, `terminated`.

### GET /pilots/{id}
Roles: government, validator, and the owning startup. Full object including milestones,
kpis, risks, and the security checklist.

```json
// 200
{
  "id": 1,
  "challenge_id": 1,
  "challenge_title": "Reduce municipal water leakage",
  "startup_id": 3,
  "startup_name": "AquaSense",
  "location": "District A",
  "duration_days": 90,
  "budget": 1000000,
  "paid_to_date": 200000,
  "status": "active",
  "security_status": "passed",
  "risk_level": "medium",
  "milestones": [
    {
      "id": 1, "seq": 1, "title": "Prototype",
      "deliverable": "40-node sensor prototype",
      "amount": 200000, "due_date": "2026-09-20",
      "status": "paid",
      "evidence_text": "Deployed 40 nodes across zone 3.",
      "evidence_url": "https://example.com/report.pdf",
      "submitted_at": "2026-09-18T10:00:00Z",
      "validation": {
        "verdict": "approved", "claimed_value": 25, "verified_value": 22,
        "validator_name": "N Sharma", "notes": "Sampled 12 of 40 nodes.",
        "validated_at": "2026-09-19T15:00:00Z"
      },
      "payment": {
        "status": "released", "amount": 200000,
        "mock_txn_ref": "MOCK-PAY-0001",
        "released_at": "2026-09-19T16:00:00Z"
      }
    }
  ],
  "kpis": [ ... ],
  "risks": [ ... ],
  "security_checklist": { ... }
}
```
Milestone `status` is one of `pending`, `in_progress`, `submitted`, `validated`,
`rejected`, `paid`. `validation` and `payment` are `null` until they happen.

### GET /pilots (list)
Roles: government, validator, startup. Returns a summary array, no nested milestones.

```json
// 200
[
  { "id": 1, "challenge_title": "Reduce municipal water leakage",
    "startup_name": "AquaSense", "location": "District A", "status": "active",
    "budget": 1000000, "paid_to_date": 200000,
    "milestones_total": 4, "milestones_paid": 1,
    "security_status": "passed", "risk_level": "medium" }
]
```

---

## 8. Milestones, Validation, Payment

### POST /milestones/{id}/submit
Roles: the owning startup.

```json
// request
{
  "evidence_text": "40 nodes live since 14 Sep. Wastage down from 30% to 22.5%.",
  "evidence_url": "https://example.com/report.pdf",
  "claimed_value": 25
}
```
```json
// 200
{ "id": 1, "status": "submitted", "submitted_at": "2026-09-18T10:00:00Z" }
```
`evidence_url` may be `null`. `claimed_value` is the number the startup says it achieved,
and it is what the validator checks against.

### POST /milestones/{id}/validate
Roles: validator. Blocked with `403` if the caller is the pilot's startup.

```json
// request
{ "verdict": "approved", "verified_value": 22, "notes": "Sampled 12 of 40 nodes." }
```
`verdict` is `approved` or `rejected`.

```json
// 200
{
  "milestone_id": 1,
  "status": "validated",
  "validation": {
    "verdict": "approved", "claimed_value": 25, "verified_value": 22,
    "validator_name": "N Sharma", "notes": "...",
    "validated_at": "2026-09-19T15:00:00Z"
  }
}
```
A `rejected` verdict sets milestone status to `rejected`, not `validated`, and payment
stays blocked.

### POST /milestones/{id}/pay
Roles: government. `400` if the milestone is not `validated`.

```json
// 200
{
  "milestone_id": 1,
  "status": "paid",
  "payment": {
    "status": "released", "amount": 200000,
    "mock_txn_ref": "MOCK-PAY-0001",
    "released_at": "2026-09-19T16:00:00Z"
  }
}
```
```json
// 400
{ "detail": "milestone must be validated before payment" }
```

---

## 9. Governance: KPIs, Risks, Security

### GET /pilots/{id}/kpis
Roles: government, validator, owning startup.

```json
// 200
[
  {
    "id": 1, "name": "Water wastage", "unit": "%",
    "baseline": 30, "target": 20, "achieved": 17,
    "category": "impact", "direction": "lower_is_better",
    "achievement": 120.0, "met": true
  }
]
```
`achievement` is computed server-side, capped at 120. `achieved` is `null` until measured.

### POST /pilots/{id}/kpis
Roles: government. Adds or updates measured values.

```json
// request
{ "kpi_id": 1, "achieved": 17 }
```
Returns the updated KPI object.

### GET /pilots/{id}/risks
```json
// 200
[
  { "id": 1, "description": "Sensor failure in monsoon", "probability": 3, "impact": 4,
    "score": 12, "mitigation": "Ship 10% spare nodes", "owner": "AquaSense" }
]
```
`probability` and `impact` are 1 to 5. `score` is their product, computed server-side.

### POST /pilots/{id}/risks
Roles: government.
```json
// request
{ "description": "Sensor failure in monsoon", "probability": 3, "impact": 4,
  "mitigation": "Ship 10% spare nodes", "owner": "AquaSense" }
```

### POST /pilots/{id}/security-check
Roles: government.

```json
// request
{
  "authentication": true, "authorization": true, "data_encryption": true,
  "secure_api": true, "data_backup": true, "vulnerability_assessment": true,
  "access_logging": true, "incident_response_plan": false
}
```
```json
// 200
{
  "pilot_id": 1,
  "security_status": "needs_remediation",
  "score": 87.5,
  "passed_count": 7,
  "total_count": 8,
  "failed": ["incident_response_plan"]
}
```
`security_status` is `passed` (all 8) or `needs_remediation` (any false).

---

## 10. Final Decision, Procurement, Replication

### POST /pilots/{id}/finalize
Roles: government. No body. Computes the final score from KPIs plus the security score.

```json
// 200
{
  "pilot_id": 1,
  "category_scores": {
    "technical": 79.0, "cost": 87.0, "impact": 120.0,
    "scalability": 89.0, "security": 96.0
  },
  "weights": {
    "technical": 30, "cost": 20, "impact": 20, "scalability": 15, "security": 15
  },
  "final_score": 92.9,
  "decision": "scale",
  "justification": "Exceeded impact target by 30 percent, security cleared, all four milestones validated."
}
```
`decision` is `scale`, `scale_with_modifications`, `extend_pilot`, or `reject`.
Thresholds are hardcoded: 85 / 70 / 55.

### GET /pilots/{id}/procurement
Roles: government.

```json
// 200
{
  "pilot_id": 1,
  "final_score": 92.9,
  "decision": "scale",
  "checks": {
    "pilot_validated": true, "performance_threshold_met": true,
    "security_approved": true, "budget_available": true
  },
  "recommended_pathway": "GeM direct procurement",
  "justification": "...",
  "replication": [
    { "district": "District A", "status": "completed" },
    { "district": "District B", "status": "planned" }
  ]
}
```

### POST /pilots/{id}/replicate
Roles: government.
```json
// request
{ "districts": ["District B", "District C"] }
```
```json
// 200
{ "pilot_id": 1, "replication": [
  { "district": "District A", "status": "completed" },
  { "district": "District B", "status": "in_progress" },
  { "district": "District C", "status": "planned" }
] }
```
`status` is `planned`, `in_progress`, or `completed`.

---

## 11. Documents

### GET /documents/{doc_type}/{entity_id}
Roles: any logged in with access to the entity. Returns **rendered HTML**, not JSON.
`Content-Type: text/html`. Pair B shows it in an `<iframe>` with a print button.

```
doc_type ∈
  problem_statement          entity = challenge id
  eligibility_criteria       entity = challenge id
  evaluation_criteria        entity = challenge id
  pilot_agreement            entity = pilot id
  milestone_contract         entity = pilot id
  data_ip                    entity = pilot id
  security_checklist         entity = pilot id
  risk_register              entity = pilot id
  kpi_report                 entity = pilot id
  validation_report          entity = milestone id
  payment_approval           entity = milestone id
  procurement_recommendation entity = pilot id
  scale_up_decision          entity = pilot id
```

### GET /documents/templates
Roles: any logged in. Powers the Template Library page.

```json
// 200
[
  { "doc_type": "pilot_agreement", "title": "Pilot Agreement",
    "description": "16-clause agreement covering scope, IP, data, security and termination.",
    "entity": "pilot" }
]
```

---

## 12. Frozen rubric criteria keys

Do not rename these after Day 0. They appear in `seed_data/rubrics.json`, the engines, the
database, and the React forms.

**kind `match`** — 6 keys, must sum to 100
```
technology_match
domain_experience
past_projects
eligibility
cost_fit
scalability
```

**kind `evaluation`** — 7 keys, must sum to 100
```
technical_feasibility
innovation
cost_effectiveness
scalability
security
implementation_capability
social_impact
```

Rules:
- `snake_case`, lowercase, no spaces
- these are **IDs, not labels**. Display text lives in `criteria[].label`.
- adding a criterion means a **new rubric row**, never a rename of an existing key
- `scalability` appears in both lists deliberately. They are separate rubrics. Do not
  "deduplicate" it.

---

## 13. Seeded demo accounts

Password for all of them: `demo1234`

| Email | Role | Name |
|---|---|---|
| officer@water.gov.in | government | R Kumar |
| admin@procura.gov.in | admin | Platform Admin |
| founder@aquasense.in | startup | AquaSense (startup id 3) |
| expert1@procura.gov.in | expert | Dr S Rao |
| expert2@procura.gov.in | expert | Prof M Iyer |
| expert3@procura.gov.in | expert | Dr A Banerjee |
| validator@procura.gov.in | validator | N Sharma |

The Login screen's role selector prefills these so the demo needs no typing.

---

## 14. Using this file with AI

This file is what keeps six separate AI sessions from inventing six different field names.

When you ask an AI for code that touches the API, **paste the relevant section of this file
into the prompt** and tell it to match exactly. Otherwise it will confidently invent
`matchScore` instead of `match_score` and you will spend an hour on a bug that was never
in the code.

- Ayushrai was here
saket was here

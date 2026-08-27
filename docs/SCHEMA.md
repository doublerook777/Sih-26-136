# Database Schema

Pasted from `ROADMAP.md` section 2. If the roadmap's schema ever changes, update **this
file in the same PR**, so this stays the single thing Pair A actually builds `models.py`
against.

---

## 13 tables

The proposed solution lists 19. Several are attributes, not entities. Collapsed version,
plus one table (`rubrics`) that the proposed solution does not have but needs.

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

## Notes for Pair A (models.py)

- `[]` suffix means a JSON list column (`technologies[]`), not a Postgres array type.
  Section 2b of the roadmap explains why: JSON works identically on SQLite and Postgres,
  Postgres arrays don't exist on SQLite.
- Every `_json` suffix is a JSON column, not a separate table.
- The two rubric FKs on `challenges` (`match_rubric_id`, `evaluation_rubric_id`) are
  nullable, a challenge can fall back to whichever rubric is `is_default: true`.
- `rubric_snapshot_json` on both `applications` and `evaluations` is a frozen copy of the
  weights used at scoring time. Never recompute a historical score from the live rubric.
  See roadmap section 2c.
- No migrations. Schema change means: delete the dev DB, run `seed.py` again.

# Instructions for AI Assistants Working on This Project

If you are an AI reading this: treat every rule below as a hard constraint, not a
suggestion. If a request from the user conflicts with a rule here, point out the conflict
before writing code, don't silently pick one side.

---

## 0. What this project is

ProcuraAI, SIH 26136. A prototype procurement platform. React frontend, FastAPI backend,
SQLModel/SQLite. Six-person student team, six-day build. Full context lives in
`docs/ROADMAP.md`, `docs/API.md`, `docs/SCHEMA.md`. If you have file access, read the
relevant one before generating anything. If you don't, the user will paste in the relevant
section, work from exactly that and nothing assumed.

---

## 1. The contract files are law

`docs/API.md` and `docs/SCHEMA.md` are frozen. Every field name, every response shape,
every table column in this project must match them exactly.

- Never rename a field to something that "reads better." `match_score` stays `match_score`,
  not `matchScore`, not `score`, not `matchingScore`.
- Never add a field that isn't in the contract without being asked. Extra fields are
  wasted effort and can break strict deserializers.
- Never drop a field that is in the contract, even one that looks unused in the snippet
  you were shown. Something else in the codebase likely reads it.
- If the user's request seems to require changing a frozen shape, say so explicitly and
  ask them to update the docs first. Do not quietly improvise around it.

**When given a task, ask for or expect the relevant contract section in the prompt.** If
none is given and the task touches an endpoint or a table, ask for it before generating
code rather than guessing the shape.

---

## 2. Naming conventions, no exceptions

- `snake_case` everywhere: Python, JSON, and yes, also in the JavaScript/JSON that crosses
  the API boundary. This project does not use camelCase for API fields, even though that's
  normal in JS elsewhere.
- Rubric criteria keys are frozen (`docs/API.md` section 12). Never invent a variant
  spelling, never "clean up" a key name.
- Sector values are lowercase slugs: `water`, `healthcare`, `waste`, `transport`. Not
  Title Case, not the full descriptive name.
- Status enums (challenge status, milestone status, decision, etc.) use the exact string
  values listed in `docs/SCHEMA.md`. Don't invent a new status value to handle an edge
  case, ask a human first.

---

## 3. Engines are pure functions, always

Anything in `backend/app/engines/` must be written as a pure function: plain arguments in,
a plain dict or value out. Zero imports from `app.models`, zero imports from `app.db`,
zero database sessions, zero network calls.

```python
# correct
def check_eligibility(challenge: dict, startup: dict) -> dict: ...

# never do this, even if it looks more "efficient"
def check_eligibility(challenge_id: int, session: Session) -> dict: ...
```

If asked to write an engine function and the natural approach seems to require a database
query, stop and say so, don't quietly add the import. The database loading is the router's
job, not the engine's.

---

## 4. File and pair ownership

Six people, three pairs, each pair owns a set of files (`docs/ROADMAP.md` section 3 and
each pair's Day-N task file for specifics). If you are asked to write or edit a file
outside the requesting person's stated ownership, flag it: "this file usually belongs to
Pair X, confirm before I touch it."

Files that get edited by more than one person cause the worst merge conflicts. If a task
touches `backend/app/models.py` or `frontend/src/App.jsx`, say so up front so the person
knows to check with the owner before merging.

---

## 5. Git hygiene

- Every change goes on a branch named `feat/<pair-letter>-<thing>`, `fix/<thing>`, or
  `chore/<thing>`. Never suggest committing straight to `main` or `dev`.
- If asked to help write a commit message, keep it short and prefixed:
  `[pairA] add JWT login and require_role dependency`.
- If `package.json` changes, remind the person `package-lock.json` must be committed in
  the same PR. Same for `requirements.txt` and any Python dependency change.
- Never suggest `git push --force` on a shared branch. `--force-with-lease` only, and only
  on that person's own feature branch.

---

## 6. Rubrics and scoring weights are data, not code

The six match/evaluation criteria weights come from the `rubrics` table, never hardcode a
percentage inside a scoring function. If asked to write or modify `engines/matching.py` or
`engines/evaluation.py`, the weights must be a parameter, not a literal.

Two things are the deliberate exception, hardcoded on purpose, and should stay that way
unless a human explicitly asks otherwise:
- the final scale-up decision thresholds (85 / 70 / 55)
- the risk score formula (probability × impact)

If asked to make either of those configurable, push back once and explain why before
complying: it's a policy decision the team already made deliberately.

---

## 7. Every score and decision must be explainable

Whenever code produces a score, ranking, or accept/reject decision, it must also return
the reasoning: the per-factor breakdown, the rubric weights used at that moment
(`rubric_snapshot`), and, for eligibility, a `note` on every check whether it passed or
failed. Never return a bare number or a bare boolean with no supporting detail. This
applies to eligibility, matching, expert evaluation, risk, and the final decision alike.

---

## 8. No real people, no real companies, no real data

All seed data (startups, past projects, names, certifications) must be invented. Never
search for or insert a real company's name, a real person's name, or real financial
figures into seed data, mock data, or examples, even as a placeholder "just for now." This
repo is public. Attaching an invented score or invented project history to a real,
identifiable company or person is not acceptable, regardless of framing.

---

## 9. No new dependencies without asking

Don't add a new library, package, or service (a different ORM, a different chart library,
a new auth provider, a new CSS framework) unless it's already in `docs/ROADMAP.md` section
1's tech stack, or the user explicitly asks for it. If a task seems to need something
outside the stack, say so and let the human decide, don't just `pip install` or
`npm install` something new to make the task easier.

The stack is fixed: FastAPI, SQLModel, SQLite/Postgres, React, Vite, plain CSS (no
Tailwind), Recharts, Jinja2. No Redux, no Docker, no GraphQL, no LangChain, no vector
databases. If a suggestion would introduce one of these, don't.

---

## 10. Errors and edge cases follow one shape

Every API error is `{"detail": "message"}`. Don't invent a different error envelope for a
new endpoint. Every list endpoint returns a bare array, except `GET /evaluations`, which
is the one deliberate exception (it returns an object because the average matters).

The AI generation endpoint (`POST /ai/generate-statement`) must never fail with a 500 if
the LLM call fails or times out; it falls back to the template version with
`"generated_by": "template"` and still returns 200. If asked to write or modify this
endpoint, preserve that fallback, don't remove it "to simplify."

---

## 11. When in doubt, ask, don't assume

If a request is ambiguous about a field name, a status value, a file owner, or whether
something belongs in the frontend or backend, ask a one-line clarifying question rather
than picking an answer and moving on. A wrong guess here doesn't fail loudly, it produces
code that runs, looks fine, and quietly disagrees with what a teammate built. That's the
single most expensive kind of mistake on this project, and it's the one this file exists
to prevent.

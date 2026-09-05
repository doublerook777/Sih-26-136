# Git Workflow

Quick reference for how we use git on this project. For full explanations of every
command and why each rule exists, see `docs/GIT_GUIDE.md`. This file is the short version
to keep open while you work.

---

## Branches

```
main                  tagged working states only, protected, PR + 1 approval required
 └── dev              everyone's work lands here
      ├── feat/a-*    Pair A (core platform)
      ├── feat/b-*    Pair B (frontend)
      ├── feat/c-*    Pair C (intelligence & governance)
      ├── fix/*       bug fixes
      └── chore/*     config, docs, tooling
```

Never push directly to `main` or `dev`. Every change goes through a branch and a PR.

---

## File ownership

| Pair | Owns |
|---|---|
| A | `backend/app/models.py`, `db.py`, `auth.py`, `seed.py`, `routers/*` |
| B | everything under `frontend/` |
| C | `backend/app/engines/*`, `ai/*`, `templates/*`, `tests/*`, `seed_data/*` |

If you need a change in a file another pair owns, message them. Don't edit it yourself.
`models.py`, `App.jsx`, and `main.py` are the three files everyone wants to touch, hence
the rule.

---

## Daily loop

```bash
git checkout dev
git pull
git checkout -b feat/a-<thing>

# work, commit hourly
git add -A
git commit -m "[pairA] <what changed>"

git push -u origin feat/a-<thing>     # -u only on the branch's first push

gh pr create --base dev --fill
# add a reviewer from a DIFFERENT pair, get approved
gh pr merge --squash --delete-branch

git checkout dev && git pull          # back to the top for the next task
```

Pull `dev` every morning before branching. A stale branch is where conflicts come from.

---

## Pull requests

- **Base is always `dev`**, never `main`.
- **Reviewer is from a different pair.** Three minutes, checking one thing: does this
  break what I built.
- **Squash merge only.** Your branch's messy commits become one clean commit on `dev`.
- **Delete the branch after merge.** GitHub does this automatically once you merge.

---

## Conflicts

```bash
git checkout dev && git pull
git checkout <your-branch>
git rebase dev
# resolve markers by hand, keep the correct final version
git add <file>
git rebase --continue
git push --force-with-lease        # never plain --force
```

Stuck or made it worse? `git rebase --abort` puts you back exactly where you started.
Nothing is lost.

---

## Nightly tag

One person, once a day, after confirming the demo path still runs:

```bash
git checkout dev && git pull
git tag -a demo-day3 -m "day 3 working state"
git push origin --tags
```

This is the fallback if a later day breaks something: `git checkout demo-dayN` gets back
to a known-good state instantly.

---

## Before committing, check

- [ ] `package.json` and `package-lock.json` changed together, same commit, if either
      changed at all
- [ ] `.env` is never committed, only `.env.example`
- [ ] No `node_modules`, no `__pycache__`, no `.db` files in `git status`
- [ ] Commit message is prefixed: `[pairA]`, `[pairB]`, `[pairC]`, `[chore]`, or `[test]`

---

## The six rules

1. Never push directly to `main` or `dev`.
2. Pull `dev` every morning before branching.
3. Respect the file ownership table. Message, don't edit.
4. One feature, one branch, one PR.
5. Reviewer comes from a different pair.
6. Push before you sleep. Unpushed work only exists on one laptop.

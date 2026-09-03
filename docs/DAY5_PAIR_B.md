# Day 5 — Pair B checkpoint status

- [x] 1. Wire the Day 5 lifecycle endpoints with mock-mode branches.
- [x] 2. Add startup milestone evidence submission with an explicitly unverified claimed value.
- [x] 3. Add the validator queue with claimed-versus-verified comparison and approve/reject actions.
- [x] 4. Gate government milestone payments on validation and display the mock transaction reference.
- [x] 5. Add direction-aware KPI charts for baseline, target, and achieved values.
- [x] 6. Add the explainable scale-up decision with weighted category scores and justification.
- [x] 7. Add district replication planning while preserving existing rollout rows.
- [x] 8. Add the document-template and rubric libraries.
- [ ] 9. Deploy and run the timed integration check on the deployed URLs. **Deferred to tomorrow morning before the bug bash.** Tonight's equivalent check runs on localhost with `VITE_USE_MOCK` unchanged; deployed-environment confidence is intentionally not claimed.

## Local integration note

For tonight, `VITE_API_URL` may continue to point to localhost. Do not change deployment configuration. The end-to-end workflow is timed locally against the existing mock configuration, with the same six-minute limit used for the integration check.

- Local result: **27.1 seconds**, passed, with zero browser console errors.
- Covered sequence: startup evidence submission → validator approval → validated milestone payment → pilot finalization → district replication → template library.
- Deferred confidence: the same sequence has not yet been verified on deployed frontend/backend URLs.

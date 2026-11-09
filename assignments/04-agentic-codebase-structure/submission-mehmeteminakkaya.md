# Week 4 Agentic Codebase Structure Submission: Mehmet Emin Akkaya

Repository: https://github.com/mehmeteminakkaya/week4-link-shortener

- `AGENTS.md` (43 lines): what the service does, file map, install/run/test commands, product
  boundaries, conventions, and the understand → test → implement → verify loop. `CLAUDE.md`
  imports it (`@AGENTS.md`) for Claude Code.
- Scoped instruction: `.claude/rules/testing.md`, a path-filtered rule (`test_*.py`,
  `**/test_*.py`, `conftest.py`) that applies only when working on test files.
- Reusable workflow: `.claude/skills/add-feature/SKILL.md` (7 steps, test-first).
- Feature: task 2, click counter (`GET /stats/{code}`), with 7 new tests; 10 tests pass in total.
  Plan and review are recorded in `docs/plan.md` and `docs/review.md`.

Planning found that the existing `links.db` has no `clicks` column and that
`CREATE TABLE IF NOT EXISTS` would not add it, so `init_db()` upgrades old databases (covered by a
test). The review returned REVISE (a misleading test name and a rule that contradicted the
migration test); both were fixed. A stress test of 100 requests over 20 threads produced exactly
100 clicks.

Limits, stated in the writeup: plan and review were separate read-only passes by the same agent
in one session, not an independent reviewer, and I did not observe the rule auto-loading.
Details are in
[writeup.md](https://github.com/mehmeteminakkaya/week4-link-shortener/blob/main/writeup.md).

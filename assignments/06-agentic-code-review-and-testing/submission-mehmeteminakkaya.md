# Week 6 AI Code Review and Testing Submission: Mehmet Emin Akkaya

Repository: https://github.com/mehmeteminakkaya/week6-habit-tracker
Writeup: https://github.com/mehmeteminakkaya/week6-habit-tracker/blob/main/writeup.md

- **Guardrails:** `black --check`, `ruff check` (E/F/I/B/UP/SIM) and `pytest`, all wired into
  `.github/workflows/ci.yml` so a red check appears on the PR. `make check` runs the same
  three locally; `docs/guardrails.md` shows a failing test exiting 1. Added per-test SQLite
  isolation (`conftest.py`), which the starter lacked.
- **Two feature PRs, both merged:** [#1](https://github.com/mehmeteminakkaya/week6-habit-tracker/pull/1)
  streak (`GET /habits/{id}/streak`) and
  [#2](https://github.com/mehmeteminakkaya/week6-habit-tracker/pull/2) weekly summary
  (`GET /habits/{id}/summary`). 20 tests pass on `main`.
- **Manual review before the AI:** each branch has the feature commit plus a review-driven
  fix commit. My line-by-line pass found two blocking defects per PR — an unknown habit
  returned `200` with an empty result, and one unparsable `day` row returned 500 — reproduced
  with tests that failed before the fix, plus the untested edge cases (window boundary, gap,
  missing today, duplicate day). Notes: `docs/reviews/feature-1-streak.md`,
  `docs/reviews/feature-2-summary.md`.
- **AI review:** CodeRabbit was not installed on the repository, so an independent AI reviewer
  pass was used instead (a separate agent given only the diff, the app and `docs/TASKS.md`,
  blind to my review notes). Its findings are posted verbatim on both PRs with an author
  triage table ([#1](https://github.com/mehmeteminakkaya/week6-habit-tracker/pull/1#issuecomment-6977503377),
  [#2](https://github.com/mehmeteminakkaya/week6-habit-tracker/pull/2#issuecomment-6977503837)).
- **Human vs AI comparison (the interesting part):** the human pass found the actual bugs; the
  AI pass was better at adversarial verification. It **falsified a claim in my own PR
  description** — that the two branches merge without conflicts — by actually merging them
  (three conflicts in `main.py`), and it found a cross-habit leak that no test covered by
  deleting `WHERE habit_id = ?` and watching the suite stay green. Both gaps are fixed in the
  merged history. The comparison table per PR is in `writeup.md`.

# Week 6 Submission: Efeblk

- **Repository:** https://github.com/Efeblk/week6-habit-tracker
- **Writeup:** https://github.com/Efeblk/week6-habit-tracker/blob/main/writeup.md
- **Agent used for implementation:** Antigravity (Gemini 4 Argon High)
- **AI PR reviewer used:** CodeRabbit

## Deliverables
- **Part I — Deterministic guardrails:** `ruff check .`, `black --check .`, and `pytest` configured in `pyproject.toml`, `requirements-dev.txt`, and `.github/workflows/ci.yml` (commit `e187779`), running on every push and pull request.
- **Part II — Two features with manual + CodeRabbit review:**
  - **PR #1 (`feature/streak`):** https://github.com/Efeblk/week6-habit-tracker/pull/1 — adds `GET /habits/{id}/streak`, with manual review fixing midnight `date.today()` flakiness and adding month-boundary, today-only, missing-today, future-checkin, and empty-habit tests (9 tests passing).
  - **PR #2 (`feature/validation`):** https://github.com/Efeblk/week6-habit-tracker/pull/2 — validates habit names (trim + non-empty) and strict `YYYY-MM-DD` check-in dates, with manual review adding trimming tests, parametrized malformed date cases (`2026-W39-2`, `2026-9-22`, leading space), leap-day coverage, and a shared error message constant (17 tests passing).
  - **Comparison PRs (agent-only commits reviewed by CodeRabbit before manual review fixes, now closed):**
    - PR #3: https://github.com/Efeblk/week6-habit-tracker/pull/3
    - PR #4: https://github.com/Efeblk/week6-habit-tracker/pull/4
- **Comparison & reflection:** Documented in `writeup.md` on `main`.
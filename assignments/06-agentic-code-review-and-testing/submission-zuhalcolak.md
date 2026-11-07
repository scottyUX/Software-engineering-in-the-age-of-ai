# Week 6 Submission (AI Code Review & Testing) - Zuhal Çolak

**Repository:** https://github.com/zuhalcolak/habit-tracker-ai-review  
**Writeup:** [`writeup.md`](https://github.com/zuhalcolak/habit-tracker-ai-review/blob/main/writeup.md)

### Feature Pull Requests:
- **PR #1 (Task 2: Input Validation):** https://github.com/zuhalcolak/habit-tracker-ai-review/pull/1
- **PR #2 (Task 1: Habit Streak):** https://github.com/zuhalcolak/habit-tracker-ai-review/pull/2

### Overview of Completed Work:
- **Part I — Deterministic Guardrails:** Configured `black` for formatting, `ruff` for linting, and `pytest` for automated test execution, unified in `check.sh` and configured via `pyproject.toml`. Confirmed that failing tests halt the build.
- **Part II — Two Features:**
  - Implemented **Input Validation** (Pydantic validators for non-empty/printable habit names and strict ISO calendar dates) and **Habit Streak** (`GET /habits/{id}/streak` with 404 handling, deduplication, and consecutive day momentum) on separate feature branches.
  - Performed manual line-by-line review of agent-generated code, catching zero-width whitespace vulnerabilities, loose ISO format parsing, missing 404s, and morning streak preservation.
  - Opened PRs with comprehensive descriptions, problem statements, trade-offs, and commit links.
  - Ran AI code review (CodeRabbit) on both PRs.
- **Part III — Human vs. AI Review Comparison & Reflection:**
  - Documented specific areas where human review excelled (business logic, security subtleties, REST consistency) vs. where AI review excelled (FastAPI error payload conventions, parameter falsiness, timezone boundaries).
  - Provided a closing reflection on combining deterministic guardrails with AI reviewers.
- **Test Results:** 11/11 tests passing (`pytest`) and all guardrails green (`black --check .`, `ruff check .`).

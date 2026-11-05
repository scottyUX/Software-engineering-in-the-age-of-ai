# Week 6 Submission (AI Code Review & Testing): Kaan Erk Toraman (220901564)

- **Student Name**: Kaan Erk Toraman
- **Student ID**: 220901564
- **Student Email**: 220901564@stu.istinye.edu.tr
- **Repository**: https://github.com/kaan-erk/week6-habit-tracker

### Highlights
- **Deterministic Guardrails**: Configured Black, Ruff, and Pytest automated via `scripts/check.sh`, `scripts/check.bat`, and GitHub Actions CI (`.github/workflows/ci.yml`). Demonstrated that failing tests halt the build on branch `demo/failing-guardrails` and documented in `docs/evidence/guardrails.txt`.
- **Feature PR #1 (Streak)**: [PR #1](https://github.com/kaan-erk/week6-habit-tracker/pull/1) (`GET /habits/{id}/streak`). Features client-supplied `today` query parameter for timezone independence and deterministic testing, `StreakOut` Pydantic response model, and edge-case tests (year boundaries, gaps, duplicates). Visible AI review comment included.
- **Feature PR #2 (Validation)**: [PR #2](https://github.com/kaan-erk/week6-habit-tracker/pull/2) (`POST /habits` & checkin validation). Enforces strict `\A[0-9]{4}-[0-9]{2}-[0-9]{2}\Z` ASCII regex to block Python 3.11+ ISO parser loopholes and newline injection, sanitizes zero-width invisible Unicode characters (`\u200b`, `\ufeff`), adheres to Ruff TRY004 (`TypeError`), and includes 30 parametrized tests ensuring DB immutability on 422 errors. Visible AI review comment included.
- **AI Code Reviewer**: Evaluated using an independent agentic reviewer (Gemini 3.8 Flash High) that analyzed the diffs statically, comparing findings with line-by-line manual reviews.
- **Comprehensive Writeup**: Detailed comparison tables and reflection on pairing deterministic guardrails with LLM code reviews available at [writeup.md](https://github.com/kaan-erk/week6-habit-tracker/blob/main/writeup.md).

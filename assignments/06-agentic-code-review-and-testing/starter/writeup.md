# Week 6 Writeup: Agentic Code Review and Testing

## 1. Pull Requests
- **PR #1 (Streak Feature):** Implemented `GET /habits/{id}/streak` endpoint and unit tests.
- **PR #2 (Input Validation Feature):** Implemented Pydantic schema validation for empty habit names and invalid `day` date strings, along with status code 422 unit tests.

## 2. Guardrails Setup
- **Linters & Formatters Installed:** `black` and `ruff`.
- **Commands Used:**
  - `black .` / `black --check .` — Ensures consistent Python code formatting.
  - `ruff check .` / `ruff check --fix .` — Catches unused imports, unsorted import blocks (I001), syntax errors, and code smells.
  - `pytest` — Verifies endpoint correctness and status codes.
- **What Guardrails Caught:**
  - `black` caught non-standard whitespace formatting across route definitions.
  - `ruff` caught unsorted standard library vs. third-party import blocks in `main.py`.
  - `pytest` verified 404/422 status codes and correct streak integer calculations before committing.

## 3. Human vs. AI Review Comparison
- **PR #1 (Streak Endpoint):**
  - **Human Review:** Flagged edge cases where non-consecutive dates or missing check-ins could skew streak calculations, and ensured `timedelta` logic correctly identified today vs. yesterday starts.
  - **AI Review (CodeRabbit):** CodeRabbit flagged free OSS review rate limits (`Review limit reached`) on submission, but identified clean PR structural diffs and base branch cleanliness.
- **PR #2 (Input Validation):**
  - **Human Review:** Specifically verified Pydantic `field_validator` execution to ensure empty whitespace strings (`"   "`) and invalid date formats return `HTTP 422` instead of causing unhandled 500 server errors.
  - **AI Review:** AI tools excel at quick pattern matching and surface-level lint checks, whereas human manual review was crucial for verifying actual business logic expectations (e.g., proper HTTP status code choices like 422 vs 400).

## 4. Learnings & Reflection
Combining deterministic guardrails (`black`, `ruff`, `pytest`) with LLM-based review creates a robust two-layer defense for software quality. Guardrails act as instant, non-negotiable filters for syntax, formatting, and regressions, freeing human and AI reviewers to focus on architecture and edge cases. While AI reviewers provide rapid automated feedback, human oversight remains necessary to validate business requirements and verify that edge cases are thoroughly tested.

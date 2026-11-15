# Week 6 — Writeup: AI Code Review & Testing (The Habit Tracker)

## 1. Overview & Guardrail Setup
In this assignment, we established a deterministic multi-layer guardrail defense and implemented two core features (**Validation** and **Streak Calculation**) for the Habit Tracker microservice.

### Deterministic Guardrail Commands
- **Formatting:** `black --check .` (ensures PEP 8 compliant AST formatting).
- **Linting:** `ruff check .` (enforces strict import order, unused symbols, and code health).
- **Unit & Integration Tests:** `pytest -q` (ensures 100% test suite pass rate).
- **Unified Guardrail Hook:** `guardrail.sh` chains all three tools sequentially and **blocks execution** if any tool fails.

---

## 2. Implemented Features & Test Coverage

### Feature 1: Input Validation (`POST /habits` & `POST /habits/{id}/checkin`)
- **Problem:** Habit names could be blank or pure whitespace; check-in `day` values accepted arbitrary strings without validating ISO `YYYY-MM-DD` formatting.
- **Approach:** Stripped habit names and rejected empty inputs with `400 Bad Request`. Parsed incoming `day` strings via `datetime.strptime(..., "%Y-%m-%d")` and returned clean `400` status on malformed values. Added `INSERT OR IGNORE` to prevent duplicate check-ins on the same calendar day.
- **Tests Added:** `test_validation_rejects_empty_habit_name`, `test_validation_rejects_malformed_day_checkin`.

### Feature 2: Streak Calculation (`GET /habits/{id}/streak`)
- **Problem:** Users had no endpoint to calculate current consecutive check-in days.
- **Approach:** Fetched distinct check-in dates ordered descending. Evaluated consecutive unbroken calendar day sequences relative to `today` (or `today - 1 day` if today is not yet checked in). Returns `{"habit_id": id, "streak": count}`.
- **Tests Added:** `test_streak_calculation`, `test_streak_unknown_habit_404`.

---

## 3. Human Review vs. AI Review Comparison

For this review cycle, we evaluated the implemented features using a **Line-by-Line Manual Human Review** contrasted against an **AI PR Reviewer (Graphite Diamond / CodeRabbit heuristic model)**.

### Comparison Table

| Review Dimension | Human Review (Manual) | AI PR Reviewer (Automated) |
|---|---|---|
| **Syntax & Formatting** | Relied on automated linter (`black`/`ruff`); manual review focused on readability. | Immediately flagged minor PEP 8 spacing and import grouping nuances. |
| **Edge Cases & Date Math** | Caught the critical calendar edge case: if a user checks their streak at 8:00 AM before today's check-in, yesterday's streak must still be counted rather than resetting to 0. | Suggested verifying timezone handling (`datetime.now(timezone.utc)` vs `date.today()`). |
| **SQL Idempotency** | Identified potential duplicate check-ins for the same day and added `INSERT OR IGNORE`. | Recommended adding a database-level `UNIQUE(habit_id, day)` constraint in `init_db()`. |
| **False Positives** | Low; understood domain context and deliberate in-memory SQLite scope. | Occasionally suggested heavy production ORMs (SQLAlchemy) outside the lightweight assignment scope. |

### Where the AI Reviewer Was Better:
- **Consistent Boundary Checks:** Reminded us of internationalization/timezone drift when using `date.today()`.
- **Database Schema Rigor:** Pointed out that relying purely on application-level `INSERT OR IGNORE` without a formal database unique index leaves room for concurrency race conditions.

### Where the Human Review Was Better:
- **Pragmatic Scope Control:** The human reviewer understood the university course constraints (keeping the starter app simple and zero-dependency) without over-engineering external dependencies.
- **User Intent & UX:** The human reviewer correctly structured the streak logic so users don't lose their streak at midnight before having a chance to check in during the new day.

---

## 4. What I Learned (Combining Guardrails with LLM Review)
Deterministic guardrails (Ruff, Black, Pytest) and LLM-based code reviews fulfill complementary roles in modern agentic software engineering. Linters and automated tests provide non-negotiable binary guarantees: code must parse, style must be uniform, and assertions must hold. However, guardrails cannot reason about semantic edge cases, such as whether a habit streak should lapse immediately at midnight. LLM reviewers excel at identifying architectural omissions, timezone ambiguities, and schema risks, but they require human judgment to filter out out-of-scope suggestions. Combining fast automated guardrails with thoughtful AI-assisted review produces a resilient engineering loop where humans focus on intent and correctness while machines handle mechanics and edge-case discovery.

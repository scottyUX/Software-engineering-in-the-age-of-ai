# Week 6 Writeup — AI Code Review & Testing: The Habit Tracker

**Student:** Zuhal Çolak  
**Repository:** https://github.com/zuhalcolak/habit-tracker-ai-review  
**AI Reviewer:** CodeRabbit  
**Deterministic Guardrails:** `black`, `ruff`, `pytest`  
**Test Suite:** 11/11 tests passing (`pytest`)  

---

## 1. Feature Pull Requests

Two distinct feature pull requests were developed, manually reviewed, and submitted on the public Habit Tracker repository:

| PR | Feature | Branch | Pull Request Link | Status |
|:---|:---|:---|:---|:---|
| **PR #1** | **Task 2: Input Validation** | `feature/validation` | [PR #1: feat(validation)](https://github.com/zuhalcolak/habit-tracker-ai-review/pull/1) | **Merged / Verified** |
| **PR #2** | **Task 1: Habit Streak** | `feature/streak` | [PR #2: feat(streak)](https://github.com/zuhalcolak/habit-tracker-ai-review/pull/2) | **Merged / Verified** |

---

## 2. Part I — Deterministic Guardrails Setup

Deterministic guardrails serve as the automated first line of defense before human or AI code review takes place.

### Guardrail Tools & Commands

```bash
# 1. Format Verification (Black)
black --check .

# 2. Linter & Static Analysis (Ruff)
ruff check .

# 3. Automated Test Suite (Pytest)
pytest

# All-in-one guardrail execution script
chmod +x check.sh
./check.sh
```

### What Each Guardrail Catches
1. **Black (`black --check .`)**: Enforces deterministic code layout, quotes, trailing commas, line wrapping (88 chars), and AST consistency without changing semantic meaning. Prevents formatting debates in code reviews.
2. **Ruff (`ruff check .`)**: Fast static analysis checking imports (`I001`), unused variables (`F841`), undefined names (`F821`), syntax traps, and PEP8 conformance. Caught unused variables (`ref`) and unsorted import blocks during development.
3. **Pytest (`pytest`)**: Executes unit and integration tests. I intentionally validated that a failing test immediately halts the build with exit code 1, ensuring regressions never slip into production unnoticed.
4. **Configuration (`pyproject.toml`)**: Centralized tool settings for Black line lengths, Ruff lint rules (`E`, `F`, `W`, `I`), and Pytest discovery paths.

---

## 3. Part II — Feature Reviews & Human vs. AI Comparison

### PR #1 — Input Validation (`feature/validation`)
- **Problem:** `POST /habits` accepted blank habit names, and `POST /habits/{id}/checkin` allowed arbitrary text as check-in dates, corrupting the database.
- **Approach:** Pydantic `@field_validator` on `HabitIn` and `CheckinIn` returning HTTP 422 with clear error messages.
- **Commits:**
  - One-shot implementation: [`e05c2ea`](https://github.com/zuhalcolak/habit-tracker-ai-review/commit/e05c2ea)
  - Review fixes & tests: [`7c0d20a`](https://github.com/zuhalcolak/habit-tracker-ai-review/commit/7c0d20a)

#### Human Review vs. AI Review (CodeRabbit) on PR #1
- **Where Human Review was Superior:**
  - *Invisible Unicode:* The agent's initial prompt used `.strip()`. My manual line-by-line review caught that `.strip()` fails on zero-width space characters (`\u200b`, `\u200e`) and control characters, which would still be saved in SQLite. I added `any(c.isprintable() and not c.isspace() for c in v)`.
  - *Strict Format Enforcement:* Python 3.11's `date.fromisoformat()` is permissive and accepts `20260922` or `2026-W39-2`. Human review mandated enforcing strict 10-character `YYYY-MM-DD` round-tripping.
- **Where AI Review was Superior:**
  - *Error Message UX & Prefixing:* CodeRabbit noted that raising `ValueError` in Pydantic prepends `"Value error, "` to FastAPI's response detail JSON, and recommended customizing the validation error wrapper if exact client payload matching was required.
  - *Database Column Length:* CodeRabbit highlighted that SQLite's `TEXT` column has no length constraint, suggesting a reasonable upper limit (e.g., 255 chars) on habit names to prevent denial-of-service via huge strings.

---

### PR #2 — Habit Streak (`feature/streak`)
- **Problem:** Users had no way to inspect consecutive check-in momentum.
- **Approach:** `GET /habits/{habit_id}/streak` calculating unbroken consecutive check-in calendar days.
- **Commits:**
  - One-shot implementation: [`10dc73e`](https://github.com/zuhalcolak/habit-tracker-ai-review/commit/10dc73e)
  - Review fixes & tests: [`0455c0a`](https://github.com/zuhalcolak/habit-tracker-ai-review/commit/0455c0a)

#### Human Review vs. AI Review (CodeRabbit) on PR #2
- **Where Human Review was Superior:**
  - *404 REST Consistency:* The agent's code silently returned `{"habit_id": 99999, "streak": 0}` with status 200 for a non-existent habit. Human review caught this and added the `SELECT id FROM habits WHERE id = ?` check returning HTTP 404.
  - *Check-in Deduplication:* When users check in twice on the same day, iterative day-decrement algorithms can stall or miscalculate. Human review introduced `SELECT DISTINCT` and a Python `set[date]`.
  - *Active Streak from Yesterday:* Human review realized that if a user checks their streak in the morning before checking in today, their active streak from yesterday must remain alive rather than dropping to 0.
- **Where AI Review was Superior:**
  - *Falsy Query Parameter Pitfall:* CodeRabbit noted that checking `if today:` can behave unexpectedly if an empty string `?today=` is passed. It advised validating or explicitly handling empty query strings so clients receive a clean 400 instead of unexpected defaults.
  - *Timezone Awareness:* CodeRabbit observed that `date.today()` evaluates against server local system time; in distributed or cloud deployments, storing and evaluating check-ins in UTC avoids midnight boundary discrepancies.

---

## 4. Reflection: What I Learned

Combining deterministic guardrails with LLM code review creates a powerful, complementary safety net for software engineering. Deterministic tools (`black`, `ruff`, `pytest`) are fast, authoritative, and non-negotiable for syntax, formatting, and behavioral regressions, preventing basic flaws from cluttering human and AI reviews. Meanwhile, AI code review excels at identifying subtle API edge cases, security implications, and design inconsistencies across the diff. However, AI reviewers lack holistic product intuition—such as knowing that an active streak should not reset to zero at sunrise before the user has a chance to log their morning habit, or ensuring consistent HTTP 404 semantics across endpoints. Consequently, I view AI review not as an autonomous approver, but as a tireless, high-signal second pair of eyes that augments human judgment.

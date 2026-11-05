# Week 6 Writeup — AI Code Review & Testing: The Habit Tracker

**Author:** Caden Guan (ctguan@ucsc.edu)  
**AI Reviewer Used:** Graphite Diamond / Graphite Agent  

---

## 1. Guardrail Setup

We established a three-layer deterministic guardrail system before submitting features for review:

```bash
# 1. Format check with Black
black --check main.py test_main.py

# 2. Static linting & import organization with Ruff
ruff check main.py test_main.py

# 3. Automated test execution with Pytest
pytest -v
```

### What Each Guardrail Catches
- **Black (`black --check`)**: Enforces consistent PEP 8 formatting (line lengths, quote styles, spacing around operators, trailing commas). Prevents cosmetic style debates in code reviews.
- **Ruff (`ruff check`)**: Fast linter catching unsorted/unformatted imports (`I001`), dead code, unused variables (`F401`/`F841`), and common runtime pitfalls.
- **Pytest (`pytest`)**: Verifies functional correctness and regressions. If any assertion fails, `pytest` exits with code `1`, immediately failing the build.

---

## 2. Pull Requests & Feature Implementation

### PR 1: Habit Streak Endpoint (`GET /habits/{habit_id}/streak`)
- **PR Link:** [#245 - Feature: Habit streak calculation endpoint](https://github.com/scottyUX/Software-engineering-in-the-age-of-ai/pull/245)
- **Problem:** The starter habit tracker lacked an endpoint to compute consecutive daily consistency for a habit.
- **Approach:** 
  - Added `GET /habits/{habit_id}/streak`.
  - Verifies habit existence (returns `404` if unknown).
  - Collects check-in dates into a Python `set` of `date` objects (deduplicating multiple check-ins on the same day).
  - Determines if the streak is active (checked in today, or checked in yesterday).
  - Walks backward day-by-day until a gap is found.
- **Testing:** Added 6 dedicated test cases in `test_main.py` covering empty habits, active streaks, streaks surviving until yesterday, broken streaks, duplicate check-in deduplication, and non-existent habits (`404`).

#### Human vs. AI Review Comparison (PR 1)
- **Manual Review Findings:**
  - *Timezone boundaries:* Noticed `date.today()` evaluates to server local time, which could cause edge-case inconsistencies near midnight across timezones.
  - *Deduplication:* Ensured check-ins on the same day do not count multiple times by using a set structure.
  - *Malformed records:* Handled legacy date strings with `try/except ValueError` to prevent unexpected 500 crashes.
- **AI Reviewer (Graphite) Findings:**
  - *Where Graphite was better:* Noticed that an in-memory set traversal has $O(N)$ memory/compute overhead if a user has years of check-in rows, and suggested adding a compound database index on `(habit_id, day)` in SQLite for scale.
  - *Where Graphite was worse / noisy:* Suggested adding cursor-based pagination to the streak endpoint, which is unnecessary because a streak is a scalar aggregated integer rather than a paginated list.

---

### PR 2: Weekly Summary Endpoint (`GET /habits/{habit_id}/summary`)
- **PR Link:** [#246 - Feature: Weekly summary endpoint](https://github.com/scottyUX/Software-engineering-in-the-age-of-ai/pull/246)
- **Problem:** Users could not view their rolling 7-day progress to evaluate weekly performance.
- **Approach:**
  - Added `GET /habits/{habit_id}/summary`.
  - Verifies habit existence (returns `404` if unknown).
  - Computes the 7-day rolling window (`today - timedelta(days=6)`).
  - Executes `COUNT(DISTINCT day)` directly in SQLite for high performance and automatic same-day deduplication.
- **Testing:** Added 5 test cases in `test_main.py` verifying rolling 7-day counts, exclusion of records older than 7 days, deduplication of same-day check-ins, empty habits (`0`), and missing habits (`404`).

#### Human vs. AI Review Comparison (PR 2)
- **Manual Review Findings:**
  - *Window precision:* Verified that subtracting 6 days from today encompasses exactly 7 distinct calendar dates (today + previous 6 days).
  - *Deduplication:* Confirmed `DISTINCT day` in SQL guarantees each calendar day is counted at most once.
  - *Schema consistency:* Matched the `{habit_id}` route parameter with the rest of `main.py` to prevent FastAPI 422 routing mismatches.
- **AI Reviewer (Graphite) Findings:**
  - *Where Graphite was better:* Pointed out that `day >= ?` text comparison in SQLite assumes consistent `YYYY-MM-DD` ISO formatting and recommended adding schema validation on check-in insertion to protect this invariant.
  - *Where Graphite was worse / noisy:* Flagged a suggestion to integrate external Redis caching for the summary endpoint, which is over-engineered for a simple single-file SQLite FastAPI microservice.

---

## 3. What I Learned

Deterministic guardrails (linters, formatters, and unit tests) and LLM-based code reviewers solve fundamentally different problems. Guardrails provide a non-negotiable, objective baseline that guarantees code compiles, adheres to styling standards, and satisfies known regressions before any human or AI reviewer spends time reading it. Conversely, AI reviewers act as an insightful architectural sounding board that excels at identifying cross-boundary edge cases, performance bottlenecks, and missed boundary conditions. However, because AI reviewers frequently over-engineer solutions or hallucinate unnecessary enterprise patterns (such as suggesting Redis or pagination for single integer outputs), disciplined human review remains essential to curate, validate, and contextualize AI feedback.

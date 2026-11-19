# Week 6 Assignment Writeup: Agentic Code Review & Testing

## Overview & Metadata

- **Repository**: [starter/](https://github.com/MohammadPoorahmadi/AI-Augmented-Software-Engineering/tree/main/assignments/06-agentic-code-review-and-testing/starter)
- **Coding Agent**: Antigravity
- **AI PR Reviewer**: CodeRabbit (`coderabbitai`)

### Pull Requests

| PR | Branch | Commits | Description |
|---|---|---|---|
| **[PR #1](https://github.com/MohammadPoorahmadi/AI-Augmented-Software-Engineering/pull/1)** | `feat/validation` &rarr; `main` | `f3cc72c`, `1b875f4` | Input validation on `POST /habits` and `POST /habits/{id}/checkin` |
| **[PR #2](https://github.com/MohammadPoorahmadi/AI-Augmented-Software-Engineering/pull/2)** | `feat/streak` &rarr; `main` | `5df6d72`, `d6ae16d` | `GET /habits/{id}/streak` endpoint, FastAPI lifespan DB init, and deterministic `MockDate` tests |

---

## Part I: Deterministic Quality Guardrails

Prior to submitting code for peer or AI review, local quality guardrails were established and run via commit `67df786`:

```bash
black --check .
ruff check .
pytest
```

Each tool operates as a deterministic gate with a specialized responsibility in the pipeline:

1. **`black --check .` (Code Formatting & AST Preservation)**:
   - **What it catches**: Inconsistent indentation, trailing commas, line-length overflows beyond 88 characters, mixed quote styles (`"` vs `'`), irregular whitespace inside brackets, and arbitrary formatting discrepancies.
   - **Why it matters**: Eliminates stylistic bikeshedding and formatting noise in PR diffs so human and AI reviewers focus entirely on logic, architecture, and correctness.

2. **`ruff check .` (Fast Static Analysis & Linting)**:
   - **What it catches**: Unused imports (`F401`), undefined variables (`F821`), bare `except` clauses, mutable default arguments in functions, shadowed built-ins, and anti-patterns across standard PEP guidelines.
   - **Why it matters**: Catches syntax-level bugs, dead code, and standard library misuse in milliseconds before running the test suite.

3. **`pytest` (Functional Correctness & Regression Suite)**:
   - **What it catches**: Runtime exceptions, endpoint regressions (unexpected HTTP status codes, schema mismatches), broken business logic, and broken contracts across SQLite read/write interactions.
   - **Why it matters**: Validates that all system components adhere to expected runtime behaviors and guarantees that newly added features do not break existing functionality.

---

## Part II: Pull Request Implementations

### PR #1: Input Validation (`feat/validation`)
- **Commits**: `f3cc72c`, `1b875f4`
- **Scope**:
  - Validates `POST /habits` to reject empty strings and whitespace-only habit names with `422 Unprocessable Entity` or `400 Bad Request`.
  - Validates `POST /habits/{id}/checkin` to ensure the `day` payload adheres to strict `YYYY-MM-DD` ISO formatting and represents a valid calendar day.

### PR #2: Streak Calculation & Lifecycle Refactoring (`feat/streak`)
- **Commits**: `5df6d72`, `d6ae16d`
- **Scope**:
  - Implements `GET /habits/{id}/streak` to calculate the current run of consecutive active days up to and including today.
  - Refactors database initialization out of module-level import time and into FastAPI's modern async `lifespan` context manager.
  - Implements deterministic `MockDate` monkeypatching in the test suite to insulate streak calculations against temporal flakiness.

---

## Part III: Manual Review vs. CodeRabbit Review Comparison

| Pull Request | Manual Review Findings | CodeRabbit AI Review Findings | Synthesis & Resolution |
|---|---|---|---|
| **PR #1: Input Validation** | • Identified database pollution: `test_main.py` wrote directly to production `habits.db`.<br>• Identified missing test coverage for whitespace-only habit names (`"   "`).<br>• Identified regex weakness: needed `re.fullmatch` instead of `re.match` to block trailing garbage characters. | • Identified database pollution: flagged persistent disk writes in tests and recommended using a temporary database fixture (`tmp_path`). | Both human and AI correctly identified test side effects on `habits.db`. Manual review demonstrated deeper edge-case rigor by catching regex boundary matching bugs (`fullmatch` vs. `match`) and whitespace trimming gaps. |
| **PR #2: Streak Calculation** | • Added `tmp_path` fixture isolation pre-PR.<br>• Designed boundary and edge tests: streak gaps (non-consecutive days), duplicate check-ins on identical days, and future-dated entries. | • Flagged module-level `init_db()` executing during pytest collection phase before fixtures could patch `DB_PATH`.<br>• Flagged midnight rollover / time-zone test flakiness when relying on raw `date.today()`. | Manual review focused on domain edge cases (duplicate check-ins, broken streaks), whereas CodeRabbit excelled at catching subtle architectural and lifecycle flaws (import-time side effects and temporal test flakiness). Both were resolved by moving to FastAPI `lifespan` and monkeypatching `main.date`. |

### Key Takeaways from the Comparison
- **CodeRabbit's Strengths**: Exceptional at spotting framework lifecycle caveats (FastAPI lifespan vs. module-level execution) and temporal test fragility (unmocked system clocks).
- **Manual Review's Strengths**: Superior contextual domain testing, ensuring boundary conditions (gaps, duplicate check-ins, future dates) and exact input parsing nuances (`re.fullmatch`) were thoroughly asserted.

---

## Part IV: What I Learned

Automated deterministic guardrails like `black`, `ruff`, and `pytest` establish an indispensable foundation by eliminating syntax errors, style drift, and behavioral regressions before code ever reaches human eyes. Layering an LLM reviewer such as CodeRabbit on top adds a powerful secondary defense that excels at spotting framework lifecycle anti-patterns and subtle runtime edge cases like time-dependent test flakiness. However, AI reviewers can still overlook domain-specific edge cases, regex boundary subtleties, and incomplete test matrices that require intentional design reasoning. Ultimately, the most resilient engineering workflow pairs fast deterministic linters and agentic AI reviewers with deliberate human verification to ensure both structural rigor and domain correctness.

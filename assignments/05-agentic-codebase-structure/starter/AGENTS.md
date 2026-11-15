# AGENTS.md — Link Shortener Agent Instructions

Welcome to the **Link Shortener** codebase. This guide establishes operational norms, directory layouts, and execution guardrails for AI coding agents.

---

## 1. Project Overview & Architecture
- **Framework:** FastAPI (Python 3.12+).
- **Core Files:**
  - `main.py`: Application entrypoint, in-memory URL store (`db`), schemas (`ShortenRequest`, `ShortenResponse`), and route handlers.
  - `test_main.py`: Pytest suite using `TestClient`.
  - `docs/TASKS.md`: Feature backlog and requirements.
  - `intent.md`: High-level system philosophy and architectural constraints.
  - `requirements.txt`: Runtime dependencies (`fastapi`, `uvicorn`, `httpx`).

---

## 2. Command Norms & Operational Boundaries

### Safe & Required Commands
- Run test suite:
  ```bash
  .venv/bin/python -m pytest -v
  ```
- Run linter/formatting check:
  ```bash
  .venv/bin/ruff check .
  ```
- Run application locally:
  ```bash
  .venv/bin/uvicorn main:app --reload --port 8000
  ```

### Forbidden Operations
- **DO NOT** wipe or reset the git history or bypass git hooks with `--no-verify`.
- **DO NOT** install heavy database engines or external persistence layers unless explicitly instructed (the project deliberately uses an in-memory dictionary store).
- **DO NOT** delete existing test cases or weaken assertions to make failing suites pass.

---

## 3. Standard Development Workflow (Red-Green-Refactor)
When implementing any feature from `docs/TASKS.md` or fixing a bug, follow this strict lifecycle:

```
[1. Failing Test] ──> [2. Implementation] ──> [3. Hook / Verification]
  (Write test_*.py)     (Update main.py)        (Run pre-commit / pytest)
```

1. **Step 1 — Failing Test (Red):** Add a targeted test case in `test_main.py` asserting the required status codes and JSON schema. Run pytest to verify that it fails as expected.
2. **Step 2 — Minimal Implementation (Green):** Implement the minimal necessary logic in `main.py` (e.g. schema additions, collision checks, route logic).
3. **Step 3 — Guardrail Hook Verification:** Run the pre-commit hook or `.venv/bin/pytest && .venv/bin/ruff check .` to guarantee formatting, linting, and 100% test pass rates before proposing a commit.

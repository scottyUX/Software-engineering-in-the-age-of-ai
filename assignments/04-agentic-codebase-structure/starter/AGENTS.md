# Agent Guidance — Link Shortener Service

## Overview
A minimalist FastAPI link shortener that generates short codes, redirects requests, and tracks click counts.

## Key Files
- `main.py`: FastAPI routes, SQLite database connection, and core business logic.
- `test_main.py`: Pytest suite testing HTTP endpoints.
- `docs/TASKS.md`: Candidate feature list for development.

## Setup & Execution
- **Install:** `pip install -r requirements.txt`
- **Test:** `pytest`
- **Run:** `uvicorn main:app --reload` (Local server: http://localhost:8000)

## Product Boundaries
- In scope: Simple URL shortening, custom slugs, redirection, and basic click tracking.
- Out of scope: User authentication, complex analytics, rate limiting, and multi-tenant persistence.

## Change Workflow
1. **Understand:** Read target task in `docs/TASKS.md` and inspect affected logic.
2. **Test:** Write failing behavioral test(s) in `test_main.py`.
3. **Implement:** Write minimal code to pass tests.
4. **Verify:** Run `pytest` to ensure 100% test pass rate.
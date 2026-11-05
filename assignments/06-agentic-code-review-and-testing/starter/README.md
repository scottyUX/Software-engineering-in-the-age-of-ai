# Habit Tracker

A FastAPI + SQLite service for habits, daily check-ins, streaks, and weekly summaries.

## Setup
```bash
pip install -r requirements.txt
pytest                      # All 14 tests pass
uvicorn main:app --reload   # http://localhost:8000  (docs at /docs)
```

## Deterministic Guardrails
Run the automated guardrail checks before committing:
```bash
black --check main.py test_main.py   # Format verification
ruff check main.py test_main.py      # Linting & import sorting
pytest -v                           # Automated regression test suite
```

## Endpoints
- `POST /habits` `{ "name": ... }`
- `GET /habits`
- `POST /habits/{id}/checkin` `{ "day": "2026-09-22" }`
- `GET /habits/{id}/checkins`
- `GET /habits/{id}/streak` — Returns consecutive daily streak ending today or yesterday.
- `GET /habits/{id}/summary` — Returns count of unique check-in days within the rolling 7-day window.

## Files
- `main.py` — The FastAPI application
- `test_main.py` — Pytest test suite covering core operations and edge cases
- `writeup.md` — Guardrail documentation, PR links, human vs. AI review comparison, and reflection
- `docs/TASKS.md` — The assignment task specifications

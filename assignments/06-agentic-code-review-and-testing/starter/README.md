# Habit Tracker — Week 6

A tiny FastAPI + SQLite service for habits and daily check-ins. This branch adds the
weekly-summary feature; the companion validation PR is linked in `writeup.md`.

## Setup
```bash
pip install -r requirements.txt
pytest
black --check .
ruff check .
ruff format --check .
uvicorn main:app --reload
```

`pytest` is the deterministic build gate: a failing assertion exits non-zero. Black checks
formatting and Ruff catches common correctness and unused-code issues.

## Endpoints
- `POST /habits` `{ "name": ... }`
- `GET /habits`
- `POST /habits/{id}/checkin` `{ "day": "2026-09-22" }`
- `GET /habits/{id}/checkins`
- `GET /habits/{id}/summary` returns `{ "habit_id", "start", "end", "count" }` for the
  inclusive seven-day window ending today.

## Files
- `main.py` — the app
- `test_main.py` — pytest suite
- `docs/TASKS.md` — the two features to implement

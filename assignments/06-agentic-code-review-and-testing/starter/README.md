# Starter — Habit Tracker

A tiny FastAPI + SQLite service for habits and daily check-ins. You'll add two features
on branches, open PRs, and run an AI reviewer.

## Setup
```bash
pip install -r requirements.txt
pytest                      # Run all tests
uvicorn main:app --reload   # http://localhost:8000  (docs at /docs)
```

## Guardrails
Run formatting, linting, and automated tests with a single command:
```bash
chmod +x check.sh
./check.sh
```

Or run tools individually:
```bash
black --check .
ruff check .
pytest
```

## Endpoints
- `POST /habits` — Create a new habit (`{"name": "..."}`)
- `GET /habits` — List all habits
- `POST /habits/{id}/checkin` — Record daily check-in (`{"day": "YYYY-MM-DD"}`)
- `GET /habits/{id}/checkins` — List all check-in days
- `GET /habits/{id}/streak` — Get current streak of consecutive days (`?today=YYYY-MM-DD` optional)

## Files
- `main.py` — FastAPI application with input validation and streak calculation
- `test_main.py` — Pytest test suite covering base behavior, validation, and streaks
- `check.sh` — Deterministic guardrail check script
- `pyproject.toml` — Tool configurations for Black, Ruff, and Pytest
- `writeup.md` — Human vs AI review reflection and guardrail documentation

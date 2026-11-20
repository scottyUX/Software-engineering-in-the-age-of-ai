# Starter — Habit Tracker

A tiny FastAPI + SQLite service for habits and daily check-ins, extended with streak tracking, input validation, and deterministic guardrails.

## Setup
```bash
pip install -r requirements.txt
pytest                      # 13 tests should pass
uvicorn main:app --reload   # http://localhost:8000  (docs at /docs)
```

## Guardrails
```bash
pip install black ruff

black --check main.py test_main.py   # formatting check
ruff check main.py test_main.py      # lint
pytest                               # tests
```

## Endpoints
- `POST /habits` `{ "name": ... }` — empty name returns 422
- `GET /habits`
- `POST /habits/{id}/checkin` `{ "day": "2026-09-22" }` — invalid date returns 422
- `GET /habits/{id}/checkins`
- `GET /habits/{id}/streak` — current consecutive-day streak

## Files
- `main.py` — the app
- `test_main.py` — pytest suite
- `pyproject.toml` — black + ruff config
- `docs/TASKS.md` — the two features to implement
- `writeup.md` — assignment writeup

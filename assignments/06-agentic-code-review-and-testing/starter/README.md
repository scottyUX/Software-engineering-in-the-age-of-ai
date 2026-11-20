# Starter — Habit Tracker

A tiny FastAPI + SQLite service for habits and daily check-ins. You'll add two features
on branches, open PRs, and run an AI reviewer.

## Setup
```bash
pip install -r requirements.txt
pytest                      # 3 tests should pass
uvicorn main:app --reload   # http://localhost:8000  (docs at /docs)
```

## Guardrails
```bash
pip install -r requirements-dev.txt
./check.sh
```
`check.sh` runs these in order, stops at the first failure, and exits non-zero:

| Step | Command | Catches |
|------|---------|---------|
| Format | `black --check .` | Code that is not formatted (line length 100, see `pyproject.toml`) |
| Lint | `ruff check .` | Unused imports, import order, likely bugs such as mutable default arguments |
| Tests | `pytest -q` | Behavior that no longer matches the tests |

## Endpoints
- `POST /habits` `{ "name": ... }`
- `GET /habits`
- `POST /habits/{id}/checkin` `{ "day": "2026-09-22" }`
- `GET /habits/{id}/checkins`

## Files
- `main.py` — the app
- `test_main.py` — pytest suite
- `docs/TASKS.md` — the two features to implement
- `check.sh`, `pyproject.toml`, `requirements-dev.txt` — guardrails

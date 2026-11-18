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
ruff check .        # lint: unused imports, undefined names, import order, likely bugs (bugbear)
black --check .     # format: fails if any file is not black-formatted (run `black .` to fix)
pytest -q           # tests: exits 1 on any failing test
```

All three run in GitHub Actions (`.github/workflows/ci.yml`) on every push, and any failure
fails the build. Settings live in `pyproject.toml`: both tools use a 100-character line length.

## Endpoints
- `POST /habits` `{ "name": ... }`
- `GET /habits`
- `POST /habits/{id}/checkin` `{ "day": "2026-09-22" }`
- `GET /habits/{id}/checkins`

## Files
- `main.py` — the app
- `test_main.py` — pytest suite
- `docs/TASKS.md` — the two features to implement

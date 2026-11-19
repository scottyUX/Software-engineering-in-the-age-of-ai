# Starter — Habit Tracker

A tiny FastAPI + SQLite service for habits and daily check-ins. You'll add two features
on branches, open PRs, and run an AI reviewer.

## Setup
```bash
pip install -r requirements.txt
pytest                      # 29 tests should pass
uvicorn main:app --reload   # http://localhost:8000  (docs at /docs)
```

## Endpoints
- `POST /habits` `{ "name": ... }`
- `GET /habits`
- `POST /habits/{id}/checkin` `{ "day": "2026-09-22" }`
- `GET /habits/{id}/checkins`
- `GET /habits/{id}/streak`: consecutive days with a check-in, ending today (PR #1)

`name` must not be blank and `day` must be a real `YYYY-MM-DD` date; otherwise 422 (PR #2).

## Files
- `main.py` — the app
- `test_main.py` — pytest suite
- `docs/TASKS.md` — the two features to implement

## Guardrails
Install the dev tools once: `pip install -r requirements-dev.txt`.

| Command | What it catches |
| --- | --- |
| `black --check --diff .` | Code that is not formatted the agreed way (line length 100) |
| `ruff check .` | Unused imports, undefined names, import order, likely bugs (bugbear), outdated syntax |
| `pytest` | Behavior regressions; any failing test exits non-zero |

`./check.sh` (Git Bash / macOS / Linux) or `.\check.ps1` (PowerShell) runs all three and stops
at the first failure. GitHub Actions (`.github/workflows/ci.yml`) runs the same three steps on
every push to `main` and every pull request, so a failing test fails the build.

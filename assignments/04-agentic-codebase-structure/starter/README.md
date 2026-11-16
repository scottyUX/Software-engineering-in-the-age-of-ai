# Starter — Link Shortener

A tiny FastAPI + SQLite service that you will make easier for a coding agent to understand and modify. The application already works; you will add repository guidance, one scoped instruction, one reusable workflow, and complete one feature.

## Setup

```bash
pip install -r requirements.txt
pytest                       # all tests should pass
uvicorn main:app --reload    # http://localhost:8000  (docs at /docs)
```

## Try it

```bash
curl -X POST localhost:8000/shorten -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com"}'
# -> {"code":"b","short_url":"/b"}  then GET localhost:8000/<code> redirects
```

## Files

- `AGENTS.md` — guidance for coding agents (start here)
- `main.py` — the app (`POST /shorten` with optional `alias`, `GET /{code}`)
- `tests/` — pytest suite; `tests/AGENTS.md` holds the testing rules
- `docs/TASKS.md` — feature backlog (task 1, custom alias, is implemented)
- `.claude/skills/implement-task/SKILL.md` — reusable workflow for a new task

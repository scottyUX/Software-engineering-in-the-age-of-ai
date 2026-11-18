# AGENTS.md — Link Shortener

## What this is
A small FastAPI + SQLite service that turns long URLs into short codes and redirects
visitors. `POST /shorten` stores a URL and returns a code; `GET /{code}` redirects to it.

## Where things are
- `main.py` — the whole app: database setup, base62 `encode`, request models, routes.
- `test_main.py` — pytest suite, run through FastAPI's `TestClient`.
- `docs/TASKS.md` — the backlog of small features.
- `links.db` — local SQLite file created on import; never commit it.
- `.claude/rules/testing.md` — rules for writing tests (loads when test files are touched).
- `.claude/skills/implement-task/SKILL.md` — the procedure for implementing a task.

## Install, run, test
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest                      # all tests must pass before and after a change
uvicorn main:app --reload   # http://localhost:8000, docs at /docs
```

## Product boundaries
In scope: creating short links, redirecting, and small link features from `docs/TASKS.md`.

Out of scope unless a task asks for it: user accounts or auth, a frontend, analytics beyond a
simple counter, rate limiting, other databases, ORMs, and new dependencies.

## Conventions
- Keep the app in `main.py` while it stays small; don't split it into packages.
- Open connections with `with closing(get_db()) as conn:` and always use `?` placeholders.
- Return errors with `HTTPException` and a short lowercase `detail`.
- Schema changes go in `init_db()` and must also upgrade an existing `links.db`.
- Route order matters: `GET /{code}` matches any single path segment, so new
  `GET /<word>/...` routes need a second segment or must be declared before it.

## Change workflow
1. **Understand**: read the task, `main.py`, and the related tests.
2. **Test**: write a failing behavioral test first.
3. **Implement**: make the smallest change that passes it.
4. **Verify**: run the full `pytest`; never edit an existing test to make it pass.

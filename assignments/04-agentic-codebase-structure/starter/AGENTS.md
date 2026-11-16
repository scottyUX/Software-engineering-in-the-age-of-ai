# AGENTS.md — Link Shortener

## What this is
A tiny FastAPI + SQLite service that turns long URLs into short codes.
- `POST /shorten` `{"url": "https://..."}` → `{"code": "b", "short_url": "/b"}`
- `GET /{code}` → `307` redirect to the stored URL, `404` if unknown

## Where things are
| Path | Purpose |
|------|---------|
| `main.py` | The whole app: DB setup, base62 `encode()`, request models, routes |
| `tests/` | pytest suite (has its own `tests/AGENTS.md` — read it before editing tests) |
| `tests/conftest.py` | Gives every test a fresh temporary SQLite DB |
| `docs/TASKS.md` | Feature backlog; implement one task at a time |
| `.claude/skills/implement-task/` | Reusable workflow for implementing a task |

`links.db` is created at runtime next to `main.py`. It is git-ignored; never commit it.

## Commands
```bash
pip install -r requirements.txt
pytest                      # must be green before and after every change
uvicorn main:app --reload   # http://localhost:8000, docs at /docs
```

## Product boundaries
In scope: creating short codes, redirecting, and small per-link features
from `docs/TASKS.md` (alias, click counts, expiry).

Out of scope — do not add without being asked:
- Authentication, users, or rate limiting
- A frontend, templates, or static files
- New dependencies, an ORM, migrations framework, or a second database
- Splitting `main.py` into packages; keep the single-file layout

## Conventions
- Keep SQL parameterized (`?` placeholders); never format user input into SQL.
- Open connections with `with closing(get_db()) as conn:` and `commit()` writes.
- Validation errors use `HTTPException` with an explicit status and short `detail`.
- Schema changes go in `init_db()` using `CREATE TABLE IF NOT EXISTS`.
- Fixed-path routes (e.g. `/stats/...`) must be declared **before** `GET /{code}`.

## Change workflow
1. **Understand** — read the task, `main.py`, and the related tests.
2. **Test** — write a failing behavioral test for the new behavior.
3. **Implement** — the smallest change in `main.py` that makes it pass.
4. **Verify** — run `pytest`; all old and new tests must pass. Summarize risks.

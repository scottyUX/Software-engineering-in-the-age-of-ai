# Link Shortener — agent guide

A tiny FastAPI + SQLite service: `POST /shorten` turns an `http(s)` URL into a short
code, and `GET /{code}` redirects (307) to the original URL.

## Where things are

| Path | What it is |
|------|------------|
| `main.py` | The whole app: DB setup (`get_db`, `init_db`), base62 `encode`, both routes |
| `tests/` | pytest suite; has its own `tests/AGENTS.md` for test-writing rules |
| `docs/TASKS.md` | The feature backlog (custom alias, click counter, expiry) |
| `.agents/skills/implement-feature/` | Reusable workflow for building a task from `docs/TASKS.md` |
| `links.db` | SQLite file created on startup; gitignored, never commit it |

## Install, run, test

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q                    # run from this folder; config is in pytest.ini
uvicorn main:app --reload    # http://localhost:8000, API docs at /docs
```

Always run commands from this folder with `.venv` active.

## Product boundaries

In scope: shortening `http://` / `https://` URLs, redirecting, and the small
features listed in `docs/TASKS.md`.

Out of scope: user accounts or auth, a web UI, analytics dashboards, background
jobs, other databases or external services. Do not add dependencies beyond
`requirements.txt` unless a task truly needs one.

Rules that keep the service working:
- A code is one URL path segment served by `GET /{code}`. It must never shadow an
  existing route: `/shorten`, `/docs`, `/redoc`, `/openapi.json`.
- Keep existing behavior backward compatible: same status codes (200, 400, 404,
  307) and the same JSON shape `{"code", "short_url"}` for existing requests.
- All DB access goes through `get_db()` with `closing(...)`; use `?` placeholders,
  never string-formatted SQL.
- `init_db()` uses `CREATE TABLE IF NOT EXISTS`, so it will not add new columns to
  an existing `links.db`. A schema change must also migrate an existing file.

## Change workflow

1. **Understand** — read the task, `main.py`, and the related tests. State the
   expected behavior and which files change before editing.
2. **Test** — add a failing behavioral test first (see `tests/AGENTS.md`).
3. **Implement** — make the smallest change in `main.py` that passes it; no
   unrelated refactors.
4. **Verify** — run `pytest -q`; all old and new tests must pass. Summarize what
   changed and any remaining risk.

Do not commit or push; leave changes for human review.

# Habit Tracker — Week 6

This starter now validates habit names and check-in dates at the API boundary. Names are trimmed
and must contain at least one non-whitespace character. Check-in days must be real, zero-padded
ISO dates such as `2026-09-22`; invalid values return HTTP 422 with a clear message.

## Setup

```bash
pip install -r requirements.txt
pytest
black --check .
ruff check .
ruff format --check .
```

`pytest` is the deterministic build gate: a failing assertion exits non-zero. Black checks
formatting, Ruff catches common correctness and unused-code issues, and Ruff format provides a
second formatting check suitable for CI.

## Run

```bash
uvicorn main:app --reload
```

## Endpoints

- `POST /habits` with `{ "name": "Read" }`
- `GET /habits`
- `POST /habits/{id}/checkin` with `{ "day": "2026-09-22" }`
- `GET /habits/{id}/checkins`

Validation examples:

- `{ "name": "   " }` returns `422` with `name must not be empty`.
- `{ "day": "2026/09/22" }` returns `422` with `day must be an ISO date in YYYY-MM-DD format`.

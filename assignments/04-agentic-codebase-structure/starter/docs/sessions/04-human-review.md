# Human review of the custom alias change — REVISE

The agent review (`03-review.md`) returned ACCEPT, but it only checked the 409 path and
did not check the change against the product rules in `AGENTS.md`. I reproduced these
problems against commit `a6348be` with `TestClient(app, raise_server_exceptions=False)`.

## F1 — An alias can shadow an existing route (breaks an `AGENTS.md` rule)

`AGENTS.md`: "A code is one URL path segment served by `GET /{code}`. It must never
shadow an existing route: `/shorten`, `/docs`, `/redoc`, `/openapi.json`."

| Alias | `POST /shorten` | `GET /<alias>` |
|-------|-----------------|----------------|
| `docs` | 200 | 200 — FastAPI's docs page, not the redirect |
| `openapi.json` | 200 | 200 — the OpenAPI JSON, not the redirect |

The short link is accepted but can never work.

**Expected:** `shorten`, `docs`, `redoc` and `openapi.json` are not available as
aliases → **409**, the same status the task uses for an alias that is taken.

## F2 — Aliases are not validated as a single URL path segment

| Alias | `POST /shorten` | `GET /<alias>` |
|-------|-----------------|----------------|
| `a/b` | 200 | 404 |
| `has space` | 200 | works only if the client encodes the space |
| `""` (empty) | 200, silently falls back to a generated code | — |

**Expected:** an alias must be 1–32 characters from `A–Z a–z 0–9 _ -`. Anything else,
including an empty string, → **400** with a clear `detail` (the same status the app
already uses for an invalid `url`). Omitting `alias` or sending `null` keeps the current
generated-code behavior.

## F3 — An alias can permanently break code generation (500)

The generated code for a row is `encode(row_id)`. An alias can claim a code that a later
row will generate. Reproduced on a fresh database:

```text
POST /shorten {"alias": "e"}   -> 200          (e = encode(4))
POST /shorten (no alias)       -> 200 {"code": "c"}
POST /shorten (no alias)       -> 200 {"code": "d"}
POST /shorten (no alias)       -> 500          (UPDATE code='e' violates UNIQUE)
POST /shorten (no alias)       -> 500          (the failed insert rolls back, so the same id is retried forever)
```

**Expected:** generating a code never fails because an alias already uses it. If
`encode(row_id)` is taken, keep trying the next candidate (e.g. `encode(row_id + k)`)
until a free code is found, inside the same transaction.

## F4 — Tests only cover the 409 failure

**Expected (following `tests/AGENTS.md`):**
- 400 for invalid aliases (at least `a/b`, `has space`, `""`, and a 33-character alias).
- 409 for each reserved name.
- A regression test for F3: after an alias takes a future generated code, the next
  shortens still return 200 and redirect correctly. This one needs a fresh database and
  `encode()`; see the exception added to `tests/AGENTS.md`.
- The suite must still pass when run twice in a row.

## Verdict

**REVISE.** Fix F1–F4 with the `implement-feature` skill (test-first), then re-review.

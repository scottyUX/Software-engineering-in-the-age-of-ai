# tests/AGENTS.md — rules for writing tests

Applies to everything under `tests/`. Read this before adding or changing a test.

- **Public API only.** Exercise the app through `TestClient` HTTP calls. Do not
  call `encode()`, `get_db()`, or query SQLite directly to make assertions.
  `monkeypatch` may set up a hard-to-reach scenario, but assert over HTTP.
- **Assert behavior.** Check status codes, response JSON, and headers
  (e.g. `location` on redirects) — not internal state or implementation details.
- **Success and failure.** Every feature gets at least one happy-path test and at
  least one failure or edge-case test (bad input, conflict, unknown code, ...).
- **Independent tests.** Each test must pass alone and in any order. The autouse
  fixture in `conftest.py` gives each test a fresh empty DB; don't rely on rows
  created by another test, and don't hard-code generated codes like `"b"`.
- **Redirects.** Use `follow_redirects=False` when asserting a `307`.
- **Naming.** `test_<feature>_<expected_behavior>`, one behavior per test.
- **Don't weaken tests** to make them pass. If an existing test breaks, fix the
  code or explain why the behavior intentionally changed.

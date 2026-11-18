---
paths:
  - "test_*.py"
  - "tests/**/*.py"
---

# Testing rules

- Test through the public HTTP API with `TestClient`; don't call route functions or query
  `links.db` directly.
- Cover the success path and at least one failure or edge case for every behavior.
- Each test creates its own data (for example, shorten a fresh URL) and must pass alone and in
  any order; never depend on another test's codes or counts.
- Assert what a client observes: status codes, JSON fields, and redirect `location` headers.
- Pass `follow_redirects=False` when asserting a redirect.
- Name tests after the behavior: `test_<action>_<expected_result>`.

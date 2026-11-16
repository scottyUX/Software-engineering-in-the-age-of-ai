# Test Suite Guidance

When creating or modifying tests in this directory:
- **Public API Only:** Test through FastAPI client HTTP requests (`client.get`, `client.post`); do not call internal database functions directly.
- **Coverage:** Include both success paths (2xx responses) and error/edge cases (4xx responses).
- **Isolation:** Each test function must execute independently without relying on shared state or order of execution.
- **Behavioral Focus:** Assert on API response status, JSON structure, and redirect targets, not implementation internals.
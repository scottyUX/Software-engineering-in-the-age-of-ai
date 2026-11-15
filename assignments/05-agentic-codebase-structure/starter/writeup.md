# Week 5 — Writeup: Structuring a Repo for Agents (The Link Shortener)

## 1. Overview & Artifact Mapping
This writeup documents making the **Link Shortener** service agent-native through operational guidelines, pre-commit guardrails, reusable workflow playbooks, and a role-specialized subagent execution pattern.

| Artifact | Purpose | Mapped Agent Capability / Feature |
|---|---|---|
| `AGENTS.md` | Documents safe commands, runtime setup, forbidden ops, and Red-Green-Refactor development norms | Cross-agent system context & operational instructions (`AGENTS.md` standard) |
| `intent.md` | Specifies high-level architecture, storage guarantees, and HTTP status code contracts | System architecture guardrails & domain invariants |
| `pre-commit.sh` | Enforces automated formatting/linting via Ruff and runs pytest prior to any commit | Git hook & CI/CD agent guardrail |
| `docs/PLAYBOOKS.md` | Standardizes `/test-and-summarize` and `/implement-task` execution flows | Reusable agent playbooks / slash commands |
| `main.py` & `test_main.py` | Completed the **Custom alias** feature (`POST /shorten` with alias; 409 on collision) | Subagent execution (Planner → Implementer → Reviewer) |

---

## 2. Guardrail Hook: Blocking a Failing Change

A git guardrail hook (`pre-commit.sh`) was wired to run `ruff check` followed by `pytest -q`. When unformatted code or a breaking test was introduced, the hook successfully intercepted the process and aborted with non-zero exit code:

```text
=== [Guardrail Hook] Running Ruff Lint Check ===
All checks passed!
=== [Guardrail Hook] Running Pytest Suite ===
...FF                                                                    [100%]
=================================== FAILURES ===================================
__________________________ test_custom_alias_success ___________________________
    def test_custom_alias_success():
        alias = "my-custom-doc"
        r = client.post("/shorten", json={"url": "https://docs.python.org", "alias": alias})
        assert r.status_code == 200
>       assert r.json()["code"] == alias
E       AssertionError: assert 'i' == 'my-custom-doc'

_______________________ test_custom_alias_collision_409 ________________________
    def test_custom_alias_collision_409():
        alias = "duplicate-alias"
        r1 = client.post("/shorten", json={"url": "https://first.com", "alias": alias})
        assert r1.status_code == 200
        r2 = client.post("/shorten", json={"url": "https://second.com", "alias": alias})
>       assert r2.status_code == 409
E       assert 200 == 409

=========================== short test summary info ============================
FAILED assignments/05-agentic-codebase-structure/starter/test_main.py::test_custom_alias_success
FAILED assignments/05-agentic-codebase-structure/starter/test_main.py::test_custom_alias_collision_409
2 failed, 3 passed, 1 warning in 0.14s
```

After implementing the required collision checks and alias storage logic in `main.py`, the hook confirmed compliance:
```text
=== [Guardrail Hook] Running Ruff Lint Check ===
All checks passed!
=== [Guardrail Hook] Running Pytest Suite ===
.....                                                                    [100%]
5 passed, 1 warning in 0.18s
=== [Guardrail Hook] All checks passed! Proceeding with commit. ===
```

---

## 3. Subagent Transcript: Planner → Implementer → Reviewer

To complete Task 1 (**Custom alias** from `docs/TASKS.md`), three specialized roles were applied:

### A. Planner Subagent
- **Objective:** Analyze `docs/TASKS.md` Task 1 and define minimal schema updates and database collision logic.
- **Plan Formulated:**
  1. Add `alias: str | None = None` to `ShortenRequest` schema.
  2. In `POST /shorten`, if `req.alias` is provided, validate non-empty string and query `links` table for existing `code == alias`.
  3. If found, raise `HTTPException(status_code=409, detail="alias '...' is already in use")`.
  4. If unique, insert `(alias, req.url)` directly into `links` table.
  5. Add test cases in `test_main.py` covering successful custom alias creation, redirect verification, and 409 conflict detection.

### B. Implementer Subagent
- **Action:**
  1. Authored `test_custom_alias_success` and `test_custom_alias_collision_409` in `test_main.py`.
  2. Confirmed test failure against current starter code (`2 failed, 3 passed`).
  3. Updated `main.py` with alias collision queries, 409 exception handling, and custom code assignment.
  4. Executed `pre-commit.sh` gate until all 5 test assertions passed cleanly.

### C. Reviewer Subagent
- **Review Findings:**
  - **Correctness:** Verified status code 409 is strictly returned on collision; redirect preserves target URL with 307.
  - **Edge Cases:** Whitespace-only aliases (`"   "`) are stripped and rejected with 400 Bad Request.
  - **Clean Code & Types:** Verified typing uses modern `str | None` conforming to Ruff standards; SQLite connections safely closed with `closing(get_db())`.
  - **Verdict:** Approved for production merge.

---

## 4. What I Learned (Structuring a Repo for Agents)
Structuring a repository for autonomous agents requires treating human operational knowledge as machine-readable specifications. When guardrails like `AGENTS.md` and `intent.md` explicitly define permissible commands, negative boundaries, and architectural contracts, agents waste significantly fewer tokens wandering or making invalid architectural assumptions. Furthermore, pairing fast local hooks (`pre-commit`) with specialized subagent loops (Planner → Implementer → Reviewer) transforms loose agent generations into an autonomous Red-Green-Refactor pipeline where regressions are caught and corrected before reaching version control.

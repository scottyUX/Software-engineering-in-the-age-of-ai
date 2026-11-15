# Reusable Playbooks & Agent Workflows

This document records standard, reusable agent workflows and command playbooks for the **Link Shortener** service.

---

## Playbook 1: Test Gate & Failure Summary (`/test-and-summarize`)
**Goal:** Run the full test suite, lint check, and provide an actionable diagnostic summary of any failures.

### Execution Command:
```bash
assignments/05-agentic-codebase-structure/starter/.venv/bin/pytest -v assignments/05-agentic-codebase-structure/starter/test_main.py && assignments/05-agentic-codebase-structure/starter/.venv/bin/ruff check assignments/05-agentic-codebase-structure/starter/
```

### Agent Instruction Template:
1. Run the test command above.
2. If tests pass, report `All green: N tests passing.`
3. If any test fails:
   - Identify the exact failing assertion line in `test_main.py`.
   - Inspect the corresponding route handler in `main.py`.
   - Output a concise markdown table with: `Test Name`, `Expected Status/Payload`, `Actual Status/Payload`, and `Root Cause`.
   - Do **NOT** modify tests to make them pass unless the requirements themselves changed.

---

## Playbook 2: Feature Implementation Cycle (`/implement-task`)
**Goal:** Add a new endpoint or schema enhancement from `docs/TASKS.md` following the mandatory Red-Green-Refactor agentic flow.

### Workflow Steps:
1. **Red (Failing Test):** Write a new test function in `test_main.py` covering positive and negative edge cases. Confirm failure.
2. **Green (Minimal Fix):** Implement logic in `main.py`. Keep dependencies minimal.
3. **Guardrail Hook Verification:** Run `assignments/05-agentic-codebase-structure/starter/pre-commit.sh`.
4. **Subagent Review:** Trigger reviewer subagent to check code quality, edge cases (e.g. 409 collisions), and security.

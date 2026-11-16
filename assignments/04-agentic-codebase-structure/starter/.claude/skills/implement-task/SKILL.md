---
name: implement-task
description: Implement one feature from docs/TASKS.md in the link shortener using a test-first loop. Use when asked to build, add, or implement a task or feature in this repo.
argument-hint: "<task number or name from docs/TASKS.md>"
---

# Implement a task from docs/TASKS.md

Task requested: $ARGUMENTS

Follow these steps in order. Do not skip ahead; each step's output feeds the next.

## 1. Read the task and the guidance
- Read the matching entry in `docs/TASKS.md`. If `$ARGUMENTS` is empty or ambiguous,
  stop and ask which task to implement.
- Read `AGENTS.md` (product boundaries, conventions) and `tests/AGENTS.md` (test rules).

## 2. Inspect the related code and tests
- Read `main.py`: the `links` schema in `init_db()`, the request model, and the
  route(s) the task touches.
- Read `tests/test_main.py` and `tests/conftest.py` to see existing coverage.
- Run `pytest` once to confirm the baseline is green. If it is not, stop and report.

## 3. State the expected behavior and affected files
Before editing, write a short contract:
- Inputs, outputs, and status codes for the success path.
- Every failure / edge case and its status code.
- Files you will change (normally only `main.py` and `tests/test_main.py`).
- Any schema change and how existing rows are affected.

## 4. Add failing behavioral tests
- Add tests to `tests/test_main.py` for the success path **and** at least one
  failure case, following `tests/AGENTS.md`.
- Run `pytest` and confirm the new tests **fail for the expected reason**
  (wrong status / missing field), not because of a typo or import error.

## 5. Implement the smallest change
- Edit `main.py` only as much as needed to make the new tests pass.
- Respect the conventions in `AGENTS.md`: parameterized SQL, `closing(get_db())`,
  `HTTPException` for errors, no new dependencies.
- Do not refactor unrelated code.

## 6. Run the tests
- Run `pytest`. All original and new tests must pass.
- If something fails, fix the code (not the test) unless the test is wrong; explain which.

## 7. Summarize
Reply with:
- **Change:** one or two sentences on what was added.
- **Files:** each file touched and why.
- **Tests:** names of the new tests and the final `pytest` result line.
- **Risks / follow-ups:** edge cases not covered, schema concerns, or open questions.

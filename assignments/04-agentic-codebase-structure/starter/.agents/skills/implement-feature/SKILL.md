---
name: implement-feature
description:
  Implement one feature from docs/TASKS.md in the link shortener, test-first. Use
  when the user asks to build, add, or implement a task from docs/TASKS.md (custom
  alias, click counter, or expiry).
---

# Implement a feature from `docs/TASKS.md`

Follow these steps in order. Do not skip ahead to editing code.

## 1. Read the task and the guidance

- Read the selected task in `docs/TASKS.md`. If the user did not say which task, ask.
- Read `AGENTS.md` (product boundaries, workflow) and `tests/AGENTS.md` (test rules).

## 2. Inspect the related code and tests

- Read `main.py` and `tests/test_main.py`.
- Note which routes, models, and DB columns the task touches, and which existing
  behavior must not change.

## 3. State the expected behavior and affected files

Before editing, write a short spec in your reply:
- Request and response for each case (status code + JSON), including every failure
  case named in the task.
- Edge cases (empty or invalid input, conflicts with existing codes or routes).
- The files you will change.

## 4. Add a failing behavioral test

- Add tests to `tests/test_main.py` for the success path and at least one failure
  case, following `tests/AGENTS.md`.
- Run `pytest -q` and confirm the new tests fail for the expected reason (not an
  import or syntax error).

## 5. Implement the smallest change

- Edit `main.py` only as much as the task needs. Keep existing responses backward
  compatible and keep all SQL parameterized.
- No unrelated refactors, renames, or new dependencies.

## 6. Run the full suite

- Run `pytest -q`. All original and new tests must pass.
- Run it a second time to confirm the tests do not depend on leftover data in
  `links.db`.

## 7. Summarize

Reply with:
- What changed, file by file.
- The tests you added and what each one proves.
- The final `pytest` result.
- Remaining risks or follow-ups (for example, behavior the task leaves undefined).

Do not commit or push.

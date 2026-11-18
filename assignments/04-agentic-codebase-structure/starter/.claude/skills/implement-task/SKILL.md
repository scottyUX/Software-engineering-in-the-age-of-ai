---
name: implement-task
description: Implement one feature from docs/TASKS.md in the link shortener, test-first. Use when asked to implement, build, or add a task or feature in this repository.
---

# Implement a task

Follow these steps in order. Don't skip ahead to code.

1. **Read the task and the guidance.** Open `docs/TASKS.md` and find the selected task. Read
   `AGENTS.md`, including the product boundaries.
2. **Inspect the code and tests.** Read `main.py` and `test_main.py` in full, and note the
   routes, the database schema, and existing test patterns.
3. **State the expected behavior and the affected files** before editing. List each
   request and response, including every error status, and each file you will change.
4. **Add failing behavioral tests.** Follow `.claude/rules/testing.md`. Run `pytest` and
   confirm the new tests fail for the expected reason, not because of a syntax or import error.
5. **Implement the smallest change** in `main.py` that makes them pass. If the schema changes,
   make `init_db()` upgrade an existing `links.db` too.
6. **Run the full suite** with `pytest`. Every original and new test must pass. If a test fails,
   fix the code, not the test.
7. **Summarize** what changed (files and behavior) and any remaining risks or untested cases.

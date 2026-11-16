---
name: feature-development-workflow
description: Standardized procedure for planning, test-driven implementation, and verification of new features.
---

# Feature Development Workflow

When implementing any feature in this repository, execute these steps sequentially:

1. **Read Requirements:** Review the selected feature in `docs/TASKS.md` and repo rules in `AGENTS.md`.
2. **Code Inspection:** Inspect affected logic in `main.py` and existing tests in `test_main.py`.
3. **Plan:** State expected behavior and specific files to be modified.
4. **Red Stage (TDD):** Add failing behavioral test(s) in `test_main.py`.
5. **Green Stage:** Implement the minimal code in `main.py` required to make tests pass.
6. **Verify:** Run `pytest` to confirm all tests pass.
7. **Summary:** Provide a concise summary of changes made and any edge-case risks.
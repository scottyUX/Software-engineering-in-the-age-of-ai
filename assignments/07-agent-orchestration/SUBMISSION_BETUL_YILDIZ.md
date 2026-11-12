# Week 7 — Agent Orchestration
## Submission — Betul Yildiz
**GitHub Repository:** https://github.com/betulyildizs/week7-recipe-box
### Part I — Concurrent Agents
Two GitHub Copilot agents worked concurrently in separate VS Code windows and Git worktrees.
- Agent A: Shopping List (`feat/shopping-list`)
- Agent B: Tag Filter (`feat/tag-filter`)
Both branches were integrated into `main`. Merge conflicts were resolved while preserving both features and their tests.
### Part II — Generator–Critic Loop
Task: Ingredient Scaling.
- Initial implementation: `1314691`
- Critic Review 1: Major decimal overflow issue identified.
- Revision 1: `c40eb60` — overflow handling and regression test.
- Critic Review 2: Approved, with optional fractional-factor test improvements.
- Revision 2: `3ff38c7` — fractional scaling tests.
- Final Critic: Approved.
### Verification
**24 tests passed**, with one non-blocking Starlette/httpx deprecation warning.
### Documentation
The linked repository includes:
- Source code and automated tests
- `writeup.md` with orchestration process and reflections
- Agent logs and integration notes
- Git commit and merge history

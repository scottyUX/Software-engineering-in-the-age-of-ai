# Week 8 Submission: Agent Orchestration - The Recipe Box Sprint

**Student:** Zuhal Çolak  
**GitHub Account:** [zuhalcolak](https://github.com/zuhalcolak)  
**Standalone Repository:** https://github.com/zuhalcolak/week8-recipe-box-orchestration  
**Writeup:** https://github.com/zuhalcolak/week8-recipe-box-orchestration/blob/main/writeup.md  

---

## Deliverables Summary

- **Part I - Concurrent Agents (Git Worktrees):**
  - **Task 1 (Shopping List):** Implemented `GET /shopping-list?ids=1,2,3` in isolated git worktree `../recipe-task-a` on branch `task-a`.
  - **Task 2 (Tag Filter):** Implemented `GET /recipes?tag=breakfast` in isolated git worktree `../recipe-task-b` on branch `task-b`.
  - **Landing & Integration:** Both branches merged cleanly into `main` without unresolved conflicts. Worktree isolation guaranteed zero cross-agent file pollution.
- **Part II - Generator-Critic Loop (Task 3: Ingredient Scaling):**
  - Predetermined rubric authored in `reviews/RUBRIC.md`.
  - **Round 1 (REVISE):** Critic discovered 5 defects (mixed fractions corruption, small factors rounding to zero, unbounded factor, unhandled whitespace, missing 404).
  - **Round 2 (REVISE):** Critic verified fixes for items 1-5, but caught missing lower factor bound (`factor=0` / `1e-300`) and range scaling issues (`2-3 eggs`).
  - **Round 3 (SIGN-OFF):** Full approval granted after strict factor bounds (`0.001 <= factor <= 1000`), range protections, and clean number formatting were confirmed.
  - Full critique logs committed in `reviews/` and verbatim transcripts detailed in `writeup.md`.
- **Part III - Testing & Verification:**
  - **22/22 tests passing** across `test_main.py`, `test_shopping_list.py`, `test_tag_filter.py`, and `test_scaling.py`.
  - Linter and style checks clean (`black --check .`, `ruff check .`).

The complete source code, worktree branches (`task-a`, `task-b`), commit history, test suites, and writeup are hosted in the repository linked above.

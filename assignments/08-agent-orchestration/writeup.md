# Week 8 Writeup: Agent Orchestration - The Recipe Box Sprint

**Student:** Zuhal Çolak  
**Repository:** https://github.com/zuhalcolak/week8-recipe-box-orchestration  
**Date:** November 2026  

---

## 1. Concurrency Notes (Part I)

### Tasks Chosen
Two independent tasks from `docs/TASKS.md` were assigned to concurrent agents:
- **Task A (Task 1: Shopping list):** `GET /shopping-list?ids=1,2,3` merges the ingredients of requested recipes into a de-duplicated, ordered list with validation (missing/empty/malformed IDs return 400; unknown recipe ID returns 404).
- **Task B (Task 2: Tag filter):** `GET /recipes?tag=breakfast` filters recipes by tag with exact, case-insensitive matching while preserving full listing when tag parameter is omitted or empty.

### Git Worktree Isolation Setup
To guarantee that neither agent interfered with the other's uncommitted changes or working tree state, independent git worktrees were provisioned:
```bash
git worktree add ../recipe-task-a -b task-a
git worktree add ../recipe-task-b -b task-b
```
Each agent was constrained to its assigned worktree and branch:
- **Agent A (Task 1):** Worked strictly in `../recipe-task-a` on branch `task-a`. Appended the `/shopping-list` route at the bottom of `main.py` and authored an isolated test suite in `test_shopping_list.py` (9 tests).
- **Agent B (Task 2):** Worked strictly in `../recipe-task-b` on branch `task-b`. Modified `list_recipes` in `main.py` to accept `tag: str | None = None` and authored an isolated test suite in `test_tag_filter.py` (4 tests).

### Collisions, Merge Experience, and Concurrency Risks
- **Textual Merging:** When landing the branches back into `main`:
  1. `task-a` was fast-forward merged into `main`.
  2. `task-b` was merged via 3-way merge (`ort` strategy). Because Agent A added code to the file footer while Agent B modified `list_recipes` in the body, Git automatically merged `main.py` with zero textual conflicts.
- **Semantic Overlap & Collision Risks:**
  - *Data model interpretation:* Task 1 treats ingredients as raw text strings (e.g., `"2 eggs"` and `"3 eggs"` are deduplicated as distinct items), whereas Task 3 parses leading numerical quantities. This reveals that concurrent agents work well at file boundaries, but high-level semantic domain models require human architectural coordination.
  - *Shared state:* Both agents rely on the shared SQLite database schema. Because neither modified table structures, schema collision risk was zero.

---

## 2. Generator-Critic Loop (Part II)

Task 3 (**Ingredient Scaling:** `GET /recipes/{id}/scaled?factor=2`) was developed using an orchestrated generator-critic loop evaluated against a predetermined rubric (`reviews/RUBRIC.md`).

### Summary of Revision Rounds

| Round | Generator Submission | Critic Review | Verdict | Outcome |
|---|---|---|---|---|
| **Round 1** | Initial scaling endpoint with naive regex `^(\d+(?:\.\d+)?)` and fixed `:.2f` formatting. | Critic discovered 5 defects: mixed numbers corrupted (`1 1/2 cups` -> `2 1/2 cups`), small factors rounded down to zero, unbounded factors (`1e308` -> `inf`), unhandled leading whitespace, and missing 404. | **REVISE** | 5 required fixes communicated to generator. |
| **Round 2** | Revision 1: added whitespace handling, protected mixed fractions, added `le=1000`, added 404 handler. | Critic verified mixed fractions and upper bound, but caught 2 regressions: missing lower bound on factor (`factor=0` / `factor=1e-300` produced zeroed items), and range expressions (`2-3 eggs` -> `4-3 eggs`). | **REVISE** | 2 required fixes communicated to generator. |
| **Round 3** | Revision 2: enforced `ge=0.001` and `le=1000`, protected hyphenated ranges, clean integer/decimal formatting. | Critic re-tested all edge cases against rubric; all criteria passed cleanly with 0 defects. | **SIGN-OFF** | Final approval granted and merged. |

---

### Verbatim Generator-Critic Exchanges

#### Round 1 Exchange
- **Generator (Round 1 Submission):**
  > "Implemented `GET /recipes/{id}/scaled?factor=2`. Uses regular expression matching on the start of the ingredient string to scale quantities and formats output with 2 decimal places. 4 basic tests pass."
- **Critic Feedback (`reviews/critique-round-1.md`):**
  > "**VERDICT: REVISE**  
  > 1. *Mixed Fractions:* `1 1/2 cups flour` with `factor=2` returns `2 1/2 cups flour`. The regex scales only the leading `1`, resulting in invalid amounts.  
  > 2. *Small Factor Rounding:* Fixed `:.2f` formatting rounds `0.1 tsp salt` * 0.01 to `0.00 tsp salt`. Non-zero ingredients must not truncate to zero.  
  > 3. *Unbounded Factor:* `factor=1e308` returns `inf kg` with HTTP 200, and non-positive factors (`0`, `-1`) do not return 422.  
  > 4. *Leading Whitespace:* `" 200 g flour"` fails to scale due to rigid anchor.  
  > 5. *Missing 404:* Unknown recipe ID crashes instead of returning HTTP 404."

#### Round 2 Exchange
- **Generator (Revision 1 Response):**
  > "Addressed all round 1 feedback:  
  > - Added `\s*` to tolerate leading whitespace.  
  > - Mixed fractions (`1 1/2 cups`) are detected and preserved unchanged per documented policy.  
  > - Added upper bound constraint `le=1000` to prevent infinite or extreme numbers.  
  > - Added 404 error response for unknown recipe IDs.  
  > - Added 24 new unit tests."
- **Critic Feedback (`reviews/critique-round-2.md`):**
  > "**VERDICT: REVISE**  
  > Improvements confirmed: mixed fractions and upper bound are now protected. However, two issues remain:  
  > 1. *Missing Lower Bound:* There is no `ge=0.001` constraint. Requesting `factor=0` or `factor=1e-300` returns HTTP 200 with zeroed quantities. Factor must be strictly bounded (`ge=0.001, le=1000`).  
  > 2. *Range Expressions:* `"2-3 eggs"` scales the leading `2` into `"4-3 eggs"`, which corrupts range semantics. Ranges must be preserved unchanged."

#### Round 3 Exchange
- **Generator (Revision 2 Response):**
  > "Addressed all round 2 feedback:  
  > - Enforced strict factor bounds `ge=0.001, le=1000` via FastAPI Query constraints; invalid/zero/negative/out-of-bounds factors return HTTP 422.  
  > - Updated lookahead regex `(?![/-]\d)` so hyphenated ranges like `2-3 eggs` are preserved unchanged.  
  > - Clean formatting helper removes trailing zeros and prints integers without floating decimals (`400` instead of `400.0`).  
  > - Full test suite in `test_scaling.py` now covers all boundary and error cases."
- **Critic Feedback (`reviews/critique-round-3.md`):**
  > "**VERDICT: SIGN-OFF**  
  > Re-verified all test cases. Leading quantities scale accurately, fractions/ranges/mixed numbers are safely preserved, factor bounds are enforced, and test coverage is comprehensive. Excellent work."

---

## 3. Autonomy Levels and Supervision

| Agent Role | Allowed Capabilities | Restricted Capabilities | Supervision & Guardrails |
|---|---|---|---|
| **Agent A (Task 1)** | Read codebase, edit `main.py` (append only), create `test_shopping_list.py`, run pytest within `recipe-task-a`. | No branch switching, no pushing to remote, no merging into `main`, no touching other files. | Confined strictly to `../recipe-task-a` worktree; diff reviewed by human coordinator prior to merge. |
| **Agent B (Task 2)** | Read codebase, edit `list_recipes` in `main.py`, create `test_tag_filter.py`, run pytest within `recipe-task-b`. | No branch switching, no pushing to remote, no merging into `main`, no touching other files. | Confined strictly to `../recipe-task-b` worktree; diff reviewed by human coordinator prior to merge. |
| **Generator Agent** | Edit `main.py` and `test_scaling.py`, run pytest. | No merging, no pushing, cannot mark reviews as approved. | Revisions triggered strictly through critic feedback forwarded by coordinator. |
| **Critic Agent** | Read code and tests, execute test suite, write review files in `reviews/`. | Read-only with respect to application source code; strictly prohibited from writing fixes. | Bound strictly to `reviews/RUBRIC.md`; every criticism required reproducible failure evidence. |
| **Human Coordinator** | Orchestrated worktrees, executed git merges, verified full regression suite, pushed to GitHub. | Did not write application logic manually; acted as referee and integrator. | Monitored test outputs and enforced formatting guardrails (`black`, `ruff`). |

---

## 4. What I Learned

Running agents concurrently through git worktrees proves that filesystem isolation is necessary but not sufficient: clean parallel execution requires clear architectural boundaries, such as appending distinct endpoints and isolating test files. The generator-critic loop demonstrated that an adversarial, read-only critic bound to an objective rubric is extraordinarily effective at catching edge cases—such as partial mixed-fraction scaling, floating-point underflow, and range corruption—that a single generator agent with green baseline tests completely overlooked. Moreover, strict autonomy separation between code generation and evaluation prevents premature sign-offs, creating a reliable and deterministic engineering workflow.

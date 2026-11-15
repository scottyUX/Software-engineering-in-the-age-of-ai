# Week 7 — Writeup: Agent Orchestration (The Recipe Box Sprint)

## 1. Part I — Concurrent Agents & Git Worktrees

### Tasks Selected
- **Task A (Agent A):** Shopping list generation (`GET /shopping-list?ids=1,2,3`) — fetches ingredients across specified recipe IDs and deduplicates items case-insensitively.
- **Task B (Agent B):** Tag filtering (`GET /recipes?tag=breakfast`) — returns only recipes containing the requested tag.

### Git Worktree Setup & Isolation
To prevent parallel agents from interfering with shared working directories or stepping on unstaged changes, we isolated their environments into distinct worktrees:
```bash
git worktree add ../recipe-task-a -b week7-task-a
git worktree add ../recipe-task-b -b week7-task-b
```
Each agent developed independently within its respective folder (`/Users/omertarikcandir/recipe-task-a` and `/Users/omertarikcandir/recipe-task-b`) and committed changes to its dedicated branch.

### Merge Collisions & Resolution
When merging both branches back into the parent branch (`week7-omertarikcandirIsu`):
- `git merge week7-task-a` succeeded via fast-forward.
- `git merge week7-task-b` triggered textual merge conflicts in `main.py` and `test_main.py` because both agents appended new endpoints and test functions at identical offsets.
- **Orchestration Resolution:** As the supervising orchestrator, we performed a structured semantic merge combining both endpoints (`/shopping-list` and `/recipes?tag=...`) and unified the test suite into a single coherent test file without regressing either feature.

---

## 2. Part II — Generator–Critic Loop Transcript (Ingredient Scaling)

We implemented **Task 3: Ingredient scaling (`GET /recipes/{id}/scaled?factor=2`)** through a multi-turn **Generator–Critic** loop over 3 rounds (2 revision rounds).

### Round 1: Initial Generation & First Critique
- **Generator (Round 1):** Produced basic scaling using simple string replacement:
  ```python
  # Initial draft
  @app.get("/recipes/{recipe_id}/scaled")
  def get_scaled_recipe(recipe_id: int, factor: float):
      ...
      scaled = [ing.replace("200", str(200 * factor)) for ing in recipe["ingredients"]]
  ```
- **Critic (Round 1 Rubric: Correctness, Tests, Edge Cases):**
  - **Verdict:** REJECTED ❌
  - **Feedback:** "Hardcoding string replacements breaks immediately for any arbitrary ingredient quantity. Use regex extraction (`re.match(r'^(\d+(?:\.\d+)?)\s*(.*)$')`) to parse leading numeric amounts. Missing negative/zero factor validation (`factor > 0`). Missing 404 test for unknown recipe."

### Round 2: First Revision & Second Critique
- **Generator (Round 2):** Refactored to regex-based quantity scaling and added `gt=0` Query validation:
  ```python
  def _scale_ingredient(text: str, factor: float) -> str:
      match = re.match(r"^(\d+(?:\.\d+)?)\s*(.*)$", text.strip())
      if match:
          num = float(match.group(1)) * factor
          return f"{num} {match.group(2)}"
      return text
  ```
- **Critic (Round 2 Rubric: Number Formatting & Non-numeric Ingredients):**
  - **Verdict:** REJECTED ❌
  - **Feedback:** "Scaling whole numbers produces awkward float representations in the UI (e.g. `2 * 2` becomes `'4.0 eggs'` instead of `'4 eggs'`). Format integer floats cleanly with `int(val) if val.is_integer() else round(val, 2)`. Ensure non-measured items (e.g. 'pinch of salt') pass through unchanged."

### Round 3: Second Revision & Final Approval
- **Generator (Round 3):** Refined number formatting and handled non-numeric strings cleanly:
  ```python
  def _scale_ingredient(text: str, factor: float) -> str:
      match = re.match(r"^(\d+(?:\.\d+)?)\s*(.*)$", text.strip())
      if match:
          orig_num = float(match.group(1))
          unit_and_name = match.group(2)
          scaled_num = orig_num * factor
          formatted_num = int(scaled_num) if scaled_num.is_integer() else round(scaled_num, 2)
          return f"{formatted_num} {unit_and_name}" if unit_and_name else str(formatted_num)
      return text
  ```
- **Critic (Round 3):**
  - **Verdict:** APPROVED ✅
  - **Assessment:** "Clean regex parsing, integer-friendly string formatting, rigorous FastAPI parameter validation (`gt=0`), and 100% test pass rate with edge case coverage."

---

## 3. Autonomy Levels & Human Supervision
- **Agent A & Agent B (Task Execution):** Granted high operational autonomy within their isolated worktrees (writing endpoints, models, and tests).
- **Merge & Integration:** Kept under human supervision; automated merges were blocked when git conflicts occurred, requiring explicit architectural arbitration.
- **Generator-Critic Loop:** Configured with semi-autonomous revision cycles where the critic operated under a strict quality rubric before permitting code integration.

---

## 4. What I Learned (Orchestrating Agents)
Orchestrating concurrent coding agents unlocks massive parallel speedups, but concurrency safety is fundamentally an architectural challenge rather than an LLM prompt problem. Isolating agents using git worktrees guarantees clean filesystem boundaries, yet semantic coordination remains necessary when parallel agents inevitably edit shared entrypoints (like API routing tables). Furthermore, implementing a generator–critic loop demonstrates that LLMs achieve vastly superior output quality when decoupled into specialized generation and critical evaluation roles, as internal blind spots in the initial draft are methodically eliminated across disciplined review rounds.

# Week 7 Writeup: Recipe Box Sprint

**Agents:** Claude Code (Claude Opus 5.5). One coordinating session started separate background
agents, each with its own prompt, working directory and context. **Result:** Tasks 1, 2 and 3 are
on `main`. `pytest` gives 79 passed.

| Part | Task | Branch / worktree | Agent(s) |
| --- | --- | --- | --- |
| I | 1. Shopping list | `task-a` in `../recipe-task-a` | agent A |
| I | 2. Tag filter | `task-b` in `../recipe-task-b` | agent B, at the same time as A |
| II | 3. Ingredient scaling | `task-c` in `../recipe-task-c` | generator + critic |

## Part I: Concurrent agents

### Worktree setup
```bash
git worktree add ../recipe-task-a -b task-a
git worktree add ../recipe-task-b -b task-b
git worktree add ../recipe-task-c -b task-c   # Part II
```
Both agents started at 14:40:07 (local time). Agent B committed `0117d5f` at 14:40:48 and agent A
committed `485ea93` at 14:41:04, so the two ran at the same time, each in its own folder. Each one
had its own working tree, its own branch and its own `recipes.db`, so neither could see the other's
unfinished files.

### How I kept them from colliding
Both tasks touch `main.py` and both need tests, so a worktree alone would not prevent a merge
conflict. Each prompt therefore drew a boundary:

- **Agent A** could only *add* a new route at the end of `main.py` and had to put its tests in a new
  `test_shopping_list.py`.
- **Agent B** could only change the body of the existing `list_recipes` and had to put its tests in a
  new `test_tag_filter.py`.
- Neither could touch `test_main.py`, `README.md`, `docs/` or `static/`, push, merge or rebase.
- Tests had to create their own data and not rely on ids (agent B used uuid-suffixed tags), because
  in this app all tests share one SQLite file.

**Result:** `git merge task-a` and then `git merge task-b` were both clean, with no conflict. After
the merge I ran the full suite (20 passed) and an integration check through `TestClient`: the tag
filter and the shopping list work together on the same data.

### Collisions and risks I saw
- **Shared database.** All tests write to one `recipes.db`. The rule "create your own data, never
  assume ids" is what kept the two new test files from breaking each other. The Part II generator
  later moved its tests to a per-test `tmp_path` database.
- **Branching from an old `main`.** `task-c` was cut before A and B landed. Its refactor of
  `get_recipe` into `_load_recipe` sits right next to where A added `/shopping-list`, so merging
  `task-c` gave a real **content conflict in `main.py`**. I resolved it by keeping both sides
  (`get_recipe` and scaling, then the shopping list). After that, all 79 tests passed and an HTTP smoke
  test against `uvicorn` passed too.
- **Semantic overlap, not textual.** The shopping list merges `"2 eggs"` and `"3 eggs"` as two
  items because it does not parse quantities, while Task 3 does parse them. Each choice is
  documented and tested, but the two features disagree about what an ingredient is. Parallel agents
  will not notice that kind of overlap on their own.

## Part II: Generator-critic loop (Task 3)

The rubric is [`reviews/RUBRIC.md`](reviews/RUBRIC.md) (correctness, tests, clarity, each PASS/FAIL
with evidence, ending in `VERDICT: SIGN-OFF` or `VERDICT: REVISE`). The generator and the critic
were separate agents: the critic could not edit code or tests, and the generator only saw
critiques through me.

### Transcript

| Time | Commit | Step | Outcome |
| --- | --- | --- | --- |
| 14:42 | `a44f6fb` | **Generator round 1** | `/recipes/{id}/scaled`, leading-number regex, `:.2f` formatting, 31 tests |
| 14:44 | `d08f828` | **Critic round 1** ([critique](reviews/critique-round-1.md)) | **REVISE**: correctness FAIL, tests FAIL, 7 required changes |
| 14:46 | `596ed9e` | **Generator round 2** (revision 1) | Fixed items 1-6, 54 tests |
| 14:49 | `170d5d0` | **Critic round 2** ([critique](reviews/critique-round-2.md)) | **REVISE**: 1 required change |
| 14:50 | `4852360` | **Generator round 3** (revision 2) | Added a lower bound, 62 tests |
| 14:51 | `4c73ba6` | **Critic round 3** ([critique](reviews/critique-round-3.md)) | **SIGN-OFF** |

**Critic round 1** reproduced each bug through `TestClient`:
1. `1 1/2 cups flour` x2 returned `2 1/2 cups flour` (should be 3 cups), although the code comment
   said fractions were left alone.
2. `0.1 tsp salt` x0.01 returned `0 tsp salt` because of fixed 2-decimal rounding.
3. `factor=1e308` returned 200 with `inf kg`, and `1e300` returned 300-digit numbers.
4. Arabic-Indic and full-width digits were scaled and silently rewritten in ASCII.
5. ` 200 g sugar` (leading space) was silently left unchanged.
6. `flour, 200 g` had no test.
7. `task-c` conflicted with the new `main` (see Part I).

**Generator round 2** left mixed numbers unchanged on purpose. It formatted values below 1 with 2
significant figures, added `le=1000`, used `re.ASCII`, stripped leading whitespace, and listed every
unchanged case in the parsing comment. It could not do item 7: the permission system blocked the
generator's `git merge main`, because its original instructions said not to merge. I did not
work around that block. I asked my user, and with their approval I did the merge myself after the
loop as an integration step.

**Critic round 2** checked items 1-6 and found the same problem at the other end: there was no
lower bound, so `factor=5e-324` returned `0 tsp salt` again and `1e-300` gave 300-character
numbers. **Generator round 3** added `MIN_FACTOR = 0.001` (`ge=`) with tests for `0.0009`, `1e-300`
and `5e-324`. It also left scientific notation (`1e3 g`) unchanged on purpose, from a critic note
that was not blocking. **Critic round 3** re-ran every attempt and signed off. The notes it left
are only inputs that follow the documented rule (`1st layer` -> `2st layer`).

## Autonomy levels and supervision

| Agent | Allowed | Not allowed | How I supervised |
| --- | --- | --- | --- |
| A, B | Edit files in their own worktree, run pytest, commit on their branch | Other folders, push, merge, rebase, shared files | Boundaries in the prompt; I read the diffs, merged, re-ran the suite |
| Generator | Edit `main.py` and `test_scaling.py`, run pytest, commit | Push, merge, rebase | It only received critiques that I forwarded |
| Critic | Run code and tests, write and commit `reviews/critique-round-N.md` | Edit code or tests, merge | Bound to the rubric; only reproduced problems count |
| Me (coordinator) | Merge to `main`, resolve conflicts, push | Bypass a permission block | Asked my user before doing the merge the generator was refused |

No agent could push, so nothing reached GitHub without my review of the diff.

## What I learned

Worktrees isolate files, not decisions. The clean merge in Part I came from the prompt rules
(append-only `main.py`, separate test files), and the one real conflict came from a branch cut
before the others landed. A critic that has to reproduce each problem was much more useful than a
generic review. It found five real problems (three wrong results, two undocumented behaviors) that 31 passing tests had missed, and in round 2 it found
that a fix for huge factors had left the same hole for tiny factors. The loop also needs a referee:
in round 2 a request I forwarded to the generator was correctly refused by its permission system,
so the person running the loop has to own merges and anything outside the agents' limits.

# Week 8 Agent Orchestration Submission: Mehmet Emin Akkaya

Repository: https://github.com/mehmeteminakkaya/week7-recipe-box
Writeup: https://github.com/mehmeteminakkaya/week7-recipe-box/blob/main/writeup.md

- **Part I — two agents concurrently, in git worktrees.** Task 1 (shopping list,
  `GET /shopping-list?ids=…`) ran in `wt-task-a` on `task/shopping-list` and task 2 (tag
  filter, `GET /recipes?tag=…`) ran in `wt-task-b` on `task/tag-filter`; both agents started
  in the same minute, each could only see its own worktree, and neither was allowed to push,
  merge or touch the other's files. Both landed: `9fa4268` → merge `7722df7`, `74fbd36` →
  merge `411f7eb`. They edited `main.py` in different regions (append at EOF vs. modify
  `list_recipes`) so both merges applied cleanly; the suite went 3 → 22 tests. Agent reports
  are verbatim in `docs/transcripts/part-i-agent-reports.md`.
- **The collision that did happen** was in Part II: its branch also appends at the end of
  `main.py`, and rebasing onto the merged main produced a real conflict there — resolved by
  keeping the preamble once and both endpoints. That is the concurrency risk the writeup
  documents.
- **Part II — generator–critic loop with ≥2 revision rounds.** Task 3 (ingredient scaling,
  `GET /recipes/{id}/scaled?factor=…`) ran against `docs/RUBRIC.md`. Round 1: **REVISE** with
  four findings — `%g` formatting broke identity and truncated large numbers, `factor` was
  unvalidated (0, negative, `inf`, `nan`), and `"1/2 cup"` / `"2,5 kg"` were corrupted.
  Round 2: **REVISE**, no source defect, two test gaps that survived mutation (end-of-string
  boundary, fractional factor). Round 3: **SIGN OFF**. Transcripts:
  `docs/transcripts/round-1-critic.md`, `round-2-critic.md`, `round-3-critic.md`.
- 43 tests pass on `main` (21 for the scaling task); `black --check` and `ruff check` clean.

# Week 7 Submission: Arda Kocadoru

**Repository:** https://github.com/ardakocadoru/week7-recipe-box
**Write-up:** https://github.com/ardakocadoru/week7-recipe-box/blob/main/writeup.md

- **Part I, concurrent agents:** tag filter (Agent A, `task-a`) and favorites (Agent B,
  `task-b`) ran at the same time in two git worktrees (started 10:42:22 and 10:42:23,
  committed 10:42:53 and 10:43:07). I chose two tasks that meet in the code: the tag filter
  changes `list_recipes`, and favorites changes the schema and `_row_to_recipe` it relies on.
  Each agent had a function-level edit boundary and its own test file. The merge had no
  textual conflict, but the merged suite failed: Agent A's shape test broke on Agent B's new
  field. I fixed it and added a test that uses both features together.
- **Part II, generator–critic loop:** ingredient scaling. One generator session, a new
  read-only critic session every round, and a rubric written beforehand (`docs/RUBRIC.md`).
  REVISE, REVISE, REVISE, then ACCEPT: three revision rounds, including a regression the
  round-2 fix introduced (`1-1/2 cups` read as a range). Tests grew from 58 to 185. Every
  critique is committed unedited in `reviews/`, and the generator's report for each round is
  in `agent-logs/`.
- **Autonomy:** the agents could edit and commit only inside their own worktree, only I
  merged, and the critic could only read. The write-up has the full autonomy table and what I
  learned.

# Week 7 Submission — Agent Orchestration: The Recipe Box Sprint

Repository: https://github.com/berfinaksoyy/recipe-box-week7
Writeup: https://github.com/berfinaksoyy/recipe-box-week7/blob/main/writeup.md

- **Part I:** tasks 1 (shopping list) and 2 (tag filter) ran in two Antigravity CLI agents at the same time, each in its own git worktree (`task-a`, `task-b`). Both landed in `main`; merging the second produced a real conflict in `test_main.py`, resolved by keeping both test blocks.
- **Part II:** task 3 (ingredient scaling) with a generator–critic loop: 4 critic rounds against `docs/RUBRIC.md`, 2 generator revision rounds. A "fresh eyes" critic found an HTTP 500 crash after an early approval; the last round found two regressions that were left open when the agent quota ran out. Transcripts are in `docs/transcripts/`.
- The writeup covers worktree setup, collisions and risks, autonomy levels and supervision, and what I learned.

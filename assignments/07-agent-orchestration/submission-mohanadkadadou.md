# Week 7 Submission (Agent Orchestration): Mohanad Kadadou (2309115218)

Repository: https://github.com/mohanadkadadou/week7-recipe-box

- **Part I, concurrent agents:** tag filter and shopping list implemented by two agents at the same time, each in its own git worktree and branch (both committed within the same second); `recipes.db` is per worktree. One real append/append conflict in `test_main.py`, resolved by hand.
- **Part II, generator-critic loop** on ingredient scaling with a read-only critic and a rubric: round 1 REVISE, round 2 REVISE (the revision introduced a crash on zero quantities), round 3 SIGN-OFF, so two full revision rounds. Verbatim transcripts in `docs/generator-critic/`; 55 tests pass.
- **Writeup:** concurrency notes, autonomy levels and supervision, and what I learned; it states that the agents are Claude subagents and that the autonomy limits were enforced by prompts: [writeup.md](https://github.com/mohanadkadadou/week7-recipe-box/blob/main/writeup.md).

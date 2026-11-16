# Week 7 Submission: Ezzgiturann

**Repository:** https://github.com/Ezzgiturann/week7-recipe-box
**Writeup:** https://github.com/Ezzgiturann/week7-recipe-box/blob/main/writeup.md
**Agent logs (prompts, every round, tool calls):** https://github.com/Ezzgiturann/week7-recipe-box/tree/main/agent-logs

## Part I: concurrent agents
- **Tasks:** Shopping list (agent A) and Tag filter (agent B). Each agent was a Claude Code CLI session in its own git worktree, and both started at 17:53:07.
- **Merge:** `main.py` merged automatically. `test_main.py` conflicted because both agents added a fixture named `temp_db`.
- **The naive "keep both" resolution was silently wrong:** all 20 tests passed, but the shopping-list tests ran on B's seeded data. I verified this with a probe test and resolved it with one shared autouse fixture.
- **Integration check:** I ran tag filter → shopping list against the merged app.

## Part II: generator–critic loop (Ingredient scaling)
- **Setup:** the generator ran in one resumed session. The critic was a fresh session each round, read-only, using my rubric.
- **Rounds:** 8 rounds, of which **7 were revisions**, each committed separately. Tests went 43 → 182.
- **Human decision:** after round 5 I changed the acceptance criterion for both agents.
- **Result:** the critic did not sign off. The first round-7 attempt hit the Claude usage limit, so its partial edit was discarded and rounds 7–8 were rerun after the reset. The loop stopped at its 8-round limit: from round 3 on, Tests and Clarity passed, and Correctness failed each round on a rarer spelling of the same pattern. The open finding and my analysis are in the writeup.

## Autonomy
- **Edits:** automatic.
- **Tools:** an allowlist per role, with no git for the agents and no file edits for the critic.
- **Integration:** commits, merges and conflict resolution were done by me.

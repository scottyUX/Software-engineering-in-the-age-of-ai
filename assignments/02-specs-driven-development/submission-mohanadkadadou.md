# Week 2 Submission: Mohanad Kadadou (2309115218)

Repository: https://github.com/mohanadkadadou/spec-kit-week2

- Built the quote-of-the-day page with GitHub Spec Kit (constitution, specify, plan, tasks, implement, converge); one commit per stage, committed `.specify/` and `specs/001-quote-of-the-day/`.
- Agent: Claude Code (integration key `claude`, `specify init ... --ignore-agent-tools` because the `claude` CLI binary is not on PATH).
- Documented refinement: the first `/speckit-converge` found that "New quote" repeated the same quote 8.4% of the time and that favorites were stored by array index (contradicting the spec's stable identity). I changed the spec and plan first (`pickDifferent`, stable string ids), then re-implemented: 0 repeats in 500 presses.
- Convergence reached; 13 unit tests pass (`npm test`). Reflection in [writeup.md](https://github.com/mohanadkadadou/spec-kit-week2/blob/main/writeup.md).

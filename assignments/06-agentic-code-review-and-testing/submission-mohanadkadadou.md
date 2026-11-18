# Week 6 Submission (AI Code Review & Testing): Mohanad Kadadou (2309115218)

Repository: https://github.com/mohanadkadadou/week6-habit-tracker

- **Guardrails:** `scripts/check.sh` (black + ruff + pytest) and a GitHub Actions CI that runs it; evidence that failing tests, formatting and lint errors fail the build (including a deliberately failing CI run).
- **Two PRs** (left open so the reviews are visible): [#1 streak](https://github.com/mohanadkadadou/week6-habit-tracker/pull/1) and [#2 validation](https://github.com/mohanadkadadou/week6-habit-tracker/pull/2). Each: agent one-shot implementation, my manual line-by-line review with fixes, an AI review comment, and fixes from it.
- **AI reviewer used:** an independent Claude (Sonnet 5.5) subagent that saw only the diff. Graphite Diamond and CodeRabbit were not used because their GitHub apps are not installed on my account; this is stated in the writeup.
- **Human vs AI comparison** with examples (e.g. the AI found zero-width-character names and a weak assertion that I missed; my hands-on test showed a regex guard worked by accident, which the static review praised) and what I learned about trusting AI reviews: [writeup.md](https://github.com/mohanadkadadou/week6-habit-tracker/blob/main/writeup.md).

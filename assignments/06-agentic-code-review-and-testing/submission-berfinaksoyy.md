# Week 6 Submission — AI Code Review & Testing: The Habit Tracker

Repository: https://github.com/berfinaksoyy/habit-tracker-week6
Writeup: https://github.com/berfinaksoyy/habit-tracker-week6/blob/main/writeup.md

- **Guardrails:** black + ruff + pytest via `scripts/check.sh` and GitHub Actions CI on every push and PR. The unmodified starter failed `black --check`; a deliberately failing test made the check exit with code 1.
- **PR #1 Streak:** https://github.com/berfinaksoyy/habit-tracker-week6/pull/1 — agent commit, my review commit (spec ambiguity, clock-dependent tests, silent skip of bad data), and a fix for CodeRabbit's finding that the API tests still used the real clock.
- **PR #2 Validation:** https://github.com/berfinaksoyy/habit-tracker-week6/pull/2 — agent commit and my review commit (misleading date message, "Value error" prefix, name length limit, future days). CodeRabbit had no actionable comments.
- Implemented with Antigravity CLI (one one-shot prompt per task); AI reviewer: CodeRabbit.

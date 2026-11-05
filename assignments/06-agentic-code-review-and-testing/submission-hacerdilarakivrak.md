# Week 6 Submission — Hacer Dilara Kıvrak

## Assignment
AI Code Review & Testing: The Habit Tracker

## GitHub Repository
https://github.com/hacerdilarakivrak/habit-tracker-ai-review

## Writeup
https://github.com/hacerdilarakivrak/habit-tracker-ai-review/blob/main/writeup.md

## Implemented Features

**Feature 1 — Input Validation**

https://github.com/hacerdilarakivrak/habit-tracker-ai-review/pull/1

- Added validation for empty or whitespace-only habit names.
- Added strict calendar date validation.
- Added automated tests and completed AI code review.

**Feature 2 — Weekly Summary**

https://github.com/hacerdilarakivrak/habit-tracker-ai-review/pull/2

- Implemented a seven-day habit check-in summary endpoint.
- Added tests for duplicate dates, invalid stored dates, timezone-offset inputs, and database isolation.
- Addressed CodeRabbit review feedback.

## Automated Guardrails

- Black for formatting
- Ruff for linting
- Pytest for automated tests
- GitHub Actions for continuous integration

The CI failure detection was verified using an intentionally failing test on a separate branch.

CI evidence: https://github.com/hacerdilarakivrak/habit-tracker-ai-review/actions

## Human and AI Code Review

Both features were manually reviewed and evaluated using CodeRabbit. The `writeup.md` document compares manual review findings with AI review feedback and describes the lessons learned.

# Week 4 Submission (Agentic Codebase Structure): Mohanad Kadadou (2309115218)

Repository: https://github.com/mohanadkadadou/week4-link-shortener

- `AGENTS.md` (61 lines) plus `intent.md`; `CLAUDE.md` imports it (`@AGENTS.md`).
- Scoped instruction: `tests/AGENTS.md` (public-API tests, success and failure, independent tests, behaviour not implementation).
- Reusable workflow: `.claude/skills/implement-feature/SKILL.md` (7 steps, test-first). Extras: pre-commit gate (ruff + pytest) with evidence that it blocks bad commits, a `/test-summary` command, and planner/implementer/reviewer subagent definitions.
- Feature: task 2, click counter (`GET /stats/{code}`) with an idempotent migration for existing databases; 12 tests pass (3 original, 9 new). Plan, implementation and review transcripts are in `docs/transcripts/`; the final review returned ACCEPT.
- Limits, stated in the writeup: the skill was written after the first implementation run and was not invoked by name; plan and review were separate read-only subagents of the same agent, and I fixed the first reviewer's findings (SQLite >= 3.35 guard, a vacuous test).
- [writeup.md](https://github.com/mohanadkadadou/week4-link-shortener/blob/main/writeup.md) (472 words).

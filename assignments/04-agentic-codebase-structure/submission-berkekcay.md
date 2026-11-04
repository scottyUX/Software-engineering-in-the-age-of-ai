# Week 4 Agentic Codebase Structure submission: Berke Eren Akçay

Repository: https://github.com/berkekcay/link-shortener-agent-ready

- `AGENTS.md` (58 lines): what the service does, file map, commands, product boundaries,
  invariants and the change loop. `CLAUDE.md` imports it for Claude Code.
- Scoped instruction: `tests/AGENTS.md` (loaded through `tests/CLAUDE.md` only when working
  under `tests/`).
- Reusable workflow: `.claude/skills/implement-task/SKILL.md`.
- Feature: task 1, custom alias, with 19 new test cases (22 pass). It was built in three
  stages, each in its own commit with its output in `docs/stages/`: a read-only plan, the
  implementation through the skill, and a read-only review that returned ACCEPT.

The planner found that an alias could make a later generated code collide and return a 500,
that `docs` and `redoc` would never redirect, and that fixed aliases break repeated test runs;
all three are covered by tests. Details are in
[writeup.md](https://github.com/berkekcay/link-shortener-agent-ready/blob/main/writeup.md).

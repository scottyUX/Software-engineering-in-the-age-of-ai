# Week 4 Submission (Agentic Codebase Structure): Riza Arslan

**Repository:** https://github.com/xXx0001-crybto/week4-link-shortener

- Agent: Claude Code (VS Code extension).
- `AGENTS.md`: purpose, file map, install/run/test commands, current API, product boundaries, conventions, and the understand → test → implement → verify workflow. `CLAUDE.md` imports it (`@AGENTS.md`).
- Scoped instruction: `tests/AGENTS.md` (public-API tests through the `client` fixture, success and failure cases, independent tests on a fresh temporary database, behaviour not SQL), loaded on demand through `tests/CLAUDE.md`.
- Reusable workflow: `.claude/skills/implement-feature/SKILL.md` (7-step test-first procedure), invoked as `/implement-feature`.
- Feature: task 2, click counter. Redirects count clicks; `GET /stats/{code}` returns `{"url", "clicks"}`, 404 for unknown codes. `init_db` upgrades an existing `links.db` that has no `clicks` column.
- Tests: 9 pass (3 original, 6 new in `tests/test_stats.py`), including the database upgrade case.
- Review returned ACCEPT.
- [writeup.md](https://github.com/xXx0001-crybto/week4-link-shortener/blob/main/writeup.md) answers the six questions.

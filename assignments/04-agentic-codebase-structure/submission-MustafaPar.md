# Week 4 Submission (Agentic Codebase Structure) — Mustafa Par

**Repository:** https://github.com/MustafaPar/week4-agentic-codebase-structure

Completed with Claude Code on the Link Shortener starter. Task 1 (Custom alias) is implemented.

| Deliverable | File |
|---|---|
| Repository guidance (55 lines) | [`AGENTS.md`](https://github.com/MustafaPar/week4-agentic-codebase-structure/blob/main/AGENTS.md), loaded through [`CLAUDE.md`](https://github.com/MustafaPar/week4-agentic-codebase-structure/blob/main/CLAUDE.md) (`@AGENTS.md`) |
| Scoped instruction | [`tests/AGENTS.md`](https://github.com/MustafaPar/week4-agentic-codebase-structure/blob/main/tests/AGENTS.md), surfaced on demand by [`tests/CLAUDE.md`](https://github.com/MustafaPar/week4-agentic-codebase-structure/blob/main/tests/CLAUDE.md) |
| Reusable workflow | [`.claude/skills/implement-feature/SKILL.md`](https://github.com/MustafaPar/week4-agentic-codebase-structure/blob/main/.claude/skills/implement-feature/SKILL.md), invoked as `/implement-feature` |
| Feature and tests | [`main.py`](https://github.com/MustafaPar/week4-agentic-codebase-structure/blob/main/main.py), [`tests/test_main.py`](https://github.com/MustafaPar/week4-agentic-codebase-structure/blob/main/tests/test_main.py) |
| Writeup | [`writeup.md`](https://github.com/MustafaPar/week4-agentic-codebase-structure/blob/main/writeup.md) (479 words) |

- `POST /shorten` accepts an optional `alias` (1–32 characters of `A-Z a-z 0-9 _ -`, not a reserved route name). It returns `409` if the code is already taken and `400` for an invalid alias. Auto-generated codes skip codes already claimed by an alias instead of failing with a 500.
- `pytest`: **14 passed** (3 original and 11 new, covering success, conflict, validation, and collision cases), including on repeated runs and in reverse order.
- Plan, Implement, and Review ran as three separate Claude Code sessions. Their transcripts are in [`docs/sessions/`](https://github.com/MustafaPar/week4-agentic-codebase-structure/tree/main/docs/sessions). The review returned **ACCEPT**.

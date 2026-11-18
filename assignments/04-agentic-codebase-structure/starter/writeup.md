# Week 4 Writeup — Structuring a Repo for Agents

**Agent:** Claude Code 2.1.316 · **Task:** Click counter (task 2) · **Result:** 8 of 8 tests pass

## 1. What is in `AGENTS.md`, and why should it be broadly available?
It covers what the service does, where each file is, how to install, run, and test, the product
boundaries, a few conventions, and the change workflow. It also flags one trap: `GET /{code}`
matches any single path segment. Every task needs this orientation, so it belongs in the one file
the agent always loads. The boundaries stop an agent from adding auth, an ORM, or dependencies.

## 2. What instruction did I scope, and when does it load?
`.claude/rules/testing.md` holds the testing rules: test through `TestClient`, cover success and
failure, keep tests independent, assert observable behavior. Its `paths:` frontmatter
(`test_*.py`, `tests/**/*.py`) means Claude Code loads it only when it reads or edits a matching
file. A task that only reads `main.py` or the docs doesn't need these rules, so loading them every
time would waste context and could distract the agent.

## 3. What procedure does the reusable workflow encode?
`.claude/skills/implement-task/SKILL.md` follows the seven steps the assignment lists: read the
task and guidance, inspect the code and tests, state behavior and affected files, add failing
tests, make the smallest change, run `pytest`, and summarize risks. It adds two repo-specific rules
learned during planning: schema changes must upgrade an existing `links.db`, and failing tests are
fixed in code, never by editing the test.

## 4. How does Claude Code discover or invoke each artifact?
- **`AGENTS.md`:** Claude Code reads it natively when no `CLAUDE.md` exists. I saw it load
  automatically as soon as the agent read a file in `starter/`.
- **Testing rule:** it loads when a file matches its `paths` globs.
- **Skill:** skills in `.claude/skills/` are listed and invoked as `/implement-task` when a session
  starts in `starter/`. My session started in my home folder, so the skill wasn't registered, and
  the agent followed the `SKILL.md` steps as written. That taught me that skill discovery depends on
  where the session starts.

## 5. What did planning or review find that improved the result?
Planning found that the existing `links.db` already had rows in the old three-column table, and
`CREATE TABLE IF NOT EXISTS` would never add the new column. Without an upgrade step, every redirect
would have crashed with "no such column". The review returned **REVISE**: the "unknown code returns
404" test passed even before `/stats` existed, because FastAPI returns 404 for a missing route. I
changed it to also check `{"detail": "unknown code"}`. I then confirmed it fails without the feature
and passes with it, and the second review returned **ACCEPT**.

## 6. What did I learn about structuring a repository for agents?
Structure means putting the right information in front of the agent at the right moment: a
short always-loaded file for direction, scoped rules for local detail, and a skill for repeatable
procedure. Separate plan and review stages each caught a real problem a single pass would have
shipped.

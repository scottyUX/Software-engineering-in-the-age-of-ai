# Week 6 Submission: Ezzgiturann

**Repository:** https://github.com/Ezzgiturann/week6-habit-tracker
**Writeup:** https://github.com/Ezzgiturann/week6-habit-tracker/blob/main/writeup.md
**Coding agent:** Claude Code (one-shot prompt per feature) · **AI reviewer:** CodeRabbit

## Guardrails
- black, ruff and pytest run through `check.sh`, with GitHub Actions CI on every push and PR.
- The unmodified starter failed both linters (ruff E501 ×2, black).
- A deliberately failing test made the check exit with code 1.
- CI first failed because of an unpinned black version. Pinning tool versions fixed it.

## PR #1: Streak (https://github.com/Ezzgiturann/week6-habit-tracker/pull/1)
- **Commits:** agent's one-shot output → 2 manual-review fixes → 1 CodeRabbit fix
- **My review found:**
  - the agent falsely claimed `"2026-3-1"` would be parsed; it was actually dropped silently
  - the tests polluted the real `habits.db`
- **CodeRabbit found:** on Python 3.11+, `date.fromisoformat` accepts `20260314`, so behavior differed between my local 3.9 and CI's 3.12. Fixed, with a regression test.

## PR #2: Validation (https://github.com/Ezzgiturann/week6-habit-tracker/pull/2)
- **Commits:** agent's one-shot output → 1 manual-review fix → 1 CodeRabbit fix
- **My review found:**
  - invisible-character names (`"\u200b"`) were accepted
  - two different error shapes
  - 422 is returned before 404
  - the agent deleted `habits.db` outside its scope
  - a merge conflict with PR #1
- **CodeRabbit:** rated test database pollution Major. I had listed it as a known limit, then fixed it.

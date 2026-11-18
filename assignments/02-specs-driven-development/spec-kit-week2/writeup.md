# Week 2 Writeup: Spec-Driven Development with Spec Kit

**Agent**: Claude Code, using Spec Kit 1.2.5 with `--integration claude`. The agent ran each stage by
following that stage's generated `.claude/skills/speckit-*/SKILL.md` file.

## Prompts given to each skill

```text
/speckit-constitution Create principles focused on code quality, testing, and maintainability.
/speckit-specify A quote-of-the-day page: one random quote from a built-in list, a "New quote" button, and favoriting that persists across reloads.
/speckit-plan Use plain HTML/CSS/JavaScript, no backend; persist favorites in localStorage.
/speckit-tasks
/speckit-implement
/speckit-converge
/speckit-implement
/speckit-converge
```

## Spec refinement: before and after

The first implementation passed all 12 of its tests, but "New quote" sometimes appeared to do
nothing. Measuring 100,000 presses showed that 8,293 (8.3%) picked the quote already on screen. The
code matched the spec, so the spec was the problem, and I changed the spec first.

| | Before | After |
|---|--------|-------|
| **FR-003** | "...replaces the shown quote with one chosen at random from the built-in list." | "...replaces the shown quote with one chosen at random from the other quotes in the built-in list, so that pressing it always visibly changes the quote." |
| **US2 scenario** | "...a quote from the built-in list replaces it." | "...a different quote from the built-in list replaces it, every time." |

**Change in output**: Implementation then added `pickDifferentQuote`, and the same measurement fell to
0 unchanged presses out of 100,000. The page test also became stricter: it now fails if any of 50
presses leaves the quote unchanged.

## Convergence outcome

- **Pass 1**: 4 gaps, recorded as tasks T015–T018 in `tasks.md`, plus the unfinished T014: the repeated
  quote (HIGH), no keyboard test for FR-008, no timing test for SC-001, and no recorded quickstart
  results.
- **Pass 2**: **Converged**, with `tasks.md` left unchanged.
- **Final tests**: 15 of 15 pass with `node --test`, including real-page tests in headless Chrome.

## What I learned

SDD felt like overhead for a page this small, because writing a constitution, a data model, and
contracts took longer than the code itself. It paid off when the repeated-quote bug appeared: all the
tests passed because they were built from the same weak sentence, so I could see that the
requirement was wrong and fix it at the source. Requiring an independent test for each user story
also exposed that gap, since "confirm the quote is replaced" did not always hold. Next time I would
check that each requirement describes what the user sees, not just what the system does.

# Quote of the Day Constitution

## Core Principles

### I. Code Quality

Code MUST be readable without explanation: descriptive names, small single-purpose functions, and
no dead code. Logic that decides behavior MUST be kept separate from code that touches the page or
browser storage, so that it can be read and tested on its own.

### II. Testing (NON-NEGOTIABLE)

Every functional requirement MUST be covered by at least one automated test or, where automation
is impractical, a written manual check in the feature's `quickstart.md`. Tests MUST assert
behavior a user can observe, and all tests MUST pass before work is reported complete.

### III. Maintainability

Dependencies MUST NOT be added without a documented need; the simplest structure that satisfies
the spec wins. Stored data formats MUST tolerate missing or corrupt data, because a browser can
hold data written by an older version of the page.

## Quality Gates

- The spec MUST be reviewed before planning, and the plan before tasks.
- When an artifact is vague or wrong, the spec or plan MUST be corrected first and the code changed
  from it, never the other way round.
- A feature is complete only when `/speckit-converge` reports `Converged`.

## Governance

This constitution takes precedence over other project practices. Every plan MUST include a
constitution check, and any violation MUST be justified in that plan. Amendments MUST update this
file and follow semantic versioning: MAJOR for removing or redefining a principle, MINOR for adding
a principle or section, PATCH for wording fixes.

**Version**: 1.0.0 | **Ratified**: 2026-10-30 | **Last Amended**: 2026-10-30

# Week 6 write-up

## Guardrails

The starter uses three deterministic checks before a pull request is ready:

```text
pytest
black --check .
ruff check .
ruff format --check .
```

`pytest` blocks a build when an assertion fails, Black catches formatting drift, and Ruff catches
common correctness issues such as unused imports. I kept the checks small enough to run locally and
documented the same commands in the starter README.

## Two feature branches and reviews

### Feature 1 — validation

Branch: `week6-validation-gaurijain21`.

My manual review focused on whether validation happened before database writes, whether whitespace
was normalized consistently, and whether malformed calendar dates were rejected rather than merely
pattern-matched. CodeRabbit was enabled on the PR; its review is the second pass over the same
boundary cases and test coverage.

### Feature 2 — weekly summary

Branch: `week6-weekly-summary-gaurijain21`.

My manual review focused on the seven-day boundary: today and six previous days are included, the
day before that is excluded, and an unknown habit returns 404 instead of an empty success. I also
checked that the route delegates to a deterministic helper so tests can inject a fixed date. The
AI review was useful as an independent check of the SQL range and response shape; the human review
was better at deciding the inclusive-window product rule because that requirement is not encoded in
the SQL itself.

## What I learned

Deterministic tests and linting catch cheap, repeatable mistakes before an LLM review is needed.
An AI reviewer is valuable for a second perspective, but its comments still need to be checked
against the task's product semantics and the actual tests. I am comfortable trusting AI review for
finding likely gaps, not for deciding whether a boundary rule is correct. The safest workflow is
guardrails first, human diff review second, and AI review as an additional signal.

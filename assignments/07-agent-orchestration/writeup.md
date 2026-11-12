# Week 7 — Agent Orchestration Write-up

Repository: https://github.com/gaurijain21/AI-Augmented-Software-Engineering

## Concurrent work

I split the independent task list into two small feature branches so the work could
run without sharing a working directory:

| Agent | Task | Worktree | Result |
| --- | --- | --- | --- |
| Agent A | Tag filter (GET /recipes?tag=...) | assignment-07-tag-filter-publish | Exact-tag filtering with tests |
| Agent B | Shopping list (GET /shopping-list?ids=...) | assignment-07-shopping-list-publish | First-seen de-duplication with tests |

Both worktrees started from origin/main and were limited to the Week 7 starter.
The tasks had disjoint implementation areas: Agent A changed the recipe-list
query path, while Agent B added a new endpoint. I merged each branch into the
submission branch and resolved the expected shared-test-file conflict by combining
the test cases. The main collision risk was SQLite state leaking between tests, so
the new test data uses unique tags and the final checks run from the starter
directory only.

## Generator–critic loop

The third task was ingredient scaling. I used a generator branch and recorded two
revision rounds:

### Generator v0

The generator added GET /recipes/{id}/scaled?factor=2. It multiplied leading
numeric quantities such as 200 g flour and left unquantified ingredients such as
salt unchanged.

### Critic round 1

The critic found three gaps:

1. Zero, negative, and non-finite factors were not rejected.
2. Floating-point output could expose noisy representations.
3. The invalid-factor case needed an explicit test.

### Generator v1 — revision

The generator added positive-finite factor validation, stable g formatting, and
the invalid-factor test. The branch passed 5 tests.

### Critic round 2

The critic checked readability and boundary behavior. It asked for a small
scaling helper, a decimal-factor test, preservation of unquantified ingredients,
and an unknown-recipe 404 test.

### Generator v2 — final revision

The generator extracted _scale_ingredient, added the decimal and 404 tests, and
kept the route response immutable. The critic signed off after 7 generator-branch
tests passed. The final integrated branch contains 9 Week 7 tests covering all
three features.

## Autonomy and supervision

The two concurrent agents had medium autonomy: they could edit the starter
implementation and tests, but not change dependencies, repository settings, or
the submission branch. The generator had medium autonomy for implementation and
low autonomy for acceptance: each revision had to address an explicit critic
finding and pass the focused test suite. I supervised integration, reviewed the
diffs, resolved the shared test-file merge, and ran the final verification.

## What I learned

Worktrees make parallel agent work practical because each agent can keep its own
branch and database state. The main integration cost is not the independent
feature code; it is coordinating shared tests and deciding which behavior is
part of the public contract. A generator–critic loop is most useful when the
critic has a short rubric and produces concrete, testable findings. Small
revision commits also make it easier to see whether the agent actually responded
to review rather than merely rewriting the same solution.

# Week 6 — AI Code Review & Testing

**Student:** OMAR DIAB - 220911379
**Repository:** https://github.com/omar-diab/habit-tracker (public)
**Implementing agent:** Claude Code · **AI reviewer:** CodeRabbit (free OSS plan, default "chill" profile)

## The two PRs

| PR | Task | Commits |
|---|---|---|
| [#1 — `GET /habits/{id}/streak`](https://github.com/omar-diab/habit-tracker/pull/1) | Task 1: streak | one-shot [`2b7076c`](https://github.com/omar-diab/habit-tracker/commit/2b7076c) → my review fixes [`41d4874`](https://github.com/omar-diab/habit-tracker/commit/41d4874) → CodeRabbit fix [`8e44a68`](https://github.com/omar-diab/habit-tracker/commit/8e44a68) |
| [#2 — Validate habit names and check-in days](https://github.com/omar-diab/habit-tracker/pull/2) | Task 2: validation | one-shot [`92aee67`](https://github.com/omar-diab/habit-tracker/commit/92aee67) → my review fixes [`0bac2fc`](https://github.com/omar-diab/habit-tracker/commit/0bac2fc) → same test fix [`51074a0`](https://github.com/omar-diab/habit-tracker/commit/51074a0) |

Each PR description covers the problem, approach, testing and tradeoffs, and lists every issue my
manual review found. CodeRabbit's walkthrough and comments are visible on both PRs.

## Guardrails (Part I)

```bash
pip install -r requirements-dev.txt   # black 26.10.1, ruff 0.17.5, pytest
ruff check .      # lint
black --check .   # format
pytest -q         # tests
```

Settings are in `pyproject.toml` (line length 100; ruff rules `E`, `F`, `W`, `I`, `B`, `UP`).
`.github/workflows/ci.yml` runs all three on Python 3.12, and any failure fails the build.

What they caught in practice:
- **ruff `B008`.** In the one-shot streak code, `Depends()` was used as a default argument. I fixed it with `Annotated`.
- **ruff `I001` and `B904`.** The one-shot validation code had unsorted imports and re-raised without `from`.
- **ruff `F401`/`F821`.** Unused imports and undefined names.
- **black.** It fails the build on any formatting drift. The starter `main.py` needed one `black .` pass.
- **pytest.** On the `ci-failure-demo` branch, I added a test that is meant to fail. CI
  [run 43596885424](https://github.com/omar-diab/habit-tracker/actions/runs/43596885424) failed at the
  "Test (pytest)" step, after lint and format had passed. So a failing test really does fail the build.

## Human review vs. AI review

One caveat about the comparison: I reviewed and fixed each one-shot commit *before* opening the PR,
as the assignment's order says. So CodeRabbit reviewed code that already had my fixes. It could only
find what I missed, not repeat what I had already found.

### PR #1 — streak

**My review (5 issues, all fixed in `41d4874`):**
1. ruff `B008`, `Depends()` as a default, which failed CI.
2. An unknown habit returned `200 {"streak": 0}` instead of 404.
3. A malformed stored day like `"not-a-date"` crashed the endpoint with a 500.
4. The test override for "today" (`app.dependency_overrides`) was never cleared, so it leaked into
   later tests.
5. Test gaps: a break in the run, duplicate check-ins, future days, a month boundary, malformed data,
   and the 404 case.

**CodeRabbit (1 Minor comment, merge risk "Low"):** at
[`test_main.py:41`](https://github.com/omar-diab/habit-tracker/pull/1#discussion_r4573930813), the
tests write through the API into the real `habits.db`, with no cleanup. It suggested a fixture that
points `DB_PATH` to a temp file and runs `init_db()`. This was a real bug that I missed. After
running the suite, my local `habits.db` held 10 leftover habits. I fixed it in `8e44a68` with an
autouse `tmp_path` fixture, then checked that `habits.db` stays empty after `pytest`.

- **Where the AI was better:** test isolation from shared state. I was focused on the endpoint's
  logic and on the clock override, and never asked where the test data was going.
- **Where the AI was worse:** it said nothing about the product decision in the PR description,
  where no check-in today means a streak of 0. That's the main thing a human reviewer should
  question. It also mostly repeated the code back in its walkthrough, and its pre-merge "checks" only
  confirmed the title.

### PR #2 — validation

**My review (6 issues, all fixed in `0bac2fc`):**
1. ruff `I001`, import order.
2. ruff `B904`, re-raising without `from`.
3. A whitespace-only name `"   "` was accepted, because `min_length=1` counts spaces.
4. Since Python 3.11, `date.fromisoformat` also accepts `20260922` and `2026-W39-2`. Those would be
   stored in a different format and break `ORDER BY day` and the streak lookup. It now requires the
   exact `YYYY-MM-DD` form.
5. The empty-name error was a generic pydantic message instead of a clear one.
6. Test gaps: whitespace names, a missing field, `2026-02-30`, other ISO formats, a leap day, and
   checking that rejected check-ins are never stored.

**CodeRabbit (0 actionable comments, merge risk "Minimal"):** it gave an accurate walkthrough,
and it linked this PR to #1, noting that #2 validates dates on the way in while #1 tolerates bad
stored dates. I hadn't connected those two in writing.

- **Where the AI was worse:** the same real-database problem it flagged in #1 is in this PR's tests
  too, since they share `test_main.py`. This time it said nothing, so its findings were not
  consistent from one PR to the next. I applied the same fix here myself (`51074a0`).
- **Where I was better:** the `fromisoformat` issue (point 4) is the kind of quiet edge case that
  only shows up when you test real inputs against the Python version you run. CodeRabbit didn't
  look for it, and it isn't something a linter can catch.

### Summary

| | PR #1 | PR #2 |
|---|---|---|
| Issues I found | 5 (1 from ruff, 4 logic/tests) | 6 (2 from ruff, 4 logic/tests) |
| CodeRabbit comments | 1, valid, which I missed | 0, and it missed the same bug it found in #1 |

## What I learned

The guardrails took the cheap, certain problems off the table. Ruff caught all three lint
violations in the one-shot code before any person or AI read it, so the reviews could focus on behavior. My
line-by-line review found most of the real bugs, because I tested the edge cases instead of only
reading the code. CodeRabbit still found one thing I missed, the shared test database. But it missed
that same issue on the next PR, and it never questioned a product decision. I'd trust an AI reviewer
as an extra pair of eyes that is sometimes right about things I overlooked. I would not treat a
clean AI review as evidence that a PR is correct.

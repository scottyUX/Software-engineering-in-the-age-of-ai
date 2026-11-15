# Week 6 Writeup: Habit Tracker, Guardrails and AI Review

**Implementation agent:** Claude Code (Claude Opus 5.5), one one-shot prompt per task, each in its
own git worktree. **AI reviewer:** CodeRabbit (GitHub app on this public repo). **Tasks:** 1
(Streak) and 2 (Validation).

| PR | Agent's one-shot commit | My review fixes | AI review |
| --- | --- | --- | --- |
| [#1 Streak](https://github.com/bsyilmaz/habit-tracker/pull/1) | [`136a7ee`](https://github.com/bsyilmaz/habit-tracker/commit/136a7ee) | [`e453219`](https://github.com/bsyilmaz/habit-tracker/commit/e453219), then [`503e7bf`](https://github.com/bsyilmaz/habit-tracker/commit/503e7bf) for CodeRabbit's finding | 1 actionable comment |
| [#2 Validation](https://github.com/bsyilmaz/habit-tracker/pull/2) | [`0a563d7`](https://github.com/bsyilmaz/habit-tracker/commit/0a563d7) | [`2fefc06`](https://github.com/bsyilmaz/habit-tracker/commit/2fefc06) | No actionable comments |

The one-shot prompt (same shape for both tasks, only the task line changed):

> Implement Task 1 from docs/TASKS.md: `GET /habits/{id}/streak` returns the current run of
> consecutive days (up to and including today) that have a check-in. Add tests for it in
> test_main.py. Keep the existing tests passing. [...] Before you finish, run `python -m black .`,
> `python -m ruff check .`, `python -m pytest`, and make sure all three pass.

## Part I: Guardrails

| Command | What it catches | Proof it fails the build |
| --- | --- | --- |
| `black --check --diff .` | Formatting drift (line length 100, `pyproject.toml`) | The **starter itself failed**: `1 file would be reformatted` (`main.py`), fixed in the guardrails commit |
| `ruff check .` | Unused imports, undefined names, import order, bugbear patterns, old syntax (`E,W,F,I,B,UP`) | Adding an unused `import os` gives `F401 'os' imported but unused`, exit 1 |
| `pytest` | Behavior regressions | Appending `assert 1 == 2` gives `1 failed, 3 passed`, and `check.sh` exits 1 |

- `./check.sh` (bash) and `.\check.ps1` (PowerShell) run the three in order and stop at the first
  failure.
- GitHub Actions ([`ci.yml`](.github/workflows/ci.yml)) runs the same three steps on every push to
  `main` and every PR. The `checks` job passed on both PRs.
- Dev tools: `pip install -r requirements-dev.txt`.
- `.gitignore` keeps `habits.db` out of the repo.

What the guardrails cannot catch: both agent diffs passed all three checks before my review, yet
both had problems. The checks prove the code is formatted, lint-clean and passing its *own* tests.
They say nothing about whether those tests are the right ones.

## PR #1, Streak: my review vs. CodeRabbit

**My review** of the agent's diff:
1. **Flaky tests.** The tests computed "today" with `date.today()` separately from the server, so a
   run that crossed midnight could fail. The agent had added a `today()` seam "so tests can
   override it", but no test used it. Fix: an autouse fixture pins `main.today`.
2. **Test gaps.** There was no month-boundary case and no future-dated check-in. Both are added.
3. **Redundant code.** `SELECT DISTINCT` and a Python `set` did the same work, so `DISTINCT` is
   dropped.
4. **Undocumented assumption.** "Today" is the server's local date. It is now in the docstring and
   the PR tradeoffs.

**CodeRabbit** posted one finding on `main.py:110`: `day` is a plain `str`, so `"20260302"` is
stored as-is. The streak compares stored values with `date.isoformat()`, so that check-in never
counts and the endpoint returns `0`. **I reproduced it** (`POST` gives 200, then `streak` gives 0).

- **Where the AI was better:** I reviewed the streak logic in isolation and assumed clean data. I
  "knew" PR #2 would validate dates, but PR #1 does not depend on it. CodeRabbit looked at the data
  flow from input to storage to comparison and found the gap between the two PRs. I missed it.
- **Where the AI was worse:** its suggested fix, typing `day` as `date`, is not safe as stated. I
  tested Pydantic: `date` rejects `"20260302"` but **accepts the Unix timestamp `1772409600` (and
  `"1772409600"`) as 2026-03-02**. I fixed it differently: I merged PR #2 into the branch (its
  strict `[0-9]{4}-[0-9]{2}-[0-9]{2}` check plus `fromisoformat`) and added
  `test_streak_cannot_be_fooled_by_a_compact_date` for both inputs. Then I replied on the thread.
- **Not comparable:** CodeRabbit reviewed the code after my fixes, so it could not have found the
  midnight flake or the missing tests. Its walkthrough did list the month and future-date tests
  correctly.

## PR #2, Validation: my review vs. CodeRabbit

**My review** of the agent's diff:
1. **Bug: `\d` is not `[0-9]`.** In Python, `\d` matches any Unicode digit. Arabic-Indic
   `٢٠٢٦-٠٩-٢٢` passed the regex, then failed `fromisoformat`, so the user got the wrong message
   ("not a valid calendar date" instead of the format message). I proved it in a REPL, switched to
   `[0-9]`, and added a test.
2. **Test gap.** There was no case for a leading space in `day` (`" 2026-09-22"`). It is added.
3. **Behavior change, kept on purpose.** Names are now stored stripped (`"  Walk  "` becomes
   `"Walk"`). This is called out in the PR so it is not a surprise.
4. **Accepted tradeoffs.** It returns 422 rather than 400 (FastAPI's standard error shape, with
   Pydantic's "Value error, " prefix). There is no maximum name length.

**CodeRabbit:** "No actionable comments were generated in the recent review." Its walkthrough
summarized the change correctly and rated merge risk "Minimal".

- **Where the AI was worse:** it raised nothing about the API-shape tradeoffs (422 vs. 400, the
  message prefix, no length limit). It also missed that every test, old and new, writes into the
  real `habits.db`. A human reviewer would at least ask about these.
- **Fair caveat:** it saw the code after I had fixed the `\d` bug. A silent review of fixed code is
  weak evidence either way. It does not prove the AI would have caught the original bug.

## What I learned

Guardrails and LLM review catch different things. Black, ruff and pytest passed on both raw agent
diffs. They only check the code against itself, and the real problems were a flaky time-dependent
test and a Unicode `\d`. CodeRabbit was most useful exactly where I was weakest: it traced data
across the boundary between the two PRs. But its suggested fix would have let Unix timestamps in as
dates, so I treat its findings as leads to reproduce, not as patches to apply. My comfort trusting
AI review is "high for finding where to look, low for accepting the fix": every comment gets
reproduced in a test before it changes code.

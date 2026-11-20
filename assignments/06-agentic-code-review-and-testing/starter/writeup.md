# Week 6 Write-up — AI Code Review & Testing

**AI reviewer:** CodeRabbit

| PR | Feature | Implemented with | Tests after fixes |
|----|---------|------------------|-------------------|
| [#253](https://github.com/scottyUX/Software-engineering-in-the-age-of-ai/pull/253) | Streak (task 1) | Gemini CLI (`gemini-3.5-flash-lite`), one-shot prompt | 13 pass |
| [#254](https://github.com/scottyUX/Software-engineering-in-the-age-of-ai/pull/254) | Validation (task 2) | A coding agent, one-shot prompt | 27 pass |

Each PR has separate commits for the agent's output, the fixes from my review, and the
fixes from CodeRabbit, so the history shows what each stage changed.

## Guardrails

```bash
pip install -r requirements-dev.txt
./check.sh
```

`check.sh` runs three steps, stops at the first failure, and exits non-zero.

| Step | Command | What it catches | Proof it fails |
|------|---------|-----------------|----------------|
| Format | `black --check .` | Unformatted code (line length 100) | `x   =  1` → "1 file would be reformatted", exit 1, later steps skipped |
| Lint | `ruff check .` | Unused imports, import order, likely bugs | `import os` unused → `F401`, exit 1, pytest skipped |
| Tests | `pytest -q` | Behavior that no longer matches the tests | A deliberately wrong test → "1 failed, 3 passed", exit 1 |

**Limit:** these guardrails run locally. GitHub only runs workflows from the repository
root, and I submitted inside the shared course repo, so a workflow in `starter/` would
never run, and one at the root would affect everyone. A real project should run
`./check.sh` in CI so that a failure blocks the merge.

The guardrails caught a real problem during the work: a test line I added while fixing
the streak findings failed `black --check`.

## Review comparison

CodeRabbit reviewed each PR after my fixes were pushed. A "—" below means the problem was
already fixed when it looked, so these tables do not show that it would have missed them.

### PR #253 — Streak

| Finding | Me | CodeRabbit |
|---------|----|------------|
| One malformed stored day (`"hello"`) made every streak call for that habit return 500 | ✅ | — |
| Code counted from yesterday, but the task says "up to and including today" | ✅ | — |
| Test gaps: yesterday path, a gap in the middle, repeated days, future days, bad data | ✅ | — |
| Unclear name `d` | ✅ | — |
| `check.sh` scans an `env/` virtual environment, because black and ruff do not exclude that name | ❌ | ✅ |

**Where my review helped most:** the 500 and the task mismatch came from comparing the code
with the assignment text and running it with bad data. Passing tests would not have shown
either one: the agent's five tests all passed while both problems existed.

**Where the AI was better:** I treated `check.sh` as finished once it worked here. CodeRabbit
reasoned about another developer's machine, and I confirmed the problem by creating an
`env/` folder.

### PR #254 — Validation

| Finding | Me | CodeRabbit |
|---------|----|------------|
| Invisible-only names (`"\u200b"`, NUL) were stored | ✅ | — |
| `fromisoformat` also accepts `20260922` and `2026-W39-2` | ✅ | — |
| `"\ufe0f"` (variation selector) and a lone combining mark still passed my fix | ❌ | ✅ |
| `field_validator` needs Pydantic v2, but `requirements.txt` did not declare it | ❌ | ✅ |

**Where the AI was better:** it found a hole in my own fix. I used `isprintable()`, and
Python treats combining marks as printable. Before changing it, I reproduced the problem
(`"\ufe0f"` returned 200). The new rule requires a letter, number, punctuation mark, or
symbol, and tests confirm that names like `日本語` and `📚` still work. The Pydantic finding
is rarer, because a fresh install already gets v2, but declaring it costs one line.

**Where it was worse:** both PRs got the same generic "docstring coverage" and PR-title
warnings, which do not fit this project's conventions, so I did not act on them.

**Limits of this comparison:**
- CodeRabbit's free plan allowed one review per hour, so #253 was skipped at first and I
  re-ran it with `@coderabbitai review`.
- The fixes on #254 were not reviewed again by CodeRabbit; `check.sh` covers them.

## What I learned

Guardrails and LLM review catch different failures, so neither one replaces the other:
`check.sh` proved the code was formatted and that its tests passed, yet the agent's tests
passed while the endpoint could still return 500. CodeRabbit was strongest on things I
did not think to look at, such as Unicode edge cases and another developer's setup, but it
cannot tell whether code matches what the task intended unless that intent is in front of
it. I am comfortable trusting an AI review as an extra set of eyes, not as a sign-off,
because a clean review only means it found nothing. My rule now is to reproduce every AI
finding before fixing it, because the findings here were real but not equally important,
and to judge correctness against the task myself.

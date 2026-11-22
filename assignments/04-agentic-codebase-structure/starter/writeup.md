# Week 4 Write-up — Agent-Ready Link Shortener

**Agent:** Gemini CLI 0.64.0 (`gemini-3.5-flash-lite`) · **Task:** 1, Custom alias · **Result:** 8 tests pass, twice in a row

## 1. `AGENTS.md`

It covers:
- what the service does;
- a file map;
- install, run and test commands;
- product boundaries: no auth, no UI, no new dependencies, and codes must never shadow
  `/docs`, `/shorten`, `/redoc` or `/openapi.json`;
- the understand → test → implement → verify loop.

Every task needs this orientation, and at 56 lines it is cheap to load every session.

## 2. Scoped instruction

`tests/AGENTS.md` holds the test rules:
- public API only;
- success and failure cases;
- independent tests;
- unique aliases, because `links.db` persists and fixed aliases fail on the second run.

At startup Gemini CLI only searches *upward* for context files
(`memoryDiscovery.ts`, `findUpwardGeminiFiles`). This file therefore loads just in time:
when a tool touches a file in `tests/`, `tools/jit-context.ts` appends it to the tool
result. In `01-plan.md` it arrived as "Newly Discovered Project Context" right after
`read_file tests/test_main.py`. Tasks that only touch `main.py` never pay for it.

## 3. Reusable workflow

`.agents/skills/implement-feature/SKILL.md`:
1. read the task and guidance;
2. inspect the code and tests;
3. state the behavior and affected files;
4. write a failing test;
5. make the smallest change;
6. run `pytest` twice;
7. summarize with risks.

## 4. Discovery

| Artifact | How Gemini CLI finds it |
|----------|-------------------------|
| `AGENTS.md` | Gemini reads `GEMINI.md` by default. `.gemini/settings.json` sets `context.fileName: ["AGENTS.md"]` (`config.ts:623`). It appears in the first message of every transcript. |
| `tests/AGENTS.md` | The same setting, loaded just in time (Q2). |
| Skill | Discovered in `.agents/skills/*/SKILL.md` (`skillManager.ts:94`) and invoked through `activate_skill` (`02-implement.md`, `05-revise.md`). |

The folder must be trusted, or `.gemini/settings.json` is ignored.

## 5. What planning and review improved

Planning proposed mapping `sqlite3.IntegrityError` to 409 and applied the unique-alias
test rule before any test existed.

**The first review returned ACCEPT, and that was wrong.** My review
(`04-human-review.md`) reproduced three bugs:
- `docs` and `openapi.json` were accepted but shadowed by FastAPI's routes;
- `a/b` was accepted but returned 404;
- an alias equal to a future generated code made every later `POST /shorten` return
  500 forever.

On REVISE, the agent wrote failing tests first (3 failed), then added reserved-name
(409) and format (400) checks and a retry loop for generated codes. The suite passed
twice, and the re-review checked each finding before ACCEPT.
CodeRabbit on the PR then caught two more (`$` accepting `"abc\n"`; an over-specific
`encode(3)` assertion), fixed in one more test-first round (`07`, `08`).

## 6. What I learned

Structure decides what an agent attends to.
- The scoped rule worked: the flaky-test trap never happened, because the rule arrived
  exactly when the test file was opened.
- Review only checks what it is pointed at. `AGENTS.md` stated the shadowing rule, yet
  the reviewer ignored it until the findings were named.

Short context, just-in-time rules and a written procedure made a small model reliable,
but an agent's ACCEPT still needs adversarial review before it means "done."

# CodeRabbit review on PR #166 — two findings to fix

CodeRabbit (the course repo's automatic PR reviewer) reviewed commit `0bf044f` and rated
the merge risk **Low**. Two of its findings are valid; I confirmed both locally.

## C1 — A trailing newline passes alias validation (Minor)

`ALIAS_REGEX = re.compile(r"^[A-Za-z0-9_-]{1,32}$")` is checked with `.match()`. In
Python, `$` also matches just before a final newline, so `"abc\n"` is accepted and
stored as an alias outside the allowed character set.

Confirmed: `ALIAS_REGEX.match("abc\n")` → match, `ALIAS_REGEX.fullmatch("abc\n")` → None.

**Expected:** validate the whole alias, e.g. with `ALIAS_REGEX.fullmatch(req.alias)`, so
`"abc\n"` → 400. Add `"abc\n"` to the invalid-alias test.

## C2 — The collision test asserts an implementation detail (Nitpick)

`test_generated_code_collision_with_alias` ends its checks with
`assert data["code"] == encode(3)`. Any free code satisfies the API contract, so this line
would fail a valid alternative fix. `tests/AGENTS.md` only allows `encode()` to *build*
the colliding alias, not to assert on results.

**Expected:** remove that one assertion. Keep the checks that the new code differs from
the alias and that both codes redirect correctly.

## Not addressed (by decision)

- Docstring coverage warning: the starter has no docstring convention, and the task does
  not require one.
- PR title check: the title follows the course's `Week N: Name` convention.

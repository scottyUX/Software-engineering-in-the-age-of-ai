# Critique, round 1 (Task 3: ingredient scaling)

Reviewed: `git diff main..HEAD -- main.py test_scaling.py` on `task-c` (commit a44f6fb).
Tests: `python -m pytest -q` gives 31 passed. Single tests run alone after deleting
`recipes.db` also pass (`test_stored_recipe_is_not_modified`, `test_unknown_recipe_returns_404`,
`test_format_quantity`). Probing was done with `fastapi.testclient` against one recipe that held
the inputs below. Every result quoted here was reproduced.

Note on the diff: `main..HEAD` shows `/shopping-list` and the `?tag=` filter as deleted. That is
because `task-c` branched from 152c425, before main merged task-a and task-b; the generator did not
remove them. But `git merge-tree --write-tree main HEAD` reports `CONFLICT (content): Merge conflict
in main.py`, because the `get_recipe` -> `_load_recipe` refactor touches the same region. So the
branch cannot be merged as it is (see change 7).

## 1. Correctness: FAIL

What works: `200 g flour` x2 -> `400 g flour`; `200g butter` -> `400g butter`; `2.5 kg` -> `5 kg`;
`10 eggs` -> `20 eggs`; `0.1 tsp` x2 -> `0.2 tsp`; `salt to taste` unchanged; `1/2 cup`, `2-3 eggs`,
`1,5 l` unchanged (the documented choice). `factor` 0, -2, abc, "", nan, inf, 1e309 and a missing
factor return 422. An unknown id returns 404 `unknown recipe`. The stored recipe is not changed.

Problems:

a. **Mixed numbers are scaled wrong without any error.** `1 1/2 cups flour` with factor=2 returns
   `2 1/2 cups flour` (the right answer is 3 cups). With factor=0.5 it returns `0.5 1/2 cups flour`.
   The lookahead `(?=\s|...)` at main.py:109 accepts the `1 ` before `1/2`. The comment at
   main.py:102-107 says fractions are "returned unchanged on purpose", so the code contradicts its
   own documented rule.
b. **Small factors round quantities down to 0.** `0.1 tsp salt` with factor=0.01 gives `0 tsp salt`.
   With factor=0.001: `2.5 kg potatoes` -> `0 kg potatoes`, `3x eggs` -> `0x eggs`. With
   factor=1e-9 every quantity becomes `0`. The cause is the fixed `:.2f` at main.py:114. A factor
   the endpoint accepts should never turn a real quantity into zero.
c. **Very large factors return `inf` and long float noise with HTTP 200.** factor=1e308 gives
   `inf kg potatoes`, `infg butter` and `inf eggs`. factor=1e300 gives `10 eggs` -> a number about
   300 digits long, `10000000000000000525047602552...`. `allow_inf_nan=False` (main.py:127) checks
   only the input, not the product. There is no upper bound and no check that the result is finite.
d. **Non-ASCII digits are scaled and rewritten in ASCII, which is not documented.**
   `٢٠٠ g flour` (Arabic-Indic digits) -> `400 g flour`, and `２００ g` (full-width) -> `400 g`.
   Python's `\d` matches any Unicode digit, but the comment says "a plain number". Either restrict
   the rule (`re.ASCII`) or document and test this behavior.
e. **Leading whitespace turns scaling off, which is not documented.** ` 200 g sugar` is returned
   unchanged (main.py:109 anchors `^` at the digit). Ingredients are not trimmed on create, so this
   input can reach the endpoint. Quantities that are not first (`flour, 200 g`) are also left
   unchanged. That one matches the "STARTS with" rule but has no test.

## 2. Tests: FAIL

`pytest` passes, and each test creates its own recipe. But none of the problems in item 1 has a
test: no mixed number (`1 1/2`), no small factor that rounds to zero, no very large factor, no
Unicode digits, no leading whitespace, no quantity that is not first (`flour, 200 g`). The test
`test_fractions_and_ranges_left_unchanged_on_purpose` (test_scaling.py:51) only checks `1/2`, so it
misses the mixed-number case that the documented rule claims to cover. Minor: tests write into the
real `recipes.db` next to main.py (main.py:24), so every run leaves rows in the app database. This
is not a rubric failure, but a temporary database would be cleaner.

## 3. Clarity: PASS (with a note)

The rule is a single named regex, `LEADING_QUANTITY` (main.py:109), with a comment block above it,
plus two small named functions, `format_quantity` and `scale_ingredient`. `400.0` is formatted as
`400` and `1.50 l` as `1.5 l`. The response keys match `GET /recipes/{id}`; this is tested in
`test_response_shape_matches_get_recipe`. Note: the comment at main.py:102-107 must be updated so
it matches whatever is decided for items 1a, 1b, 1d and 1e.

## Required changes

1. Make `1 1/2 cups flour` scale correctly (factor=2 -> `3 cups flour`) or leave it unchanged on
   purpose (factor=2 -> `1 1/2 cups flour`). Add an endpoint or `scale_ingredient` test that
   asserts the chosen result.
2. Stop small factors from producing `0`: `scale_ingredient("0.1 tsp salt", 0.01)` must not return
   `"0 tsp salt"`. Use significant-figure formatting, or reject factors whose result rounds to
   zero with a 4xx. Add a test.
3. Bound the factor or check the result: `GET /recipes/{id}/scaled?factor=1e308` must not return
   200 with `inf` in an ingredient, and `factor=1e300` must not return 300-digit numbers. For
   example, add `le=1000` (or a similar limit) and return 422 above it. Add a test with a huge
   factor.
4. Decide how non-ASCII digits are handled. Either add `re.ASCII` so `٢٠٠ g flour` is unchanged, or
   document the conversion to ASCII. Add a test for the chosen behavior.
5. Handle leading whitespace: ` 200 g sugar` x2 should give `400 g sugar` (strip first), or
   document that it is left unchanged. Add a test.
6. Add a test showing that `flour, 200 g` is unchanged on purpose, and update the parsing-rule
   comment (main.py:102-107) so it lists every case from changes 1-5.
7. Rebase or merge `task-c` onto current `main` (d70b1a7) and resolve the `main.py` conflict so
   `/shopping-list` and `GET /recipes?tag=` still exist. After that, the full `pytest` (test_main.py
   and test_scaling.py) must pass.

VERDICT: REVISE

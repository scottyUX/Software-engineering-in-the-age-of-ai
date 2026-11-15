# Critique, round 3 (Task 3: ingredient scaling)

Reviewed: commit 4852360 on `task-c` (`git show 4852360`, main.py:104-157, test_scaling.py).
Tests: `python -m pytest -q` gives 62 passed. `test_scaling.py` alone gives 59 passed. Both file
orders pass, and single tests run alone also pass (`test_smallest_allowed_factor`,
`test_scientific_notation_left_unchanged_on_purpose`, `test_stored_recipe_is_not_modified`).
Probing used `fastapi.testclient` against a temporary database. Every result quoted here was
reproduced.

Round-1 item 7 (integration with main's `/shopping-list` and `?tag=`) is out of scope and is not
scored.

## Status of the round-2 required change

1. **Lower bound on factor: DONE.** `MIN_FACTOR = 0.001` and `ge=MIN_FACTOR` (main.py:119, 150),
   with the description and comment updated (main.py:114). Requests sent:
   `0.0009`, `0.000999999`, `1e-300`, `5e-324`, `0`, `-0.001` give 422; `0.001`, `1e-3`,
   `0.0010` and `1000` give 200; `1000.0000000000001`, `nan`, `inf`, `-inf`, `""` and a missing
   factor give 422. The tiny-factor results from round 2 (`0 tsp salt`, 300-character numbers)
   can no longer be produced through the endpoint. Tests: `0.0009`, `1e-300` and `5e-324` were
   added to `test_bad_factor_returns_422`. `test_smallest_allowed_factor` checks
   `0.2 g flour` / `0.0005 tsp salt`. The `1e-9` case was replaced by `("2 eggs", 0.001, ...)`.

Round-1 items 1-6 still hold. Mixed numbers, non-ASCII digits, `flour, 200 g`, fractions, ranges
and comma decimals are unchanged at every factor below, and ` 200 g sugar` is scaled.

## Break attempts (factor 2 / 1.5 / 1000 / 0.001)

- `1.0 kg sugar` -> `2` / `1.5` / `1000` / `0.001 kg`; `200g butter` -> `400g` / `300g` /
  `200000g` / `0.2g`; `3` -> `6` / `4.5` / `3000` / `0.003`; `0.5` -> `1` / `0.75` / `500` /
  `0.0005`; `2.50 l` -> `5` / `3.75` / `2500` / `0.0025 l`; `10 eggs` -> `20` / `15` / `10000` /
  `0.01`; `200 g flour` x1.5 -> `300 g flour`. All correct.
- New lookahead `(?![eE][+-]?\d)` (main.py:116): `1e3 g`, `1.5e3 g`, `1E-2 kg`, `1e+3 g` and
  `12e3 g` stay unchanged at every factor. Backtracking cannot get around it: `1.5e3` and `12e3`
  stay unchanged. Words that start with e still scale: `2 eggs` -> `4 eggs` and `2eggs` -> `4eggs`.
  `3e` -> `6e` and `1e` -> `2e`, because no digit follows the `e`.
- Very long text: `"1"*10**6 + "e" + "1"*10**6` takes 0.14 s, a 1M-digit decimal followed by `e5`
  takes 0.29 s, and `"200 g " + "e1"*100000` through the endpoint takes 0.01 s. No catastrophic
  backtracking.
- The stored recipe was identical after all requests.

Non-blocking notes (reproduced, consistent with the documented rule, no change required):
- `1 e3 g` x2 -> `2 e3 g` (with a space, the `e` is read as the unit word) and `1st layer` ->
  `2st layer`. Both follow "next non-space character is an ASCII letter".
- Absurd stored quantities can still produce odd output, because only the factor is bounded:
  `scale_ingredient("0." + "0"*400 + "1 g", 0.001)` returns `'0 g'` (the input already parses to
  0.0), and 300 leading zeros give a 308-character result. Unlike the round-2 problem, this
  comes from the stored text and not from any accepted factor. It is the small-number mirror of
  the `MAX_QUANTITY` guard, if the generator ever wants one.

## 1. Correctness: PASS

Every quantity in the "200 g flour" form scales correctly across the allowed factor range
[0.001, 1000]. Ingredients without a quantity, fractions, mixed numbers, ranges, comma
decimals, non-ASCII digits, scientific notation and quantities that are not first are left
unchanged on purpose and documented (main.py:104-115). Bad factors (0, negative, non-numeric,
empty, nan, inf, out of range, missing) return 422. Unknown ids return 404 `unknown recipe`.
The stored recipe is never modified.

## 2. Tests: PASS

Every behavior above has a test, including the failure cases and both bounds
(`test_bad_factor_returns_422`, `test_smallest_allowed_factor`, `test_largest_allowed_factor`,
`test_scientific_notation_left_unchanged_on_purpose`). Each test uses its own temporary
database, and the tests pass alone and in any file order. `pytest` gives 62 passed.

## 3. Clarity: PASS

`LEADING_QUANTITY` is one named regex with a comment that gives examples for each case.
`MIN_FACTOR`, `MAX_FACTOR` and `MAX_QUANTITY` are named constants. `format_quantity` gives
`400`, `2.5`, `0.33` and `0.0005` (never `400.0`). The response shape matches `GET /recipes/{id}`.

## Required changes

None.

VERDICT: SIGN-OFF

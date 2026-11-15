# Critique, round 2 (Task 3: ingredient scaling)

Reviewed: commit 596ed9e on `task-c` (`git show 596ed9e`, main.py:104-152, test_scaling.py).
Tests: `python -m pytest -q` gives 54 passed. `test_scaling.py` alone gives 51 passed. Both file
orders (`test_main.py test_scaling.py` and the reverse) pass. Single tests run alone also pass
(`test_stored_recipe_is_not_modified`, `test_unknown_recipe_returns_404`,
`test_small_factor_never_rounds_to_zero`, `test_leading_whitespace_is_stripped_and_scaled`).
Probing used `fastapi.testclient` against a temporary database. Every result quoted here was
reproduced.

Round-1 item 7 (integration with main's `/shopping-list` and `?tag=`) is out of scope for this
round and is not scored.

## Status of round-1 required changes

1. **Mixed numbers: DONE.** `1 1/2 cups flour` and `1 ½ cups` are unchanged at x2
   (lookahead `\s*[A-Za-z]|\s*$` at main.py:113). Tested in
   `test_mixed_numbers_left_unchanged_on_purpose` and in `test_scale_ingredient`.
2. **Small factors round to 0: PARTLY DONE.** `format_quantity` (main.py:119-128) uses 2
   significant figures below 1, so `0.1 tsp salt` x0.01 -> `0.001 tsp salt` (tested), and
   x0.001 -> `0.0001 tsp salt`. But factor has no lower bound, so the product can underflow to
   0.0: `GET /recipes/{id}/scaled?factor=5e-324` returns 200 with `0 tsp salt` and `0.5` -> `0`.
   `scale_ingredient("0.1 tsp salt", 5e-324)` returns `'0 tsp salt'`. See new change 1.
3. **Huge factors: DONE for the upper end.** `le=MAX_FACTOR` (main.py:145) gives 422 for
   1000.5, 1000.0000000000001, 1e300, 1e308 and 1e309 (tested). `MAX_QUANTITY` (main.py:136)
   leaves a 300- or 400-digit quantity unchanged (tested). But the same problem now appears at
   the low end: factor=1e-300 returns 200 with every quantity about 300 characters long
   (`0.000...0002 kg sugar`, length 311). See new change 1.
4. **Non-ASCII digits: DONE.** `re.ASCII` (main.py:113); `٢٠٠ g flour` and `２００ g sugar` are
   unchanged. Documented at main.py:112 and tested.
5. **Leading whitespace: DONE.** ` 200 g sugar` -> `400 g sugar`, `\t2 eggs` -> `4 eggs`.
   Documented at main.py:108 and tested.
6. **`flour, 200 g` test and comment: DONE.** `test_quantity_not_first_left_unchanged_on_purpose`
   exists; the comment at main.py:104-112 lists every case.

The round-1 minor note about tests writing into the real `recipes.db` is fixed: the `temp_db`
fixture points `DB_PATH` at `tmp_path`. `import main` still creates an empty `recipes.db` through
`init_db()` at main.py:49, but no rows are written to it (`select count(*)` gave 0).

## Break attempts (factor 2 / 1.5 / 1000 / 0.001)

- `1.0 kg sugar` -> `2` / `1.5` / `1000` / `0.001 kg sugar`. Correct.
- `200g butter` -> `400g` / `300g` / `200000g` / `0.2g`. Correct.
- `3` -> `6` / `4.5` / `3000` / `0.003`; `0.5` -> `1` / `0.75` / `500` / `0.0005`. Correct.
- `2.50 l water` -> `5` / `3.75` / `2500` / `0.0025 l`. Correct.
- `10 eggs` -> `20` / `15` / `10000` / `0.01 eggs`. Correct.
- `200 g flour` x1.5 -> `300 g flour`. Correct.
- `1e3 g flour` -> `2e3` / `1.5e3` / `1000e3` / `0.001e3 g flour`. Only the mantissa is scaled
  (`e` counts as the letter after the number). The value is right, but this happens by accident
  and is not documented. Not blocking.
- `1st layer` x2 -> `2st layer`. This follows the documented rule ("next character is an ASCII
  letter"). Not blocking.
- `format_quantity`: 0.9999 -> `1`, 0.00999 -> `0.01`, 999999999999999.0 -> `999999999999999`.
  Float noise appears just below `MAX_QUANTITY`: `format_quantity(1e14 * 1.1)` ->
  `110000000000000.02`. The quantities are absurd, so this is not blocking.
- Very long text: a 200,006-character ingredient (`200 g ` + 200,000 `x`) scales in 0.05 s.
  Regex worst cases (`"1"*10**6 + " "*10**6 + "/"`, a million spaces, `"1"*10**6 + "." +
  "1"*10**6 + "/"`) finish in 0.3 s or less with no catastrophic backtracking. Quantities that
  overflow to inf are left unchanged.
- The stored recipe was identical after all of these requests.

## 1. Correctness: FAIL

Everything in the rubric holds except the small end of `factor`. `factor` accepts any value
`> 0` (main.py:145 has `gt=0` and no lower bound). So `factor=5e-324` returns HTTP 200 with
`0 tsp salt` and `0`, which is the zero result round-1 change 2 said must not happen. And
`factor=1e-300` returns 300-character numbers, which round-1 change 3 rejected for big factors.
Fractions, ranges, comma decimals, mixed numbers and non-ASCII digits are left unchanged on
purpose and documented (main.py:104-112). Unknown ids return 404, and 0, negative, non-numeric,
empty, nan, inf, missing and > 1000 return 422.

## 2. Tests: FAIL

Every behavior from round 1 now has a test, the tests use a temporary database per test, and
they pass alone and in any file order. The missing test is the lower bound: there is no test
with a tiny factor such as `1e-300` or `5e-324`. `test_scale_ingredient` even locks in
`("2 eggs", 1e-9, "0.000000002 eggs")`, so the test suite treats unbounded tiny factors as
intended.

## 3. Clarity: PASS

`LEADING_QUANTITY` (main.py:113) is one named regex with a comment that gives examples for each
case. `format_quantity` and `scale_ingredient` are small, and `MAX_FACTOR` and `MAX_QUANTITY` are
named constants. `400.0` is formatted as `400`, `2.50` as `2.5` and `1/3` as `0.33`. The
response shape matches `GET /recipes/{id}` (`test_response_shape_matches_get_recipe`).

## Required changes

1. Add a lower bound to `factor` that mirrors `MAX_FACTOR`, for example
   `MIN_FACTOR = 0.001` with `ge=MIN_FACTOR` at main.py:145, so that `factor=1e-300` and
   `factor=5e-324` return 422 instead of 200 with 300-character numbers or `0 tsp salt`.
   Update the `description` and the comment. Add `1e-300` and `5e-324` (and a value just
   below the bound) to `test_bad_factor_returns_422`, plus a test for the smallest allowed
   factor. Replace or drop the `("2 eggs", 1e-9, ...)` case in `test_scale_ingredient` so it
   no longer suggests that such factors are supported. (A check that the scaled value is
   above 0 and below a small-size limit is also fine, as long as the endpoint can no longer
   return `0` or a 300-character quantity for a real ingredient.)

VERDICT: REVISE

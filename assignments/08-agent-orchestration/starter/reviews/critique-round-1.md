# Critique, Round 1 (Task 3: Ingredient Scaling)

**Review Target:** Generator Round 1 Implementation  
**Reviewed Against:** `reviews/RUBRIC.md`  

---

## Evaluation Against Rubric

### 1. Correctness: FAIL
- **What works:** Basic scaling like `200 g flour` * 2 -> `400 g flour` succeeds.
- **Failures Identified:**
  1. **Mixed fractions corruption:** `1 1/2 cups flour` with `factor=2` returns `2 1/2 cups flour`. The naive regex matches the leading integer `1` and leaves `1/2` untouched, resulting in an incorrect total quantity.
  2. **Leading whitespace unhandled:** `" 200 g flour"` fails to match because the regex starts with `^(\d+)` without leading `\s*`.
  3. **Precision loss on small factors:** Fixed `:.2f` formatting rounds `0.1 tsp salt` * 0.01 to `0.00 tsp salt` or `0 tsp`. Real ingredients should not become zero.
  4. **Unbounded factors:** `factor=1e308` returns `inf kg`, and `factor=0` or `factor=-1` does not return 422 Unprocessable Entity.
  5. **Missing 404 handling:** Unknown recipe IDs raise internal server error instead of standard 404 response.

### 2. Tests: FAIL
- Only 4 basic tests exist; no tests for mixed numbers, bounds checking, or error status codes.

### 3. Clarity: FAIL
- No documentation explaining what patterns scale vs what patterns remain unchanged.

---

## Required Revisions
1. Enforce factor validation with bounds: factor must be finite, positive, and <= 1000 (return 422 otherwise).
2. Fix regex to handle leading whitespace.
3. Protect fractions and mixed numbers (`1/2 cup`, `1 1/2 cups`) from partial scaling; leave them unchanged per documented policy.
4. Improve float formatting so small non-zero quantities do not truncate to zero.
5. Return 404 for unknown recipe IDs.

**VERDICT: REVISE**

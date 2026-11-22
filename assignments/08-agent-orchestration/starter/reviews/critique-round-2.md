# Critique, Round 2 (Task 3: Ingredient Scaling)

**Review Target:** Generator Round 2 (Revision 1)  
**Reviewed Against:** `reviews/RUBRIC.md`  

---

## Evaluation Against Rubric

### 1. Correctness: FAIL
- **What was fixed:**
  - Leading whitespace is now supported (`\s*`).
  - Mixed fractions (`1 1/2 cups`) are protected and left unchanged.
  - Upper bound `le=1000` added; factor=1e308 correctly returns HTTP 422.
  - Unknown recipe IDs return 404.
- **Remaining / New Failures Identified:**
  1. **Missing lower bound on factor:** While `le=1000` was added, there is no lower bound (`ge=0.001`). Calling `GET /recipes/1/scaled?factor=0` or `factor=1e-300` results in HTTP 200 with zeroed quantities or floating-point underflow.
  2. **Range quantities partially scaled:** Inputs such as `"2-3 eggs"` or `"1-2 cups"` have their first number scaled, yielding `"4-3 eggs"`, which corrupts the range semantics.

### 2. Tests: PASS
- Test suite expanded to 28 tests covering standard scaling, mixed fractions preservation, and 404 responses.

### 3. Clarity: PASS
- Documented parsing rules added in comments.

---

## Required Revisions
1. Enforce strict minimum factor bound (`ge=0.001`) so non-positive or near-zero factors return HTTP 422.
2. Protect range expressions (`2-3 eggs`, `1-2 cups`) from partial scaling; leave them unchanged.

**VERDICT: REVISE**

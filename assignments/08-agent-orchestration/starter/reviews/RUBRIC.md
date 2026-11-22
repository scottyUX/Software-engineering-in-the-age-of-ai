# Generator-Critic Rubric (Task 3: Ingredient Scaling)

## Criteria

### 1. Correctness (PASS / FAIL)
- Endpoint: `GET /recipes/{id}/scaled?factor=N`.
- Returns recipe object with `ingredients` array scaled by `factor`.
- Leading quantities (integers and decimals) must scale accurately:
  - `200 g flour` * 2 -> `400 g flour`
  - `1.5 kg rice` * 2 -> `3 kg rice`
  - `10 eggs` * 0.5 -> `5 eggs`
- Formatting: Clean representation with no floating-point noise or awkward trailing zeros (e.g., `400` not `400.00`, `0.5` not `0.50000000001`).
- Preserved cases (must not corrupt or crash):
  - Ingredients without quantities (`salt to taste`) remain unchanged.
  - Fractions and mixed numbers (`1/2 cup`, `1 1/2 cups`, `2-3 eggs`) must either be cleanly handled or safely left unchanged per documented policy.
  - Ingredients with quantity not first (`flour, 200 g`) remain unchanged.
- Validation:
  - `factor` must be a positive finite float between `0.001` and `1000`.
  - Non-positive (`factor=0`, `factor=-2`), non-numeric, `inf`, `nan`, or extreme factors must return HTTP 422.
  - Unknown recipe ID must return HTTP 404 (`unknown recipe`).
  - Stored recipe in the database must never be mutated.

### 2. Tests (PASS / FAIL)
- Unit tests covering standard scaling, boundary factors, fractions/edge cases, error responses (404 and 422).
- Pure test isolation without altering existing test suites.

### 3. Clarity (PASS / FAIL)
- Documented parsing rules and explicit regex.
- Clean error messages and docstrings.

---
**Verdict options:** `VERDICT: SIGN-OFF` or `VERDICT: REVISE` (with numbered required revisions).

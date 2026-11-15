# Critic rubric (Task 3: ingredient scaling)

The critic scores each item PASS or FAIL with evidence (file:line, a command it ran, or a
request it sent) and signs off only when every item is PASS.

1. **Correctness**: `GET /recipes/{id}/scaled?factor=2` scales every quantity in
   ingredients like "200 g flour". Ingredients without a quantity are left unchanged.
   Decimals, fractions or ranges either scale correctly or are left unchanged on purpose
   (documented). Bad `factor` values (0, negative, non-numeric, missing) and unknown ids return
   a clear 4xx. The stored recipe is never modified.
2. **Tests**: every behavior above has a test, including the failure cases. Tests create their
   own data and pass alone and in any order. `pytest` passes.
3. **Clarity**: the parsing rule is small, named and easy to read; numbers are formatted
   cleanly (`400 g`, not `400.0 g`); the response shape is obvious and consistent with
   `GET /recipes/{id}`.

Verdict line, last line of every critique: `VERDICT: SIGN-OFF` or `VERDICT: REVISE`.

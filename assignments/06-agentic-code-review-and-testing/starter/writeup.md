# Week 6 — AI Code Review & Testing: Writeup

## Guardrails

**Tools:** `black` (formatter) + `ruff` (linter) + `pytest` (test runner)

**Commands:**

```bash
# Install guardrail tools (one-time)
pip install black ruff

# Format code (auto-fix)
black main.py test_main.py

# Check formatting without modifying (CI-style)
black --check main.py test_main.py

# Lint
ruff check main.py test_main.py

# Run tests — a failing test exits non-zero, blocking the build
pytest
```

**What they catch:**
- `black` enforces consistent formatting (line length, whitespace, quotes) — eliminates style debates in code review.
- `ruff` catches unused imports, undefined names, shadowed variables, and style violations (E/F/W/I rules).
- `pytest` failing with a non-zero exit code means any CI step that runs `pytest` will block a merge if tests are red.

**One-command local check (Windows):**
```powershell
.\check.ps1
```

**CI (GitHub Actions):** `.github/workflows/ci.yml` runs `black --check`, `ruff check`, and `pytest` on every push and pull request. A failing step blocks the merge.

**Demonstration — failing test blocks build:**
```bash
# Temporarily break a test → pytest exits 1 → build fails
# Fix it → pytest exits 0 → build passes
```

---

## PR 1 — Streak Feature

**Branch:** `feature/streak`
**Endpoint:** `GET /habits/{id}/streak`

### What it does
Returns the current run of consecutive days with a check-in, counting backwards from today. If today has no check-in the streak is 0, even if yesterday had one.

### Implementation notes
- Fetches all distinct check-in days for the habit, converts to `date` objects, and walks backwards from `date.today()` while each day is in the set. O(n) on the number of unique days.
- Uses `DISTINCT` in the SQL query to avoid counting duplicate check-ins on the same day.
- Returns `{"habit_id": ..., "streak": N}`.

### Tests added (5)
| Test | What it checks |
|------|----------------|
| `test_streak_zero_no_checkins` | New habit with no check-ins → 0 |
| `test_streak_zero_old_checkin` | Check-in 2 days ago with gap → 0 |
| `test_streak_today_only` | Only today checked in → 1 |
| `test_streak_consecutive_days` | Today + 2 previous days → 3 |
| `test_streak_unknown_habit_404` | Non-existent habit → 404 |

### My manual review notes
- **Edge case coverage:** The duplicate check-in case (same day checked in twice) is handled by `DISTINCT` in SQL but not explicitly tested. Added a note but left it for now — the test suite would catch a regression.
- **Return shape:** Returning `habit_id` alongside `streak` makes the response self-describing and easier to use in multi-habit dashboards. Good call.
- **No timezone handling:** `date.today()` uses the server's local timezone. If the app serves users across timezones this could cause off-by-one streak mismatches at midnight. Worth a TODO comment.

### AI reviewer (CodeRabbit) notes
_[To be filled after PR is opened and CodeRabbit reviews it]_

### Human vs AI comparison — Streak
_[To be filled after PR review]_

---

## PR 2 — Validation Feature

**Branch:** `feature/validation`
**Endpoints affected:** `POST /habits`, `POST /habits/{id}/checkin`

### What it does
- Rejects empty or whitespace-only habit names with HTTP 422 and a clear message.
- Rejects malformed or non-ISO `day` values with HTTP 422 and a clear message.

### Implementation notes
- Uses Pydantic `@field_validator` on both models — validation happens at deserialization before the endpoint body runs. FastAPI automatically returns 422 with the validator's message.
- `name` validator strips whitespace after validation so stored names are clean.
- `day` validator calls `date.fromisoformat()` — this accepts only strict `YYYY-MM-DD` format, so `22/09/2026` and `not-a-date` are both rejected.

### Tests added (5)
| Test | What it checks |
|------|----------------|
| `test_create_habit_empty_name_rejected` | `""` → 422 |
| `test_create_habit_whitespace_only_rejected` | `"   "` → 422 |
| `test_checkin_invalid_date_rejected` | `"not-a-date"` → 422 |
| `test_checkin_wrong_date_format_rejected` | `"22/09/2026"` → 422 |
| `test_valid_habit_and_checkin_still_work` | Valid inputs still → 200 |

### My manual review notes
- **Missing field vs empty string:** Sending `{"name": null}` returns a 422 from Pydantic automatically (type error), which is correct behavior — no extra code needed.
- **Stripping name:** The validator strips leading/trailing whitespace and stores the cleaned value. This means `"  Read  "` becomes `"Read"` — intentional, good UX.
- **Future:** Could add max-length validation on `name` to prevent DB abuse, but the assignment doesn't require it.

### AI reviewer (CodeRabbit) notes
_[To be filled after PR is opened and CodeRabbit reviews it]_

### Human vs AI comparison — Validation
_[To be filled after PR review]_

---

## What I learned

_[To be filled after both PRs are reviewed — 3–5 sentences on combining guardrails with LLM review and comfort level trusting AI reviews]_

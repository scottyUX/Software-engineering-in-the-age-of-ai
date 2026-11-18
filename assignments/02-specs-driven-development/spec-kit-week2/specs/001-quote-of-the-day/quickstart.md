# Quickstart: Validate Quote of the Day

**Prerequisites**: A current browser. To run the tests: Node.js 20 or newer, and Google Chrome for
the real-page test.

## Run the page

Open `index.html` in a browser. No server or build step is needed.

## Run the tests

```bash
node --test
```

Expected: all tests pass. The real-page test reports as skipped if Chrome is not found.

## Manual validation

| Scenario | Steps | Expected | Covers |
|----------|-------|----------|--------|
| See a quote | Open the page | One quote and author appear | US1, FR-001 |
| New quote | Press "New quote" | A different quote from the list is shown | US2, FR-003 |
| Mark favorite | Press "Favorite" | Label reads "Favorited" | US3, FR-004, FR-005 |
| Unmark favorite | Press "Favorited" | Label reads "Favorite" | US3 |
| Persistence | Mark a quote, reload until it returns | It still reads "Favorited" | FR-006 |
| Keyboard | Tab to each button, press Enter | Each button works | FR-008 |

See [contracts/ui.md](contracts/ui.md) for the page elements and
[contracts/storage.md](contracts/storage.md) for saved-data states.

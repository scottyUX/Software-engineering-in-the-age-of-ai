# Quickstart & Validation Guide: Quote of the Day

This guide provides end-to-end instructions for running, manually verifying, and executing automated tests for the Quote of the Day feature.

## 1. Prerequisites

- Any modern web browser (Chrome, Firefox, Safari, Edge).
- Python 3.x (already installed on system) for running a lightweight local static server and headless test validations.

---

## 2. Running the Application Locally

Because the application uses standard ES6 modules (`import`/`export`), it should be served via a local web server (to avoid local browser `file://` CORS restrictions on module scripts).

1. From the repository root (`spec-kit-week2`), start the built-in HTTP server:
   ```bash
   python -m http.server 8000
   ```
2. Open your web browser and navigate to:
   ```text
   http://localhost:8000
   ```

---

## 3. Automated Validation

### 3.1 Browser Test Runner
1. In your browser, navigate to:
   ```text
   http://localhost:8000/tests/index.html
   ```
2. The zero-dependency test runner automatically executes:
   - `quote-service.test.js`: Verifies catalog integrity, random selection, non-repeat guarantees, edge cases.
   - `storage-service.test.js`: Verifies serialization, toggle favorite, schema fallback on corruption, private browsing simulation.
3. **Expected Outcome**: All assertion suites display green with 0 failures reported.

### 3.2 CLI Headless Automated Runner
Run the automated test validation script using Python:
```bash
python tests/run-tests.py
```
**Expected Outcome**: Process exits with code `0`, outputting `All tests passed successfully`.

---

## 4. Manual Verification Scenarios

### Scenario 1: Initial Presentation & Smooth Fade-In (User Story 1 / P1)
1. Open `http://localhost:8000` in a fresh browser session.
2. **Verify**: A quote is immediately visible with distinct quote text and author citation.
3. **Verify**: The quote text fades in smoothly over 0.5 seconds upon initial appearance.
4. **Verify**: The favorite button indicates an active un-favorited state (`aria-pressed="false"`).

### Scenario 2: Requesting a New Quote & Transition Reset (User Story 2 / P2)
1. Click the **"New quote"** button.
2. **Verify**: The displayed quote updates immediately, and the new quote text fades in smoothly over 0.5 seconds.
3. **Verify**: The new quote is different from the quote displayed immediately prior.
4. Click **"New quote"** 5 times in rapid succession.
5. **Verify**: The animation cleanly restarts for each new quote without stuttering, text duplication, or overlapping artifacts.

### Scenario 3: Favoriting and Persistence (User Story 3 / P3)
1. On the currently displayed quote, click the **Favorite** button.
2. **Verify**: The button updates visually to indicate favorited status (`aria-pressed="true"`).
3. Refresh the browser page (`F5` or `Ctrl+R`).
4. Click **"New quote"** until you return to the favorited quote.
5. **Verify**: The favorite indicator remains filled/active.
6. Click the **Favorite** button again to toggle it off.
7. Refresh the page.
8. **Verify**: The quote is no longer marked as favorite.

### Scenario 4: Viewing Favorites Collection (User Story 4 / P4)
1. Favorite 2 different quotes.
2. Click the **"View Favorites"** button.
3. **Verify**: The favorites panel opens displaying both favorited quotes with their authors.
4. Click the remove button next to one of the quotes in the list.
5. **Verify**: The quote is removed immediately from the list, and if it is currently displayed on the main card, its favorite indicator toggles off.

# Quickstart Validation Guide: Quote of the Day

**Feature**: Quote of the Day
**Branch**: `001-quote-of-the-day`
**Date**: 2026-10-07

This guide outlines prerequisites, execution commands, and step-by-step verification procedures to validate the feature end-to-end.

---

## 1. Prerequisites

- **Web Browser**: Any modern web browser (Chrome, Firefox, Safari, Edge).
- **Node.js**: Node.js 18+ (used strictly for running automated test suites via `node:test`; zero npm packages required).
- **Static HTTP Server** (Optional for development): Python 3 (`python3 -m http.server`) or Node (`npx serve src`).

---

## 2. Running Automated Tests

Run the zero-dependency test suite directly from the project root:

```bash
# Run all unit and integration tests
node --test tests/**/*.test.js
```

### Expected Output:
```text
✔ QuoteManager - Initial quote selection returns valid quote
✔ QuoteManager - getNextQuote never repeats the same quote consecutively
✔ QuoteManager - toggleFavorite adds and removes quote IDs correctly
✔ StorageService - saves and loads favorites to and from localStorage
✔ StorageService - handles corrupted storage gracefully with fallback
✔ Full Flow - quote display, cycle, and persistence integration
ℹ tests 6
ℹ suites 0
ℹ pass 6
ℹ fail 0
```

---

## 3. Running the Web Application

Because the application is built with vanilla HTML, CSS, and ES Modules, you can serve it with any local static server:

```bash
# Option A: Using Python built-in server
python3 -m http.server 8080 --directory src

# Option B: Using Node npx serve
npx serve src -p 8080
```

Then open `http://localhost:8080` in your web browser.

---

## 4. End-to-End Manual Validation Scenarios

### Scenario 1: Initial Load & Random Quote Display (P1)
1. Open `http://localhost:8080` in an incognito or fresh browser window.
2. **Verify**:
   - A quote is displayed inside `#quote-text`.
   - The author name is clearly visible in `#quote-author`.
   - The favorite button `#btn-favorite` is visible and indicates an unfavorited state (`aria-pressed="false"`).

### Scenario 2: "New Quote" On-Demand Cycling (P2)
1. Click the "New quote" button (`#btn-new-quote`).
2. **Verify**:
   - The quote text and author immediately update.
   - The newly presented quote is different from the quote that was just displayed.
   - Click the button 5 times rapidly; verify there is no UI lag, error in the browser console, or flickering.

### Scenario 3: Favoriting with Persistence Across Reloads (P3)
1. On any displayed quote, click the favorite button (`#btn-favorite`).
2. **Verify**:
   - The favorite button immediately reflects the favorited state (`aria-pressed="true"` and filled icon/highlight).
3. Reload the browser page (`Cmd+R` / `F5`).
4. Click "New quote" until the quote from step 1 is displayed again.
5. **Verify**:
   - The favorited quote retains its active favorite state (`aria-pressed="true"`).
6. Click the favorite button again to unfavorite the quote.
7. Reload the page and re-encounter the quote; verify it is now unfavorited (`aria-pressed="false"`).

### Scenario 4: Storage Restriction Fallback (Edge Case)
1. In browser settings, disable cookies / site storage or open in strict private mode where `localStorage` throws an exception.
2. Load the page and click "New quote" and favorite.
3. **Verify**:
   - The page loads quotes without crashing.
   - Favoriting updates visually for the session with graceful console logging.

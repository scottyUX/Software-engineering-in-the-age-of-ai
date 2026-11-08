# Quickstart Validation Guide: Quote of the Day

**Feature**: `001-quote-of-the-day`  
**Date**: 2026-10-20  
**Status**: Ready  

## 1. Prerequisites
- Modern web browser (Chrome, Safari, Firefox, or Edge).
- Node.js ($\ge 18$) for running automated unit tests.

---

## 2. Running the Application

1. Open `index.html` directly in your browser:
   ```bash
   # On macOS
   open index.html
   # On Linux
   xdg-open index.html
   ```
   Or launch a local static server if preferred:
   ```bash
   npx serve .
   # or
   python3 -m http.server 8080
   ```

---

## 3. Automated Validation

Execute the unit test suite verifying data structures, non-repetition logic, and storage persistence:

```bash
node --test tests/unit/*.test.js
```

### Expected Output
```text
✔ QuoteService returns a valid random quote
✔ QuoteService avoids immediate duplicate quote when requested
✔ FavoriteStorage correctly persists and toggles favorites
✔ FavoriteStorage recovers gracefully from corrupted storage data
✔ All tests passing
```

---

## 4. Manual Verification Walkthrough

Follow these steps to validate all acceptance criteria from [spec.md](./spec.md):

| Step | Action | Expected Result | Verified FR |
| :--- | :--- | :--- | :--- |
| **1. Initial Load** | Open `index.html` in browser | A quote with text and author attribution appears immediately | FR-001, FR-002 |
| **2. New Quote** | Click the "New quote" button | The quote updates to a different quote (never repeats immediately) | FR-003, FR-004 |
| **3. Favorite Quote** | Click the favorite (heart) button | The heart icon turns active/filled (e.g., ❤️) | FR-005, FR-006 |
| **4. Persistence Test** | Refresh the browser page (`F5` or `Cmd+R`) until the favorited quote appears (or favorite the initial quote, then reload) | When the favorited quote is shown, the heart remains active/filled | FR-007, FR-008 |
| **5. Unfavorite** | Click the active heart button again | The heart returns to inactive outline state (e.g., 🤍) and persists | FR-005, FR-008 |
| **6. Corrupted Storage** | In DevTools Console run: `localStorage.setItem('quote_of_the_day_favorites', '{bad-json}')` and refresh | Page loads normally without JavaScript error; storage resets cleanly | FR-007, Resilience |


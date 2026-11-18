# Validation Guide: Quote of the Day

This document describes how to validate the completed feature end-to-end.

## Prerequisites
- A modern web browser (Chrome, Firefox, Safari, Edge).
- No backend server or build tools (like npm/Node.js) are strictly necessary to run the application, though a local static server (e.g., `npx serve` or python's `http.server`) is recommended to avoid `file://` protocol restrictions on some browsers if modules are used.

## Scenario 1: Initial Load
1. Open `src/index.html` in your browser.
2. **Expected**: A quote and its author are immediately displayed. The favorite indicator (e.g., star/heart) should be in its "empty" (unfavorited) state.

## Scenario 2: Generate a New Quote
1. Click the "New quote" button.
2. **Expected**: The quote text and author update to a different quote instantly without the page reloading.

## Scenario 3: Favoriting and Persistence
1. With a quote displayed, click the favorite toggle icon.
2. **Expected**: The icon visually changes to a "filled" state.
3. Click "New quote" until the *same* favorited quote appears again.
4. **Expected**: The icon remains in the "filled" state for this specific quote.
5. Reload the browser tab entirely (F5 or CMD+R).
6. Continue clicking "New quote" until the favorited quote appears.
7. **Expected**: The icon is still in the "filled" state, proving `localStorage` persistence.

## Scenario 4: Un-favoriting
1. While viewing the favorited quote from Scenario 3, click the "filled" favorite toggle icon.
2. **Expected**: The icon reverts to the "empty" state.
3. Reload the page and find the quote again.
4. **Expected**: The quote remains in the "empty" (unfavorited) state.


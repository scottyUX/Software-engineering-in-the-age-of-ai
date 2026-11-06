# Contract: Quote Manager Domain Interface

**Feature**: Quote of the Day
**Branch**: `001-quote-of-the-day`
**Date**: 2026-10-07

This document defines the interface contract for the `QuoteManager` core domain module.

---

## Class / Module Interface

```javascript
/**
 * @typedef {Object} Quote
 * @property {string} id
 * @property {string} text
 * @property {string} author
 */

export class QuoteManager {
  /**
   * Initializes the manager with a catalog and existing favorite IDs.
   * @param {Quote[]} catalog - List of available quotes.
   * @param {Set<string>|string[]} [initialFavorites] - Pre-loaded favorite quote IDs.
   */
  constructor(catalog, initialFavorites = new Set());

  /**
   * Selects an initial random quote.
   * @returns {Quote}
   */
  getInitialQuote(): Quote;

  /**
   * Selects a random quote ensuring it does not immediately repeat the previous quote.
   * If catalog.length === 1, returns the single quote.
   * @returns {Quote}
   */
  getNextQuote(): Quote;

  /**
   * Returns the currently displayed quote, or null if none selected.
   * @returns {Quote|null}
   */
  getCurrentQuote(): Quote | null;

  /**
   * Checks if a given quote ID is currently favorited.
   * @param {string} quoteId
   * @returns {boolean}
   */
  isFavorite(quoteId: string): boolean;

  /**
   * Toggles the favorite status of the specified quote ID.
   * @param {string} quoteId
   * @returns {boolean} The new favorite status (true if now favorite, false if unfavorited).
   */
  toggleFavorite(quoteId: string): boolean;

  /**
   * Returns a copy of all currently favorited quote IDs.
   * @returns {Set<string>}
   */
  getFavoriteIds(): Set<string>;
}
```

---

## Invariants & Behavioral Rules

1. **Non-Empty Catalog**:
   - If instantiated with an empty array or non-array, `QuoteManager` MUST throw an `Error("Quote catalog must contain at least one quote.")`.
2. **Deterministic Non-Consecutive Selection**:
   - `getNextQuote()` MUST never return the quote where `quote.id === currentQuote.id` when `catalog.length > 1`.
3. **Immutability of Returned Quote**:
   - Returned quotes are read-only objects. Modifying properties on returned quotes does not mutate the source catalog.
4. **Isolated Pure Logic**:
   - `QuoteManager` contains zero DOM or `localStorage` calls. It accepts dependencies/data in the constructor and exposes clean pure methods, making it 100% testable under `node:test`.

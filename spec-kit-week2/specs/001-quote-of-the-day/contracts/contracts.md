# Module Contracts: Quote of the Day

**Feature**: `001-quote-of-the-day`  
**Date**: 2026-10-20  
**Status**: Completed  

## 1. Storage Manager Contract (`storage.js`)

Manages persistence of user favorite preferences to `localStorage`.

```javascript
/**
 * Interface definition for FavoriteStorage
 */
export interface FavoriteStorage {
  /**
   * Retrieves the set of favorited quote IDs.
   * Handles missing data, parsing errors, and storage exceptions gracefully.
   * @returns {Set<string>} Set of quote IDs
   */
  getFavorites(): Set<string>;

  /**
   * Persists the provided set of quote IDs to localStorage.
   * @param {Set<string> | string[]} favoriteIds
   * @returns {boolean} True if successfully persisted, false if failed
   */
  saveFavorites(favoriteIds: Set<string> | string[]): boolean;

  /**
   * Toggles the favorite status of a specific quote ID and persists the change.
   * @param {string} quoteId
   * @returns {boolean} The new favorite status (true if now favorite, false if removed)
   */
  toggleFavorite(quoteId: string): boolean;

  /**
   * Checks whether a specific quote ID is currently marked as favorite.
   * @param {string} quoteId
   * @returns {boolean}
   */
  isFavorite(quoteId: string): boolean;
}
```

---

## 2. Quote Service Contract (`quote-service.js`)

Encapsulates quote selection logic, catalog access, and non-repetition guarantees.

```javascript
/**
 * Interface definition for QuoteService
 */
export interface QuoteService {
  /**
   * Returns a random quote from the collection.
   * If excludeId is provided and collection size > 1, the returned quote will not have excludeId.
   * @param {string} [excludeId] - ID of the quote to exclude from selection
   * @returns {Quote} The selected quote object
   */
  getRandomQuote(excludeId?: string): Quote;

  /**
   * Returns all available quotes in the catalog.
   * @returns {Quote[]}
   */
  getAllQuotes(): Quote[];

  /**
   * Retrieves a quote by its unique ID.
   * @param {string} id
   * @returns {Quote | undefined}
   */
  getQuoteById(id: string): Quote | undefined;
}
```

---

## 3. UI DOM Contract (`index.html`)

The DOM elements required by the UI controller (`app.js`):

| Element Selector | Element Type | Purpose |
| :--- | :--- | :--- |
| `#quote-text` | `<p>` / `<blockquote>` | Displays the current quote text |
| `#quote-author` | `<cite>` / `<p>` | Displays the current quote author |
| `#new-quote-btn` | `<button>` | Interactive button to request another quote |
| `#favorite-btn` | `<button>` | Interactive button to toggle favorite state |
| `#favorite-icon` | `<span>` / `<svg>` | Visual icon representing favorite state (e.g. ❤️ vs 🤍) |


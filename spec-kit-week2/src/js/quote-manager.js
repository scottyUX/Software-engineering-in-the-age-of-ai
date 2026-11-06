/**
 * QuoteManager encapsulates domain logic for quote selection, non-repeating
 * sequence guarantees, and favorite status management.
 * Strictly decoupled from DOM and storage APIs.
 */

export class QuoteManager {
  /**
   * @param {Array<{id: string, text: string, author: string}>} catalog - Available quote collection.
   * @param {Set<string>|string[]} [initialFavorites] - Initial favorite quote IDs.
   */
  constructor(catalog, initialFavorites = new Set()) {
    if (!Array.isArray(catalog) || catalog.length === 0) {
      throw new Error("Quote catalog must contain at least one quote.");
    }

    // Defensive copy of catalog
    this.catalog = catalog.map(q => ({
      id: String(q.id),
      text: String(q.text),
      author: q.author ? String(q.author) : "Anonymous"
    }));

    this.currentQuote = null;
    this.previousQuoteId = null;

    // Convert initialFavorites to Set
    this.favoriteIds = initialFavorites instanceof Set
      ? new Set(initialFavorites)
      : new Set(Array.from(initialFavorites || []));
  }

  /**
   * Selects an initial random quote from the catalog.
   * @returns {{id: string, text: string, author: string}}
   */
  getInitialQuote() {
    const randomIndex = Math.floor(Math.random() * this.catalog.length);
    const selected = this.catalog[randomIndex];
    this.currentQuote = selected;
    this.previousQuoteId = selected.id;
    return { ...selected };
  }

  /**
   * Selects a random quote ensuring it does not consecutively repeat the previous quote.
   * If catalog contains only one quote, returns that quote gracefully.
   * @returns {{id: string, text: string, author: string}}
   */
  getNextQuote() {
    if (this.catalog.length === 1) {
      const selected = this.catalog[0];
      this.currentQuote = selected;
      this.previousQuoteId = selected.id;
      return { ...selected };
    }

    // Filter out the quote shown immediately prior
    const candidates = this.catalog.filter(q => q.id !== this.previousQuoteId);
    const randomIndex = Math.floor(Math.random() * candidates.length);
    const selected = candidates[randomIndex];

    this.currentQuote = selected;
    this.previousQuoteId = selected.id;
    return { ...selected };
  }

  /**
   * Returns the currently selected quote, or null if none selected.
   * @returns {{id: string, text: string, author: string}|null}
   */
  getCurrentQuote() {
    return this.currentQuote ? { ...this.currentQuote } : null;
  }

  /**
   * Checks whether a quote is currently favorited.
   * @param {string} quoteId
   * @returns {boolean}
   */
  isFavorite(quoteId) {
    if (!quoteId) return false;
    return this.favoriteIds.has(String(quoteId));
  }

  /**
   * Toggles the favorite status of the specified quote ID.
   * @param {string} quoteId
   * @returns {boolean} The new favorite status (true if added, false if removed).
   */
  toggleFavorite(quoteId) {
    if (!quoteId) return false;
    const id = String(quoteId);

    if (this.favoriteIds.has(id)) {
      this.favoriteIds.delete(id);
      return false;
    } else {
      this.favoriteIds.add(id);
      return true;
    }
  }

  /**
   * Returns a copy of the current set of favorite quote IDs.
   * @returns {Set<string>}
   */
  getFavoriteIds() {
    return new Set(this.favoriteIds);
  }
}

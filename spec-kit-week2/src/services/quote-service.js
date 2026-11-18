/**
 * QuoteService
 * Pure domain logic for managing the quotes catalog and random selection.
 */

import { quotes as defaultQuotes } from '../data/quotes.js';

export class QuoteService {
  /**
   * @param {Array} [catalog] Optional quote catalog for testing (defaults to curated catalog)
   */
  constructor(catalog) {
    this._catalog = Array.isArray(catalog) ? catalog : defaultQuotes;
  }

  /**
   * Returns all quotes in the catalog.
   */
  getAllQuotes() {
    return [...this._catalog];
  }

  /**
   * Returns quote by ID or null if not found.
   */
  getQuoteById(id) {
    return this._catalog.find(q => q.id === id) || null;
  }

  /**
   * Returns total count of quotes.
   */
  getQuoteCount() {
    return this._catalog.length;
  }

  /**
   * Selects a random quote.
   * If currentId is provided and catalog has >= 2 items, the selected quote
   * will not match currentId.
   */
  getRandomQuote(currentId) {
    if (this._catalog.length === 0) {
      throw new Error('Quote catalog is empty');
    }

    if (this._catalog.length === 1) {
      return this._catalog[0];
    }

    let candidates = this._catalog;
    if (currentId) {
      candidates = this._catalog.filter(q => q.id !== currentId);
      if (candidates.length === 0) {
        candidates = this._catalog;
      }
    }

    const randomIndex = Math.floor(Math.random() * candidates.length);
    return candidates[randomIndex];
  }
}

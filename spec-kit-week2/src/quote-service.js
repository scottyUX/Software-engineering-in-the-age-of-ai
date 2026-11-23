/**
 * Service managing quote catalog access and randomized selection.
 */
export class QuoteService {
  /**
   * @param {Array<{id: string, text: string, author: string}>} quotesCatalog
   */
  constructor(quotesCatalog = []) {
    this.quotes = quotesCatalog;
  }

  /**
   * Returns all available quotes in the catalog.
   * @returns {Array<{id: string, text: string, author: string}>}
   */
  getAllQuotes() {
    return [...this.quotes];
  }

  /**
   * Returns a quote by its unique ID.
   * @param {string} id
   * @returns {{id: string, text: string, author: string} | undefined}
   */
  getQuoteById(id) {
    return this.quotes.find(q => q.id === id);
  }

  /**
   * Returns a random quote from the collection.
   * If excludeId is provided and the catalog contains more than one quote,
   * the returned quote is guaranteed not to have excludeId (FR-004).
   * 
   * @param {string} [excludeId] - ID of the quote to exclude from selection
   * @returns {{id: string, text: string, author: string}}
   */
  getRandomQuote(excludeId) {
    if (this.quotes.length === 0) {
      throw new Error('Quote catalog is empty');
    }

    if (this.quotes.length === 1 || !excludeId) {
      const index = Math.floor(Math.random() * this.quotes.length);
      return this.quotes[index];
    }

    // Filter out the excluded quote to guarantee no immediate duplicate
    const candidateQuotes = this.quotes.filter(q => q.id !== excludeId);
    const candidatePool = candidateQuotes.length > 0 ? candidateQuotes : this.quotes;
    const selectedIndex = Math.floor(Math.random() * candidatePool.length);
    return candidatePool[selectedIndex];
  }
}


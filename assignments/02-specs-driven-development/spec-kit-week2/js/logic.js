const QuoteLogic = {
  pickRandomQuote(quotes, random = Math.random) {
    return quotes[Math.floor(random() * quotes.length)];
  },

  pickDifferentQuote(quotes, currentQuote, random = Math.random) {
    const others = quotes.filter((quote) => quote.id !== currentQuote.id);
    return QuoteLogic.pickRandomQuote(others, random);
  },

  toggleFavorite(favorites, quoteId) {
    return favorites.includes(quoteId)
      ? favorites.filter((id) => id !== quoteId)
      : [...favorites, quoteId];
  },

  // Saved data may be missing, corrupt, or written for an older quote list.
  parseFavorites(saved, quotes) {
    let parsed;
    try {
      parsed = JSON.parse(saved);
    } catch {
      return [];
    }
    if (!Array.isArray(parsed)) {
      return [];
    }
    const knownIds = new Set(quotes.map((quote) => quote.id));
    return [...new Set(parsed)].filter((id) => knownIds.has(id));
  },
};

if (typeof module !== "undefined") {
  module.exports = { QuoteLogic };
}

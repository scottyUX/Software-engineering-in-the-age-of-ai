const quotes = [
  { id: "q1", text: "The only limit to our realization of tomorrow is our doubts of today.", author: "Franklin D. Roosevelt" },
  { id: "q2", text: "The purpose of our lives is to be happy.", author: "Dalai Lama" },
  { id: "q3", text: "Life is what happens when you're busy making other plans.", author: "John Lennon" },
  { id: "q4", text: "Get busy living or get busy dying.", author: "Stephen King" },
  { id: "q5", text: "You only live once, but if you do it right, once is enough.", author: "Mae West" }
];

let appState = {
  currentQuoteId: null,
  favorites: []
};

function loadFavorites() {
  if (typeof localStorage !== 'undefined') {
    const saved = localStorage.getItem('quoteApp_favorites');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        return [];
      }
    }
  }
  return [];
}

function saveFavorites() {
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem('quoteApp_favorites', JSON.stringify(appState.favorites));
  }
}

function toggleFavorite() {
  if (!appState.currentQuoteId) return;
  
  const index = appState.favorites.indexOf(appState.currentQuoteId);
  if (index === -1) {
    appState.favorites.push(appState.currentQuoteId);
  } else {
    appState.favorites.splice(index, 1);
  }
  saveFavorites();
  updateFavoriteIcon();
}

function updateFavoriteIcon() {
  const favoriteBtn = document.getElementById('favorite-btn');
  if (favoriteBtn) {
    if (appState.favorites.includes(appState.currentQuoteId)) {
      favoriteBtn.classList.remove('icon-empty');
      favoriteBtn.classList.add('icon-filled');
    } else {
      favoriteBtn.classList.remove('icon-filled');
      favoriteBtn.classList.add('icon-empty');
    }
  }
}

function getRandomQuote() {
  const randomIndex = Math.floor(Math.random() * quotes.length);
  return quotes[randomIndex];
}

function renderQuote(quote) {
  const quoteTextEl = document.getElementById('quote-text');
  const quoteAuthorEl = document.getElementById('quote-author');
  
  if (quoteTextEl && quoteAuthorEl) {
    quoteTextEl.textContent = `"${quote.text}"`;
    quoteAuthorEl.textContent = `- ${quote.author}`;
    appState.currentQuoteId = quote.id;
    updateFavoriteIcon();
  }
}

// Initial load
if (typeof window !== 'undefined') {
  document.addEventListener('DOMContentLoaded', () => {
    appState.favorites = loadFavorites();
    
    const quote = getRandomQuote();
    renderQuote(quote);

    const newQuoteBtn = document.getElementById('new-quote-btn');
    if (newQuoteBtn) {
      newQuoteBtn.addEventListener('click', () => {
        let nextQuote = getRandomQuote();
        // Ensure we don't just show the same quote if there are others
        while (nextQuote.id === appState.currentQuoteId && quotes.length > 1) {
          nextQuote = getRandomQuote();
        }
        renderQuote(nextQuote);
      });
    }

    const favoriteBtn = document.getElementById('favorite-btn');
    if (favoriteBtn) {
      favoriteBtn.addEventListener('click', () => {
        toggleFavorite();
      });
    }
  });
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { quotes, getRandomQuote, renderQuote, appState, loadFavorites, saveFavorites, toggleFavorite };
}


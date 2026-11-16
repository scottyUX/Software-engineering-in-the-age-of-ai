import { QUOTES } from './quotes.js';
import { QuoteService } from './quote-service.js';
import { FavoriteStorage } from './storage.js';

// Initialize services
const quoteService = new QuoteService(QUOTES);
const favoriteStorage = new FavoriteStorage();

// Cached DOM Elements
const quoteTextEl = document.getElementById('quote-text');
const quoteAuthorEl = document.getElementById('quote-author');
const newQuoteBtn = document.getElementById('new-quote-btn');
const favoriteBtn = document.getElementById('favorite-btn');
const favoriteIconEl = document.getElementById('favorite-icon');

// Active state
let currentQuote = null;

/**
 * Updates the favorite button UI to reflect whether the quote is a favorite.
 * @param {boolean} isFav
 */
function updateFavoriteButtonUI(isFav) {
  if (!favoriteBtn || !favoriteIconEl) return;

  if (isFav) {
    favoriteIconEl.textContent = '❤️';
    favoriteBtn.classList.add('is-favorite');
    favoriteBtn.setAttribute('aria-pressed', 'true');
    favoriteBtn.setAttribute('title', 'Remove from favorites');
  } else {
    favoriteIconEl.textContent = '🤍';
    favoriteBtn.classList.remove('is-favorite');
    favoriteBtn.setAttribute('aria-pressed', 'false');
    favoriteBtn.setAttribute('title', 'Mark as favorite');
  }
}

/**
 * Renders the given quote to the DOM and restores its favorite status.
 * @param {{id: string, text: string, author: string}} quote
 */
function renderQuote(quote) {
  if (!quote) return;
  currentQuote = quote;

  if (quoteTextEl) {
    quoteTextEl.textContent = quote.text;
  }
  if (quoteAuthorEl) {
    quoteAuthorEl.textContent = quote.author;
  }

  // Restore and display persisted favorite state (FR-006, FR-008)
  const isFav = favoriteStorage.isFavorite(quote.id);
  updateFavoriteButtonUI(isFav);
}

/**
 * Handles displaying a new non-repeating quote.
 */
function handleNewQuote() {
  const excludeId = currentQuote ? currentQuote.id : undefined;
  const nextQuote = quoteService.getRandomQuote(excludeId);
  renderQuote(nextQuote);
}

/**
 * Handles toggling the favorite state for the currently displayed quote.
 */
function handleToggleFavorite() {
  if (!currentQuote) return;
  const isNowFav = favoriteStorage.toggleFavorite(currentQuote.id);
  updateFavoriteButtonUI(isNowFav);
}

// Attach Event Listeners
if (newQuoteBtn) {
  newQuoteBtn.addEventListener('click', handleNewQuote);
}

if (favoriteBtn) {
  favoriteBtn.addEventListener('click', handleToggleFavorite);
}

// Initial quote on load (FR-001)
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    renderQuote(quoteService.getRandomQuote());
  });
} else {
  renderQuote(quoteService.getRandomQuote());
}


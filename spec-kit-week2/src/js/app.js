import { QUOTES } from './quotes-data.js';
import { StorageService } from './storage.js';
import { QuoteManager } from './quote-manager.js';

/**
 * Main application coordinator.
 * Bridges domain logic (QuoteManager), persistence (StorageService), and the DOM.
 */
class App {
  constructor() {
    this.storageService = new StorageService();
    const initialFavorites = this.storageService.loadFavorites();
    this.quoteManager = new QuoteManager(QUOTES, initialFavorites);

    // DOM Elements
    this.quoteContainer = null;
    this.quoteText = null;
    this.quoteAuthor = null;
    this.btnNewQuote = null;
    this.btnFavorite = null;
    this.btnCopy = null;
    this.favoriteIcon = null;
  }

  /**
   * Initializes DOM references and renders the initial quote.
   */
  init() {
    try {
      this.quoteContainer = document.getElementById('quote-container');
      this.quoteText = document.getElementById('quote-text');
      this.quoteAuthor = document.getElementById('quote-author');
      this.btnNewQuote = document.getElementById('btn-new-quote');
      this.btnFavorite = document.getElementById('btn-favorite');
      this.btnCopy = document.getElementById('btn-copy');
      this.favoriteIcon = document.getElementById('favorite-icon');

      if (!this.quoteText || !this.quoteAuthor) {
        console.error('Required quote display elements missing from DOM (#quote-text or #quote-author).');
        return;
      }

      // Display initial quote on page load (User Story 1 - P1 MVP)
      const initialQuote = this.quoteManager.getInitialQuote();
      this.renderQuote(initialQuote);

      // Wire 'New quote' button (User Story 2 - P2)
      if (this.btnNewQuote) {
        this.btnNewQuote.addEventListener('click', () => this.handleNewQuote());
      }

      // Wire 'Favorite' button (User Story 3 - P3)
      if (this.btnFavorite) {
        this.btnFavorite.addEventListener('click', () => this.handleToggleFavorite());
      }

      // Wire 'Copy' button
      if (this.btnCopy) {
        this.btnCopy.addEventListener('click', () => this.handleCopyToClipboard());
      }
    } catch (err) {
      console.error('Initialization error in Quote of the Day app:', err);
    }
  }

  /**
   * Handles user request for a new quote.
   */
  handleNewQuote() {
    try {
      const nextQuote = this.quoteManager.getNextQuote();
      this.renderQuote(nextQuote);
    } catch (err) {
      console.error('Failed to cycle quote:', err);
    }
  }

  /**
   * Handles user toggle of favorite status for current quote.
   */
  handleToggleFavorite() {
    try {
      const current = this.quoteManager.getCurrentQuote();
      if (!current) return;

      const isFav = this.quoteManager.toggleFavorite(current.id);
      const saved = this.storageService.saveFavorites(this.quoteManager.getFavoriteIds());
      if (!saved && this.storageService.isAvailable()) {
        console.warn('Storage persistence failed; favorite retained in session memory only.');
      }
      this.updateFavoriteUI(isFav);
    } catch (err) {
      console.error('Failed to toggle favorite status:', err);
    }
  }

  /**
   * Copies the current quote text and author to the system clipboard.
   * Shows transient "Copied!" feedback on the button for 1.5 seconds.
   */
  handleCopyToClipboard() {
    const current = this.quoteManager.getCurrentQuote();
    if (!current || !this.btnCopy) return;

    const clipboardText = `"${current.text}" — ${current.author}`;
    const labelEl = this.btnCopy.querySelector('.copy-label');

    if (!navigator.clipboard) {
      console.warn('Clipboard API not available in this environment.');
      return;
    }

    navigator.clipboard.writeText(clipboardText).then(() => {
      this.btnCopy.classList.add('copied');
      if (labelEl) labelEl.textContent = 'Copied!';

      setTimeout(() => {
        this.btnCopy.classList.remove('copied');
        if (labelEl) labelEl.textContent = 'Copy';
      }, 1500);
    }).catch((err) => {
      console.warn('Failed to copy quote to clipboard:', err);
    });
  }

  /**
   * Updates the UI with the given quote data.
   * @param {{id: string, text: string, author: string}} quote
   */
  renderQuote(quote) {
    if (!quote) return;

    this.quoteText.textContent = quote.text;
    this.quoteAuthor.textContent = `— ${quote.author}`;

    // Update favorite button state if present
    this.updateFavoriteUI(this.quoteManager.isFavorite(quote.id));
  }

  /**
   * Updates the visual and accessible state of the favorite button.
   * @param {boolean} isFav
   */
  updateFavoriteUI(isFav) {
    if (!this.btnFavorite) return;

    this.btnFavorite.setAttribute('aria-pressed', isFav ? 'true' : 'false');
    this.btnFavorite.setAttribute(
      'aria-label',
      isFav ? 'Remove quote from favorites' : 'Add quote to favorites'
    );

    if (isFav) {
      this.btnFavorite.classList.add('is-favorite');
      if (this.favoriteIcon) {
        this.favoriteIcon.textContent = '♥';
      }
    } else {
      this.btnFavorite.classList.remove('is-favorite');
      if (this.favoriteIcon) {
        this.favoriteIcon.textContent = '♡';
      }
    }
  }
}

// Bootstrap application once DOM is ready
const app = new App();
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => app.init());
} else {
  app.init();
}

export { app, App };

/**
 * Main Application Bootstrap & Coordinator
 */

import { QuoteService } from './services/quote-service.js';
import { StorageService } from './services/storage-service.js';
import { UIController } from './ui/ui-controller.js';

class App {
  constructor() {
    this.quoteService = new QuoteService();
    this.storageService = new StorageService();
    this.ui = new UIController();
    this.currentQuote = null;
  }

  init() {
    // Check storage availability and alert if blocked
    if (!this.storageService.isStorageAvailable()) {
      this.ui.showStorageWarning(true);
    }

    // Bind UI actions
    this._bindEvents();

    // Load initial random quote
    this.loadNewQuote();

    // Update favorites badge
    this._refreshFavoritesUI();
  }

  loadNewQuote() {
    try {
      const currentId = this.currentQuote ? this.currentQuote.id : undefined;
      const quote = this.quoteService.getRandomQuote(currentId);
      this.currentQuote = quote;
      const isFav = this.storageService.isFavorite(quote.id);
      this.ui.renderQuote(quote, isFav);
    } catch (err) {
      console.error('Failed to load new quote:', err);
    }
  }

  toggleCurrentFavorite() {
    if (!this.currentQuote) return;
    const newStatus = this.storageService.toggleFavorite(this.currentQuote.id);
    this.ui.updateFavoriteStatus(newStatus);
    this._refreshFavoritesUI();
  }

  removeFavorite(quoteId) {
    this.storageService.removeFavorite(quoteId);
    if (this.currentQuote && this.currentQuote.id === quoteId) {
      this.ui.updateFavoriteStatus(false);
    }
    this._refreshFavoritesUI();
  }

  _refreshFavoritesUI() {
    const favRecords = this.storageService.getFavorites();
    this.ui.updateFavoritesCount(favRecords.length);

    // Map to quote details for drawer list
    const items = favRecords
      .map(rec => {
        const quote = this.quoteService.getQuoteById(rec.quoteId);
        return quote ? { quote, favoritedAt: rec.favoritedAt } : null;
      })
      .filter(Boolean);

    this.ui.renderFavoritesList(items, (quoteId) => this.removeFavorite(quoteId));
  }

  _bindEvents() {
    // "New quote" button
    if (this.ui.btnNewQuote) {
      this.ui.btnNewQuote.addEventListener('click', () => this.loadNewQuote());
    }

    // Favorite toggle button
    if (this.ui.btnFavorite) {
      this.ui.btnFavorite.addEventListener('click', () => this.toggleCurrentFavorite());
    }

    // Open favorites drawer
    if (this.ui.btnOpenFavorites) {
      this.ui.btnOpenFavorites.addEventListener('click', () => {
        this._refreshFavoritesUI();
        this.ui.toggleFavoritesDrawer(true);
      });
    }

    // Close favorites drawer
    if (this.ui.btnCloseFavorites) {
      this.ui.btnCloseFavorites.addEventListener('click', () => {
        this.ui.toggleFavoritesDrawer(false);
      });
    }

    // Backdrop click closes drawer
    if (this.ui.drawerBackdrop) {
      this.ui.drawerBackdrop.addEventListener('click', () => {
        this.ui.toggleFavoritesDrawer(false);
      });
    }

    // Keyboard accessibility: Escape closes drawer, Space/Enter on buttons handled natively
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        this.ui.toggleFavoritesDrawer(false);
      }
    });
  }
}

// Bootstrap application on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  const app = new App();
  app.init();
});

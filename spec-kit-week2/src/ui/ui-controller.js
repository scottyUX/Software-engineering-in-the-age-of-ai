/**
 * UIController
 * Handles DOM rendering, view state, and user interactions.
 */

export class UIController {
  constructor() {
    this.quoteCard = document.getElementById('quote-card');
    this.quoteText = document.getElementById('quote-text');
    this.quoteAuthor = document.getElementById('quote-author');
    this.quoteCategory = document.getElementById('quote-category');
    
    this.btnFavorite = document.getElementById('btn-favorite');
    this.favoriteBtnText = document.getElementById('favorite-btn-text');
    this.btnNewQuote = document.getElementById('btn-new-quote');
    
    this.btnOpenFavorites = document.getElementById('btn-open-favorites');
    this.btnCloseFavorites = document.getElementById('btn-close-favorites');
    this.favoritesDrawer = document.getElementById('favorites-drawer');
    this.drawerBackdrop = document.getElementById('drawer-backdrop');
    this.favoritesList = document.getElementById('favorites-list');
    this.favoritesEmpty = document.getElementById('favorites-empty');
    this.favoritesCount = document.getElementById('favorites-count');
    
    this.storageWarning = document.getElementById('storage-warning');
  }

  /**
   * Renders the given quote in the quote card.
   * @param {Object} quote 
   * @param {boolean} isFavorited 
   */
  renderQuote(quote, isFavorited) {
    if (!quote) return;

    // Trigger smooth 0.5s fade-in animation with reflow flush for rapid click reset
    if (this.quoteText) {
      this.quoteText.classList.remove('fade-in');
      void this.quoteText.offsetWidth; // Force DOM reflow to cleanly restart animation
      this.quoteText.textContent = quote.text;
      this.quoteText.classList.add('fade-in');
    }

    this.quoteAuthor.textContent = quote.author || 'Unknown';
    
    if (quote.category) {
      this.quoteCategory.textContent = quote.category;
      this.quoteCategory.style.display = 'inline-block';
    } else {
      this.quoteCategory.textContent = '';
      this.quoteCategory.style.display = 'none';
    }

    this.updateFavoriteStatus(isFavorited);
  }

  /**
   * Updates the visual indicator of the favorite button.
   * @param {boolean} isFavorited 
   */
  updateFavoriteStatus(isFavorited) {
    if (!this.btnFavorite) return;
    this.btnFavorite.setAttribute('aria-pressed', isFavorited ? 'true' : 'false');
    if (this.favoriteBtnText) {
      this.favoriteBtnText.textContent = isFavorited ? 'Favorited' : 'Favorite';
    }
    this.btnFavorite.title = isFavorited ? 'Remove from favorites' : 'Add to favorites';
  }

  /**
   * Updates the numeric count badge in the favorites button.
   * @param {number} count 
   */
  updateFavoritesCount(count) {
    if (this.favoritesCount) {
      this.favoritesCount.textContent = String(count);
    }
  }

  /**
   * Displays or hides the storage warning banner.
   * @param {boolean} show 
   */
  showStorageWarning(show) {
    if (!this.storageWarning) return;
    this.storageWarning.hidden = !show;
    this.storageWarning.setAttribute('aria-hidden', show ? 'false' : 'true');
  }

  /**
   * Opens or closes the favorites drawer.
   * @param {boolean} isOpen 
   */
  toggleFavoritesDrawer(isOpen) {
    if (!this.favoritesDrawer || !this.drawerBackdrop) return;
    
    if (isOpen) {
      this.favoritesDrawer.classList.add('open');
      this.favoritesDrawer.setAttribute('aria-hidden', 'false');
      this.drawerBackdrop.classList.add('active');
      this.drawerBackdrop.setAttribute('aria-hidden', 'false');
    } else {
      this.favoritesDrawer.classList.remove('open');
      this.favoritesDrawer.setAttribute('aria-hidden', 'true');
      this.drawerBackdrop.classList.remove('active');
      this.drawerBackdrop.setAttribute('aria-hidden', 'true');
    }
  }

  /**
   * Renders the list of saved favorites.
   * @param {Array<{ quote: Object, favoritedAt: number }>} items 
   * @param {Function} onRemove Callback invoked when a user clicks remove on an item
   */
  renderFavoritesList(items, onRemove) {
    if (!this.favoritesList || !this.favoritesEmpty) return;

    this.favoritesList.innerHTML = '';
    
    if (!items || items.length === 0) {
      this.favoritesEmpty.style.display = 'block';
      return;
    }

    this.favoritesEmpty.style.display = 'none';

    for (const item of items) {
      const li = document.createElement('li');
      li.className = 'favorite-item';
      li.dataset.quoteId = item.quote.id;

      const pText = document.createElement('p');
      pText.className = 'favorite-item-text';
      pText.textContent = `“${item.quote.text}”`;

      const footer = document.createElement('div');
      footer.className = 'favorite-item-footer';

      const authorSpan = document.createElement('span');
      authorSpan.textContent = `— ${item.quote.author}`;

      const btnRemove = document.createElement('button');
      btnRemove.type = 'button';
      btnRemove.className = 'btn-remove-favorite';
      btnRemove.textContent = 'Remove';
      btnRemove.setAttribute('aria-label', `Remove quote by ${item.quote.author} from favorites`);
      btnRemove.addEventListener('click', () => {
        if (typeof onRemove === 'function') {
          onRemove(item.quote.id);
        }
      });

      footer.appendChild(authorSpan);
      footer.appendChild(btnRemove);

      li.appendChild(pText);
      li.appendChild(footer);
      this.favoritesList.appendChild(li);
    }
  }
}

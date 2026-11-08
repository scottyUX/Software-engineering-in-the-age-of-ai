/**
 * Service managing user favorite quotes persistence in localStorage with defensive error handling.
 */
export class FavoriteStorage {
  static STORAGE_KEY = 'quote_of_the_day_favorites';

  /**
   * @param {Storage} [storageBackend] - Browser localStorage or custom storage object
   */
  constructor(storageBackend) {
    if (storageBackend) {
      this.storage = storageBackend;
    } else if (typeof window !== 'undefined' && window.localStorage) {
      this.storage = window.localStorage;
    } else {
      this.storage = null;
    }

    // In-memory cache of favorites for instant O(1) checks and fallback
    this.memoryFavorites = this._loadInitialFavorites();
  }

  /**
   * Safely loads initial favorite IDs from storage.
   * Handles missing key, corrupted JSON, and storage access errors.
   * @private
   * @returns {Set<string>}
   */
  _loadInitialFavorites() {
    if (!this.storage) {
      return new Set();
    }

    try {
      const rawData = this.storage.getItem(FavoriteStorage.STORAGE_KEY);
      if (!rawData) {
        return new Set();
      }

      const parsed = JSON.parse(rawData);
      if (Array.isArray(parsed)) {
        return new Set(parsed.filter(id => typeof id === 'string'));
      }

      // If data is not an array, treat as corrupted and reset
      this._saveToStorage([]);
      return new Set();
    } catch (err) {
      // Corrupted JSON or storage access error: fall back safely to empty set
      console.warn('Storage read error; resetting favorites to empty set:', err);
      try {
        this._saveToStorage([]);
      } catch (_) {
        // Ignore secondary storage error
      }
      return new Set();
    }
  }

  /**
   * Safely writes an array or Set of IDs to storage backend.
   * @private
   * @param {Array<string> | Set<string>} items
   * @returns {boolean}
   */
  _saveToStorage(items) {
    if (!this.storage) return false;
    try {
      const arrayToSave = Array.isArray(items) ? items : Array.from(items);
      this.storage.setItem(FavoriteStorage.STORAGE_KEY, JSON.stringify(arrayToSave));
      return true;
    } catch (err) {
      console.warn('Storage write error; operating in-memory for session:', err);
      return false;
    }
  }

  /**
   * Returns a copy of the current favorited quote IDs.
   * @returns {Set<string>}
   */
  getFavorites() {
    return new Set(this.memoryFavorites);
  }

  /**
   * Checks whether a quote ID is currently marked as favorite.
   * @param {string} quoteId
   * @returns {boolean}
   */
  isFavorite(quoteId) {
    return this.memoryFavorites.has(quoteId);
  }

  /**
   * Toggles the favorite status of a quote ID and persists the change.
   * @param {string} quoteId
   * @returns {boolean} The new favorite state (true if favorite, false if unfavorited)
   */
  toggleFavorite(quoteId) {
    if (!quoteId) return false;

    const willBeFavorite = !this.memoryFavorites.has(quoteId);

    if (willBeFavorite) {
      this.memoryFavorites.add(quoteId);
    } else {
      this.memoryFavorites.delete(quoteId);
    }

    this._saveToStorage(this.memoryFavorites);
    return willBeFavorite;
  }
}


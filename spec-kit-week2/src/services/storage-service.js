/**
 * StorageService
 * Manages persistence of favorite quotes using localStorage with JSON schema versioning
 * and resilient in-memory fallback.
 */

const STORAGE_KEY = 'qotd_favorites_v1';
const CURRENT_VERSION = 1;

export class StorageService {
  /**
   * @param {Storage} [storageBackend] Optional storage backend for testing (defaults to window.localStorage)
   */
  constructor(storageBackend) {
    this._backend = storageBackend !== undefined ? storageBackend : this._getGlobalStorage();
    this._storageAvailable = this._testStorageAvailability();
    this._memoryFavorites = new Map();

    this._load();
  }

  _getGlobalStorage() {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        return window.localStorage;
      }
    } catch {
      // Access to localStorage blocked (SecurityError)
    }
    return null;
  }

  _testStorageAvailability() {
    if (!this._backend) return false;
    try {
      const probeKey = '__qotd_probe__';
      this._backend.setItem(probeKey, '1');
      this._backend.removeItem(probeKey);
      return true;
    } catch {
      return false;
    }
  }

  _load() {
    this._memoryFavorites.clear();
    if (!this._storageAvailable || !this._backend) {
      return;
    }

    try {
      const raw = this._backend.getItem(STORAGE_KEY);
      if (!raw) return;

      const parsed = JSON.parse(raw);
      if (parsed && Array.isArray(parsed.favorites)) {
        for (const item of parsed.favorites) {
          if (item && typeof item.quoteId === 'string') {
            this._memoryFavorites.set(item.quoteId, {
              quoteId: item.quoteId,
              favoritedAt: typeof item.favoritedAt === 'number' ? item.favoritedAt : Date.now()
            });
          }
        }
      }
    } catch (err) {
      // Corrupted JSON or parsing error: reset corrupted entry gracefully
      console.warn('StorageService: Corrupted storage detected, resetting favorites envelope.', err);
      this._persist();
    }
  }

  _persist() {
    if (!this._storageAvailable || !this._backend) {
      return false;
    }

    try {
      const envelope = {
        version: CURRENT_VERSION,
        updatedAt: Date.now(),
        favorites: Array.from(this._memoryFavorites.values())
      };
      this._backend.setItem(STORAGE_KEY, JSON.stringify(envelope));
      return true;
    } catch (err) {
      console.warn('StorageService: Failed to persist to localStorage, switching to memory mode.', err);
      this._storageAvailable = false;
      return false;
    }
  }

  /**
   * Returns all favorited records as an array.
   */
  getFavorites() {
    return Array.from(this._memoryFavorites.values());
  }

  /**
   * Checks whether a quote is currently favorited.
   */
  isFavorite(quoteId) {
    if (!quoteId) return false;
    return this._memoryFavorites.has(quoteId);
  }

  /**
   * Adds a quote to favorites.
   */
  addFavorite(quoteId) {
    if (!quoteId) return false;
    if (!this._memoryFavorites.has(quoteId)) {
      this._memoryFavorites.set(quoteId, {
        quoteId,
        favoritedAt: Date.now()
      });
      this._persist();
    }
    return true;
  }

  /**
   * Removes a quote from favorites.
   */
  removeFavorite(quoteId) {
    if (!quoteId) return false;
    if (this._memoryFavorites.has(quoteId)) {
      this._memoryFavorites.delete(quoteId);
      this._persist();
    }
    return true;
  }

  /**
   * Toggles favorite status.
   * @returns {boolean} New favorited state (true = favorited, false = unfavorited).
   */
  toggleFavorite(quoteId) {
    if (this.isFavorite(quoteId)) {
      this.removeFavorite(quoteId);
      return false;
    } else {
      this.addFavorite(quoteId);
      return true;
    }
  }

  /**
   * Clears all stored favorites.
   */
  clearFavorites() {
    this._memoryFavorites.clear();
    this._persist();
  }

  /**
   * Checks if persistent localStorage is available and operational.
   */
  isStorageAvailable() {
    return this._storageAvailable;
  }
}

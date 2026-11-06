/**
 * StorageService provides robust persistence for quote favorites using window.localStorage.
 * Implements defensive fallback mechanisms for private browsing modes, quota limits,
 * and corrupted JSON payloads.
 */

export const STORAGE_KEY = 'qod_favorite_quote_ids';

export class StorageService {
  /**
   * @param {Storage|Object} [storageBackend] - Storage backend (defaults to window.localStorage)
   */
  constructor(storageBackend) {
    if (storageBackend !== undefined) {
      this.storage = storageBackend;
    } else if (typeof window !== 'undefined' && window.localStorage) {
      try {
        // Probe storage availability
        const probeKey = '__storage_probe__';
        window.localStorage.setItem(probeKey, probeKey);
        window.localStorage.removeItem(probeKey);
        this.storage = window.localStorage;
      } catch (e) {
      if (typeof console !== 'undefined' && console.warn) {
        console.warn('localStorage is restricted or unavailable:', e.message);
      }
        this.storage = null;
      }
    } else {
      this.storage = null;
    }

    this.memoryFallback = new Set();
  }

  /**
   * Checks whether the underlying persistent storage is operational.
   * @returns {boolean}
   */
  isAvailable() {
    return this.storage !== null;
  }

  /**
   * Loads saved favorite quote IDs from storage.
   * Falls back to in-memory set and resets invalid data.
   * @returns {Set<string>} Set of unique favorite quote IDs.
   */
  loadFavorites() {
    if (!this.storage) {
      return new Set(this.memoryFallback);
    }

    try {
      const raw = this.storage.getItem(STORAGE_KEY);
      if (!raw) {
        return new Set(this.memoryFallback);
      }

      const parsed = JSON.parse(raw);
      if (!Array.isArray(parsed)) {
        if (typeof console !== 'undefined' && console.warn) {
          console.warn('Invalid storage format for favorites; expected array. Resetting.');
        }
        this.storage.setItem(STORAGE_KEY, JSON.stringify([]));
        return new Set();
      }

      // Filter only non-empty string IDs
      const validIds = parsed.filter(item => typeof item === 'string' && item.trim().length > 0);
      return new Set(validIds);
    } catch (err) {
      if (typeof console !== 'undefined' && console.warn) {
        console.warn('Failed to parse stored favorites; resetting corrupted payload:', err.message);
      }
      try {
        this.storage.setItem(STORAGE_KEY, JSON.stringify([]));
      } catch (_) {
        // Ignore secondary storage error
      }
      return new Set(this.memoryFallback);
    }
  }

  /**
   * Persists favorite quote IDs to storage.
   * @param {Set<string>|string[]} favoriteIds
   * @returns {boolean} True if successfully stored in persistent storage, false if fallback used.
   */
  saveFavorites(favoriteIds) {
    const idsArray = Array.from(favoriteIds || []).filter(item => typeof item === 'string');

    // Always update session memory fallback
    this.memoryFallback = new Set(idsArray);

    if (!this.storage) {
      return false;
    }

    try {
      this.storage.setItem(STORAGE_KEY, JSON.stringify(idsArray));
      return true;
    } catch (err) {
      if (typeof console !== 'undefined' && console.error) {
        console.error('Failed to write favorites to localStorage:', err.message);
      }
      return false;
    }
  }
}

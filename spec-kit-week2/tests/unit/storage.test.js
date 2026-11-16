import { describe, it, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import { FavoriteStorage } from '../../src/storage.js';

/**
 * Mock localStorage implementation for Node test environment
 */
class MockLocalStorage {
  constructor() {
    this.store = {};
  }
  getItem(key) {
    return Object.prototype.hasOwnProperty.call(this.store, key) ? this.store[key] : null;
  }
  setItem(key, value) {
    this.store[key] = String(value);
  }
  removeItem(key) {
    delete this.store[key];
  }
  clear() {
    this.store = {};
  }
}

describe('FavoriteStorage', () => {
  let mockStorage;
  let favoriteStorage;

  beforeEach(() => {
    mockStorage = new MockLocalStorage();
    favoriteStorage = new FavoriteStorage(mockStorage);
  });

  it('should initialize with empty set when no saved favorites exist', () => {
    const favorites = favoriteStorage.getFavorites();
    assert.equal(favorites.size, 0);
    assert.equal(favoriteStorage.isFavorite('quote-1'), false);
  });

  it('should toggle a quote to favorited state (US3)', () => {
    const isNowFav = favoriteStorage.toggleFavorite('quote-1');
    assert.equal(isNowFav, true);
    assert.equal(favoriteStorage.isFavorite('quote-1'), true);
  });

  it('should toggle a favorited quote back to unfavorited state (US3)', () => {
    favoriteStorage.toggleFavorite('quote-1');
    assert.equal(favoriteStorage.isFavorite('quote-1'), true);

    const isNowFav = favoriteStorage.toggleFavorite('quote-1');
    assert.equal(isNowFav, false);
    assert.equal(favoriteStorage.isFavorite('quote-1'), false);
  });

  it('should persist favorited quotes to localStorage across instances (US4)', () => {
    favoriteStorage.toggleFavorite('quote-1');
    favoriteStorage.toggleFavorite('quote-3');

    // Create a new FavoriteStorage instance backed by the same storage
    const newSessionStorage = new FavoriteStorage(mockStorage);
    assert.equal(newSessionStorage.isFavorite('quote-1'), true);
    assert.equal(newSessionStorage.isFavorite('quote-3'), true);
    assert.equal(newSessionStorage.isFavorite('quote-2'), false);
  });

  it('should recover gracefully when localStorage contains corrupted JSON (US4 Resilience)', () => {
    // Inject corrupt JSON into storage
    mockStorage.setItem(FavoriteStorage.STORAGE_KEY, '{invalid-json:');

    const resilientStorage = new FavoriteStorage(mockStorage);
    // Should not throw, and should return an empty set
    const favorites = resilientStorage.getFavorites();
    assert.equal(favorites.size, 0);
    assert.equal(resilientStorage.isFavorite('quote-1'), false);
  });

  it('should recover gracefully when storage content is not an array', () => {
    mockStorage.setItem(FavoriteStorage.STORAGE_KEY, JSON.stringify({ not: 'an-array' }));

    const resilientStorage = new FavoriteStorage(mockStorage);
    const favorites = resilientStorage.getFavorites();
    assert.equal(favorites.size, 0);
  });

  it('should operate in-memory if localStorage is unavailable or throws', () => {
    const throwingStorage = {
      getItem() { throw new Error('QuotaExceeded / SecurityError'); },
      setItem() { throw new Error('QuotaExceeded / SecurityError'); }
    };

    const fallbackStorage = new FavoriteStorage(throwingStorage);
    assert.equal(fallbackStorage.isFavorite('quote-1'), false);
    
    // Toggling in-memory should still work for the session
    const status = fallbackStorage.toggleFavorite('quote-1');
    assert.equal(status, true);
    assert.equal(fallbackStorage.isFavorite('quote-1'), true);
  });
});


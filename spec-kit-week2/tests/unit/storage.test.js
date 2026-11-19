import { describe, it, assert, assertEqual, assertDeepEqual } from '../test-utils.js';
import { StorageService } from '../../src/js/storage.js';

describe('StorageService Unit Tests', () => {
  // Create a mock localStorage for isolated testing
  function createMockStorage(options = {}) {
    let store = {};
    return {
      getItem(key) {
        if (options.throwOnGet) throw new Error('Simulated security error on get');
        return Object.prototype.hasOwnProperty.call(store, key) ? store[key] : null;
      },
      setItem(key, val) {
        if (options.throwOnSet) throw new Error('Simulated QuotaExceededError');
        store[key] = String(val);
      },
      removeItem(key) {
        delete store[key];
      },
      clear() {
        store = {};
      },
      _raw: store
    };
  }

  it('detects available storage and saves/loads favorite IDs successfully', () => {
    const mockStorage = createMockStorage();
    const service = new StorageService(mockStorage);

    assertEqual(service.isAvailable(), true, 'Storage should be reported as available');

    const favorites = new Set(['quote-001', 'quote-005']);
    const saved = service.saveFavorites(favorites);
    assertEqual(saved, true, 'saveFavorites should return true on success');

    const loaded = service.loadFavorites();
    assertEqual(loaded instanceof Set, true, 'loadFavorites should return a Set');
    assertEqual(loaded.size, 2, 'Loaded set should contain 2 favorites');
    assertEqual(loaded.has('quote-001'), true, 'Should contain quote-001');
    assertEqual(loaded.has('quote-005'), true, 'Should contain quote-005');
  });

  it('handles empty storage on initial load', () => {
    const mockStorage = createMockStorage();
    const service = new StorageService(mockStorage);

    const loaded = service.loadFavorites();
    assertEqual(loaded instanceof Set, true);
    assertEqual(loaded.size, 0, 'Initial favorites set should be empty');
  });

  it('recovers gracefully from corrupted/malformed JSON in storage', () => {
    const mockStorage = createMockStorage();
    mockStorage.setItem('qod_favorite_quote_ids', '{malformed json!#$');
    const service = new StorageService(mockStorage);

    const loaded = service.loadFavorites();
    assertEqual(loaded instanceof Set, true);
    assertEqual(loaded.size, 0, 'Corrupted JSON should fall back to empty Set');
  });

  it('filters out non-string items or non-array JSON objects', () => {
    const mockStorage = createMockStorage();
    mockStorage.setItem('qod_favorite_quote_ids', JSON.stringify({ notAnArray: true }));
    const service = new StorageService(mockStorage);

    const loaded = service.loadFavorites();
    assertEqual(loaded.size, 0, 'Non-array JSON should return empty Set');
  });

  it('filters non-string values within an array payload', () => {
    const mockStorage = createMockStorage();
    mockStorage.setItem('qod_favorite_quote_ids', JSON.stringify(['quote-001', 123, null, 'quote-002']));
    const service = new StorageService(mockStorage);

    const loaded = service.loadFavorites();
    assertEqual(loaded.size, 2, 'Should only keep string IDs');
    assertEqual(loaded.has('quote-001'), true);
    assertEqual(loaded.has('quote-002'), true);
  });

  it('gracefully falls back to in-memory store when storage access throws', () => {
    const restrictedStorage = createMockStorage({ throwOnSet: true });
    const service = new StorageService(restrictedStorage);

    const saved = service.saveFavorites(new Set(['quote-fallback-01']));
    assertEqual(saved, false, 'Should return false when underlying storage throws');

    // In-memory fallback still functions for the session
    const loaded = service.loadFavorites();
    assertEqual(loaded.has('quote-fallback-01'), true, 'In-memory fallback should retain favorites');
  });
});

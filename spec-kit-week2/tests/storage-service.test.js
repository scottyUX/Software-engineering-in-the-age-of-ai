/**
 * Unit Tests for StorageService
 */

import { describe, test } from './test-runner.js';
import { assert, assertEqual, assertTrue, assertFalse } from './assert.js';
import { StorageService } from '../src/services/storage-service.js';

// In-memory mock for localStorage
class MockLocalStorage {
  constructor(shouldThrow = false) {
    this.store = {};
    this.shouldThrow = shouldThrow;
  }

  getItem(key) {
    if (this.shouldThrow) throw new Error('SecurityError: Local storage blocked');
    return this.store[key] !== undefined ? this.store[key] : null;
  }

  setItem(key, value) {
    if (this.shouldThrow) throw new Error('QuotaExceededError or SecurityError');
    this.store[key] = String(value);
  }

  removeItem(key) {
    if (this.shouldThrow) throw new Error('SecurityError');
    delete this.store[key];
  }

  clear() {
    this.store = {};
  }
}

describe('StorageService Test Suite', () => {
  test('Initializes with empty favorites when storage key is missing', () => {
    const mockStorage = new MockLocalStorage();
    const service = new StorageService(mockStorage);
    
    assertEqual(service.getFavorites(), []);
    assertFalse(service.isFavorite('q-001'));
    assertTrue(service.isStorageAvailable());
  });

  test('Adds, checks, and removes favorites correctly', () => {
    const mockStorage = new MockLocalStorage();
    const service = new StorageService(mockStorage);

    service.addFavorite('q-001');
    assertTrue(service.isFavorite('q-001'), 'q-001 should be favorited');
    assertFalse(service.isFavorite('q-002'), 'q-002 should not be favorited');

    const favs = service.getFavorites();
    assertEqual(favs.length, 1);
    assertEqual(favs[0].quoteId, 'q-001');

    // Remove favorite
    service.removeFavorite('q-001');
    assertFalse(service.isFavorite('q-001'));
    assertEqual(service.getFavorites().length, 0);
  });

  test('Toggles favorite status idempotently', () => {
    const mockStorage = new MockLocalStorage();
    const service = new StorageService(mockStorage);

    const firstState = service.toggleFavorite('q-005');
    assertTrue(firstState, 'First toggle should favorite the item');
    assertTrue(service.isFavorite('q-005'));

    const secondState = service.toggleFavorite('q-005');
    assertFalse(secondState, 'Second toggle should unfavorite the item');
    assertFalse(service.isFavorite('q-005'));
  });

  test('Persists favorites as JSON envelope matching data model', () => {
    const mockStorage = new MockLocalStorage();
    const service = new StorageService(mockStorage);

    service.addFavorite('q-003');
    const rawData = mockStorage.getItem('qotd_favorites_v1');
    assert(rawData !== null, 'Raw data must be stored in localStorage');

    const parsed = JSON.parse(rawData);
    assertEqual(parsed.version, 1);
    assert(Array.isArray(parsed.favorites), 'favorites must be an array');
    assertEqual(parsed.favorites[0].quoteId, 'q-003');
  });

  test('Gracefully recovers when stored payload is corrupted JSON', () => {
    const mockStorage = new MockLocalStorage();
    mockStorage.setItem('qotd_favorites_v1', '{ invalid json [ syntax error');

    const service = new StorageService(mockStorage);
    assertEqual(service.getFavorites(), [], 'Should reset corrupted data to empty array');
    assertFalse(service.isFavorite('q-001'));

    // Can still add new favorite after recovery
    service.addFavorite('q-002');
    assertTrue(service.isFavorite('q-002'));
  });

  test('Falls back to in-memory storage when localStorage throws SecurityError', () => {
    const throwingStorage = new MockLocalStorage(true);
    const service = new StorageService(throwingStorage);

    assertFalse(service.isStorageAvailable(), 'Should detect storage unavailability');
    
    // In-memory operations must still function without crashing
    service.addFavorite('q-010');
    assertTrue(service.isFavorite('q-010'));
    assertEqual(service.getFavorites().length, 1);

    service.removeFavorite('q-010');
    assertFalse(service.isFavorite('q-010'));
  });
});

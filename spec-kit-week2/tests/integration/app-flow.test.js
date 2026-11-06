import { describe, it, assert, assertEqual } from '../test-utils.js';
import { StorageService } from '../../src/js/storage.js';
import { QuoteManager } from '../../src/js/quote-manager.js';
import { QUOTES } from '../../src/js/quotes-data.js';

describe('Integration Test: Cross-Reload Persistence Lifecycle', () => {
  function createSharedStorage() {
    const memory = {};
    return {
      getItem(key) {
        return Object.prototype.hasOwnProperty.call(memory, key) ? memory[key] : null;
      },
      setItem(key, val) {
        memory[key] = String(val);
      },
      removeItem(key) {
        delete memory[key];
      }
    };
  }

  it('preserves favorited quotes across simulated session reloads', () => {
    const sharedStorageBackend = createSharedStorage();

    // --- SESSION 1: Initial visit and favoriting ---
    const storageSession1 = new StorageService(sharedStorageBackend);
    const initialFavorites1 = storageSession1.loadFavorites();
    const manager1 = new QuoteManager(QUOTES, initialFavorites1);

    const initialQuote = manager1.getInitialQuote();
    assertEqual(manager1.isFavorite(initialQuote.id), false, 'Initially not favorited');

    // User toggles favorite on
    const isNowFavorite = manager1.toggleFavorite(initialQuote.id);
    assertEqual(isNowFavorite, true);
    assertEqual(manager1.isFavorite(initialQuote.id), true);

    // Persist to storage
    const saved = storageSession1.saveFavorites(manager1.getFavoriteIds());
    assertEqual(saved, true);

    // --- SESSION 2: Simulated browser reload ---
    const storageSession2 = new StorageService(sharedStorageBackend);
    const reloadedFavorites2 = storageSession2.loadFavorites();
    const manager2 = new QuoteManager(QUOTES, reloadedFavorites2);

    // Verify favorite retained
    assertEqual(
      manager2.isFavorite(initialQuote.id),
      true,
      'Favorite state MUST persist across simulated page reload'
    );

    // Cycle to a different quote in session 2
    const nextQuote = manager2.getNextQuote();
    if (nextQuote.id !== initialQuote.id) {
      assertEqual(manager2.isFavorite(nextQuote.id), false);
    }

    // --- SESSION 3: User unfavorites and reloads again ---
    manager2.toggleFavorite(initialQuote.id);
    assertEqual(manager2.isFavorite(initialQuote.id), false);
    storageSession2.saveFavorites(manager2.getFavoriteIds());

    const storageSession3 = new StorageService(sharedStorageBackend);
    const reloadedFavorites3 = storageSession3.loadFavorites();
    const manager3 = new QuoteManager(QUOTES, reloadedFavorites3);

    assertEqual(
      manager3.isFavorite(initialQuote.id),
      false,
      'Unfavorited state MUST persist across subsequent reloads'
    );
  });
});

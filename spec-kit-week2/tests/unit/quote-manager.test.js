import { describe, it, assert, assertEqual, assertNotEqual, assertThrows } from '../test-utils.js';
import { QuoteManager } from '../../src/js/quote-manager.js';

describe('QuoteManager - Foundational Tests', () => {
  const sampleCatalog = [
    { id: 'q-1', text: 'Quote 1', author: 'Author 1' },
    { id: 'q-2', text: 'Quote 2', author: 'Author 2' },
    { id: 'q-3', text: 'Quote 3', author: 'Author 3' }
  ];

  it('throws an error if catalog is empty or invalid', () => {
    assertThrows(() => new QuoteManager([]), /at least one quote/);
    assertThrows(() => new QuoteManager(null), /at least one quote/);
    assertThrows(() => new QuoteManager('not-an-array'), /at least one quote/);
  });

  it('initializes successfully with a valid catalog', () => {
    const manager = new QuoteManager(sampleCatalog);
    assertEqual(manager.catalog.length, 3);
    assertEqual(manager.getCurrentQuote(), null, 'Initially currentQuote is null before selection');
  });

  it('initializes with pre-existing favorite IDs', () => {
    const manager = new QuoteManager(sampleCatalog, new Set(['q-1', 'q-3']));
    assertEqual(manager.isFavorite('q-1'), true);
    assertEqual(manager.isFavorite('q-2'), false);
    assertEqual(manager.isFavorite('q-3'), true);
  });
});

describe('QuoteManager - User Story 1: Initial Quote Selection', () => {
  const sampleCatalog = [
    { id: 'q-1', text: 'First Quote', author: 'Author One' },
    { id: 'q-2', text: 'Second Quote', author: 'Author Two' },
    { id: 'q-3', text: 'Third Quote', author: 'Author Three' }
  ];

  it('selects and returns a valid quote from the catalog on getInitialQuote()', () => {
    const manager = new QuoteManager(sampleCatalog);
    const initial = manager.getInitialQuote();

    assert(initial !== null, 'Initial quote must not be null');
    assert(['q-1', 'q-2', 'q-3'].includes(initial.id), 'Selected quote ID must exist in catalog');
    assert(initial.text.length > 0, 'Quote text must be non-empty');
    assert(initial.author.length > 0, 'Author must be non-empty');

    const current = manager.getCurrentQuote();
    assertEqual(current.id, initial.id, 'getCurrentQuote should match getInitialQuote');
    assertEqual(manager.previousQuoteId, initial.id, 'previousQuoteId should be set to initial quote ID');
  });

  it('works when catalog has only one quote', () => {
    const singleCatalog = [{ id: 'solo-1', text: 'Only quote', author: 'Solo' }];
    const manager = new QuoteManager(singleCatalog);
    const initial = manager.getInitialQuote();
    assertEqual(initial.id, 'solo-1');
  });
});

describe('QuoteManager - User Story 2: Request New Random Quote', () => {
  const multiCatalog = [
    { id: 'q-1', text: 'First Quote', author: 'Author One' },
    { id: 'q-2', text: 'Second Quote', author: 'Author Two' },
    { id: 'q-3', text: 'Third Quote', author: 'Author Three' }
  ];

  it('selects a valid quote and never returns the same quote consecutively', () => {
    const manager = new QuoteManager(multiCatalog);
    let previousQuote = manager.getInitialQuote();

    for (let i = 0; i < 50; i++) {
      const nextQuote = manager.getNextQuote();
      assert(nextQuote !== null, 'Next quote must not be null');
      assert(['q-1', 'q-2', 'q-3'].includes(nextQuote.id), 'Next quote ID must exist in catalog');
      assertNotEqual(
        nextQuote.id,
        previousQuote.id,
        `Consecutive repeat detected on iteration ${i}: ${nextQuote.id} matches previous ${previousQuote.id}`
      );
      assertEqual(manager.getCurrentQuote().id, nextQuote.id);
      assertEqual(manager.previousQuoteId, nextQuote.id);
      previousQuote = nextQuote;
    }
  });

  it('handles single-item catalog gracefully on getNextQuote()', () => {
    const singleCatalog = [{ id: 'solo-1', text: 'Only quote', author: 'Solo' }];
    const manager = new QuoteManager(singleCatalog);
    manager.getInitialQuote();

    const next = manager.getNextQuote();
    assertEqual(next.id, 'solo-1', 'Should return the single quote without error');
  });
});

describe('QuoteManager - User Story 3: Favorite Toggling', () => {
  const sampleCatalog = [
    { id: 'q-1', text: 'First Quote', author: 'Author One' },
    { id: 'q-2', text: 'Second Quote', author: 'Author Two' }
  ];

  it('correctly toggles favorite status on and off', () => {
    const manager = new QuoteManager(sampleCatalog);

    assertEqual(manager.isFavorite('q-1'), false, 'Initially quote should not be favorited');

    // Toggle ON
    const state1 = manager.toggleFavorite('q-1');
    assertEqual(state1, true, 'toggleFavorite should return true when turning ON');
    assertEqual(manager.isFavorite('q-1'), true, 'isFavorite should return true');
    assertEqual(manager.getFavoriteIds().has('q-1'), true, 'Favorite set must include q-1');

    // Toggle OFF
    const state2 = manager.toggleFavorite('q-1');
    assertEqual(state2, false, 'toggleFavorite should return false when turning OFF');
    assertEqual(manager.isFavorite('q-1'), false, 'isFavorite should return false');
    assertEqual(manager.getFavoriteIds().has('q-1'), false, 'Favorite set must no longer include q-1');
  });

  it('handles toggling with null or empty ID gracefully without throwing', () => {
    const manager = new QuoteManager(sampleCatalog);
    const result = manager.toggleFavorite(null);
    assertEqual(result, false);
    assertEqual(manager.isFavorite(null), false);
  });
});

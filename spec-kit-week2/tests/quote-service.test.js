/**
 * Unit Tests for QuoteService
 */

import { describe, test } from './test-runner.js';
import { assert, assertEqual, assertTrue, assertFalse } from './assert.js';
import { QuoteService } from '../src/services/quote-service.js';

const mockCatalog = [
  { id: 'q-001', text: 'First quote body', author: 'Author One', category: 'Testing' },
  { id: 'q-002', text: 'Second quote body', author: 'Author Two', category: 'Wisdom' },
  { id: 'q-003', text: 'Third quote body', author: 'Author Three', category: 'Action' }
];

describe('QuoteService Test Suite', () => {
  test('Returns full list of quotes and correct count', () => {
    const service = new QuoteService(mockCatalog);
    assertEqual(service.getQuoteCount(), 3);
    assertEqual(service.getAllQuotes().length, 3);
  });

  test('Retrieves quote by unique ID correctly', () => {
    const service = new QuoteService(mockCatalog);
    const quote = service.getQuoteById('q-002');
    assert(quote !== null, 'Quote q-002 should be found');
    assertEqual(quote.author, 'Author Two');

    const notFound = service.getQuoteById('q-999');
    assertEqual(notFound, null, 'Non-existent quote should return null');
  });

  test('Picks a valid random quote initially', () => {
    const service = new QuoteService(mockCatalog);
    const quote = service.getRandomQuote();
    assert(quote !== null, 'Random quote must not be null');
    assert(['q-001', 'q-002', 'q-003'].includes(quote.id), 'Quote ID must be from catalog');
  });

  test('Guarantees no immediate consecutive repeat when catalog size >= 2', () => {
    const service = new QuoteService(mockCatalog);
    const currentId = 'q-002';

    // Run 50 random selections excluding q-002
    for (let i = 0; i < 50; i++) {
      const nextQuote = service.getRandomQuote(currentId);
      assert(nextQuote.id !== currentId, `Next quote ${nextQuote.id} must not equal current quote ${currentId}`);
    }
  });

  test('Handles edge case of single-quote catalog gracefully', () => {
    const singleCatalog = [{ id: 'q-001', text: 'Only quote', author: 'Solo' }];
    const service = new QuoteService(singleCatalog);

    const quote = service.getRandomQuote('q-001');
    assertEqual(quote.id, 'q-001', 'Should return the single available quote without error');
  });
});

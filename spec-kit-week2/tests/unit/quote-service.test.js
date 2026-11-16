import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { QuoteService } from '../../src/quote-service.js';
import { QUOTES } from '../../src/quotes.js';

describe('QuoteService', () => {
  const service = new QuoteService(QUOTES);

  it('should return all quotes from catalog', () => {
    const quotes = service.getAllQuotes();
    assert.equal(quotes.length, QUOTES.length);
    assert.ok(quotes.length >= 5, 'Catalog must contain at least 5 quotes');
  });

  it('should return a valid random quote with non-empty text and author (US1)', () => {
    const quote = service.getRandomQuote();
    assert.ok(quote, 'Quote should be defined');
    assert.ok(typeof quote.id === 'string' && quote.id.length > 0);
    assert.ok(typeof quote.text === 'string' && quote.text.length > 0);
    assert.ok(typeof quote.author === 'string' && quote.author.length > 0);
  });

  it('should avoid immediate duplicate quote when excludeId is provided (US2)', () => {
    const firstQuote = service.getRandomQuote();
    
    // Sample multiple times to verify it never returns firstQuote.id
    for (let i = 0; i < 50; i++) {
      const nextQuote = service.getRandomQuote(firstQuote.id);
      assert.notEqual(
        nextQuote.id,
        firstQuote.id,
        `Expected quote different from ${firstQuote.id}, but got ${nextQuote.id}`
      );
    }
  });

  it('should retrieve a quote by id', () => {
    const quote = service.getQuoteById('quote-1');
    assert.ok(quote);
    assert.equal(quote.id, 'quote-1');
  });

  it('should handle single-item catalog without throwing when excluding id', () => {
    const singleCatalogService = new QuoteService([
      { id: 'lone-quote', text: 'Solo quote', author: 'Solo' }
    ]);
    const quote = singleCatalogService.getRandomQuote('lone-quote');
    assert.equal(quote.id, 'lone-quote');
  });
});


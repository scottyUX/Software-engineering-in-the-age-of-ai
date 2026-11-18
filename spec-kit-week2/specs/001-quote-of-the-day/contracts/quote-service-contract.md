# Contract: Quote Service (`QuoteService`)

The `QuoteService` manages the static quote catalog and provides deterministic and random retrieval operations.

## Module Interface

```typescript
export interface Quote {
  id: string;
  text: string;
  author: string;
  category?: string;
}

export interface IQuoteService {
  /**
   * Returns all quotes in the catalog.
   */
  getAllQuotes(): Quote[];

  /**
   * Retrieves a quote by its unique ID.
   * Returns null if not found.
   */
  getQuoteById(id: string): Quote | null;

  /**
   * Selects a random quote from the catalog.
   * If currentId is provided and catalog length > 1, the returned quote
   * will NOT match currentId.
   */
  getRandomQuote(currentId?: string): Quote;

  /**
   * Returns the total count of quotes in the catalog.
   */
  getQuoteCount(): number;
}
```

## Invariants & Behavioral Guarantees

1. `getRandomQuote(currentId)` MUST return a non-null `Quote` object as long as catalog length $\ge 1$.
2. When catalog contains $\ge 2$ items and `currentId` is passed, `getRandomQuote(currentId).id !== currentId` is guaranteed.
3. When catalog contains exactly 1 item, `getRandomQuote(currentId)` returns that single item without recursion or error.
4. All quotes returned MUST conform to the schema defined in [data-model.md](../data-model.md).

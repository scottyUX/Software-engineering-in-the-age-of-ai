# Contract: Storage Service (`StorageService`)

The `StorageService` encapsulates persistence across browser sessions, wrapping `localStorage` with error handling, defensive fallbacks, and schema validation.

## Module Interface

```typescript
export interface FavoriteRecord {
  quoteId: string;
  favoritedAt: number;
}

export interface StorageEnvelope {
  version: number;
  updatedAt: number;
  favorites: FavoriteRecord[];
}

export interface IStorageService {
  /**
   * Retrieves all persisted favorites as an array of FavoriteRecord.
   * Returns empty array if none exist or storage is corrupted/inaccessible.
   */
  getFavorites(): FavoriteRecord[];

  /**
   * Checks if a given quoteId is currently favorited.
   */
  isFavorite(quoteId: string): boolean;

  /**
   * Adds a quoteId to favorites.
   * Idempotent: If already favorited, updates or preserves record.
   * Returns true on success, false if storage failed.
   */
  addFavorite(quoteId: string): boolean;

  /**
   * Removes a quoteId from favorites.
   * Returns true on success, false if storage failed.
   */
  removeFavorite(quoteId: string): boolean;

  /**
   * Toggles the favorite status of a quoteId.
   * Returns the new favorite state (true = favorited, false = unfavorited).
   */
  toggleFavorite(quoteId: string): boolean;

  /**
   * Clears all stored favorites.
   */
  clearFavorites(): void;

  /**
   * Indicates whether persistent storage (localStorage) is operational.
   */
  isStorageAvailable(): boolean;
}
```

## Invariants & Behavioral Guarantees

1. If `localStorage` is disabled or throws an exception (`SecurityError`, `QuotaExceededError`), the service MUST NOT throw unhandled exceptions; it gracefully falls back to an in-memory `Set` and reports `isStorageAvailable() === false`.
2. Any malformed or non-JSON data stored under the key MUST be safely cleared and re-initialized with an empty envelope.
3. Every mutating call (`addFavorite`, `removeFavorite`, `toggleFavorite`) immediately syncs state to both memory and persistent storage.

# Contract: Storage & Persistence Interface

**Feature**: Quote of the Day
**Branch**: `001-quote-of-the-day`
**Date**: 2026-10-07

This document defines the storage key contracts, serialization formats, and error handling behaviors for persisting favorites in browser `localStorage`.

---

## 1. Storage Keys & Payload

- **Storage Key**: `qod_favorite_quote_ids`
- **Storage Target**: `window.localStorage`
- **MIME / Format**: UTF-8 encoded JSON string

### Schema

```json
[
  "quote-id-1",
  "quote-id-2"
]
```

#### Example Stored Value
```text
["q-002","q-005","q-012"]
```

---

## 2. API / Contract Methods

The storage layer must be exposed through a `StorageService` interface:

```javascript
export class StorageService {
  /**
   * Loads saved favorite quote IDs from storage.
   * @returns {Set<string>} Set of saved favorite quote IDs.
   */
  loadFavorites(): Set<string>;

  /**
   * Persists the given set of favorite quote IDs to storage.
   * @param {Set<string> | string[]} favoriteIds
   * @returns {boolean} True if saved successfully, false if storage failed.
   */
  saveFavorites(favoriteIds: Set<string> | string[]): boolean;

  /**
   * Checks whether storage is available and operational.
   * @returns {boolean}
   */
  isAvailable(): boolean;
}
```

---

## 3. Resilience & Error Contracts

1. **Storage Unavailable (Incognito / Disabled)**:
   - If accessing `window.localStorage` throws a `SecurityError` or returns `null`/`undefined`, `isAvailable()` MUST return `false`.
   - `loadFavorites()` MUST return an empty `Set<string>()` and log a diagnostic notice to `console.warn`.
   - `saveFavorites()` MUST update an internal in-memory fallback set, return `false`, and not throw an unhandled exception.

2. **Malformed / Corrupted Data**:
   - If `localStorage.getItem(STORAGE_KEY)` returns invalid JSON or a non-array value (e.g. `{}` or `null` or raw invalid string):
     - `loadFavorites()` MUST catch the parse error.
     - Reset storage key to `"[]"`.
     - Return an empty `Set<string>()`.

3. **Quota Exceeded**:
   - If `localStorage.setItem` throws `QuotaExceededError`:
     - Catch exception, log error to `console.error`.
     - Return `false` without crashing the application.

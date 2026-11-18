# Phase 1 Data Model: Quote of the Day

## 1. Domain Entities

### 1.1 Quote Entity
Represents an individual curated quote in the static catalog.

| Field | Type | Description | Constraints |
| :--- | :--- | :--- | :--- |
| `id` | `string` | Unique identifier for the quote (e.g., `"q-001"`) | Required, non-empty, unique across catalog |
| `text` | `string` | Full body text of the quote | Required, non-empty, trimmed |
| `author` | `string` | Attribution or author name | Required, non-empty, defaults to `"Unknown"` if anonymous |
| `category` | `string` | Optional thematic category (e.g., `"Wisdom"`, `"Perseverance"`) | Optional, non-empty string |

#### Validation Rules
- `id` must match pattern `^q-[0-9]{3,}$`.
- `text` length must be between 5 and 500 characters.
- `author` length must be between 1 and 100 characters.

---

### 1.2 FavoriteRecord Entity
Represents the persisted association indicating a quote has been favorited by the user.

| Field | Type | Description | Constraints |
| :--- | :--- | :--- | :--- |
| `quoteId` | `string` | Identifier of the referenced quote | Required, matches existing Quote `id` |
| `favoritedAt` | `number` | Unix epoch timestamp in milliseconds when favorited | Required, positive integer ($\le \text{Date.now()}$) |

#### Validation Rules
- `quoteId` must be a valid string identifier.
- `favoritedAt` must be an integer epoch timestamp.
- Duplicates: `quoteId` must be unique within the favorites set (set semantics).

---

### 1.3 AppState (Runtime Client State)
In-memory state managed during an active browser session.

| Field | Type | Description | Initial Value |
| :--- | :--- | :--- | :--- |
| `currentQuote` | `Quote \| null` | The currently displayed quote object | `null` (populated during bootstrap) |
| `favorites` | `Map<string, FavoriteRecord>` | Fast lookup set of favorited quote IDs and metadata | Loaded from `localStorage` |
| `favoritesOpen` | `boolean` | Whether the favorites modal/drawer is open | `false` |
| `storageAvailable` | `boolean` | Whether `localStorage` is operational | Verified on init |

---

## 2. Storage Schema (`localStorage`)

### 2.1 Storage Key & Envelope
- **Key**: `qotd_favorites_v1`
- **Format**: JSON serialized object

```json
{
  "version": 1,
  "updatedAt": 1775668800000,
  "favorites": [
    {
      "quoteId": "q-001",
      "favoritedAt": 1775668800000
    },
    {
      "quoteId": "q-007",
      "favoritedAt": 1775668920000
    }
  ]
}
```

### 2.2 Defensive Deserialization & Recovery
1. If key `qotd_favorites_v1` does not exist: Initialize with `{ version: 1, updatedAt: Date.now(), favorites: [] }`.
2. If JSON parsing fails (syntax error or corrupted payload): Log diagnostic warning, reset to empty favorites envelope without raising an unhandled exception.
3. If payload version is unrecognized: Fall back to empty array and write current version.
4. Filter out any malformed entries where `quoteId` is missing or not a string.

---

## 3. State Transitions

```
[ App Launch ]
      │
      ▼
┌──────────────┐   Load Favorites    ┌──────────────────┐
│ Initializing ├────────────────────►│ Favorites Loaded │
└──────────────┘                     └────────┬─────────┘
                                              │ Pick Random Quote
                                              ▼
                                     ┌──────────────────┐
                                     │ Quote Displayed  │
                                     └────────┬─────────┘
                     ┌────────────────────────┼────────────────────────┐
      Click "New Quote"                       │ Toggle Favorite        │ Open Favorites
                     ▼                        ▼                        ▼
        ┌──────────────────┐        ┌──────────────────┐     ┌──────────────────┐
        │ Select Distinct  │        │ Update Store &   │     │ Render Favorites │
        │   Random Quote   │        │ Toggle Indicator │     │      Drawer      │
        └────────┬─────────┘        └────────┬─────────┘     └────────┬─────────┘
                 │                           │                        │ Close Drawer
                 └───────────────────────────┴────────────────────────┘
```

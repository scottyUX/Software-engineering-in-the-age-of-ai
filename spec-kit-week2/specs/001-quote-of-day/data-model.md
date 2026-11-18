# Data Model: Quote of the Day

## Quote

A built-in, immutable quotation that can be displayed and saved by a visitor.

| Field | Type | Rules |
|---|---|---|
| `id` | String | Required; stable and unique across the built-in collection; used as the favorite key. |
| `text` | String | Required; non-empty, trimmed quotation text. |
| `attribution` | String | Required; non-empty author or source attribution shown with the quotation. |

**Collection constraints**:

- The shipped collection MUST contain at least five distinct usable quotes.
- Distinctness is determined by normalized quote text and attribution; duplicate entries MUST NOT be treated as a different selection.
- Each entry MUST have accurate attribution and reuse rights checked before inclusion.

## Favorite Collection

The visitor's set of saved quote references, scoped to the current browser origin and profile.

| Field | Type | Rules |
|---|---|---|
| `quoteIds` | Array of String | Unique IDs that match built-in quotes; unknown IDs are ignored when restoring. |

**Persistence representation**: A JSON-serialized array of quote IDs in one namespaced `localStorage` key. Storage is best-effort: inaccessible, malformed, or failed reads/writes result in an empty in-memory collection, a user-visible persistence warning, and continued quote browsing.

## Page State and Transitions

- **Current quote**: One usable quote selected randomly on page load. Selecting New quote chooses a different distinct entry when at least two are available; a one-entry collection retains that entry.
- **Favorite state**: Toggling the current quote adds or removes its ID from the favorite collection and changes the heart's accessible and visual state.
- **Restoration**: Page load reads and validates stored IDs against the built-in collection before presenting favorites. Reload does not alter valid saved favorites.
- **Failure fallback**: A persistence error disables claims of durable saving but MUST NOT disable showing or changing quotes.

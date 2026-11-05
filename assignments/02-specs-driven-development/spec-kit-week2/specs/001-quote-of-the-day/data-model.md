# Data Model: Quote of the Day

## Quote

Built in; never changed at runtime.

| Field | Type | Rules |
|-------|------|-------|
| `id` | string | Required, unique, stable if the list is reordered |
| `text` | string | Required, non-empty |
| `author` | string | Required, non-empty |

The list must contain at least 10 quotes (FR-002).

## Favorites

The set of quote ids the visitor has marked.

- Contains no duplicates.
- Contains only ids present in the built-in list; unknown ids are dropped on load.
- Starts empty when saved data is missing, corrupt, or unavailable.

**State transitions** for one quote: `not favorite` ⇄ `favorite`, by the favorite control.

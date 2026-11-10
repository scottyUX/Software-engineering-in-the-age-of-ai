# Contract: Page Interface

| Element id | Purpose | Behavior |
|------------|---------|----------|
| `quote-text` | Quote text | Always holds the current quote |
| `quote-author` | Quote author | Always holds the current quote's author |
| `new-quote` | Button labeled "New quote" | Replaces the shown quote |
| `favorite` | Favorite toggle button | `aria-pressed` is `"true"` when the shown quote is a favorite, otherwise `"false"`; its label reads "Favorite" or "Favorited" |

Both controls are native `<button>` elements, so they work by keyboard (FR-008).

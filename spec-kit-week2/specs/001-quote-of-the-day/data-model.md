# Data Model

## Entities

### `Quote`
Represents a single quote within the built-in list.
- `id` (String | Number): Unique identifier for the quote (necessary to track favorites in localStorage reliably, regardless of quote text changes).
- `text` (String): The actual quote content.
- `author` (String): The author of the quote.

### `AppState`
Represents the client-side state of the application.
- `currentQuoteId` (String | Number): The ID of the quote currently being displayed.
- `favorites` (Array of Strings/Numbers): A list of quote IDs that the user has favorited.

## State Transitions
- **Action**: "New quote"
  - Updates `AppState.currentQuoteId` to a randomly selected `Quote.id` that is different from the current one (if there's more than one quote).
- **Action**: "Toggle favorite"
  - If `AppState.currentQuoteId` is in `AppState.favorites`, remove it.
  - If `AppState.currentQuoteId` is not in `AppState.favorites`, add it.
  - Persist the updated `favorites` array to `localStorage`.


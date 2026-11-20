# Data Model: Quote of the Day

## Entities

### Quote
Represents one item in the built-in quote collection.

- `id`: unique identifier for the quote
- `text`: quote content to display
- `author`: optional attribution or source label

### Favorite Collection
Represents the set of favorite quote identifiers chosen by the user.

- `favoriteIds`: array of unique quote IDs persisted in browser storage
- `storageKey`: stable key used to access persisted favorites

### UI State
Represents the ephemeral browser state for the active page view.

- `currentQuoteId`: the quote currently displayed
- `isFavorite`: whether the current quote is included in the saved favorites

## Validation Rules
- Each quote must have a unique identifier.
- Quote text must be non-empty and displayable to the user.
- Favorite identifiers must match an existing quote in the built-in data set.
- Persisted values must be treated safely when storage data is missing, malformed, or corrupted.

## State Transitions
1. Initial load: choose a quote from the available list and render it.
2. New quote action: select a different quote and update the visible state.
3. Favorite toggle: add or remove the active quote ID from the favorite collection.
4. Reload: rehydrate the favorite collection from browser storage and restore the saved state.

## Persistence Rules
- Favorite state is stored in `localStorage` so it survives page reloads.
- Invalid or empty stored values are ignored and replaced with a safe default.
- The UI should never rely on a backend to maintain favorite state.

# Client-Side Storage Contract

Since there is no backend API, the primary integration surface is the browser's `localStorage` API.

## LocalStorage Schema

### Key: `quoteApp_favorites`
- **Type**: JSON Array of `Quote.id` strings/numbers.
- **Description**: Stores the list of IDs for quotes that the user has favorited.
- **Example**: `["1", "4", "7"]`
- **Default**: If the key does not exist, the app should assume an empty array `[]`.

## DOM Interface Contract
The application exposes a standard web interface.
- Must be accessible via a standard web browser without a build step or server running (e.g., opening `index.html` via `file://` protocol or a static file server).


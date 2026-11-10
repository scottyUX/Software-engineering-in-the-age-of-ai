# Research: Quote of the Day

## Script loading

- **Decision**: Classic `<script>` tags that share one `QuoteLogic` global.
- **Rationale**: Browsers block ES modules on `file://` pages, and the page must work when
  `index.html` is opened directly.
- **Alternatives considered**: ES modules (need a local server); a bundler (adds a dependency and a
  build step).

## Testing

- **Decision**: `node --test` for the rules, plus a real-page test that drives Chrome through its
  built-in DevTools protocol.
- **Rationale**: Reload persistence can only be proven in a real browser, and neither approach adds
  a package.
- **Alternatives considered**: Playwright and jsdom (both add dependencies; jsdom also would not
  prove real persistence).

## Quote identity

- **Decision**: Each quote has a fixed short string `id`.
- **Rationale**: The spec requires identity that does not depend on list position, so that reordering
  the list cannot move a favorite to a different quote.
- **Alternatives considered**: Array index (breaks on reorder); the quote text (breaks on a typo fix).

## Storage failure handling

- **Decision**: Wrap every localStorage call in `try/catch` and validate the parsed value.
- **Rationale**: Reading or writing can throw when storage is blocked, and saved content may be
  corrupt (FR-007).
- **Alternatives considered**: Checking for `window.localStorage` only (misses thrown errors).

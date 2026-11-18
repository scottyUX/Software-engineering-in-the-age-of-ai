# User Interface Contract

## Quote Panel

- On load with a usable built-in collection, render exactly one quote's text and its attribution.
- Provide a clearly named **New quote** button. Selecting it displays a random distinct quote when at least two distinct entries exist; with one entry, keep that entry visible.
- If there are no usable quotes, show a plain-language unavailable message and disable quote-specific controls.

## Favorite Toggle

- Render a heart-icon button for the current quote.
- The button MUST be keyboard-operable, have an accessible name that communicates the action and quote, and expose its current state (for example, `aria-pressed`).
- Use outlined/unfilled appearance when not saved and filled appearance when saved; update state immediately when toggled.
- Saving or removing a favorite updates the favorites list and best-effort persistence.

## Favorites List and Feedback

- Show saved quote text and attribution so visitors can review favorites without waiting for them to appear as the current quote.
- Each saved quote has a clearly named, keyboard-operable removal action that removes it from the list and saved state.
- Show a clear empty state when there are no favorites.
- When storage is blocked, invalid, or fails, show a non-blocking message that favorites may not persist; quote display and browsing remain available.

## Accessibility and Content

- Use semantic headings, buttons, quote text, and attribution markup with visible focus indicators and adequate contrast.
- Keep all interactive actions operable using keyboard input and expose status messages to assistive technology.
- Include at least five distinct built-in quotes with accurate attribution and verified reuse rights.

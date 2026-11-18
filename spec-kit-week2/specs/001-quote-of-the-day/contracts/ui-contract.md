# Contract: UI Controller & DOM Contract

Defines the DOM contract, elements, semantic structure, accessibility attributes, transitions, and event interactions for the Quote of the Day web page.

## Required DOM Selectors & Roles

| DOM Element / Selector | Tag / Role | ARIA Attributes | Purpose |
| :--- | :--- | :--- | :--- |
| `#quote-card` | `<article>` | `aria-live="polite"` | Container for the currently displayed quote |
| `#quote-text` | `<blockquote>` | N/A | Displays the quote content text; receives `.fade-in` animation on change |
| `#quote-author` | `<cite>` | N/A | Displays the quote author attribution |
| `#btn-new-quote` | `<button>` | `aria-label="Get new quote"` | Triggers selection of a new random quote |
| `#btn-favorite` | `<button>` | `aria-label="Toggle favorite"`, `aria-pressed="false\|true"` | Toggles favorite status for active quote |
| `#btn-open-favorites` | `<button>` | `aria-label="View saved favorites"` | Toggles visibility of the favorites drawer |
| `#favorites-drawer` | `<aside>` | `aria-hidden="true\|false"`, `role="region"` | Slide-out panel or modal displaying saved favorites |
| `#favorites-list` | `<ul>` | `aria-label="Saved quotes list"` | Lists all favorited quotes with removal buttons |
| `#storage-warning` | `<div role="alert">` | `aria-hidden="true\|false"` | Visible warning banner if localStorage is blocked |

## Visual Transition Contract

- **Animation Class**: `.fade-in`
- **Duration**: `0.5s` (500ms) with `ease-out` timing.
- **Keyframes**:
  ```css
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(4px); }
    to { opacity: 1; transform: translateY(0); }
  }
  ```
- **Rapid Click Guarantee**: Upon consecutive updates, the `.fade-in` class is cleanly removed and re-applied (via forced reflow `void element.offsetWidth`), resetting the animation to 0 without visual artifacts.
- **Reduced Motion**: Under `@media (prefers-reduced-motion: reduce)`, animation duration collapses to 0ms, rendering text immediately.

## User Action Contract

```typescript
export interface IUIController {
  /**
   * Renders the given quote in the primary quote display and triggers
   * the 0.5-second fade-in transition on the quote text.
   */
  renderQuote(quote: Quote, isFavorited: boolean): void;

  /**
   * Updates the favorite button indicator state.
   */
  updateFavoriteStatus(isFavorited: boolean): void;

  /**
   * Renders the list of saved favorites in the favorites drawer.
   */
  renderFavoritesList(favorites: Array<{ quote: Quote; favoritedAt: number }>): void;

  /**
   * Opens or closes the favorites drawer.
   */
  toggleFavoritesDrawer(isOpen: boolean): void;

  /**
   * Displays or hides the storage unavailability alert banner.
   */
  showStorageWarning(show: boolean): void;
}
```

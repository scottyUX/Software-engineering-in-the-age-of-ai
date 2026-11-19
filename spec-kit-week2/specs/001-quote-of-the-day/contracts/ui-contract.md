# Contract: User Interface & DOM Elements

**Feature**: Quote of the Day
**Branch**: `001-quote-of-the-day`
**Date**: 2026-10-07

This document specifies the DOM interface, accessibility attributes, and user interaction contracts.

---

## 1. Required DOM Elements & Selectors

The semantic HTML structure MUST provide the following IDs and attributes for robust script binding and testing:

| Element Role | Selector / ID | HTML Element | Purpose |
|---|---|---|---|
| **Quote Card Container** | `#quote-container` | `<article>` / `<figure>` | Container wrapping the quote, author, and actions. |
| **Quote Text Display** | `#quote-text` | `<blockquote>` / `<p>` | Displays quotation text. Has `aria-live="polite"` on parent. |
| **Author Attribution** | `#quote-author` | `<figcaption>` / `<cite>` | Displays author name. |
| **"New Quote" Button** | `#btn-new-quote` | `<button type="button">` | Triggers fetching and displaying a new quote. Renders as text only — no icon span. |
| **"Favorite" Toggle Button** | `#btn-favorite` | `<button type="button">` | Toggles favorite state for the currently displayed quote. |
| **Favorite Visual Icon** | `#favorite-icon` | `<span>` or `<svg>` | Visual glyph indicating active or inactive favorite state. |
| **"Copy" Button** | `#btn-copy` | `<button type="button">` | Copies current quote text + author to the system clipboard. Positioned between `#btn-favorite` and `#btn-new-quote`. |

---

## 2. Accessibility & ARIA Contract

To ensure accessibility compliance (WCAG 2.1 AA):

- **Favorite Toggle Button (`#btn-favorite`)**:
  - Attribute: `aria-pressed="false"` when the current quote is NOT favorited.
  - Attribute: `aria-pressed="true"` when the current quote IS favorited.
  - Attribute: `aria-label="Add quote to favorites"` when unfavorited; `aria-label="Remove quote from favorites"` when favorited.
- **Quote Live Region (`#quote-container`)**:
  - Attribute: `aria-live="polite"` and `aria-atomic="true"` so screen readers announce changes when a new quote is loaded without interrupting user focus.
- **Keyboard Navigation**:
  - Buttons MUST be reachable via standard `Tab` navigation.
  - Buttons MUST be actionable using both `Enter` and `Space` keys.

---

## 3. DOM Event Contracts

### 3.1 "New Quote" Click Event
- **Trigger**: User activates `#btn-new-quote` (click or keypress).
- **Behavior**:
  1. Invokes `quoteManager.getNextQuote()`.
  2. Updates text content of `#quote-text` and `#quote-author`.
  3. Updates `#btn-favorite` state (`aria-pressed`, label, visual icon) based on whether the new quote is in the favorites set.
  4. Response time target: < 50ms.

### 3.2 "Favorite" Toggle Click Event
- **Trigger**: User activates `#btn-favorite`.
- **Behavior**:
  1. Invokes `quoteManager.toggleFavorite(currentQuote.id)`.
  2. Toggles `aria-pressed` between `"true"` and `"false"`.
  3. Toggles visual CSS class (e.g., `.is-favorite`) on `#btn-favorite`.
  4. Persists the updated set via `storageService`.

### 3.3 "Copy" Click Event
- **Trigger**: User activates `#btn-copy` (click or keypress).
- **Behavior**:
  1. Reads the current quote's `text` and `author` from `quoteManager.getCurrentQuote()`.
  2. Calls `navigator.clipboard.writeText("<text> — <author>")`.
  3. On success: temporarily adds `.copied` class to `#btn-copy` and changes its visible label to "Copied!" for ~1.5 seconds, then reverts.
  4. On failure (API unavailable or permission denied): emits `console.warn` — no user-visible error shown.

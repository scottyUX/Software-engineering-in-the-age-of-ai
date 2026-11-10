# Feature Specification: Quote of the Day

**Feature Branch**: `week2-omar-diab`

**Created**: 2026-10-30

**Status**: Draft

**Input**: User description: "A quote-of-the-day page: one random quote from a built-in list, a "New quote" button, and favoriting that persists across reloads."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read a random quote (Priority: P1)

A visitor opens the page and immediately sees one quote and its author, chosen at random from the
built-in list.

**Why this priority**: Showing a quote is the purpose of the page; nothing else matters without it.

**Independent Test**: Open the page and confirm that one quote with its author is displayed.

**Acceptance Scenarios**:

1. **Given** the page is closed, **When** a visitor opens it, **Then** exactly one quote from the
   built-in list is shown with its author.
2. **Given** the page has been opened many times, **When** the shown quotes are compared, **Then**
   more than one different quote has appeared.

---

### User Story 2 - Ask for a new quote (Priority: P2)

A visitor who wants something different presses the "New quote" button and sees another quote.

**Why this priority**: It makes the page worth staying on, but depends on a quote being shown.

**Independent Test**: Press "New quote" and confirm the displayed quote is replaced.

**Acceptance Scenarios**:

1. **Given** a quote is shown, **When** the visitor presses "New quote", **Then** a different quote
   from the built-in list replaces it, every time.

---

### User Story 3 - Keep favorites (Priority: P3)

A visitor marks a quote as a favorite and finds it still marked after reloading the page.

**Why this priority**: It adds lasting value, but the page is useful without it.

**Independent Test**: Mark a quote as a favorite, reload, return to that quote, and confirm it is
still marked.

**Acceptance Scenarios**:

1. **Given** a quote is shown that is not a favorite, **When** the visitor marks it, **Then** it is
   visibly shown as a favorite.
2. **Given** a quote is a favorite, **When** the visitor unmarks it, **Then** it is no longer shown
   as a favorite.
3. **Given** a quote is a favorite, **When** the page is reloaded and that quote appears, **Then**
   it is still shown as a favorite.

---

### Edge Cases

- The browser's saved favorites are missing, corrupt, or cannot be read: the page still shows
  quotes and starts with no favorites.
- Saving is unavailable (for example, storage is blocked): the visitor can still mark favorites for
  the current visit, and is not shown a broken page.
- A saved favorite refers to a quote no longer in the built-in list: it is ignored.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The page MUST show exactly one quote and its author at all times after loading.
- **FR-002**: The page MUST choose the first quote at random from a built-in list of at least 10
  quotes.
- **FR-003**: The page MUST provide a control labeled "New quote" that replaces the shown quote
  with one chosen at random from the other quotes in the built-in list, so that pressing it always
  visibly changes the quote.
- **FR-004**: Users MUST be able to mark and unmark the shown quote as a favorite.
- **FR-005**: The page MUST show whether the currently displayed quote is a favorite.
- **FR-006**: Favorites MUST persist across page reloads in the same browser.
- **FR-007**: The page MUST keep working when saved favorites are missing, corrupt, or unavailable.
- **FR-008**: All controls MUST be usable by keyboard, and the favorite state MUST be conveyed to
  assistive technology, not by color alone.

### Key Entities

- **Quote**: A built-in saying with its text, its author, and a stable identity that does not depend
  on its position in the list.
- **Favorites**: The set of quotes the visitor has marked, saved in their browser.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A visitor sees a quote within 1 second of the page opening.
- **SC-002**: Over 100 presses of "New quote", at least half of the built-in quotes appear.
- **SC-003**: 100% of favorites marked before a reload are still marked after it.
- **SC-004**: The page shows a quote and working controls in all of these saved-data states:
  missing, corrupt, and unavailable.

## Assumptions

- There is one visitor per browser; there are no accounts and favorites are not synced to other
  devices.
- "Quote of the day" is the page's name: the assignment asks for a random quote on each load, not a
  quote fixed for the calendar day.
- A list of saved favorites to browse is out of scope; favorites are only marked on the quote shown.
- The page is in English and works in current desktop and mobile browsers.

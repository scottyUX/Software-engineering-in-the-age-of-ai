# Tasks for Quote of the Day

## Phase 1: Setup (Shared Infrastructure)
**Purpose**: Project initialization and basic structure

- [x] T001 Create `src` and `tests` directories
- [x] T002 [P] Create empty `src/index.html` file
- [x] T003 [P] Create empty `src/styles.css` file
- [x] T004 [P] Create empty `src/app.js` file
- [x] T005 [P] Create empty `tests/app.test.js` file
- [x] T006 Initialize Node.js project (for testing) and install Jest

---

## Phase 2: Foundational (Blocking Prerequisites)
**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T007 Create hardcoded `Quote` array data structure with `id`, `text`, and `author` fields in `src/app.js`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Random Quote (Priority: P1) → MVP
**Goal**: Users visit the page and are immediately presented with a random quote from the system's built-in list.
**Independent Test**: Can be independently tested by opening the page and verifying a quote is visible.

### Tests for User Story 1
> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**
- [x] T008 [US1] Write test for random quote selection function in `tests/app.test.js`

### Implementation for User Story 1
- [x] T009 [P] [US1] Scaffold basic HTML structure in `src/index.html` including elements for quote text and author
- [x] T010 [US1] Implement `getRandomQuote()` logic in `src/app.js`
- [x] T011 [US1] Implement DOM rendering logic to display the selected quote on initial page load in `src/app.js`
- [x] T012 [P] [US1] Add basic styling for the quote container in `src/styles.css`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Get a New Quote (Priority: P2)
**Goal**: Users can click a "New quote" button to replace the currently displayed quote with another random one from the list.
**Independent Test**: Can be tested by clicking the button and verifying the text changes to a different quote.

### Tests for User Story 2
- [x] T013 [US2] Write test for updating `AppState.currentQuoteId` logic in `tests/app.test.js`

### Implementation for User Story 2
- [x] T014 [US2] Add a "New quote" button to `src/index.html`
- [x] T015 [US2] Implement event listener for the "New quote" button in `src/app.js` to select and render a new quote
- [x] T016 [P] [US2] Add styling for the button in `src/styles.css`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Favorite and Un-favorite a Quote (Priority: P3)
**Goal**: Users can mark the currently displayed quote as a favorite and un-favorite it. This selection persists across reloads via localStorage.
**Independent Test**: Can be tested by favoriting a quote, observing the visual indicator change, refreshing the page (or getting a new quote and coming back to the favorited one) to verify it remains favorited, and then unfavoriting it to see the indicator revert.

### Tests for User Story 3
- [x] T017 [US3] Write test for reading/writing `quoteApp_favorites` array in localStorage in `tests/app.test.js`
- [x] T018 [US3] Write test for toggle favorite logic (adding/removing IDs from favorites array) in `tests/app.test.js`

### Implementation for User Story 3
- [x] T019 [P] [US3] Add a favorite toggle icon (e.g., star/heart) next to the quote in `src/index.html`
- [x] T020 [P] [US3] Add CSS classes for empty vs. filled indicator states (e.g., `.icon-empty`, `.icon-filled`) in `src/styles.css`
- [x] T021 [US3] Implement `localStorage` read/write functions for `quoteApp_favorites` in `src/app.js`
- [x] T022 [US3] Implement favorite toggle event listener in `src/app.js` to update state and localStorage
- [x] T023 [US3] Update DOM rendering logic in `src/app.js` to correctly apply the filled/empty visual indicator based on the quote's favorite status

**Checkpoint**: All user stories should now be independently functional

---

## Phase N: Polish & Cross-Cutting Concerns
**Purpose**: Improvements that affect multiple user stories

- [x] T024 [P] Finalize and polish overall design in `src/styles.css`
- [x] T025 Run quickstart.md validation to verify end-to-end functionality

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - Sequential priority order: US1 → US2 → US3
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies
- **User Story 1 (P1)**: Can start after Foundational (Phase 2)
- **User Story 2 (P2)**: Can start after User Story 1 (relies on rendering logic)
- **User Story 3 (P3)**: Can start after User Story 2

### Parallel Opportunities
- All Setup file creation tasks marked [P] can run in parallel
- HTML and CSS scaffolding tasks marked [P] can run in parallel with their respective JavaScript logic tasks within each user story

## Implementation Strategy

### Incremental Delivery
1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories


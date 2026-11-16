# Tasks: Quote of the Day

**Input**: Design documents from `/specs/001-quote-of-the-day/`  
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/contracts.md](./contracts/contracts.md), [quickstart.md](./quickstart.md)  
**Tests**: Automated tests included per Constitution Principle II (Test-First & Automated Verification).  
**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.  

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Descriptions include exact file paths

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize repository structure and test harness

- [X] T001 Create project directories in src/ and tests/unit/ per implementation plan
- [X] T002 [P] Configure package.json with test script using Node.js test runner ("test": "node --test") in package.json

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data and layout prerequisites that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 [P] Create quote catalog in src/quotes.js with at least 5 quotes having "id", "text", and "author" per data-model.md
- [X] T004 [P] Create semantic HTML5 shell in index.html with quote card, typography, and controls per contracts/contracts.md
- [X] T005 [P] Create responsive card styling and accessible visual theme in style.css

**Checkpoint**: Foundation ready — user story implementation can begin.

---

## Phase 3: User Story 1 - View Initial Quote of the Day (Priority: P1) 🎯 MVP

**Goal**: When a user visits the page, a random quote and author attribution from the catalog is displayed immediately.  
**Independent Test**: Load `index.html` in browser; verify quote text and author appear without interaction.  

### Tests for User Story 1 ⚠️
> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**
- [X] T006 [P] [US1] Unit test for initial quote selection and catalog access in tests/unit/quote-service.test.js

### Implementation for User Story 1
- [X] T007 [US1] Implement QuoteService in src/quote-service.js (getAllQuotes, getRandomQuote)
- [X] T008 [US1] Implement initial quote rendering on DOMContentLoaded in src/app.js

**Checkpoint**: User Story 1 is functional and testable independently (MVP complete).

---

## Phase 4: User Story 2 - Request a New Random Quote (Priority: P1)

**Goal**: Clicking "New quote" displays another quote from the collection without immediate duplicate repetition.  
**Independent Test**: Click "New quote"; verify the displayed quote changes and does not repeat the previous quote.  

### Tests for User Story 2 ⚠️
- [X] T009 [P] [US2] Unit test for non-repetition logic with excludeId in tests/unit/quote-service.test.js

### Implementation for User Story 2
- [X] T010 [US2] Implement non-repetition filtering in getRandomQuote(excludeId) in src/quote-service.js
- [X] T011 [US2] Bind "New quote" button click listener in src/app.js to fetch and render a new non-duplicate quote

**Checkpoint**: User Story 1 and 2 work seamlessly together.

---

## Phase 5: User Story 3 - Favorite and Unfavorite Quotes (Priority: P2)

**Goal**: Allow users to toggle an in-place favorite indicator (heart icon) for the displayed quote.  
**Independent Test**: Click favorite toggle on active quote; verify indicator toggles between active and inactive.  

### Tests for User Story 3 ⚠️
- [X] T012 [P] [US3] Unit test for favorite toggle state transitions in tests/unit/storage.test.js

### Implementation for User Story 3
- [X] T013 [US3] Implement FavoriteStorage in-memory toggle and isFavorite check in src/storage.js
- [X] T014 [US3] Add favorite toggle button and active/inactive styling in index.html and style.css
- [X] T015 [US3] Wire favorite toggle button click handler and state update in src/app.js

**Checkpoint**: In-place favoriting works interactively for all displayed quotes.

---

## Phase 6: User Story 4 - Persistent Favorite State Across Reloads (Priority: P2)

**Goal**: Persist favorited quotes to `localStorage` and restore favorite state across page reloads and browser sessions.  
**Independent Test**: Mark a quote as favorite, reload the page, cycle back to that quote, and verify the favorite state is preserved.  

### Tests for User Story 4 ⚠️
- [X] T016 [P] [US4] Unit test for localStorage serialization, deserialization, and corrupted JSON recovery in tests/unit/storage.test.js

### Implementation for User Story 4
- [X] T017 [US4] Implement safe localStorage synchronization and corrupted JSON recovery in src/storage.js
- [X] T018 [US4] Integrate persistent favorite status check into quote render cycle in src/app.js

**Checkpoint**: All user stories functional with full persistence and resilient error handling.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Accessibility, cross-browser polish, and end-to-end verification

- [X] T019 [P] Enhance keyboard navigation and ARIA attributes in index.html
- [X] T020 Run automated unit test suite (node --test) and verify quickstart.md validation scenarios

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Setup (T001-T002); BLOCKS all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational completion.
- **User Story 2 (Phase 4)**: Depends on US1 (Phase 3).
- **User Story 3 (Phase 5)**: Depends on US1 (Phase 3).
- **User Story 4 (Phase 6)**: Depends on US3 (Phase 5).
- **Polish (Phase 7)**: Depends on all user stories being complete.

### Parallel Opportunities
- T003, T004, and T005 in Foundational Phase can be created in parallel.
- Test tasks marked with `[P]` can be authored alongside or before implementation tasks.
- US2 and US3 can proceed in parallel once US1 is complete.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Complete Phase 1 (Setup) and Phase 2 (Foundational).
2. Complete Phase 3 (US1: View Initial Quote).
3. **STOP and VALIDATE**: Open `index.html` to verify initial quote renders cleanly.

### Incremental Delivery
1. Add US2 (New Quote Button) → Verify non-repeating cycle.
2. Add US3 (Favorite Toggle) → Verify interactive active/inactive UI indicator.
3. Add US4 (Persistence) → Verify `localStorage` retention across reloads.
4. Run automated test suite (`node --test`) to achieve convergence.

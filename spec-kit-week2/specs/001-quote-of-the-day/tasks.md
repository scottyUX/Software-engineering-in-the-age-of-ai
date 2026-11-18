# Tasks: Quote of the Day

**Feature**: Quote of the Day
**Branch**: `001-quote-of-the-day`
**Specification**: [spec.md](spec.md)
**Implementation Plan**: [plan.md](plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, directory structure, and zero-dependency test framework.

- [X] T001 Create project directory structure (`css/`, `src/data/`, `src/services/`, `src/ui/`, `tests/`) per implementation plan
- [X] T002 [P] Create base HTML shell in `index.html` with viewport meta, semantic layout containers, and ES6 module script tags
- [X] T003 [P] Create CSS design tokens, typography, dark/light contrast rules, and reset styles in `css/styles.css`
- [X] T004 [P] Implement zero-dependency assertion library (`assert`, `assertEqual`, `assertTrue`, `assertThrows`) in `tests/assert.js`
- [X] T005 [P] Implement browser test harness and visual test runner in `tests/test-runner.js` and `tests/index.html`
- [X] T006 [P] Implement headless CLI test execution script using Python standard library in `tests/run-tests.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data catalog and persistence adapter that MUST be complete before user stories can proceed.

**⚠️ CRITICAL**: No user story implementation can begin until this phase is complete.

- [X] T007 [P] Create curated static quote catalog in `src/data/quotes.js` containing $\ge 15$ quotes with fields `id` (`^q-[0-9]{3,}$`), `text` (5 to 500 characters), `author` (1 to 100 characters), and optional `category`
- [X] T008 [P] Create unit tests for StorageService in `tests/storage-service.test.js` covering envelope parsing, fallback on corrupted JSON, and private browsing simulation
- [X] T009 Implement `StorageService` in `src/services/storage-service.js` wrapping `localStorage` key `qotd_favorites_v1` with JSON serialization, schema versioning, and defensive in-memory fallback

**Checkpoint**: Foundation ready — user story implementation can now begin.

---

## Phase 3: User Story 1 - Viewing Initial Random Quote (Priority: P1) 🎯 MVP

**Goal**: Display an initial random quote with text and author attribution immediately upon application load, with a smooth 0.5s fade-in transition.

**Independent Test**: Load `index.html` in browser; verify that a non-empty quote text and author from the built-in catalog are visibly rendered inside `#quote-card` and fade in smoothly over 0.5 seconds.

### Tests for User Story 1 🧪
- [X] T010 [P] [US1] Create unit tests for QuoteService in `tests/quote-service.test.js` validating `getAllQuotes`, `getQuoteById`, and initial `getRandomQuote`

### Implementation for User Story 1
- [X] T011 [US1] Implement `QuoteService` core methods in `src/services/quote-service.js` matching [quote-service-contract.md](contracts/quote-service-contract.md)
- [X] T012 [P] [US1] Add quote card semantic markup (`#quote-card`, `#quote-text`, `#quote-author`) with `aria-live="polite"` in `index.html`
- [X] T013 [P] [US1] Add quote card layout, typography, and container styles in `css/styles.css`
- [X] T014 [P] [US1] Implement CSS `@keyframes fadeIn` animation (0.5s ease-out) and `@media (prefers-reduced-motion: reduce)` override in `css/styles.css`
- [X] T015 [US1] Implement `renderQuote` method in `src/ui/ui-controller.js` to update `#quote-text` and `#quote-author` with `.fade-in` animation
- [X] T016 [US1] Wire application bootstrap in `src/app.js` to retrieve and render an initial random quote on `DOMContentLoaded`

**Checkpoint**: User Story 1 is functional with 0.5s fade-in and delivers the Minimum Viable Product (MVP).

---

## Phase 4: User Story 2 - Requesting a New Random Quote (Priority: P2)

**Goal**: Allow users to discover additional quotes on demand without reloading the page, smoothly fading in new quote text over 0.5 seconds and guaranteeing no immediate consecutive repeats when catalog $> 1$.

**Independent Test**: Click `#btn-new-quote` multiple times; verify that the displayed quote updates to a different quote from the catalog without matching the immediate predecessor, restarting the 0.5s fade-in animation cleanly each time.

### Tests for User Story 2 🧪
- [X] T017 [P] [US2] Add unit test in `tests/quote-service.test.js` verifying `getRandomQuote(currentId)` never returns `currentId` when catalog size $\ge 2$

### Implementation for User Story 2
- [X] T018 [US2] Implement consecutive duplicate exclusion algorithm in `src/services/quote-service.js`
- [X] T019 [P] [US2] Add `#btn-new-quote` interactive control with `aria-label="Get new quote"` in `index.html`
- [X] T020 [P] [US2] Add interactive button styles, hover transitions, and keyboard focus outlines in `css/styles.css`
- [X] T021 [US2] Implement animation re-triggering logic (reflow flush) in `src/ui/ui-controller.js` to restart the 0.5s fade-in on consecutive quote selections
- [X] T022 [US2] Wire `#btn-new-quote` click event in `src/ui/ui-controller.js` and `src/app.js` to cycle to the next random quote

**Checkpoint**: User Stories 1 and 2 work seamlessly together with fluid 0.5s transitions.

---

## Phase 5: User Story 3 - Favoriting and Unfavoriting with Persistence (Priority: P3)

**Goal**: Enable users to favorite and unfavorite quotes, persisting their saved state in `localStorage` across page reloads and browser sessions.

**Independent Test**: Favorite the currently displayed quote, reload the page, navigate back to that quote, and verify it remains marked as favorited; toggle off, reload, and verify it is unfavorited.

### Tests for User Story 3 🧪
- [X] T023 [P] [US3] Add unit tests in `tests/storage-service.test.js` verifying `toggleFavorite`, `isFavorite`, and persistent state serialization

### Implementation for User Story 3
- [X] T024 [P] [US3] Add `#btn-favorite` control (`aria-label="Toggle favorite"`, `aria-pressed="false|true"`) and `#storage-warning` alert container in `index.html`
- [X] T025 [P] [US3] Add favorite button styling (active vs inactive states) and warning banner styling in `css/styles.css`
- [X] T026 [US3] Implement `updateFavoriteStatus` and `showStorageWarning` in `src/ui/ui-controller.js`
- [X] T027 [US3] Wire favorite toggle click event and storage synchronization in `src/app.js`

**Checkpoint**: Favoriting is fully functional, persistent, and resilient to storage failures.

---

## Phase 6: User Story 4 - Viewing Saved Favorites (Priority: P4)

**Goal**: Provide a dedicated drawer/modal for users to view all favorited quotes with authors and remove favorites directly.

**Independent Test**: Favorite two quotes, open the favorites drawer, verify both quotes appear with author citations, remove one, and verify instant removal from the list and storage.

### Implementation for User Story 4
- [X] T028 [P] [US4] Add favorites drawer markup (`#btn-open-favorites`, `#favorites-drawer`, `#favorites-list`, `#btn-close-favorites`) in `index.html`
- [X] T029 [P] [US4] Add drawer slide animation, backdrop, empty-state styling, and remove button styles in `css/styles.css`
- [X] T030 [US4] Implement `renderFavoritesList` and `toggleFavoritesDrawer` in `src/ui/ui-controller.js`
- [X] T031 [US4] Wire drawer open/close and favorite removal event delegation in `src/app.js`

**Checkpoint**: All user stories are complete and independently verifiable.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Automated test validation, accessibility hardening, and responsive verification.

- [X] T032 [P] Execute headless test suite via `python tests/run-tests.py` and verify 100% test pass rate
- [X] T033 [P] Audit and refine responsive styles, 0.5s transition timing, and keyboard accessibility in `css/styles.css` and `src/ui/ui-controller.js`
- [X] T034 Validate all end-to-end scenarios per [quickstart.md](quickstart.md)

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (Phase 1)**: Completed.
- **Foundational (Phase 2)**: Completed.
- **User Stories (Phase 3+)**: Completed.
- **Polish (Phase 7)**: Completed.

### User Story Dependencies
- **User Story 1 (P1)**: Completed & verified.
- **User Story 2 (P2)**: Completed & verified.
- **User Story 3 (P3)**: Completed & verified.
- **User Story 4 (P4)**: Completed & verified.

---

## Implementation Strategy Status

- [X] **MVP First (User Story 1 Only)**: Verified with smooth 0.5s fade-in.
- [X] **Incremental Delivery (US2, US3, US4)**: Fully integrated and verified.
- [X] **Automated Tests**: 13/13 browser and static assertions passing.

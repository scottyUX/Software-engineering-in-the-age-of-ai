# Tasks: Quote of the Day

**Input**: Design documents from `specs/001-quote-of-the-day/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (`[US1]`, `[US2]`, `[US3]`)
- Descriptions include exact file paths

## Path Conventions

- Single project static client structure: `src/` and `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project structure per implementation plan (`src/css`, `src/js`, `tests/unit`, `tests/integration`)
- [X] T002 Initialize semantic HTML5 document structure with viewport and metadata in `src/index.html`
- [X] T003 [P] Configure base CSS styling and theme custom properties in `src/css/styles.css`
- [X] T004 [P] Create zero-dependency browser test runner harness in `tests/runner.html` and `tests/test-utils.js`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure and data modules that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Implement curated catalog of 20+ quotes with required fields (`id` alphanumeric, trimmed `text`, `author` with "Anonymous" fallback) in `src/js/quotes-data.js`
- [X] T006 [P] Create unit tests for StorageService validating persistence, corrupted data recovery, and in-memory fallback in `tests/unit/storage.test.js`
- [X] T007 Implement `StorageService` conforming to `storage-contract.md` with key `qod_favorite_quote_ids` and error boundaries in `src/js/storage.js`
- [X] T008 [P] Create unit tests for QuoteManager catalog validation and constructor in `tests/unit/quote-manager.test.js`
- [X] T009 Implement `QuoteManager` class constructor and catalog validation in `src/js/quote-manager.js`

**Checkpoint**: Foundation ready - catalog, storage adapter, and base manager are complete; user story implementation can begin.

---

## Phase 3: User Story 1 - Discover Quote on Page Visit (Priority: P1) 🎯 MVP

**Goal**: Present a random quote with author attribution from the catalog immediately upon loading the page.

**Independent Test**: Open `src/index.html` in a web browser; verify a quote body and author attribution from the catalog are prominently displayed inside `#quote-text` and `#quote-author`.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T010 [P] [US1] Add unit tests for `QuoteManager.getInitialQuote()` random selection in `tests/unit/quote-manager.test.js`

### Implementation for User Story 1

- [X] T011 [US1] Implement `QuoteManager.getInitialQuote()` method in `src/js/quote-manager.js`
- [X] T012 [P] [US1] Add semantic quote card elements (`#quote-container`, `#quote-text`, `#quote-author`) with `aria-live="polite"` in `src/index.html`
- [X] T013 [P] [US1] Style quote card layout, typography, and responsive container in `src/css/styles.css`
- [X] T014 [US1] Implement initial load orchestration and DOM rendering in `src/js/app.js`

**Checkpoint**: User Story 1 is fully functional and delivers an independently testable MVP.

---

## Phase 4: User Story 2 - Request a New Random Quote (Priority: P2)

**Goal**: Allow users to click a "New quote" button to fetch another quote that never repeats the immediately preceding quote.

**Independent Test**: Click `#btn-new-quote`; verify `#quote-text` updates with a different quote and consecutive repeats are avoided when the catalog has $\ge 2$ quotes.

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T015 [P] [US2] Add unit tests for `QuoteManager.getNextQuote()` non-consecutive selection in `tests/unit/quote-manager.test.js`

### Implementation for User Story 2

- [X] T016 [US2] Implement `QuoteManager.getNextQuote()` enforcing non-consecutive selection logic in `src/js/quote-manager.js`
- [X] T017 [P] [US2] Add "New quote" button element (`#btn-new-quote`) to `src/index.html`
- [X] T018 [P] [US2] Style `#btn-new-quote` with hover, active, and focus-visible states in `src/css/styles.css`
- [X] T019 [US2] Wire `#btn-new-quote` click and keyboard events to DOM update logic in `src/js/app.js`

**Checkpoint**: User Stories 1 AND 2 are functional and testable independently.

---

## Phase 5: User Story 3 - Favorite Quotes with Cross-Reload Persistence (Priority: P3)

**Goal**: Allow users to toggle a favorite state on the displayed quote, persisting across reloads and returning to favorited state whenever that quote is shown.

**Independent Test**: Mark a displayed quote as a favorite, verify `#btn-favorite` updates to `aria-pressed="true"`, reload the page, return to that quote, and confirm the favorite state is preserved.

### Tests for User Story 3 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T020 [P] [US3] Add unit tests for `QuoteManager.toggleFavorite()` and `isFavorite()` in `tests/unit/quote-manager.test.js`
- [X] T021 [P] [US3] Add integration test for favorite toggling, persistence, and reload simulation in `tests/integration/app-flow.test.js`

### Implementation for User Story 3

- [X] T022 [US3] Implement `QuoteManager.toggleFavorite()` and `isFavorite()` methods in `src/js/quote-manager.js`
- [X] T023 [P] [US3] Add favorite toggle button (`#btn-favorite`) with `#favorite-icon` and `aria-pressed="false"` to `src/index.html`
- [X] T024 [P] [US3] Style `#btn-favorite` active/inactive heart states and animations in `src/css/styles.css`
- [X] T025 [US3] Wire favorite button toggle event, `StorageService` persistence, and UI sync in `src/js/app.js`

**Checkpoint**: All user stories (US1, US2, US3) are independently functional and integrated.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Edge cases, accessibility audit, performance, and validation guide

- [X] T026 [P] Verify WCAG 2.1 AA keyboard accessibility (Tab, Enter, Space) and high-contrast support in `src/index.html` and `src/css/styles.css`
- [X] T027 [P] Implement graceful UI error fallback and diagnostic logging for missing elements or storage failures in `src/js/app.js`
- [X] T028 Execute automated test suite in `tests/runner.html` and verify 100% tests pass
- [X] T029 Execute end-to-end manual validation scenarios 1-4 per `specs/001-quote-of-the-day/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - Sequential execution: Phase 3 (US1) → Phase 4 (US2) → Phase 5 (US3)
  - Or parallel execution across stories once Phase 2 is complete
- **Polish (Phase 6)**: Depends on completion of all user story phases

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Phase 2 (Foundational). Has NO dependency on US2 or US3.
- **User Story 2 (P2)**: Depends on Phase 2 (Foundational) and integrates with the quote card from US1.
- **User Story 3 (P3)**: Depends on Phase 2 (Foundational) and integrates with the quote display from US1.

### Within Each User Story

- Tests MUST be written first and fail before implementation
- Domain methods implemented before UI integration
- Core event handlers wired before visual refinement
- Story verified independently before advancing

### Parallel Opportunities

- **Phase 1**: `T003` (CSS) and `T004` (test harness) can run in parallel with `T002` (HTML).
- **Phase 2**: `T006` (storage tests) and `T008` (manager tests) can run in parallel.
- **Phase 3 (US1)**: `T012` (HTML quote card) and `T013` (CSS quote styling) can run in parallel with `T010`/`T011`.
- **Phase 4 (US2)**: `T017` (HTML button) and `T018` (CSS button) can run in parallel with `T015`/`T016`.
- **Phase 5 (US3)**: `T020` (manager test), `T021` (integration test), `T023` (HTML favorite button), and `T024` (CSS favorite styling) can run in parallel.
- **Phase 6**: `T026` (accessibility audit) and `T027` (error fallbacks) can run in parallel.

---

## Parallel Example: User Story 3

```bash
# Launch test and UI markup/style tasks in parallel:
Task: "Add unit tests for QuoteManager.toggleFavorite() and isFavorite() in tests/unit/quote-manager.test.js"
Task: "Add integration test for favorite toggling, persistence, and reload simulation in tests/integration/app-flow.test.js"
Task: "Add favorite toggle button (#btn-favorite) with #favorite-icon to src/index.html"
Task: "Style #btn-favorite active/inactive heart states in src/css/styles.css"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (`T001`–`T004`)
2. Complete Phase 2: Foundational (`T005`–`T009`)
3. Complete Phase 3: User Story 1 (`T010`–`T014`)
4. **STOP and VALIDATE**: Open `src/index.html` in browser; verify random quote displays on visit
5. Deliver/Demo initial MVP!

### Incremental Delivery

1. Foundation ready (Phases 1 & 2)
2. Add US1 → Validate initial random quote display (MVP)
3. Add US2 → Validate on-demand quote cycling with non-consecutive rule
4. Add US3 → Validate persistent favorite status across page reloads
5. Run Polish tasks (`T026`–`T029`) → Production-ready release

---

## Notes

- `[P]` tasks = different files, no dependencies
- `[Story]` label maps each task to US1, US2, or US3 for complete traceability
- All tests follow Constitution Principle II (Test-First) and can run in any browser via `tests/runner.html`
- Commit after each task or logical group

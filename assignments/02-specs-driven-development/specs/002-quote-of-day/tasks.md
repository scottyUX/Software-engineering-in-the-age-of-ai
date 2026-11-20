# Tasks: Quote of the Day

**Input**: Design documents from `/specs/002-quote-of-day/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the static web app structure and confirm the project is ready for browser-only implementation.

- [X] T001 Create the base web app structure with `index.html`, `styles.css`, and `script.js`
- [X] T002 [P] Define the quote data model and built-in quote list structure in `script.js`
- [X] T003 [P] Add the base HTML shell for the quote display area and primary controls in `index.html`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create the shared UI and state foundations that all user stories depend on.

- [X] T004 Implement the initial render flow for a valid quote from the built-in list in `script.js`
- [X] T005 [P] Build the default page styling for quote display, quote actions, and favorite state in `styles.css`
- [X] T006 [P] Add the browser state utilities needed to read and write favorites from `localStorage` in `script.js`
- [X] T007 Wire the quote container and favorite indicator placeholders to the page structure in `index.html`

**Checkpoint**: The app can render a valid page state and manage browser-side favorites before story-specific behavior is added.

---

## Phase 3: User Story 1 - View a daily quote without effort (Priority: P1) 🎯 MVP

**Goal**: Display one meaningful quote immediately when the page loads.

**Independent Test**: A user loads the page and confirms a valid quote appears from the built-in list without extra setup.

### Implementation for User Story 1

- [X] T008 [P] [US1] Create the quote selection logic for the first page load in `script.js`
- [X] T009 [US1] Render the selected quote and associated text in the page view in `script.js`
- [X] T010 [US1] Ensure the page gracefully handles a missing or invalid quote source in `script.js`

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Discover another quote when desired (Priority: P1)

**Goal**: Allow the user to request a different quote without leaving the page.

**Independent Test**: A user triggers the “New quote” action and sees a valid replacement quote from the built-in collection.

### Implementation for User Story 2

- [X] T011 [P] [US2] Add the “New quote” action to the page interaction model in `index.html`
- [X] T012 [US2] Implement quote rotation logic that selects another valid item from the built-in list in `script.js`
- [X] T013 [US2] Prevent the page from breaking when the same quote is selected again or the list is short in `script.js`

**Checkpoint**: User Story 2 is independently functional and testable.

---

## Phase 5: User Story 3 - Save and revisit favorite quotes (Priority: P1)

**Goal**: Let the user favorite a quote and retain it across browser reloads.

**Independent Test**: A user marks a quote as a favorite, reloads the page, and confirms the favorite state persists.

### Implementation for User Story 3

- [X] T014 [P] [US3] Add the favorite toggle control to the UI in `index.html`
- [X] T015 [US3] Implement favorite-state calculation for the current quote in `script.js`
- [X] T016 [US3] Persist favorite quote identifiers in `localStorage` and restore them on page load in `script.js`
- [X] T017 [US3] Ensure the saved state remains valid when storage is empty, missing, or malformed in `script.js`

**Checkpoint**: User Story 3 is independently functional and testable.

---

## Phase 6: User Story 4 - Manage favorites without confusion (Priority: P2)

**Goal**: Keep favorite state clear, predictable, and easy to manage across repeated interactions.

**Independent Test**: A user can toggle favorite status and see a consistent state without duplicate or conflicting entries.

### Implementation for User Story 4

- [X] T018 [P] [US4] Update the page styling to visually distinguish favorite and non-favorite quotes in `styles.css`
- [X] T019 [US4] Enforce a single favorite record per quote ID in `script.js`
- [X] T020 [US4] Allow toggling a quote in and out of favorites without leaving the page in an inconsistent state in `script.js`

**Checkpoint**: User Story 4 is independently functional and testable.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements that affect the whole feature and ensure readiness for manual validation.

- [X] T021 [P] Review the page for accessibility and interaction clarity in `index.html`, `styles.css`, and `script.js`
- [X] T022 [P] Verify the app behaves correctly when `localStorage` contains invalid or stale favorite data in `script.js`
- [X] T023 Run the quickstart validation scenarios from `quickstart.md` and confirm the supported user flows are working end-to-end
- [X] T024 Update any remaining documentation or usage details needed for future maintenance in `quickstart.md`

---

## Phase 8: Empty-State Validation & Quote Collection Safety

**Purpose**: Cover the refined empty-state requirement for unavailable, empty, and invalid quote collections without changing the existing architecture or scope.

- [X] T025 Validate the built-in quote collection before selection and guard the empty-state path when the collection is unavailable, empty, or invalid after filtering in `script.js` per `FR-011`, `SC-006`, `US1/AC3`, `US1/AC4`, `US1/AC5`, `US2/AC3`, `US2/AC4`, and `US2/AC5`
- [X] T026 Add the empty-state render path for initial page load so the UI shows a clear user-facing message rather than stale content, an undefined quote, or a permanent loading state in `script.js` and the relevant page view code per `FR-011`, `SC-006`, `US1/AC3`, `US1/AC4`, and `US1/AC5`
- [X] T027 Add the empty-state render path for the “New quote” action so the page remains stable and displays the empty-state message when the collection is empty or invalid in `script.js` per `FR-011`, `SC-006`, `US2/AC3`, `US2/AC4`, and `US2/AC5`
- [X] T028 Verify the empty-state behavior on initial load and after clicking “New quote” for the browser-tested conditions: empty collection and collection with no valid entries after validation; confirm normal rotation and favorite persistence remain working; note that the unavailable-source case is covered by code inspection of the validation guard but was not independently injected and validated in the browser because the current static implementation uses a top-level constant collection in `quickstart.md` and the final browser validation flow per `FR-011`, `SC-006`, `US1/AC3`, `US1/AC4`, `US1/AC5`, `US2/AC3`, `US2/AC4`, and `US2/AC5`

**Checkpoint**: The quote collection validation and empty-state behavior are covered for all refined failure modes and are verifiable on both initial load and quote rotation.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories.
- **User Stories (Phases 3-6)**: All depend on Phase 2 completion.
- **Polish (Phase 7)**: Depends on the completed user stories and final validation.

### User Story Dependencies

- **User Story 1 (P1)**: No dependency on other stories; delivers the core page experience.
- **User Story 2 (P1)**: Depends only on the quote display foundation; can be implemented after Story 1 or in parallel with it if staffing allows.
- **User Story 3 (P1)**: Depends on the rendered quote and persisted state foundation.
- **User Story 4 (P2)**: Depends on the favorite state behavior added in Story 3.

### Parallel Opportunities

- Tasks T002 and T003 can run in parallel.
- Tasks T005 and T006 can run in parallel.
- Tasks T008 and T011 can run in parallel once the foundational state is in place.
- Tasks T014 and T018 can run in parallel while the favorite behavior is being finalized.
- Tasks T021 and T022 can run in parallel during Polish.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate the page displays a valid quote without setup
5. Stop and confirm the feature works before continuing

### Incremental Delivery

1. Add the visible quote experience
2. Add new quote selection
3. Add favorite persistence
4. Tighten favorite state behavior and polish the interface
5. Complete final validation and documentation checks

### Parallel Team Strategy

With multiple developers:

1. One developer completes the shared setup and foundational tasks.
2. One developer implements the initial quote display and “New quote” flow.
3. One developer focuses on favorite persistence and state rules.
4. A final pass confirms the UI polish and validation scenarios work end-to-end.

---

## Notes

- [P] tasks indicate different files or independent work that can be run in parallel.
- Tasks are grouped by user story so each story can be implemented and validated independently.
- Validation should prioritize the browser experiences defined in `quickstart.md` and the acceptance criteria from `spec.md`.
- The feature remains intentionally simple and implementation-agnostic at the task level; actual wiring, DOM operations, and browser storage details are left to implementation.

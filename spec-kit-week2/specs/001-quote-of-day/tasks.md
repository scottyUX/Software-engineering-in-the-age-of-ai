# Tasks: Quote of the Day

**Input**: Design documents from `specs/001-quote-of-day/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/ui-contract.md](contracts/ui-contract.md), [quickstart.md](quickstart.md)

**Tests**: Automated browser tests are required by the plan and project constitution. Write each story's tests before its implementation and confirm they fail for the expected missing behavior.

## Format

Every task uses `- [ ] Tnnn [P?] [USn?] Description with exact file path`. `[P]` appears only for tasks that can be performed concurrently without editing the same file or depending on unfinished work. Story labels appear only in user-story phases.

## Phase 1: Setup

**Purpose**: Initialize the plain-JavaScript project and browser test environment.

- [X] T001 Create `package.json` with Node.js 22+ engine, ES module mode, `start` and `test` scripts, and `@playwright/test` as the only development dependency.
- [X] T002 [P] Configure `playwright.config.js` to run the Chromium project, discover `tests/quote-app.spec.js`, and start `node scripts/serve.js` on localhost as Playwright's development-only static web server.
- [X] T003 [P] Create `scripts/serve.js` to serve repository static files on localhost with correct content types, reject paths outside the repository root, and provide `index.html` for the root URL; do not implement application/backend routes.
- [X] T004 [P] Add `.gitignore` entries for `node_modules/`, `playwright-report/`, and `test-results/`.

---

## Phase 2: Foundational

**Purpose**: Establish shared page landmarks and accessible base styling before implementing either story.

- [X] T005 Create the semantic page shell, quote/favorites content regions, and polite status-message region in `index.html`, and add responsive design tokens, readable defaults, and visible keyboard focus styles in `styles.css`.

**Checkpoint**: Shared static page shell and local browser test environment are ready.

---

## Phase 3: User Story 1 - Read and browse quotes (Priority: P1) 🎯 MVP

**Goal**: Show one random quote with attribution and let visitors request a different quote.

**Independent Test**: Verify the built-in collection has at least five distinct usable quotes, the page displays one quote and attribution, New quote displays a different entry when alternatives exist, and the selection helper handles empty and single-entry collections.

### Tests for User Story 1

- [X] T006 [US1] Add and run failing browser and selection tests in `tests/quote-app.spec.js` for at least five distinct quotes with text/attribution, one initial displayed quote, a different quote after New quote, and empty/single-entry selection behavior.

### Implementation for User Story 1

- [X] T007 [P] [US1] Add the built-in quote records and an exported random-selection helper in `app.js`; satisfy the data-model constraints verbatim: `id` is "Required; stable and unique across the built-in collection; used as the favorite key", `text` is "Required; non-empty, trimmed quotation text", and `attribution` is "Required; non-empty author or source attribution shown with the quotation". The collection MUST contain at least five distinct entries, and comments MUST record each quotation's source and reuse-rights basis.
- [X] T008 [P] [US1] Add the quote text, attribution, and clearly labeled New quote button to the quote panel in `index.html`, with responsive quote typography and action styling in `styles.css`.
- [X] T009 [US1] Initialize the current quote randomly, render its text and attribution, bind New quote to choose a different distinct entry when alternatives exist, and render a clear unavailable state for an empty collection in `app.js`.

**Checkpoint**: User Story 1 works and its tests pass independently; this is the MVP increment.

---

## Phase 4: User Story 2 - Save and revisit favorite quotes (Priority: P2)

**Goal**: Toggle the current quote as a favorite, review/remove saved quotes, and restore favorites after reload.

**Independent Test**: Save a displayed quote, reload and find it in the favorites list with the heart marked saved, remove it and confirm it stays absent after reload; verify an empty state and graceful behavior when storage is invalid or unavailable.

### Tests for User Story 2

- [X] T010 [US2] Add and run failing browser tests in `tests/quote-app.spec.js` for keyboard-operable heart toggle and pressed state, favorites list add/remove and empty state, same-profile reload persistence, malformed saved data, and storage access/write failure that leaves quote browsing usable.

### Implementation for User Story 2

- [X] T011 [P] [US2] Implement guarded favorite restoration and persistence helpers in `app.js` using one namespaced `localStorage` key containing JSON `quoteIds`; satisfy the data-model constraint verbatim: "Unique IDs that match built-in quotes; unknown IDs are ignored when restoring." Also deduplicate restored IDs and handle property-access, parse, and write errors without throwing.
- [X] T012 [P] [US2] Add a heart-icon favorite toggle and favorites-list/empty-state markup in `index.html`; provide accessible names, `aria-pressed`, filled/outlined saved states, and visible focus styling in `styles.css`.
- [X] T013 [US2] Wire favorite restoration, toggle, favorites rendering/removal, and the non-blocking persistence warning into `app.js`; quote selection and browsing MUST continue if storage is blocked or fails.

**Checkpoint**: User Stories 1 and 2 work; favorite state is restored when browser storage permits.

---

## Phase 5: Polish and Cross-Cutting Concerns

**Purpose**: Verify content, usage guidance, and the integrated behavior.

- [X] T014 [P] Audit the built-in quotations in `app.js` for five-or-more distinct entries, accurate attributions, source provenance, and verified reuse rights; correct any entry that fails review.
- [X] T015 [P] Align setup, run, and validation instructions with the delivered scripts and tests in `specs/001-quote-of-day/quickstart.md`.
- [X] T016 Run `npm test` for `tests/quote-app.spec.js`, resolve any browser-test failures in the corresponding implementation files, and record the validated commands and scenarios in `specs/001-quote-of-day/quickstart.md`.

---

## Dependencies and Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: All four tasks edit separate files and can start in parallel using the shared commands/paths defined above.
- **Foundational (Phase 2)**: Starts after the setup tasks are complete; the shared HTML/CSS shell blocks both stories.
- **User Story 1 (Phase 3)**: Starts after Phase 2; its tests are authored and observed failing before quote implementation.
- **User Story 2 (Phase 4)**: Starts after User Story 1 because favorites are applied to the currently displayed quote; its tests are authored and observed failing before favorite implementation.
- **Polish (Phase 5)**: Starts after both stories; content audit and quickstart alignment may run in parallel, then integrated tests run last.

### User Story Dependencies

- **US1 (P1)**: Depends on shared setup only; delivers the first independently useful increment.
- **US2 (P2)**: Depends on US1's current-quote display and quote IDs; does not require an account or external service.

### Parallel Opportunities

- **Setup**: T001, T002, T003, and T004 may run concurrently; they configure distinct files and agree on `node scripts/serve.js`, localhost, and the npm scripts specified above.
- **US1**: After T006's tests are written and observed failing, T007 (`app.js` quote data/helper) and T008 (`index.html`/`styles.css` quote panel) may run concurrently. T009 integrates them.
- **US2**: After T010's tests are written and observed failing, T011 (`app.js` storage helpers) and T012 (`index.html`/`styles.css` favorite controls) may run concurrently. T013 integrates them.
- **Polish**: T014 (quote content audit in `app.js`) and T015 (guide update in `quickstart.md`) use separate files and may run concurrently; T016 follows both.

## Parallel Example: User Story 1

```text
1. Complete T006 and confirm the new tests fail for the missing quote page.
2. In parallel, complete T007 in app.js and T008 in index.html/styles.css.
3. Complete T009 in app.js, then run the User Story 1 tests.
```

## Parallel Example: User Story 2

```text
1. Complete T010 and confirm the new favorite tests fail against the US1-only page.
2. In parallel, complete T011 in app.js and T012 in index.html/styles.css.
3. Complete T013 in app.js, then run the User Story 2 tests.
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup and Foundational phases.
2. Write/fail the US1 tests, then implement and pass User Story 1.
3. Validate quote display, attribution, minimum collection size, and changing quotes.
4. Stop at the US1 checkpoint for an independently demonstrable MVP.

### Incremental Delivery

1. Deliver the static quote page as US1.
2. Add persistent favorites as US2 without changing the quote-page contract.
3. Complete the content audit, quickstart verification, and full browser suite.

## Phase 6: Convergence

- [X] T017 Expand the initial-display browser test in `tests/quote-app.spec.js` to perform 20 consecutive page openings/reloads and verify each shows exactly one non-empty quote and attribution per SC-001 (partial).
- [X] T018 Update the New quote browser test in `tests/quote-app.spec.js` to perform 20 selections and verify each quote differs from the immediately preceding quote when alternatives exist per SC-002 (partial).
- [X] T019 Expand the favorite persistence browser test in `tests/quote-app.spec.js` to run 20 same-profile save/reload checks and verify removed quotes remain absent after reload per SC-003 (partial).

# Tasks: Quote of the Day

**Input**: Design documents from `/specs/001-quote-of-the-day/`

**Tests**: Included, because Constitution Principle II requires them.

## Phase 1: Setup

- [X] T001 Create the page skeleton per contracts/ui.md in index.html
- [X] T002 [P] Add page presentation in styles.css

## Phase 2: Foundational

- [X] T003 Create at least 10 quotes, each with a required, unique `id`, non-empty `text`, and non-empty `author`, in js/quotes.js

## Phase 3: User Story 1 - Read a random quote (Priority: P1) 🎯 MVP

**Goal**: A visitor sees one random quote on opening the page.

**Independent Test**: Open the page and confirm one quote with its author is displayed.

- [X] T004 [P] [US1] Write tests for random selection and the quote list in tests/logic.test.js
- [X] T005 [P] [US1] Write a real-page test that a quote and author appear in tests/page.test.js
- [X] T006 [US1] Implement `pickRandomQuote` in js/logic.js
- [X] T007 [US1] Render a random quote on load in js/app.js

## Phase 4: User Story 2 - Ask for a new quote (Priority: P2)

**Goal**: "New quote" replaces the displayed quote.

**Independent Test**: Press "New quote" and confirm the displayed quote is replaced.

- [X] T008 [US2] Add a real-page test for the "New quote" button in tests/page.test.js
- [X] T009 [US2] Connect the `new-quote` button in js/app.js

## Phase 5: User Story 3 - Keep favorites (Priority: P3)

**Goal**: Favorites survive a page reload.

**Independent Test**: Mark a quote, reload, return to that quote, and confirm it is still marked.

- [X] T010 [P] [US3] Write tests for toggling and for parsing saved favorites, covering missing, corrupt, and unknown entries, in tests/logic.test.js
- [X] T011 [P] [US3] Add real-page tests for marking, unmarking, reloading, corrupt data, and blocked storage in tests/page.test.js
- [X] T012 [US3] Implement `toggleFavorite` and `parseFavorites` in js/logic.js
- [X] T013 [US3] Connect the `favorite` button, `aria-pressed`, label, and safe localStorage access in js/app.js

## Phase 6: Polish

- [X] T014 Run every scenario in specs/001-quote-of-the-day/quickstart.md and record the result in README.md

## Dependencies

- Setup and Foundational come before all stories.
- US1 comes before US2 and US3, which both need a displayed quote; US2 and US3 are otherwise independent.

## Parallel Example

```text
T004 tests/logic.test.js and T005 tests/page.test.js can be written together.
```

## Implementation Strategy

Deliver US1 as the MVP, then add US2 and US3, running the tests after each phase.

## Phase 7: Convergence

- [X] T015 Make "New quote" never show the quote already displayed, in js/logic.js and js/app.js, per US2/AC1 and FR-003 (partial)
- [X] T016 Test that "New quote" always changes the quote, in tests/logic.test.js and tests/page.test.js, per US2/AC1 and FR-003 (partial)
- [X] T017 Test keyboard operation of both buttons in tests/page.test.js per FR-008 (partial)
- [X] T018 Test that a quote is visible within 1 second in tests/page.test.js per SC-001 (partial)

# Phase 0 Research & Technical Decisions: Quote of the Day

## 1. Application Architecture & Modular Design

- **Decision**: Structure the application using standard vanilla ES6 JavaScript modules with strict separation of concerns across single-responsibility modules:
  - `src/data/quotes.js`: Static catalog of curated quotes.
  - `src/services/quote-service.js`: Pure domain logic for selecting random quotes and preventing immediate duplicate repeats.
  - `src/services/storage-service.js`: Encapsulated storage adapter for persisting and retrieving favorites.
  - `src/ui/ui-controller.js`: DOM manipulation, rendering, event handling, and ARIA updates.
  - `src/app.js`: Application bootstrapping and coordination.
- **Rationale**: Complies directly with Constitution Principle I (Single Responsibility & Expressive Code) and Principle III (Maintainability & Modular Loose Coupling). Eliminates framework overhead while ensuring business logic is decoupled from DOM manipulation, allowing pure domain services to be tested in isolation.
- **Alternatives Considered**:
  - *Single monolithic script (`app.js` containing all logic)*: Rejected because it tightly couples DOM operations to data manipulation, violates separation of concerns, and hinders automated unit testing.
  - *Frontend Frameworks (React, Vue, Svelte)*: Rejected per user requirement ("plain HTML/CSS/JavaScript, no backend") and YAGNI principle.

---

## 2. Persistence Strategy via localStorage

- **Decision**: Persist favorites in browser `window.localStorage` under a dedicated, versioned key `qotd_favorites_v1` using JSON serialization with schema validation and in-memory fallback.
  - Storage payload schema: Array of favorite records: `[{ "quoteId": "q-1", "favoritedAt": 1775668800000 }]`.
  - Defensive fallback: If `localStorage` is disabled, throws a `SecurityError` (e.g., restricted private browsing), or fails due to quota limits, catch the exception gracefully and fall back to an in-memory session store with user notification.
- **Rationale**: Satisfies the explicit requirement for `localStorage` persistence while adhering to Constitution Principle IV (Defensive Programming & Observable Robustness). Ensures the app remains 100% operational even in restricted storage environments.
- **Alternatives Considered**:
  - *IndexedDB*: Rejected as over-engineered for a small set of favorited IDs (YAGNI/KISS).
  - *Cookies*: Rejected due to 4KB size limits, unnecessary inclusion in HTTP headers, and clunky parsing APIs.
  - *Unchecked raw localStorage access*: Rejected because unhandled `SecurityError` or `QuotaExceededError` crashes the user interface in private browsing mode.

---

## 3. Random Quote Selection & De-duplication Strategy

- **Decision**: Maintain the current quote index/ID in state and implement random selection that explicitly excludes the active quote ID whenever catalog size $> 1$.
  - Algorithm: Filter catalog for IDs $\neq$ current ID, generate a cryptographically uniform random index via `Math.floor(Math.random() * filteredList.length)`.
  - Fallback: If catalog length is 1, return the single available quote without looping.
- **Rationale**: Directly satisfies Functional Requirement FR-004 and User Story 2 ("avoid immediate consecutive duplicates") while guaranteeing $O(1)$ selection performance without recursion hazards.
- **Alternatives Considered**:
  - *Shuffled Deck / Permutation Playlist*: Tracks a full shuffle queue. Rejected as unnecessary complexity for MVP; simple prior-exclusion random selection satisfies all requirements with minimal state.
  - *Pure random selection without exclusion*: Rejected because it allows immediate consecutive repeats, degrading user experience.

---

## 4. Zero-Dependency Automated Testing Strategy

- **Decision**: Implement an in-browser HTML-based unit test runner (`tests/index.html` and `tests/test-runner.js`) that imports ES6 modules directly and executes assertions with a lightweight assertion library (`assert.js`), paired with a Python-based headless test execution script (`tests/run-tests.py`) using Python's standard library and local HTTP server.
- **Rationale**: Since Node.js and npm are not installed on the host system, an in-browser runner combined with standard Python tooling provides 100% native automated test execution with zero external package dependencies. Fulfills Constitution Principle II (Automated Verification & Test-First).
- **Alternatives Considered**:
  - *Installing npm/Jest/Vitest*: Not feasible without Node.js on the host environment; introduces heavy `node_modules` dependency footprint.
  - *Manual testing only*: Rejected as a direct violation of Constitution Principle II (Automated Verification is non-negotiable).

---

## 5. UI/UX, Accessibility, and Responsive Styling

- **Decision**: Build a modern, responsive layout using semantic HTML5 elements (`<main>`, `<article>`, `<blockquote>`, `<button>`) and pure CSS (CSS Variables, Flexbox, media queries for mobile-friendly viewports).
  - Accessibility: Quote card includes an `aria-live="polite"` region and semantic `<blockquote>` / `<cite>` tags. Buttons feature explicit `aria-label` attributes and state indicators (`aria-pressed="true|false"` for the favorite toggle).
- **Rationale**: Guarantees fast rendering (<100ms), cross-browser compatibility, screen-reader support, and clean aesthetic without CSS framework dependencies.
- **Alternatives Considered**:
  - *Third-party CSS framework (Tailwind/Bootstrap)*: Rejected to avoid build tooling dependencies, keeping the project pure vanilla HTML/CSS.

---

## 6. Smooth 0.5s Fade-In Transition & Motion Accessibility

- **Decision**: Implement the 0.5-second quote text fade-in transition using pure CSS opacity keyframe animation (`@keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }`) or CSS class toggle (`.fade-in { animation: fadeIn 0.5s ease-out; }`).
  - In `UIController.renderQuote`, trigger animation restart by re-triggering class application (`classList.remove('fade-in')`, force reflow, `classList.add('fade-in')`).
  - Accessibility: Respect `@media (prefers-reduced-motion: reduce)` by disabling transition duration (`animation: none !important; transition: none !important; opacity: 1 !important;`).
- **Rationale**: Complies directly with FR-011 and FR-012. Native CSS transitions execute on the GPU/compositor thread for fluid 60fps rendering without jank or timer drift. Reflow-based retrigger handles rapid clicks without animation stacking bugs.
- **Alternatives Considered**:
  - *JavaScript `requestAnimationFrame` loop*: Rejected as overly complex, imperative, and CPU-intensive for standard opacity fading.
  - *External JS animation library (GSAP, Anime.js)*: Rejected to avoid unnecessary third-party dependencies.

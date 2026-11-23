# Technical Research: Quote of the Day

**Feature**: `001-quote-of-the-day`  
**Date**: 2026-10-20  
**Status**: Completed  

## 1. Architectural Stack Selection

### Decision
Use vanilla HTML5, CSS3, and ES6+ JavaScript with zero build steps and zero external dependencies.

### Rationale
- **Simplicity & Performance**: For a lightweight single-page quote generator, frameworks (React, Vue, etc.) introduce unnecessary bundle size, build tooling (Vite/Webpack), and configuration overhead without providing tangible architectural benefits (aligns with Constitution Principle I: YAGNI & Simplicity).
- **Portability**: The application can be served statically by any web server, GitHub Pages, or opened directly via `file://` in a web browser.
- **Maintainability**: Standard modern web APIs provide native DOM manipulation, CSS custom properties, and storage without third-party maintenance risk.

### Alternatives Considered
- **React / Svelte**: Rejected due to unnecessary bundle overhead, setup complexity, and requirement for node packaging/compilation for a single interactive card.
- **jQuery**: Rejected because modern vanilla DOM APIs (`querySelector`, `addEventListener`, `classList`) are concise, standardized, and natively supported.

---

## 2. Persistence Strategy with `localStorage`

### Decision
Persist favorites as a JSON array of quote IDs under the storage key `quote_of_the_day_favorites`.

### Rationale
- **Normalized Data Model**: Storing only the unique quote identifier (e.g., `["q1", "q3"]`) keeps the quote content and author metadata in a single source of truth (the built-in quote catalog) and avoids data staleness or serialization bloat.
- **Atomic Operations**: Reading and writing the favorite ID array is simple, fast, and synchronous.
- **Defensive Error Handling**: Wrapped in a try/catch module (`storage.js`) to handle scenarios where `localStorage` is disabled (e.g., private browsing mode quota errors) or corrupted (JSON parse error), falling back safely to an in-memory Set without crashing (Constitution Resilience constraint).

### Alternatives Considered
- **IndexedDB**: Rejected as overengineered for storing a small list of string IDs; introduces asynchronous complexity.
- **Cookies**: Rejected due to size limits and unnecessary inclusion in HTTP request headers.
- **Storing Full Quote Objects**: Rejected to prevent data duplication and schema drift if quote text or author attribution is updated.

---

## 3. Random Selection and Immediate Repetition Avoidance

### Decision
Maintain the active quote's ID in application state. When "New quote" is requested, filter the quote catalog to exclude the active ID, then pick randomly from the remaining list using `Math.floor(Math.random() * pool.length)`.

### Rationale
- Guarantees that as long as the collection has $\ge 2$ quotes, the user will never see the same quote consecutively.
- Constant-time and zero-delay calculation for small collections ($\le 100$ items).

### Alternatives Considered
- **Full Shuffle Deck (Fisher-Yates)**: Cycles through all quotes before reshuffling. Rejected because the requirement specifically asked for random selection avoiding immediate repetition; a full shuffle cycle adds tracking state without being requested.
- **Pure Random (`Math.random() * total`) with Retry Loop**: Could theoretically loop multiple times or stall; filtering candidates directly is deterministic and avoids unbounded loops.

---

## 4. Automated Testing Strategy

### Decision
Organize JavaScript into pure, testable modules (`quotes.js`, `storage.js`, `quote-service.js`) and test them using Node.js's built-in test runner (`node --test`).

### Rationale
- **Constitution Compliance**: Fulfills Principle II ("Test-First & Automated Verification - NON-NEGOTIABLE") without requiring external npm packages or build configurations.
- **Instant Execution**: Tests run in milliseconds using standard Node.js $\ge 18$.
- **Mock Storage**: Provide an in-memory storage adapter interface to verify persistence, duplicate avoidance, and corrupted storage recovery independently of a real browser window.

### Alternatives Considered
- **Jest / Vitest**: Rejected to keep the repository zero-dependency without `node_modules` clutter.
- **Manual Verification Only**: Rejected as a direct violation of the project constitution.


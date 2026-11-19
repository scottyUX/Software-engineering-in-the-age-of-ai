# Technical Research: Quote of the Day

**Feature**: Quote of the Day
**Branch**: `001-quote-of-the-day`
**Date**: 2026-10-07

This document details the architectural decisions, trade-offs, and design patterns selected for implementing the client-side Quote of the Day application.

---

## Research Topics & Decisions

### 1. Architecture: Vanilla ES Modules vs. Frameworks/Bundlers

- **Decision**: Use standard ECMAScript Modules (`type="module"`) with native HTML5, CSS3, and JavaScript, requiring zero compilers, bundlers, or runtime frameworks.
- **Rationale**:
  - The feature requirements specify a lightweight, single-page application with no backend.
  - Native ES Modules are supported across all modern evergreen browsers (Chrome, Firefox, Safari, Edge).
  - Eliminates build pipelines, dependencies, configuration files, and potential supply-chain issues in adherence to Constitution Principle IV (Maintainability & Simplicity) and Principle I (Code Craftsmanship).
  - Allows clean separation of concerns into distinct domain modules (`quotes-data.js`, `storage.js`, `quote-manager.js`, `app.js`).
- **Alternatives Considered**:
  - *React/Vue/Svelte*: Rejected. Adds unnecessary virtual DOM overhead, bundle tooling (`vite`/`webpack`), and violates the user's explicit requirement for plain HTML/CSS/JS.
  - *Single monolithic script file*: Rejected. Difficult to unit-test business logic in isolation without DOM coupling; violates Constitution Principle I (Single Responsibility Principle) and Principle II (Test-First).

---

### 2. Persistence: LocalStorage Schema & Key Management

- **Decision**: Store favorited quote identifiers as a JSON array of strings under a namespaced key: `qod_favorite_quote_ids`.
- **Rationale**:
  - Quotes in the catalog have stable, immutable IDs (e.g., `"quote-1"`, `"quote-2"`). Storing only IDs rather than duplicating entire quote objects minimizes storage size, avoids data drift if quote wording is refined, and makes checking favorite status an $O(1)$ set lookup in memory.
  - Using a namespaced key (`qod_favorite_quote_ids`) prevents collisions with any other applications or tools sharing the same domain/origin.
  - Synchronous reading on initialization ensures that when the first quote is rendered, its favorite status is instantly known with zero UI flickering.
- **Alternatives Considered**:
  - *Storing full quote objects in an array*: Rejected. Redundant data duplication; if quote text or author attribution is updated in the catalog, stored copies would become stale or mismatched.
  - *IndexedDB*: Rejected. Excessive complexity and asynchronous overhead for storing a small set of string identifiers (< 100 entries). Violates Principle IV (Simplicity).
  - *Cookies*: Rejected. Cookies are meant for server communication, have a 4KB limit, and introduce unnecessary HTTP overhead.

---

### 3. Selection Algorithm: Non-Consecutive Random Selection

- **Decision**: Maintain the current quote's ID in memory (`currentQuoteId`). When requesting a new quote:
  - If the catalog has $\ge 2$ items, filter out the current quote (or generate a random index among the remaining candidates) so that the same quote is never presented twice in succession.
  - If the catalog has only 1 item, return that item gracefully without throwing an error.
- **Rationale**:
  - Direct requirement from FR-005 and Acceptance Scenario 2 of User Story 2.
  - Provides a predictable, high-satisfaction user experience by ensuring that clicking "New quote" always renders a visual change when possible.
- **Alternatives Considered**:
  - *Pure unconstrained `Math.random()`*: Rejected. Allows consecutive duplicates, making the user think the "New quote" button failed or was unresponsive.
  - *Full shuffle queue (Fisher-Yates) across all quotes*: Rejected as unnecessarily complex for v1. Non-consecutive single-step avoidance provides immediate variation with minimal state management.

---

### 4. Storage Resilience: Graceful Degradation & Error Handling

- **Decision**: Encapsulate all `localStorage` access within a resilient `StorageService` that handles `SecurityError`, `QuotaExceededError`, corrupted JSON payloads, and environments where `localStorage` is completely unavailable.
- **Rationale**:
  - In strict private/incognito browsing modes or locked-down enterprise profiles, `window.localStorage` may throw a security exception upon access.
  - Corrupted or manually modified `localStorage` data must not crash the application; it should log a warning, reset/repair the state, and fall back to in-memory storage for the active session.
  - Aligns with Constitution Principle V (Actionable Observability & Explicit Contracts) and Edge Case specifications.
- **Alternatives Considered**:
  - *Raw, unprotected `localStorage.getItem/setItem` calls in UI code*: Rejected. Any thrown exception crashes the entire UI script and breaks quote display.
  - *Blocking the user if storage is unavailable*: Rejected. The user should still be able to read quotes, cycle quotes, and favorite quotes within the current session even if persistence is disabled.

---

### 5. Automated Verification: Zero-Dependency Node.js Test Harness

- **Decision**: Use Node.js built-in `node:test` and `node:assert` modules (`node --test tests/**/*.test.js`) to test the business logic and storage service without installing npm packages.
- **Rationale**:
  - Directly enforces Constitution Principle II (Test-First & Comprehensive Coverage) and Principle III (Multi-Tier Automated Verification) without requiring external dependencies (`jest`, `mocha`, `npm install`).
  - By cleanly decoupling domain logic (`quote-manager.js` and `storage.js`) from browser DOM APIs, unit tests execute in milliseconds directly in standard Node.js environments.
  - Provides deterministic, fast, continuous testing runnable via a single command.
- **Alternatives Considered**:
  - *Manual browser testing only*: Rejected. Violates Constitution Principle II (Automated testing mandatory).
  - *Installing Jest or Vitest via npm*: Rejected. Requires `package.json`, `node_modules` (hundreds of MBs), lockfiles, and configuration for what is otherwise a pure vanilla web application.

---

## Summary of Architectural Constraints

| Constraint | Resolution |
|---|---|
| **Runtime Dependencies** | 0 external libraries; native Web Platform APIs only |
| **Backend** | None; static client-side single-page application |
| **Persistence** | `localStorage` with in-memory fallback |
| **Testing** | Node.js native `node:test` + `node:assert` |
| **Browser Compatibility** | All modern browsers supporting ES6 Modules |

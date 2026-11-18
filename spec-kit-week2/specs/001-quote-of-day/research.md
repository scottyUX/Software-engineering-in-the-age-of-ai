# Research: Quote of the Day

## Decisions

### Static browser application

- **Decision**: Implement the page with plain HTML, CSS, and browser JavaScript. Do not add an application backend, user accounts, external quote service, framework, or runtime dependency.
- **Rationale**: This follows the user's planning constraint and the specification's built-in quote collection and no-account assumptions. The repository has no application code or established frontend toolchain.
- **Alternatives considered**: A frontend framework or remote quote API; both add complexity or contradict the requested offline, built-in content scope.

### Favorites persistence

- **Decision**: Save stable quote IDs as JSON in `localStorage`, and restore them on page load. Validate parsed values against the built-in quote IDs. Treat inaccessible storage, invalid JSON, and write errors as a persistence-unavailable condition; keep quote browsing operational and communicate the limitation.
- **Rationale**: The user explicitly selected `localStorage`. MDN documents that it is origin-scoped and persists across browser sessions, but access may throw `SecurityError`; behavior for `file:` URLs is undefined. Defensive access and an HTTP localhost origin avoid treating persistence as guaranteed in unsupported contexts.
- **Alternatives considered**: Server/database persistence is excluded by the no-backend requirement; session storage does not meet persistence across browser sessions.
- **Sources**: [MDN: Window.localStorage](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage), [MDN: Using the Web Storage API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API/Using_the_Web_Storage_API).

### Browser verification

- **Decision**: Use Playwright Test for automated browser acceptance tests, with a small development-only static file server on localhost. Keep the shipped application as static files; the server is not an application backend.
- **Rationale**: The constitution requires automated tests for behavior changes. There is no existing test harness. Browser-level tests can verify rendering, keyboard-accessible heart controls, random quote changes, saved-list behavior, reload persistence, and storage failures end to end. Playwright supports a configured local web server and browser projects.
- **Alternatives considered**: Manual-only testing does not satisfy the constitution's automated-test requirement; a framework or separate application backend is unnecessary. Native-only unit tests would not verify browser storage and UI integration.
- **Sources**: [Playwright: Installation](https://playwright.dev/docs/intro), [Playwright: Web server](https://playwright.dev/docs/test-webserver).
- **Environment**: Playwright's current system requirements list Node.js 22.x, 24.x, or 26.x; use Node.js 22 or newer for the test tooling. Install only the Chromium browser needed by this feature's test suite.

## Resolved Technical Context

- Keep quote data local and include at least five distinct entries with text, accurate attribution, stable IDs, and checked reuse rights. Prefer verified public-domain quotations and record their source/provenance in the implementation.
- Avoid JavaScript module loading requirements if they add friction; serve all files on localhost for reliable storage and browser tests. Do not rely on `file:` URL persistence.
- Keep storage reads and writes behind small defensive helpers. Invalid or blocked storage MUST not prevent quote selection, browsing, or rendering.
- Configure automated checks to exercise behavior from the specification, including a minimum-five-quote assertion, no immediate repeat when alternatives exist, filled/outlined heart state, add/remove favorites, reload persistence, and graceful storage failure.

## Unresolved Questions

None. The requested stack, persistence mechanism, and no-backend boundary are explicit; local test tooling is a development-only choice required to verify behavior.

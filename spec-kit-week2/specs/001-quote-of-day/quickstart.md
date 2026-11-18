# Quickstart: Quote of the Day

## Prerequisites

- Node.js 22 or newer and npm, for the development test tooling.
- A supported desktop browser. The automated suite uses Playwright Chromium.

The application itself is static HTML, CSS, and JavaScript and has no server-side runtime or account requirement. Serve it on localhost rather than opening it with a `file:` URL because browser storage behavior for `file:` pages is undefined.

## Setup and Run

1. Install project development dependencies with `npm install`.
2. Install the test browser with `npx playwright install chromium`.
3. Start the local static preview with `npm start` and open the printed localhost URL.
4. Run the automated browser suite with `npm test` (the test runner starts or reuses the local static server).

## Validation Scenarios

- On initial load, exactly one quote and its attribution appear; the built-in quote collection contains at least five distinct entries.
- Select **New quote** repeatedly; each selection differs from the immediately preceding quote while alternatives exist.
- Use the heart toggle with mouse and keyboard; verify its filled/outlined state and accessible pressed state update, and the quote appears in or leaves the favorites list.
- Reload after saving a quote; verify the favorite remains. Remove it, reload again, and verify it remains absent.
- Clear favorites and verify the empty state.
- Simulate blocked storage and malformed saved data; verify a non-blocking warning appears and quote browsing continues.

**Last verified**: 2026-10-05 — `npm test -- --workers=1` completed with all 10 Playwright tests passing in Chromium.

See [the data model](data-model.md) for favorite persistence and quote constraints, and [the UI contract](contracts/ui-contract.md) for interaction and accessibility expectations.

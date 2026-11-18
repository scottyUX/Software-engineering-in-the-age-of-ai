# Quote of the Day

A static page that shows a random quote, replaces it on "New quote", and remembers favorites in the
browser. Built with [Spec Kit](https://github.com/github/spec-kit); see
[`specs/001-quote-of-the-day/`](specs/001-quote-of-the-day/) for the spec, plan, and tasks.

## Run

Open `index.html` in a browser. No server or build step is needed.

## Test

```bash
node --test
```

Needs Node.js 20 or newer. The real-page tests use installed Google Chrome and are skipped if it is
not found.

## Validation results

Run on 2026-10-30 with Node.js 24 and headless Google Chrome, using the automated tests.

| Quickstart scenario | Result |
|---------------------|--------|
| See a quote | Pass |
| New quote | Pass |
| Mark favorite | Pass |
| Unmark favorite | Pass |
| Persistence | Pass |
| Keyboard | Pass |

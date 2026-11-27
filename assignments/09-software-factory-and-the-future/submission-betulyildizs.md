# Week 9 - The Software Factory: Generate & Critique

## Student Information

- Name: Betül Yıldız
- GitHub: betulyildizs
- Project: Gatherly - Event RSVP

## Repository

https://github.com/betulyildizs/week9-software-factory

## Deliverables

- [Application Source Code](https://github.com/betulyildizs/week9-software-factory/tree/main/event-rsvp)
- [README and Local Setup Instructions](https://github.com/betulyildizs/week9-software-factory/blob/main/event-rsvp/README.md)
- [Critical Evaluation and Writeup](https://github.com/betulyildizs/week9-software-factory/blob/main/event-rsvp/writeup.md)
- [Automated Integration Test](https://github.com/betulyildizs/week9-software-factory/blob/main/event-rsvp/tests/concurrency.mjs)

## Project Summary

Gatherly is an event management and RSVP application generated using Bolt.new, critically evaluated and improved through manual code review, regression testing, and database-level validation.

## Key Improvements

- Fixed RSVP capacity enforcement bypass.
- Fixed fractional capacity validation.
- Implemented database-level capacity enforcement.
- Prevented capacity reduction below confirmed attendance.
- Corrected misleading waitlist messages.
- Fixed stale attendee counts.
- Patched reported production dependency vulnerabilities.

## Verification Results

- Manual regression tests: 9/9 passed.
- Automated database checks: 3/3 passed.
- Production build: passed.
- TypeScript typecheck: passed.
- Production dependency audit: 0 reported vulnerabilities.
- Bolt prompt iterations: 2.

The original generated implementation and subsequent improvements are preserved in separate Git commits.

Known limitations, generation prompts, implementation decisions, and the learning reflection are documented in the writeup.

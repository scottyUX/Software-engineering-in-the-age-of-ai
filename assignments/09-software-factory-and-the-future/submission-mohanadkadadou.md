# Week 9 Submission (Software Factory): Mohanad Kadadou (2309115218)

Repository: https://github.com/mohanadkadadou/week9-event-rsvp (app in `event-rsvp/`)

- **Deviation, stated up front:** bolt.new needs an account and credits that I could not create, so the app was generated in one pass from the exact `PROMPT.md` by a separate Claude subagent acting as the generator (1 iteration); its output is the first commit, unmodified. A bolt.new version can be checked with the same issue list.
- **Evaluation:** 5 real issues found by probing the running server (capacity coercion and a 500 on huge numbers, unvalidated dates, **attendee emails exposed by the API**, no length/body limits, weak email regex), fixed by hand; 8 end-to-end tests, 5 of which fail on the unmodified generated code.
- README with prerequisites/install/run/env, and a writeup with the prompt, iterations, the issues and the reflection on generating vs building and on self-improving systems: [writeup.md](https://github.com/mohanadkadadou/week9-event-rsvp/blob/main/writeup.md).

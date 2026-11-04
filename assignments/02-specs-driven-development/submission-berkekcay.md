# Week 2 submission: Berke Eren Akçay

Repository: https://github.com/berkekcay/quote-of-the-day-speckit

The constitution is in `.specify/memory/constitution.md`, and the spec, plan, research, data
model, contracts, quickstart and tasks are in `specs/001-quote-of-the-day/`. Each stage has its
own commit. The page is plain HTML, CSS and JavaScript with favorites in `localStorage`, and
`npm test` runs 21 passing tests.

For the refinement, the first spec let "New quote" pick the quote already on screen (it happened
once in 60 clicks). I changed FR-003 in the spec so it never repeats, regenerated from it, and
got 0 repeats in 500 clicks. `/speckit-converge` took three rounds to report Converged. The
prompts, the before and after, and what I learned are in
[writeup.md](https://github.com/berkekcay/quote-of-the-day-speckit/blob/main/writeup.md).

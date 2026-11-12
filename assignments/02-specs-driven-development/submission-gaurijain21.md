# Week 2 Submission: gaurijain21

**Repo:** https://github.com/gaurijain21/spec-kit-week2

**Writeup:** https://github.com/gaurijain21/spec-kit-week2/blob/main/writeup.md

## What's in the repo

- Spec Kit project (specify-cli v1.2.1) set up with the `claude` integration
- All the spec artifacts, committed one stage at a time: constitution, spec, plan (with
  research, data model, contracts and quickstart) and tasks
- The quote-of-the-day page (`index.html`, `src/`), with favorites saved in localStorage
- Unit tests: `node --test` passes 11/11

## Spec refinement

The first spec only said "New quote" picks a random quote, so about 1 in 12 clicks it
picked the one already on screen and looked broken (4 out of 60 in my browser test). I
changed FR-003 so the new quote has to be different. Then converge added two tasks for it,
and after implementing them it went to 0 out of 60. I also had to fix the test command in
the plan because `node --test tests/` doesn't work on Node 22.

## Convergence

I ran converge three times. It said Converged, then found the FR-003 gap after I changed
the spec, then said Converged again at the end.

# Week 2 — Spec-Driven Development with Spec Kit

**Estimated time: ~3 hours.**

## Overview
You'll build a small feature the **spec-driven** way using GitHub's
[**Spec Kit**](https://github.com/github/spec-kit): define **what and why** before
**how**, then let your coding agent implement against the spec and iterate until it
*converges*. The point is the **process** and the durable spec artifacts, not the app.

To keep this to ~3 hours, the feature is **pre-scoped** for you (below).

## Learning goals
- Run the Spec Kit loop: **constitution → specify → plan → tasks → implement → converge**.
- Write a spec precise enough for an agent to implement without guessing.
- Experience the human review gate between stages.

---

## Prerequisites
- Python **3.11+** and [**uv**](https://github.github.io/spec-kit/install/uv.html).
- The coding agent you set up in Week 1 (Antigravity by default).

## Setup
Replace `copilot` with your agent's
[integration key](https://github.github.io/spec-kit/reference/integrations.html):
```bash
uv tool install specify-cli
specify init spec-kit-week2 --integration copilot
cd spec-kit-week2
```
Launch your agent **inside the project directory**. The `/speckit-*` skills run in the
agent's **chat**, not the terminal.

> **Common mistake:** `specify init` checks that your agent's command-line tool is installed.
> If you use an agent that runs as a desktop app or editor extension (so there is no CLI
> on your `PATH`), init stops with `<agent> not found`. Re-run it with
> `--ignore-agent-tools`, and add `--non-interactive` if it hangs waiting for a prompt:
> ```bash
> specify init spec-kit-week2 --integration <key> --non-interactive --ignore-agent-tools
> ```
> Then run `git init` and **commit after each stage**. Your history becomes evidence of the
> constitution → specify → plan → tasks → implement → converge loop for the grader.

## The feature (pre-scoped — build exactly this)
> A **quote-of-the-day** page: shows one random quote from a small built-in list, with a
> "New quote" button, and a way to mark a quote as a favorite that persists on reload.

## Run the loop
Invoke each skill in your agent's chat, **reviewing each artifact before continuing**:
```text
/speckit-constitution Create principles focused on code quality, testing, and maintainability.
/speckit-specify A quote-of-the-day page: one random quote from a built-in list, a "New quote" button, and favoriting that persists across reloads.
/speckit-plan Use plain HTML/CSS/JavaScript, no backend; persist favorites in localStorage.
/speckit-tasks
/speckit-implement
/speckit-converge
```
Repeat **implement → converge** until it reports **Converged**. If `/speckit-converge`
reports gaps, ask yourself whether the **spec/plan** was vague (a good candidate for your
documented refinement) or the code simply missed something. Tip: measure the gap (for example,
run the behavior 1,000 times) so your before/after is evidence, not opinion. At least once, when an
artifact is vague or wrong, **refine the spec/plan** (not the code) and note what changed.

## Deliverables
**Submit the GitHub repository link** for `spec-kit-week2/` (add the instructor as a
collaborator if private), including:
1. The committed **spec artifacts** in `.specify/` (not gitignored).
2. The **working page** produced by `/speckit-implement`.
3. A `writeup.md`: the prompts you gave each skill; one before/after where refining the
   **spec or plan** changed the output; the convergence outcome; and **what you learned**
   (3–4 sentences on where SDD felt like overhead vs. where it paid off).

## Evaluation (100 pts)
- 40 — Complete, committed spec artifacts for all stages.
- 30 — Working page that matches its spec; convergence reached.
- 20 — At least one documented spec/plan refinement that changed the output.
- 10 — Clear `writeup.md` with the "what you learned" reflection.

## References
- Spec Kit: https://github.com/github/spec-kit
- Quickstart: https://github.github.io/spec-kit/quickstart.html
- Integration keys: https://github.github.io/spec-kit/reference/integrations.html

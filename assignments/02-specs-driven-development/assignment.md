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

## The feature (pre-scoped — build exactly this)
> A **quote-of-the-day** page: shows one random quote from a small built-in list, with a
> "New quote" button, and a way to mark a quote as a favorite that persists on reload.

## Acceptance Criteria & Functional Validation Guide

This section provides measurable acceptance criteria and a structured validation approach for the Quote of the Day feature. Its purpose is to help students evaluate implementation correctness, trace requirements to observable behavior, and identify specification gaps during the Spec Kit convergence process.

### 1. Functional Acceptance Criteria

The following criteria define the expected behavior of the Quote of the Day application. Each criterion includes a clear requirement and a practical method for verifying its implementation.

**AC-01 — Initial Quote Display**

- **Expected Behavior:** On page load, exactly one quote from the predefined built-in list is displayed.
- **Validation:** Open the application and verify that a valid quote is visible.

**AC-02 — Quote Generation**

- **Expected Behavior:** Clicking "New quote" selects and displays a quote from the built-in list.
- **Validation:** Click the button multiple times and verify that the displayed quotes belong to the predefined list.

**AC-03 — Favorite Selection**

- **Expected Behavior:** Users can mark the displayed quote as a favorite, and the interface clearly indicates its selected state.
- **Validation:** Mark a quote as a favorite and verify that the UI reflects the selection.

**AC-04 — Favorite Deselection**

- **Expected Behavior:** Users can remove a previously selected quote from their favorites.
- **Validation:** Unmark a favorite and verify that the interface reflects the updated state.

**AC-05 — Favorite Persistence**

- **Expected Behavior:** Favorite selections are preserved in browser localStorage across page reloads.
- **Validation:** Favorite a quote, refresh the page, and verify that its favorite status is retained when revisiting it.

**AC-06 — Implementation Constraints**

- **Expected Behavior:** The application is implemented using plain HTML, CSS, and JavaScript, without a backend.
- **Validation:** Review the implementation and confirm that favorites are stored locally using browser localStorage.


### 2. Boundary and Consistency Checks

In addition to the primary acceptance criteria, verify the following behaviors:

- **Duplicate prevention:** Repeatedly selecting the same favorite does not create duplicate stored entries.
- **Persistence after removal:** Removing a favorite updates localStorage, and the quote remains unfavorited after refreshing and revisiting it.

These checks validate the reliability of the existing requirements without introducing additional application features.

### 3. Validation During the Spec Kit Workflow

1. **Review:** Confirm that the generated specification and implementation plan address the acceptance criteria.
2. **Validate:** Test the implemented application against the functional and consistency checks above.
3. **Refine:** If requirements are missing or ambiguous, update the specification or plan rather than directly modifying the generated code.
4. **Converge:** Repeat implementation and convergence as needed, verify the final behavior, and document meaningful refinements in `writeup.md`.

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
Repeat **implement → converge** until it reports **Converged**. At least once, when an
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

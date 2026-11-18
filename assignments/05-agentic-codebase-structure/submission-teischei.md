# Week 5 Submission - Thalia Eischeid

Week 5 repository: https://github.com/teischei/week5-agentic-codebase-structure

Writeup: https://github.com/teischei/week5-agentic-codebase-structure/blob/main/writeup.md

This project makes the Link Shortener easier for a coding agent to work with.

It includes a root `AGENTS.md` with repository context and boundaries, scoped test instructions in `tests/AGENTS.md`, and a reusable `implement-link-task` skill.

I completed the custom alias feature. A user can provide an alias when creating a short link. Duplicate aliases return a 409 response, while blank, reserved, and invalid path aliases return clear errors.

The final test suite has 7 passing tests. The writeup explains the planning, implementation, review, and what I learned about structuring a repository for coding agents.
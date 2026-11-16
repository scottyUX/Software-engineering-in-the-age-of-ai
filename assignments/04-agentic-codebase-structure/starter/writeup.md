# Assignment Writeup: Agentic Codebase Structure — The Link Shortener

## 1. AGENTS.md Rationale
`AGENTS.md` contains high-level repository context, key file locations, execution/testing commands, product boundaries, and a core development workflow. It is broadly available to give any agent an immediate mental model of the codebase without cluttering prompts with deep implementation specifics.

## 2. Scoped Instruction
The instruction was scoped in `tests/AGENTS.md`. It loads specifically when an agent operates on or generates code inside the test directory. It is scoped here because testing guidelines apply during test construction and would add noise if loaded during core business logic implementation.

## 3. Reusable Workflow Procedure
The reusable workflow (`SKILL.md`) encodes a 7-step Test-Driven Development (TDD) cycle: requirement reading, code inspection, plan declaration, writing a failing behavioral test, minimal implementation, pytest verification, and risk summarization.

## 4. Agent Discovery Mechanisms
- **`AGENTS.md`**: Automatically discovered at root by MCP agents and AI IDEs as default context.
- **`tests/AGENTS.md`**: Discovered dynamically when viewing or editing files within the `tests/` directory tree.
- **`SKILL.md`**: Invoked explicitly via `/feature-development-workflow` or discovered by skill-aware agents scanning repo metadata.

## 5. Planning and Review Impact
During planning, inspecting `docs/TASKS.md` made it clear that custom slug collision handling needed explicit HTTP 400 responses. During review, the agent flagged that empty custom slug strings should default back to randomly generated codes, leading to cleaner input sanitization.

## 6. Reflections on Agentic Repository Design
Structuring a repository for AI agents requires setting clear boundaries and modular guidelines. Providing root context keeps agents aligned with project goals, while scoped instructions ensure agents follow specific rules only when relevant, maximizing context efficiency.
# AGENTS.md

Guidance for coding agents working in this repository. Humans should start with [README.md](README.md).

## What this repo is

Course materials for **AI-Augmented Software Engineering** (UCSC CSE 115A, Fall 2026). It is mostly Markdown plus lecture-slide PDFs and a few small Python starter apps. Students read it and fork the starters; treat every change as student-facing.

```
lectures/<NN-topic>/      README.md (topic list) + slide PDF, one folder per lecture
assignments/<NN-topic>/   assignment.md + starter/ (code students extend)
resources/<NN-topic>/     README.md + papers-to-read.md
resources/midterm-study-guide/   per-week study notes, checklist, self-check questions
resources/cse115a-sprint-task-specifications.md   sprint task rubric
```

The `NN-topic` slug is shared across `lectures/`, `assignments/`, and `resources/`. A new week needs a folder in all three, plus entries in the top-level `README.md` and `lectures/README.md`.

## Ground rules

- **Starter bugs and old pins can be deliberate.** Starters exist for students to fix, review, or scan. Do not "fix" a starter's bugs, TODOs, or pinned versions unless the task asks for it. Examples:
  - `assignments/08-security-in-the-age-of-ai/starter/requirements.txt` pins `requests==2.25.1` on purpose so the SCA scan has something to flag.
  - `assignments/05-advanced-context-management/starter/requirements.txt` pins `mcp<2` because `server.py` uses the 1.x `FastMCP` API.
  - Read the comments in `requirements.txt` and the assignment's `docs/TASKS.md` before changing anything.
- **Keep starters runnable.** Each Python starter must still install and pass its stated checks from a clean venv (`pip install -r requirements.txt && pytest`). If you change a starter, run that and say what you ran.
- **Week numbering.** Lectures 4 and 5 were taught in the order Context Management, then Codebase Structure, but the folders are numbered `04-agentic-codebase-structure` and `05-advanced-context-management`. The midterm study guide uses taught order. Don't renumber folders; links depend on them.
- **Don't edit slide PDFs.** They are exported from the instructor's decks. Add or replace them only when asked.
- **Don't commit local artifacts:** `.venv/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `*.db`, `.env`. They are already in `.gitignore`.
- **Links are relative.** Use relative Markdown links between files; check that they resolve after moving or renaming anything.

## Writing style

- Plain, direct prose aimed at undergraduates. Short paragraphs; bold the key term the first time it matters.
- Headings: `# Lecture N — Title`, `# Week N — Title`, `# Papers to Read — Topic` (em dash, not hyphen).
- Assignments state an **Estimated time**, an Overview, Learning goals, and concrete deliverables. Stay tool-agnostic where possible: name a default tool and list alternatives.
- Paper entries in `papers-to-read.md` follow the existing shape: authors and year, paper links (arXiv abstract + PDF where available), **Why this paper**, and a **How to read it** walkthrough. Only cite papers you have verified exist; never invent authors, titles, or numbers.
- Dates and tool claims go stale fast (APIs retire, SDKs rename things). When you state a fact about a tool or service, check it rather than relying on memory.

## Python starters

| Assignment | Stack | Check |
| --- | --- | --- |
| `04-agentic-codebase-structure` | FastAPI | `pytest` |
| `05-advanced-context-management` | MCP server (`mcp<2`, `httpx`) | run `python server.py` through an MCP client |
| `06-agentic-code-review-and-testing` | FastAPI + SQLite | `pytest` |
| `07-agent-orchestration` | FastAPI + static HTML | `pytest` |
| `08-security-in-the-age-of-ai` | FastAPI | `pytest` |
| `10-ai-native-engineering-teams` | LiteLLM gateway | see starter README |
| `09-software-factory-and-the-future` | none — `PROMPT.md` for an app generator | — |

Each starter's `README.md` gives setup and endpoints; `docs/TASKS.md` (where present) lists what students implement.

## Git

- Branch from `main`; open a PR. Branch names are short and descriptive (`week6-coderabbit-default`, `fix/week5-mcp-pin`).
- Commit subject: imperative, sentence case, no trailing period, names the week when relevant ("Make CodeRabbit the default AI reviewer for Week 6").
- Commit body: explain *why* and what was verified, wrapped at ~72 columns.

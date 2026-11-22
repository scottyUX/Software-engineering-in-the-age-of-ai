# Recipe Box — Week 8 Agent Orchestration

A tiny FastAPI + SQLite service for recipes and tags, with a static frontend. Extended with concurrent agents and a generator-critic loop.

## Setup
```bash
pip install -r requirements.txt
pytest                      # 22 tests pass
uvicorn main:app --reload   # http://localhost:8000  (UI at /, docs at /docs)
```

## Endpoints
- `POST /recipes` `{ "title": ..., "ingredients": [...], "tags": [...] }`
- `GET /recipes`: list all recipes
- `GET /recipes?tag=breakfast`: list recipes filtered by tag (Task 2)
- `GET /recipes/{id}`: get recipe by ID
- `GET /recipes/{id}/scaled?factor=2`: scale recipe ingredient quantities (Task 3)
- `GET /shopping-list?ids=1,2,3`: merged and de-duplicated shopping list (Task 1)

## Orchestration Architecture
- **Part I — Concurrent Agents:** Tasks 1 and 2 were completed simultaneously by two agents isolated in separate git worktrees (`task-a`, `task-b`) and merged into `main`.
- **Part II — Generator-Critic Loop:** Task 3 was developed via a multi-round generator-critic workflow against `reviews/RUBRIC.md`. Reviews are documented in `reviews/` and `writeup.md`.

## Files
- `main.py` — FastAPI application
- `test_main.py` — base test suite
- `test_shopping_list.py` — Task 1 tests
- `test_tag_filter.py` — Task 2 tests
- `test_scaling.py` — Task 3 tests
- `reviews/` — Generator-critic rubric and critique logs
- `writeup.md` — Complete sprint writeup

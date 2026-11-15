# Starter — Recipe Box

A tiny FastAPI + SQLite service with a static frontend. Your playground for concurrent
agents and a generator–critic loop.

## Setup
```bash
pip install -r requirements.txt
pytest                      # 3 tests should pass
uvicorn main:app --reload   # http://localhost:8000  (UI at /, docs at /docs)
```

## Endpoints
- `POST /recipes` `{ "title": ..., "ingredients": [...], "tags": [...] }`
- `GET /recipes`, `GET /recipes/{id}`
- `GET /recipes?tag=breakfast`: only recipes with that tag (exact, case-insensitive)
- `GET /shopping-list?ids=1,2,3`: de-duplicated ingredients of those recipes
- `GET /recipes/{id}/scaled?factor=2`: the recipe with leading quantities scaled (0.001 <= factor <= 1000)

## How this was built
Tasks 1 and 2 were built by two agents running at the same time in separate git worktrees (`task-a`,
`task-b`). Task 3 went through a generator-critic loop; the rubric and every critique are in
[`reviews/`](reviews/). See [`writeup.md`](writeup.md).

## Parallel work with git worktrees
```bash
git worktree add ../recipe-task-a -b task-a
git worktree add ../recipe-task-b -b task-b
```

## Files
- `main.py` — the app
- `static/index.html` — minimal UI
- `test_main.py` — pytest suite
- `docs/TASKS.md` — independent tasks (safe to run in parallel)

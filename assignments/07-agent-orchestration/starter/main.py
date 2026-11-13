"""Recipe Box — starter app for Week 7.

A tiny FastAPI service for recipes and tags, with a static frontend. Use it as the
playground for concurrent multi-agent work and a generator-critic loop.

Run:
    pip install -r requirements.txt
    uvicorn main:app --reload
    # open http://localhost:8000/
Test:
    pytest
"""
import json
import sqlite3
from contextlib import closing
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

BASE = Path(__file__).parent
DB_PATH = BASE / "recipes.db"

app = FastAPI(title="Recipe Box")


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with closing(get_db()) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS recipes (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                ingredients TEXT NOT NULL,  -- JSON list of strings
                tags        TEXT NOT NULL   -- JSON list of strings
            )"""
        )
        conn.commit()


init_db()


class RecipeIn(BaseModel):
    title: str
    ingredients: list[str] = []
    tags: list[str] = []


def _row_to_recipe(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "ingredients": json.loads(row["ingredients"]),
        "tags": json.loads(row["tags"]),
    }


@app.get("/")
def index():
    return FileResponse(BASE / "static" / "index.html")


@app.post("/recipes")
def create_recipe(recipe: RecipeIn):
    with closing(get_db()) as conn:
        cur = conn.execute(
            "INSERT INTO recipes (title, ingredients, tags) VALUES (?, ?, ?)",
            (recipe.title, json.dumps(recipe.ingredients), json.dumps(recipe.tags)),
        )
        conn.commit()
        rid = cur.lastrowid
    return {"id": rid, **recipe.model_dump()}


@app.get("/recipes")
def list_recipes(
    tag: str | None = Query(
        default=None,
        description="Filter recipes by tag. Empty or whitespace-only values return all recipes.",
    ),
):
    with closing(get_db()) as conn:
        if tag is not None and tag.strip():
            target = tag.strip()
            rows = conn.execute(
                """
                SELECT * FROM recipes
                WHERE EXISTS (
                    SELECT 1 FROM json_each(recipes.tags) WHERE value = ?
                )
                ORDER BY id
                """,
                (target,),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM recipes ORDER BY id").fetchall()
    return [_row_to_recipe(r) for r in rows]


@app.get("/recipes/{recipe_id}")
def get_recipe(recipe_id: int):
    with closing(get_db()) as conn:
        row = conn.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="unknown recipe")
    return _row_to_recipe(row)


@app.get("/shopping-list")
def get_shopping_list(ids: str | None = None):
    if ids is None:
        raise HTTPException(status_code=400, detail="Missing required query parameter: ids")

    raw_tokens = [part.strip() for part in ids.split(",")]
    if not raw_tokens or all(not token for token in raw_tokens):
        raise HTTPException(status_code=400, detail="No recipe IDs provided")

    parsed_ids = []
    for token in raw_tokens:
        if not token:
            raise HTTPException(status_code=400, detail="Empty recipe ID in query parameter")
        try:
            val = int(token)
            if val <= 0:
                raise HTTPException(
                    status_code=400, detail=f"Invalid recipe ID (must be positive): {token}"
                )
            parsed_ids.append(val)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid recipe ID: {token}")

    unique_ids = list(dict.fromkeys(parsed_ids))

    with closing(get_db()) as conn:
        placeholders = ",".join("?" for _ in unique_ids)
        rows = conn.execute(
            f"SELECT * FROM recipes WHERE id IN ({placeholders})", unique_ids
        ).fetchall()

    recipes_by_id = {row["id"]: _row_to_recipe(row) for row in rows}

    missing = [rid for rid in unique_ids if rid not in recipes_by_id]
    if missing:
        raise HTTPException(
            status_code=404,
            detail=f"unknown recipe: {', '.join(str(m) for m in missing)}",
        )

    seen = set()
    shopping_list = []
    for rid in unique_ids:
        recipe = recipes_by_id[rid]
        for ingredient in recipe["ingredients"]:
            cleaned = ingredient.strip()
            if not cleaned:
                continue
            key = cleaned.lower()
            if key not in seen:
                seen.add(key)
                shopping_list.append(cleaned)

    return shopping_list


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
import math
import re
import sqlite3
from contextlib import closing
from pathlib import Path

from fastapi import FastAPI, HTTPException
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
def list_recipes(tag: str | None = None):
    with closing(get_db()) as conn:
        rows = conn.execute("SELECT * FROM recipes ORDER BY id").fetchall()
    recipes = [_row_to_recipe(r) for r in rows]
    if tag is None:
        return recipes
    return [recipe for recipe in recipes if tag in recipe["tags"]]


@app.get("/recipes/{recipe_id}")
def get_recipe(recipe_id: int):
    with closing(get_db()) as conn:
        row = conn.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="unknown recipe")
    return _row_to_recipe(row)


@app.get("/shopping-list")
def shopping_list(ids: str = ""):
    raw_ids = [item.strip() for item in ids.split(",") if item.strip()]
    try:
        recipe_ids = [int(item) for item in raw_ids]
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="ids must be comma-separated integers") from exc

    merged: list[str] = []
    seen: set[str] = set()
    with closing(get_db()) as conn:
        for recipe_id in recipe_ids:
            row = conn.execute(
                "SELECT ingredients FROM recipes WHERE id = ?", (recipe_id,)
            ).fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="unknown recipe")
            for ingredient in json.loads(row["ingredients"]):
                if ingredient not in seen:
                    seen.add(ingredient)
                    merged.append(ingredient)
    return merged


def _scale_ingredient(ingredient: str, factor: float) -> str:
    match = re.match(r"^(\d+(?:\.\d+)?)\s+(.+)$", ingredient)
    if match is None:
        return ingredient
    amount = float(match.group(1)) * factor
    return f"{amount:g} {match.group(2)}"


@app.get("/recipes/{recipe_id}/scaled")
def scaled_recipe(recipe_id: int, factor: float = 1):
    if not math.isfinite(factor) or factor <= 0:
        raise HTTPException(status_code=422, detail="factor must be a positive number")
    recipe = get_recipe(recipe_id)
    return {
        **recipe,
        "ingredients": [_scale_ingredient(item, factor) for item in recipe["ingredients"]],
    }

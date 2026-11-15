"""Recipe Box — starter app for Week 7.

A tiny FastAPI service for recipes and tags, with a static frontend.
Integrated both concurrent agent features:
- Task A: Shopping list (/shopping-list?ids=1,2,3)
- Task B: Tag filter (/recipes?tag=breakfast)
- Part II: Ingredient scaling (/recipes/{id}/scaled?factor=2) via Generator-Critic loop.
"""

import json
import re
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


def _scale_ingredient(text: str, factor: float) -> str:
    """Scale numeric quantities in ingredient text (e.g. '200 g flour' -> '400 g flour')."""
    match = re.match(r"^(\d+(?:\.\d+)?)\s*(.*)$", text.strip())
    if match:
        orig_num = float(match.group(1))
        unit_and_name = match.group(2)
        scaled_num = orig_num * factor
        # format cleanly: 4.0 -> 4, 2.5 -> 2.5
        formatted_num = (
            int(scaled_num) if scaled_num.is_integer() else round(scaled_num, 2)
        )
        return (
            f"{formatted_num} {unit_and_name}"
            if unit_and_name
            else str(formatted_num)
        )
    return text


@app.get("/")
def index():
    return FileResponse(BASE / "static" / "index.html")


@app.post("/recipes")
def create_recipe(recipe: RecipeIn):
    with closing(get_db()) as conn:
        cur = conn.execute(
            "INSERT INTO recipes (title, ingredients, tags) VALUES (?, ?, ?)",
            (
                recipe.title,
                json.dumps(recipe.ingredients),
                json.dumps(recipe.tags),
            ),
        )
        conn.commit()
        rid = cur.lastrowid
    return {"id": rid, **recipe.model_dump()}


@app.get("/recipes")
def list_recipes(
    tag: str | None = Query(None, description="Optional tag filter"),
):
    with closing(get_db()) as conn:
        rows = conn.execute("SELECT * FROM recipes ORDER BY id").fetchall()

    recipes = [_row_to_recipe(r) for r in rows]
    if tag is not None and tag.strip():
        clean_tag = tag.strip().lower()
        recipes = [
            r
            for r in recipes
            if any(clean_tag == t.lower() for t in r.get("tags", []))
        ]

    return recipes


@app.get("/recipes/{recipe_id}")
def get_recipe(recipe_id: int):
    with closing(get_db()) as conn:
        row = conn.execute(
            "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="unknown recipe")
    return _row_to_recipe(row)


@app.get("/recipes/{recipe_id}/scaled")
def get_scaled_recipe(
    recipe_id: int,
    factor: float = Query(
        ..., gt=0, description="Scaling multiplier, e.g. 2 or 0.5"
    ),
):
    with closing(get_db()) as conn:
        row = conn.execute(
            "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="unknown recipe")

    recipe = _row_to_recipe(row)
    scaled_ingredients = [
        _scale_ingredient(ing, factor) for ing in recipe["ingredients"]
    ]
    return {
        "id": recipe["id"],
        "title": recipe["title"],
        "scale_factor": factor,
        "ingredients": scaled_ingredients,
        "tags": recipe["tags"],
    }


@app.get("/shopping-list")
def get_shopping_list(
    ids: str = Query(
        ..., description="Comma-separated recipe IDs, e.g. 1,2,3"
    ),
):
    if not ids.strip():
        return {"items": []}

    try:
        id_list = [int(i.strip()) for i in ids.split(",") if i.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid recipe ID in list")

    if not id_list:
        return {"items": []}

    placeholders = ",".join("?" for _ in id_list)
    with closing(get_db()) as conn:
        rows = conn.execute(
            f"SELECT ingredients FROM recipes WHERE id IN ({placeholders})",
            id_list,
        ).fetchall()

    merged_items = []
    seen = set()
    for row in rows:
        ing_list = json.loads(row["ingredients"])
        for item in ing_list:
            clean_item = item.strip()
            item_key = clean_item.lower()
            if item_key not in seen:
                seen.add(item_key)
                merged_items.append(clean_item)

    return {"items": merged_items}

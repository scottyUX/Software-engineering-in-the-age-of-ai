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
def list_recipes(tag: str | None = None):
    """List recipes, optionally only those carrying `tag`.

    Tag matching is exact per tag (no substring matches), case-insensitive and
    ignores surrounding whitespace. A missing, empty or whitespace-only `tag`
    means "no filter" and returns every recipe, as before.
    """
    with closing(get_db()) as conn:
        rows = conn.execute("SELECT * FROM recipes ORDER BY id").fetchall()
    recipes = [_row_to_recipe(r) for r in rows]
    wanted = (tag or "").strip().casefold()
    if not wanted:
        return recipes
    return [
        rec for rec in recipes
        if any(t.strip().casefold() == wanted for t in rec["tags"])
    ]


def _load_recipe(recipe_id: int) -> dict:
    with closing(get_db()) as conn:
        row = conn.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="unknown recipe")
    return _row_to_recipe(row)


@app.get("/recipes/{recipe_id}")
def get_recipe(recipe_id: int):
    return _load_recipe(recipe_id)


# Parsing rule: an ingredient is scaled only when, after any leading whitespace, it
# STARTS with a plain ASCII number, an integer ("200") or a dot decimal ("1.5"),
# and the next non-space character is an ASCII letter or the end of the text:
#   "200 g flour" -> scaled,  "1.5kg rice" -> scaled,  "3" -> scaled,
#   " 200 g sugar" -> scaled (leading whitespace is dropped in the result).
# Everything else is returned unchanged on purpose:
#   no leading number ("salt to taste"), quantity not first ("flour, 200 g"),
#   fractions ("1/2 cup"), mixed numbers ("1 1/2 cups", "1 ½ cups"),
#   ranges ("2-3 eggs"), comma decimals ("1,5 l"), non-ASCII digits ("٢٠٠ g", "２００ g"),
#   scientific notation ("1e3 g").
# The factor must be between MIN_FACTOR and MAX_FACTOR (inclusive), otherwise 422.
LEADING_QUANTITY = re.compile(
    r"^\s*(\d+(?:\.\d+)?)(?![eE][+-]?\d)(?=\s*[A-Za-z]|\s*$)", re.ASCII
)

MIN_FACTOR = 0.001  # smaller factors get a 422
MAX_FACTOR = 1000  # larger factors get a 422
MAX_QUANTITY = 1e15  # a scaled result this big (or inf) leaves the ingredient unchanged


def format_quantity(value: float) -> str:
    """2 decimals for values >= 1, 2 significant figures below 1, no trailing zeros.

    400.0 -> "400", 0.5 -> "0.5", 1/3 -> "0.33", 0.001 -> "0.001", 0.00123 -> "0.0012".
    A non-zero value never rounds to "0".
    """
    if value == 0:
        return "0"
    decimals = max(2, 1 - math.floor(math.log10(abs(value))))
    return f"{value:.{decimals}f}".rstrip("0").rstrip(".")


def scale_ingredient(ingredient: str, factor: float) -> str:
    match = LEADING_QUANTITY.match(ingredient)
    if match is None:
        return ingredient
    scaled = float(match.group(1)) * factor
    if scaled >= MAX_QUANTITY:  # absurd input like a 300-digit number: leave it alone
        return ingredient
    return format_quantity(scaled) + ingredient[match.end():]


@app.get("/recipes/{recipe_id}/scaled")
def get_scaled_recipe(
    recipe_id: int,
    factor: float = Query(
        ..., ge=MIN_FACTOR, le=MAX_FACTOR, allow_inf_nan=False,
        description=f"multiplier, {MIN_FACTOR} <= factor <= {MAX_FACTOR}",
    ),
):
    """Same shape as GET /recipes/{id}, ingredients scaled. The stored recipe is not changed."""
    recipe = _load_recipe(recipe_id)
    recipe["ingredients"] = [scale_ingredient(i, factor) for i in recipe["ingredients"]]
    return recipe


@app.get("/shopping-list")
def shopping_list(ids: str | None = None):
    """Merge the ingredients of the given recipes into a de-duplicated list.

    `ids` is a comma-separated list of positive recipe ids, e.g. `?ids=1,2,3`.
    Ingredients are compared case-insensitively after trimming and collapsing
    whitespace; the first spelling seen is kept. Order follows the requested
    recipe order, then each recipe's ingredient order. Blank ingredients are
    dropped. Repeated ids are counted once.
    """
    if ids is None or not ids.strip():
        raise HTTPException(status_code=400, detail="query parameter 'ids' is required, e.g. ?ids=1,2,3")
    recipe_ids: list[int] = []
    for part in ids.split(","):
        token = part.strip()
        if not (token.isascii() and token.isdigit()) or int(token) <= 0:
            raise HTTPException(
                status_code=400,
                detail=f"invalid recipe id {token!r}: ids must be positive integers separated by commas",
            )
        rid = int(token)
        if rid not in recipe_ids:
            recipe_ids.append(rid)

    with closing(get_db()) as conn:
        placeholders = ",".join("?" * len(recipe_ids))
        rows = conn.execute(
            f"SELECT * FROM recipes WHERE id IN ({placeholders})", recipe_ids
        ).fetchall()
    by_id = {row["id"]: row for row in rows}
    missing = [rid for rid in recipe_ids if rid not in by_id]
    if missing:
        raise HTTPException(
            status_code=404,
            detail=f"unknown recipe id(s): {', '.join(str(m) for m in missing)}",
        )

    seen: set[str] = set()
    ingredients: list[str] = []
    for rid in recipe_ids:
        for item in json.loads(by_id[rid]["ingredients"]):
            display = " ".join(str(item).split())
            key = display.casefold()
            if not key or key in seen:
                continue
            seen.add(key)
            ingredients.append(display)
    return {"recipe_ids": recipe_ids, "ingredients": ingredients, "count": len(ingredients)}

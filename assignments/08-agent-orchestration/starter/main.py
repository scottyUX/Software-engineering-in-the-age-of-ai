"""Recipe Box — starter app for Week 8.

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
        conn.execute("""CREATE TABLE IF NOT EXISTS recipes (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                ingredients TEXT NOT NULL,  -- JSON list of strings
                tags        TEXT NOT NULL   -- JSON list of strings
            )""")
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
        rec
        for rec in recipes
        if any(t.strip().casefold() == wanted for t in rec["tags"])
    ]


@app.get("/recipes/{recipe_id}")
def get_recipe(recipe_id: int):
    with closing(get_db()) as conn:
        row = conn.execute(
            "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="unknown recipe")
    return _row_to_recipe(row)


# Parsing rule: an ingredient is scaled only when, after any leading whitespace, it
# starts with a plain ASCII number, an integer ("200") or a dot decimal ("1.5"),
# and the next non-space character is an ASCII letter or the end of the text.
# The following patterns are preserved unchanged:
#   - Fractions ("1/2 cup")
#   - Mixed numbers ("1 1/2 cups")
#   - Ranges ("2-3 eggs", "1-2 cups")
#   - Text without leading number ("salt to taste")
#   - Quantity not first ("flour, 200 g")
LEADING_QUANTITY = re.compile(
    r"^\s*(\d+(?:\.\d+)?)(?![eE][+-]?\d)(?![/-]\d)(?=\s*[A-Za-z]|\s*$)", re.ASCII
)

MIN_FACTOR = 0.001
MAX_FACTOR = 1000


def format_quantity(value: float) -> str:
    """Format scaled quantity cleanly without floating-point noise or awkward trailing zeros."""
    if abs(value - round(value)) < 1e-9:
        return str(round(value))
    if value >= 1:
        return f"{value:.2f}".rstrip("0").rstrip(".")
    formatted = f"{value:.4f}".rstrip("0").rstrip(".")
    if formatted == "0" and value > 0:
        return f"{value:.2g}"
    return formatted


def scale_ingredient(ingredient: str, factor: float) -> str:
    """Scales leading numerical quantity in an ingredient string by factor."""
    parts = ingredient.strip().split()
    if len(parts) >= 2 and "/" in parts[1]:
        # Mixed number: e.g. "1 1/2 cups" -> preserve unchanged
        return ingredient

    m = LEADING_QUANTITY.match(ingredient)
    if not m:
        return ingredient

    raw_num = m.group(1)
    val = float(raw_num)
    scaled_val = val * factor
    rest = ingredient[m.end() :]
    return f"{format_quantity(scaled_val)}{rest}"


@app.get("/recipes/{recipe_id}/scaled")
def get_scaled_recipe(
    recipe_id: int,
    factor: float = Query(
        ...,
        ge=MIN_FACTOR,
        le=MAX_FACTOR,
        description="Scaling factor between 0.001 and 1000",
    ),
):
    """Returns a recipe with leading ingredient quantities scaled by factor."""
    recipe = get_recipe(recipe_id)
    scaled_ingredients = [
        scale_ingredient(ing, factor) for ing in recipe["ingredients"]
    ]
    return {
        **recipe,
        "ingredients": scaled_ingredients,
        "scaling_factor": factor,
    }


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
        raise HTTPException(
            status_code=400,
            detail="query parameter 'ids' is required, e.g. ?ids=1,2,3",
        )
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
        all_ingredients = []
        for rid in recipe_ids:
            row = conn.execute(
                "SELECT ingredients FROM recipes WHERE id = ?", (rid,)
            ).fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail=f"unknown recipe {rid}")
            ingredients = json.loads(row["ingredients"])
            all_ingredients.extend(ingredients)

    seen = set()
    deduped = []
    for raw in all_ingredients:
        collapsed = re.sub(r"\s+", " ", raw.strip())
        if not collapsed:
            continue
        key = collapsed.casefold()
        if key not in seen:
            seen.add(key)
            deduped.append(collapsed)

    return {
        "recipe_ids": recipe_ids,
        "ingredients": deduped,
        "count": len(deduped),
    }

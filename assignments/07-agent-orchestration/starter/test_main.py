from fastapi import HTTPException

from main import (
    RecipeIn,
    create_recipe,
    get_recipe,
    list_recipes,
    scaled_recipe,
    shopping_list,
)


def test_create_and_get_recipe():
    recipe = create_recipe(
        RecipeIn(title="Pancakes", ingredients=["flour", "milk"], tags=["breakfast"])
    )
    assert get_recipe(recipe["id"])["title"] == "Pancakes"
    assert get_recipe(recipe["id"])["tags"] == ["breakfast"]


def test_list_recipes():
    create_recipe(RecipeIn(title="Toast"))
    assert any(rec["title"] == "Toast" for rec in list_recipes())


def test_unknown_recipe_404():
    try:
        get_recipe(99999)
    except HTTPException as exc:
        assert exc.status_code == 404
    else:
        raise AssertionError("missing recipe should raise HTTPException")


def test_tag_filter_returns_only_matching_recipes():
    create_recipe(RecipeIn(title="Waffles", tags=["week7-breakfast"]))
    create_recipe(RecipeIn(title="Pasta", tags=["week7-dinner"]))
    assert [recipe["title"] for recipe in list_recipes(tag="week7-breakfast")] == ["Waffles"]


def test_shopping_list_deduplicates_in_first_seen_order():
    first = create_recipe(
        RecipeIn(title="Soup", ingredients=["onion", "carrot", "salt"])
    )["id"]
    second = create_recipe(
        RecipeIn(title="Stew", ingredients=["carrot", "potato", "salt"])
    )["id"]
    assert shopping_list(f"{first},{second}") == ["onion", "carrot", "salt", "potato"]


def test_scaled_recipe_doubles_numeric_ingredients():
    recipe = create_recipe(
        RecipeIn(title="Pancakes", ingredients=["200 g flour", "2 eggs", "salt"])
    )
    result = scaled_recipe(recipe["id"], factor=2)
    assert result["ingredients"] == ["400 g flour", "4 eggs", "salt"]


def test_scaled_recipe_rejects_non_positive_factor():
    recipe = create_recipe(RecipeIn(title="Soup", ingredients=["1 l stock"]))
    try:
        scaled_recipe(recipe["id"], factor=0)
    except HTTPException as exc:
        assert exc.status_code == 422
    else:
        raise AssertionError("non-positive factors should be rejected")


def test_scaled_recipe_formats_decimal_results_and_keeps_unquantified_items():
    recipe = create_recipe(
        RecipeIn(title="Sauce", ingredients=["200 g tomatoes", "pepper"])
    )
    result = scaled_recipe(recipe["id"], factor=0.5)
    assert result["ingredients"] == ["100 g tomatoes", "pepper"]


def test_scaled_recipe_unknown_recipe_404():
    try:
        scaled_recipe(99999, factor=2)
    except HTTPException as exc:
        assert exc.status_code == 404
    else:
        raise AssertionError("missing recipe should raise HTTPException")

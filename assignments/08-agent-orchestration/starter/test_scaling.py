"""Tests for GET /recipes/{id}/scaled?factor=... (Task 3: ingredient scaling)."""

from fastapi.testclient import TestClient

from main import app, format_quantity, scale_ingredient

client = TestClient(app)


def _make_recipe(title: str, ingredients: list[str]) -> int:
    r = client.post(
        "/recipes", json={"title": title, "ingredients": ingredients, "tags": []}
    )
    assert r.status_code == 200
    return r.json()["id"]


def test_scale_ingredient_integers_and_decimals():
    assert scale_ingredient("200 g flour", 2.0) == "400 g flour"
    assert scale_ingredient("1.5 kg rice", 2.0) == "3 kg rice"
    assert scale_ingredient("10 eggs", 0.5) == "5 eggs"
    assert scale_ingredient(" 200 g sugar", 2.0) == "400 g sugar"


def test_scale_ingredient_preserves_fractions_and_mixed():
    # Fractions, mixed numbers, ranges, and text without leading quantities stay untouched
    assert scale_ingredient("1/2 cup milk", 2.0) == "1/2 cup milk"
    assert scale_ingredient("1 1/2 cups flour", 2.0) == "1 1/2 cups flour"
    assert scale_ingredient("2-3 eggs", 2.0) == "2-3 eggs"
    assert scale_ingredient("salt to taste", 2.0) == "salt to taste"
    assert scale_ingredient("flour, 200 g", 2.0) == "flour, 200 g"


def test_format_quantity_cleanliness():
    assert format_quantity(400.0) == "400"
    assert format_quantity(0.5) == "0.5"
    assert format_quantity(1.25) == "1.25"
    assert format_quantity(0.001) == "0.001"
    # Never rounds non-zero to zero
    assert format_quantity(0.0005) != "0"


def test_scaled_endpoint_success():
    rid = _make_recipe("Pancake", ["200 g flour", "100 ml milk", "1/2 cup sugar"])
    r = client.get(f"/recipes/{rid}/scaled?factor=2")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == rid
    assert data["scaling_factor"] == 2.0
    assert data["ingredients"] == ["400 g flour", "200 ml milk", "1/2 cup sugar"]

    # Verify original recipe in DB is not modified
    orig = client.get(f"/recipes/{rid}").json()
    assert orig["ingredients"] == ["200 g flour", "100 ml milk", "1/2 cup sugar"]


def test_scaled_endpoint_factor_bounds_validation():
    rid = _make_recipe("Item", ["100 g flour"])

    # Valid lower and upper bounds
    assert client.get(f"/recipes/{rid}/scaled?factor=0.001").status_code == 200
    assert client.get(f"/recipes/{rid}/scaled?factor=1000").status_code == 200

    # Below lower bound (422)
    assert client.get(f"/recipes/{rid}/scaled?factor=0.0009").status_code == 422
    assert client.get(f"/recipes/{rid}/scaled?factor=0").status_code == 422
    assert client.get(f"/recipes/{rid}/scaled?factor=-1").status_code == 422

    # Above upper bound (422)
    assert client.get(f"/recipes/{rid}/scaled?factor=1001").status_code == 422
    assert client.get(f"/recipes/{rid}/scaled?factor=1e308").status_code == 422

    # Invalid non-numeric factor (422)
    assert client.get(f"/recipes/{rid}/scaled?factor=abc").status_code == 422


def test_scaled_endpoint_unknown_recipe_404():
    r = client.get("/recipes/99999/scaled?factor=2")
    assert r.status_code == 404
    assert "unknown recipe" in r.json()["detail"]

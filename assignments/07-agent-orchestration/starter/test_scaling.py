import pytest
from fastapi.testclient import TestClient

import main
from main import app, format_quantity, scale_ingredient

client = TestClient(app)


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    """Each test gets its own empty SQLite file, so the app's recipes.db is never touched."""
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "recipes.db")
    main.init_db()


def make_recipe(ingredients):
    r = client.post(
        "/recipes",
        json={"title": "Scaling test", "ingredients": ingredients, "tags": ["test"]},
    )
    assert r.status_code == 200
    return r.json()["id"]


# --- endpoint ---------------------------------------------------------------


def test_scales_every_quantity_by_factor_2():
    rid = make_recipe(["200 g flour", "2 eggs", "300 ml milk"])
    r = client.get(f"/recipes/{rid}/scaled", params={"factor": 2})
    assert r.status_code == 200
    assert r.json()["ingredients"] == ["400 g flour", "4 eggs", "600 ml milk"]


def test_response_shape_matches_get_recipe():
    rid = make_recipe(["200 g flour"])
    plain = client.get(f"/recipes/{rid}").json()
    scaled = client.get(f"/recipes/{rid}/scaled", params={"factor": 2}).json()
    assert scaled.keys() == plain.keys()
    assert scaled["id"] == plain["id"]
    assert scaled["title"] == plain["title"]
    assert scaled["tags"] == plain["tags"]


def test_ingredients_without_quantity_are_unchanged():
    rid = make_recipe(["salt to taste", "200 g flour", "a pinch of pepper"])
    r = client.get(f"/recipes/{rid}/scaled", params={"factor": 3})
    assert r.json()["ingredients"] == ["salt to taste", "600 g flour", "a pinch of pepper"]


def test_fractional_factor_and_decimal_quantity():
    rid = make_recipe(["1.5 kg potatoes", "3 eggs"])
    r = client.get(f"/recipes/{rid}/scaled", params={"factor": 0.5})
    assert r.status_code == 200
    assert r.json()["ingredients"] == ["0.75 kg potatoes", "1.5 eggs"]


def test_fractions_and_ranges_left_unchanged_on_purpose():
    unchanged = ["1/2 cup milk", "2-3 eggs", "1,5 l water"]
    rid = make_recipe(unchanged)
    r = client.get(f"/recipes/{rid}/scaled", params={"factor": 2})
    assert r.json()["ingredients"] == unchanged


def test_recipe_with_no_ingredients():
    rid = make_recipe([])
    r = client.get(f"/recipes/{rid}/scaled", params={"factor": 2})
    assert r.status_code == 200
    assert r.json()["ingredients"] == []


def test_stored_recipe_is_not_modified():
    rid = make_recipe(["200 g flour"])
    client.get(f"/recipes/{rid}/scaled", params={"factor": 2})
    client.get(f"/recipes/{rid}/scaled", params={"factor": 2})
    assert client.get(f"/recipes/{rid}").json()["ingredients"] == ["200 g flour"]


def test_unknown_recipe_returns_404():
    r = client.get("/recipes/99999999/scaled", params={"factor": 2})
    assert r.status_code == 404
    assert r.json()["detail"] == "unknown recipe"


def test_mixed_numbers_left_unchanged_on_purpose():
    rid = make_recipe(["1 1/2 cups flour", "1 ½ cups sugar"])
    r = client.get(f"/recipes/{rid}/scaled", params={"factor": 2})
    assert r.json()["ingredients"] == ["1 1/2 cups flour", "1 ½ cups sugar"]


def test_non_ascii_digits_left_unchanged_on_purpose():
    unchanged = ["٢٠٠ g flour", "２００ g sugar"]
    rid = make_recipe(unchanged)
    r = client.get(f"/recipes/{rid}/scaled", params={"factor": 2})
    assert r.json()["ingredients"] == unchanged


def test_leading_whitespace_is_stripped_and_scaled():
    rid = make_recipe([" 200 g sugar", "\t2 eggs"])
    r = client.get(f"/recipes/{rid}/scaled", params={"factor": 2})
    assert r.json()["ingredients"] == ["400 g sugar", "4 eggs"]


def test_quantity_not_first_left_unchanged_on_purpose():
    rid = make_recipe(["flour, 200 g"])
    r = client.get(f"/recipes/{rid}/scaled", params={"factor": 2})
    assert r.json()["ingredients"] == ["flour, 200 g"]


def test_small_factor_never_rounds_to_zero():
    rid = make_recipe(["0.1 tsp salt", "2.5 kg potatoes"])
    r = client.get(f"/recipes/{rid}/scaled", params={"factor": 0.01})
    assert r.status_code == 200
    assert r.json()["ingredients"] == ["0.001 tsp salt", "0.025 kg potatoes"]


def test_largest_allowed_factor():
    rid = make_recipe(["200 g flour"])
    r = client.get(f"/recipes/{rid}/scaled", params={"factor": 1000})
    assert r.status_code == 200
    assert r.json()["ingredients"] == ["200000 g flour"]


def test_smallest_allowed_factor():
    rid = make_recipe(["200 g flour", "0.5 tsp salt"])
    r = client.get(f"/recipes/{rid}/scaled", params={"factor": 0.001})
    assert r.status_code == 200
    assert r.json()["ingredients"] == ["0.2 g flour", "0.0005 tsp salt"]


def test_scientific_notation_left_unchanged_on_purpose():
    rid = make_recipe(["1e3 g flour"])
    r = client.get(f"/recipes/{rid}/scaled", params={"factor": 2})
    assert r.json()["ingredients"] == ["1e3 g flour"]


@pytest.mark.parametrize(
    "factor",
    [
        "0", "-2", "abc", "", "nan", "inf",
        "1000.5", "1e300", "1e308", "1e309",
        "0.0009", "1e-300", "5e-324",
    ],
)
def test_bad_factor_returns_422(factor):
    rid = make_recipe(["200 g flour"])
    r = client.get(f"/recipes/{rid}/scaled", params={"factor": factor})
    assert r.status_code == 422


def test_missing_factor_returns_422():
    rid = make_recipe(["200 g flour"])
    r = client.get(f"/recipes/{rid}/scaled")
    assert r.status_code == 422


# --- parsing rule and formatting -------------------------------------------


@pytest.mark.parametrize(
    "ingredient, factor, expected",
    [
        ("200 g flour", 2, "400 g flour"),
        ("1.5kg rice", 2, "3kg rice"),
        ("2 eggs", 1.5, "3 eggs"),
        ("1 cup sugar", 1 / 3, "0.33 cup sugar"),
        ("salt", 2, "salt"),
        ("1/2 cup milk", 2, "1/2 cup milk"),
        ("2-3 eggs", 2, "2-3 eggs"),
        ("100", 2, "200"),
        ("0.1 tsp salt", 0.01, "0.001 tsp salt"),
        ("2 eggs", 0.001, "0.002 eggs"),
        ("1e3 g flour", 2, "1e3 g flour"),
        ("1E-2 kg salt", 2, "1E-2 kg salt"),
        ("2 eggs", 2, "4 eggs"),
        ("1 1/2 cups flour", 2, "1 1/2 cups flour"),
        ("1 ½ cups flour", 2, "1 ½ cups flour"),
        ("٢٠٠ g flour", 2, "٢٠٠ g flour"),
        (" 200 g sugar", 2, "400 g sugar"),
        ("flour, 200 g", 2, "flour, 200 g"),
        ("200 (7 oz) flour", 2, "200 (7 oz) flour"),
        ("1" + "0" * 300 + " g flour", 1000, "1" + "0" * 300 + " g flour"),
        ("9" * 400 + " g flour", 2, "9" * 400 + " g flour"),
    ],
)
def test_scale_ingredient(ingredient, factor, expected):
    assert scale_ingredient(ingredient, factor) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (400.0, "400"),
        (0.5, "0.5"),
        (0.75, "0.75"),
        (1 / 3, "0.33"),
        (10.0, "10"),
        (0.001, "0.001"),
        (0.00123, "0.0012"),
        (0.0, "0"),
    ],
)
def test_format_quantity(value, expected):
    assert format_quantity(value) == expected

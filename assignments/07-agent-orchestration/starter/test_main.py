import sqlite3
from contextlib import closing

import pytest
from fastapi.testclient import TestClient

import main
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    """Redirect main.DB_PATH to a fresh temporary SQLite database for each test."""
    test_db = tmp_path / "test_recipes.db"
    monkeypatch.setattr(main, "DB_PATH", test_db)
    main.init_db()
    yield test_db


# --- Original tests (preserved) ---


def test_create_and_get_recipe():
    r = client.post(
        "/recipes",
        json={"title": "Pancakes", "ingredients": ["flour", "milk"], "tags": ["breakfast"]},
    )
    assert r.status_code == 200
    rid = r.json()["id"]
    r2 = client.get(f"/recipes/{rid}")
    assert r2.status_code == 200
    assert r2.json()["title"] == "Pancakes"
    assert r2.json()["tags"] == ["breakfast"]


def test_list_recipes():
    client.post("/recipes", json={"title": "Toast"})
    r = client.get("/recipes")
    assert r.status_code == 200
    assert any(rec["title"] == "Toast" for rec in r.json())


def test_unknown_recipe_404():
    r = client.get("/recipes/99999")
    assert r.status_code == 404


# --- Finding 1: Database isolation verification ---


def test_database_isolation_does_not_modify_persistent_db():
    persistent_db_path = main.BASE / "recipes.db"
    initial_count = None
    if persistent_db_path.exists():
        with closing(sqlite3.connect(persistent_db_path)) as conn:
            initial_count = conn.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]

    client.post(
        "/recipes",
        json={"title": "Temporary Test Item", "ingredients": ["salt"], "tags": ["test"]},
    )

    if persistent_db_path.exists():
        with closing(sqlite3.connect(persistent_db_path)) as conn:
            final_count = conn.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
        assert initial_count == final_count


# --- Tag filter tests ---


def test_filter_recipes_by_matching_tag():
    r1 = client.post(
        "/recipes",
        json={"title": "Avocado Toast", "ingredients": ["bread", "avocado"], "tags": ["breakfast", "quick"]},
    )
    r2 = client.post(
        "/recipes",
        json={"title": "Tomato Pasta", "ingredients": ["pasta", "tomato"], "tags": ["dinner", "italian"]},
    )
    assert r1.status_code == 200
    assert r2.status_code == 200

    r = client.get("/recipes?tag=breakfast")
    assert r.status_code == 200
    recipes = r.json()
    assert any(rec["title"] == "Avocado Toast" for rec in recipes)
    assert not any(rec["title"] == "Tomato Pasta" for rec in recipes)
    for rec in recipes:
        assert "breakfast" in rec["tags"]


def test_filter_recipes_by_non_matching_tag():
    r = client.get("/recipes?tag=nonexistent_tag_xyz")
    assert r.status_code == 200
    assert r.json() == []


def test_list_recipes_without_tag():
    client.post(
        "/recipes",
        json={"title": "Granola Bowl", "ingredients": ["oats", "yogurt"], "tags": ["snack"]},
    )
    client.post(
        "/recipes",
        json={"title": "Plain Toast", "ingredients": ["bread"], "tags": []},
    )
    r = client.get("/recipes")
    assert r.status_code == 200
    titles = [rec["title"] for rec in r.json()]
    assert "Granola Bowl" in titles
    assert "Plain Toast" in titles


# --- Finding 2: Empty and whitespace-only tag queries ---


def test_filter_recipes_empty_tag_returns_all():
    client.post(
        "/recipes",
        json={"title": "Pancake", "ingredients": ["flour"], "tags": ["breakfast"]},
    )
    client.post(
        "/recipes",
        json={"title": "Salad", "ingredients": ["lettuce"], "tags": ["lunch"]},
    )

    r = client.get("/recipes?tag=")
    assert r.status_code == 200
    titles = [rec["title"] for rec in r.json()]
    assert "Pancake" in titles
    assert "Salad" in titles
    assert len(r.json()) == 2


def test_filter_recipes_whitespace_tag_returns_all():
    client.post(
        "/recipes",
        json={"title": "Pancake", "ingredients": ["flour"], "tags": ["breakfast"]},
    )
    client.post(
        "/recipes",
        json={"title": "Salad", "ingredients": ["lettuce"], "tags": ["lunch"]},
    )

    r = client.get("/recipes?tag=   ")
    assert r.status_code == 200
    titles = [rec["title"] for rec in r.json()]
    assert "Pancake" in titles
    assert "Salad" in titles
    assert len(r.json()) == 2


# --- Finding 3: Edge-case coverage ---


def test_filter_recipes_by_secondary_tag():
    client.post(
        "/recipes",
        json={"title": "Avocado Toast", "ingredients": ["bread", "avocado"], "tags": ["breakfast", "quick", "vegan"]},
    )
    client.post(
        "/recipes",
        json={"title": "Slow Roast", "ingredients": ["beef"], "tags": ["dinner", "slow-cook"]},
    )

    r_sec = client.get("/recipes?tag=quick")
    assert r_sec.status_code == 200
    recipes_sec = r_sec.json()
    assert len(recipes_sec) == 1
    assert recipes_sec[0]["title"] == "Avocado Toast"

    r_tri = client.get("/recipes?tag=vegan")
    assert r_tri.status_code == 200
    recipes_tri = r_tri.json()
    assert len(recipes_tri) == 1
    assert recipes_tri[0]["title"] == "Avocado Toast"


def test_filter_recipes_excludes_recipes_with_empty_tags():
    client.post(
        "/recipes",
        json={"title": "Plain Bread", "ingredients": ["flour", "water"], "tags": []},
    )
    client.post(
        "/recipes",
        json={"title": "Eggs Benedict", "ingredients": ["egg", "muffin"], "tags": ["breakfast"]},
    )

    r = client.get("/recipes?tag=breakfast")
    assert r.status_code == 200
    recipes = r.json()
    assert len(recipes) == 1
    assert recipes[0]["title"] == "Eggs Benedict"
    assert not any(rec["title"] == "Plain Bread" for rec in recipes)


def test_filter_recipes_exact_tag_matching_preserved():
    client.post(
        "/recipes",
        json={"title": "Pancakes", "ingredients": ["flour"], "tags": ["breakfast"]},
    )

    # Substring suffix should not match
    r_suffix = client.get("/recipes?tag=fast")
    assert r_suffix.status_code == 200
    assert r_suffix.json() == []

    # Substring prefix should not match
    r_prefix = client.get("/recipes?tag=break")
    assert r_prefix.status_code == 200
    assert r_prefix.json() == []

    # Plural should not match
    r_plural = client.get("/recipes?tag=breakfasts")
    assert r_plural.status_code == 200
    assert r_plural.json() == []

    # Exact match matches
    r_exact = client.get("/recipes?tag=breakfast")
    assert r_exact.status_code == 200
    assert len(r_exact.json()) == 1
    assert r_exact.json()[0]["title"] == "Pancakes"


# --- Revision Round 2: SQL filtering and edge-case regression tests ---


def test_filter_recipes_with_duplicate_tags_in_recipe():
    client.post(
        "/recipes",
        json={
            "title": "Double Tagged Muffin",
            "ingredients": ["flour", "sugar"],
            "tags": ["quick", "quick", "snack"],
        },
    )
    r = client.get("/recipes?tag=quick")
    assert r.status_code == 200
    recipes = r.json()
    assert len(recipes) == 1
    assert recipes[0]["title"] == "Double Tagged Muffin"


def test_filter_recipes_with_special_characters_in_tag():
    client.post(
        "/recipes",
        json={
            "title": "Special Diet Bowl",
            "ingredients": ["quinoa", "kale"],
            "tags": [
                "gluten-free & vegan (quick!)",
                "tag/with/slashes",
                "quotes'\"test",
                "#healthy-eats!",
            ],
        },
    )
    client.post(
        "/recipes",
        json={
            "title": "Standard Bowl",
            "ingredients": ["rice"],
            "tags": ["vegan", "regular"],
        },
    )

    # Tag with spaces, ampersand, and parentheses
    r1 = client.get("/recipes", params={"tag": "gluten-free & vegan (quick!)"})
    assert r1.status_code == 200
    assert len(r1.json()) == 1
    assert r1.json()[0]["title"] == "Special Diet Bowl"

    # Tag with slashes
    r2 = client.get("/recipes", params={"tag": "tag/with/slashes"})
    assert r2.status_code == 200
    assert len(r2.json()) == 1
    assert r2.json()[0]["title"] == "Special Diet Bowl"

    # Tag with single and double quotes
    r3 = client.get("/recipes", params={"tag": "quotes'\"test"})
    assert r3.status_code == 200
    assert len(r3.json()) == 1
    assert r3.json()[0]["title"] == "Special Diet Bowl"

    # Tag with hashtag and exclamation
    r4 = client.get("/recipes", params={"tag": "#healthy-eats!"})
    assert r4.status_code == 200
    assert len(r4.json()) == 1
    assert r4.json()[0]["title"] == "Special Diet Bowl"


def test_filter_recipes_preserves_id_ordering():
    r1 = client.post("/recipes", json={"title": "First", "tags": ["lunch"]})
    r2 = client.post("/recipes", json={"title": "Second", "tags": ["dinner"]})
    r3 = client.post("/recipes", json={"title": "Third", "tags": ["lunch"]})
    r4 = client.post("/recipes", json={"title": "Fourth", "tags": ["lunch"]})

    r = client.get("/recipes?tag=lunch")
    assert r.status_code == 200
    ids = [rec["id"] for rec in r.json()]
    assert ids == [r1.json()["id"], r3.json()["id"], r4.json()["id"]]
    assert ids == sorted(ids)
def test_shopping_list_multiple_recipes():
    r1 = client.post(
        "/recipes",
        json={"title": "Pasta", "ingredients": ["pasta", "tomato sauce", "garlic"]},
    )
    r2 = client.post(
        "/recipes",
        json={"title": "Salad", "ingredients": ["lettuce", "cucumber", "olive oil"]},
    )
    id1 = r1.json()["id"]
    id2 = r2.json()["id"]

    resp = client.get(f"/shopping-list?ids={id1},{id2}")
    assert resp.status_code == 200
    items = resp.json()
    assert items == ["pasta", "tomato sauce", "garlic", "lettuce", "cucumber", "olive oil"]


def test_shopping_list_duplicate_ingredients():
    # Duplicate ingredients across recipes and within the same recipe
    r1 = client.post(
        "/recipes",
        json={"title": "Cake", "ingredients": ["flour", "sugar", "eggs", "butter", "flour"]},
    )
    r2 = client.post(
        "/recipes",
        json={"title": "Cookies", "ingredients": ["flour", "butter", "chocolate chips", "sugar"]},
    )
    id1 = r1.json()["id"]
    id2 = r2.json()["id"]

    resp = client.get(f"/shopping-list?ids={id1},{id2}")
    assert resp.status_code == 200
    items = resp.json()
    assert items == ["flour", "sugar", "eggs", "butter", "chocolate chips"]
    assert len(items) == len(set(items))


def test_shopping_list_case_insensitive_deduplication():
    r1 = client.post(
        "/recipes",
        json={"title": "Morning Oats", "ingredients": ["Oats", "Milk", "Honey"]},
    )
    r2 = client.post(
        "/recipes",
        json={"title": "Smoothie", "ingredients": ["milk", "banana", "HONEY"]},
    )
    id1 = r1.json()["id"]
    id2 = r2.json()["id"]

    resp = client.get(f"/shopping-list?ids={id1},{id2}")
    assert resp.status_code == 200
    items = resp.json()
    assert items == ["Oats", "Milk", "Honey", "banana"]


def test_shopping_list_invalid_recipe_ids():
    # Non-integer ID
    r = client.get("/shopping-list?ids=abc")
    assert r.status_code == 400

    # Mixed valid and non-integer ID
    r = client.get("/shopping-list?ids=1,abc,2")
    assert r.status_code == 400

    # Negative ID
    r = client.get("/shopping-list?ids=-1")
    assert r.status_code == 400

    # Zero ID
    r = client.get("/shopping-list?ids=0")
    assert r.status_code == 400

    # Empty string ID between commas
    r = client.get("/shopping-list?ids=1,,2")
    assert r.status_code == 400

    # Empty query parameter
    r = client.get("/shopping-list?ids=")
    assert r.status_code == 400


def test_shopping_list_missing_recipe_ids():
    # Missing query parameter entirely
    r = client.get("/shopping-list")
    assert r.status_code == 400

    # Non-existent ID (missing from database)
    r = client.get("/shopping-list?ids=99999")
    assert r.status_code == 404

    # Combination of valid and non-existent IDs
    r_valid = client.post("/recipes", json={"title": "Bread", "ingredients": ["flour", "water", "yeast"]})
    valid_id = r_valid.json()["id"]

    r_mixed = client.get(f"/shopping-list?ids={valid_id},99999")
    assert r_mixed.status_code == 404


def test_shopping_list_duplicate_ids_in_query():
    r = client.post(
        "/recipes",
        json={"title": "Tea", "ingredients": ["water", "tea leaves"]},
    )
    rid = r.json()["id"]

    resp = client.get(f"/shopping-list?ids={rid},{rid}")
    assert resp.status_code == 200
    assert resp.json() == ["water", "tea leaves"]


def test_shopping_list_whitespace_handling():
    r1 = client.post(
        "/recipes",
        json={"title": "Rice", "ingredients": ["rice", "water"]},
    )
    r2 = client.post(
        "/recipes",
        json={"title": "Beans", "ingredients": ["beans", "salt"]},
    )
    id1 = r1.json()["id"]
    id2 = r2.json()["id"]

    resp = client.get(f"/shopping-list?ids= {id1} , {id2} ")
    assert resp.status_code == 200
    assert resp.json() == ["rice", "water", "beans", "salt"]


def test_shopping_list_empty_ingredients():
    r = client.post(
        "/recipes",
        json={"title": "Empty Recipe", "ingredients": []},
    )
    rid = r.json()["id"]

    resp = client.get(f"/shopping-list?ids={rid}")
    assert resp.status_code == 200
    assert resp.json() == []

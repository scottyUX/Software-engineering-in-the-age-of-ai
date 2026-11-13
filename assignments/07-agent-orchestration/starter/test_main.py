from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


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


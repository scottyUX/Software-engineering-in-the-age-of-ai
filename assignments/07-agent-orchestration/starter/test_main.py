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


def test_shopping_list_merges_and_deduplicates():
    r1 = client.post(
        "/recipes",
        json={"title": "Cake", "ingredients": ["Flour", "Sugar", "Eggs"]},
    )
    r2 = client.post(
        "/recipes",
        json={"title": "Cookies", "ingredients": ["flour", "Butter", "Sugar", "Chocolate"]},
    )
    id1, id2 = r1.json()["id"], r2.json()["id"]

    res = client.get(f"/shopping-list?ids={id1},{id2}")
    assert res.status_code == 200
    items = res.json()["items"]
    # Should deduplicate case-insensitively ("Flour" and "flour" -> 1 entry)
    lower_items = [i.lower() for i in items]
    assert len(lower_items) == len(set(lower_items))
    assert "flour" in lower_items
    assert "sugar" in lower_items
    assert "eggs" in lower_items
    assert "butter" in lower_items
    assert "chocolate" in lower_items


def test_shopping_list_invalid_ids():
    res = client.get("/shopping-list?ids=1,abc,3")
    assert res.status_code == 400

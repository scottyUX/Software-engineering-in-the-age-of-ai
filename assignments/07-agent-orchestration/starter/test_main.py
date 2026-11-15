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


def test_filter_recipes_by_tag():
    client.post(
        "/recipes",
        json={"title": "Omelette", "ingredients": ["eggs"], "tags": ["breakfast", "quick"]},
    )
    client.post(
        "/recipes",
        json={"title": "Spaghetti", "ingredients": ["pasta"], "tags": ["dinner", "italian"]},
    )

    # Filter breakfast
    r_breakfast = client.get("/recipes?tag=breakfast")
    assert r_breakfast.status_code == 200
    titles = [rec["title"] for rec in r_breakfast.json()]
    assert "Omelette" in titles
    assert "Spaghetti" not in titles

    # Filter italian
    r_italian = client.get("/recipes?tag=italian")
    assert r_italian.status_code == 200
    titles_it = [rec["title"] for rec in r_italian.json()]
    assert "Spaghetti" in titles_it
    assert "Omelette" not in titles_it

    # Filter nonexistent tag
    r_none = client.get("/recipes?tag=nonexistenttag99")
    assert r_none.status_code == 200
    assert len(r_none.json()) == 0

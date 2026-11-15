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


# --- Concurrent Agent A: Shopping List Tests ---
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
    lower_items = [i.lower() for i in items]
    assert len(lower_items) == len(set(lower_items))
    assert "flour" in lower_items
    assert "sugar" in lower_items
    assert "eggs" in lower_items


def test_shopping_list_invalid_ids():
    res = client.get("/shopping-list?ids=1,abc,3")
    assert res.status_code == 400


# --- Concurrent Agent B: Tag Filter Tests ---
def test_filter_recipes_by_tag():
    client.post(
        "/recipes",
        json={"title": "Omelette", "ingredients": ["eggs"], "tags": ["breakfast", "quick"]},
    )
    client.post(
        "/recipes",
        json={"title": "Spaghetti", "ingredients": ["pasta"], "tags": ["dinner", "italian"]},
    )

    r_breakfast = client.get("/recipes?tag=breakfast")
    assert r_breakfast.status_code == 200
    titles = [rec["title"] for rec in r_breakfast.json()]
    assert "Omelette" in titles
    assert "Spaghetti" not in titles


# --- Part II: Generator-Critic Loop Feature Tests (Ingredient Scaling) ---
def test_scale_ingredients():
    r = client.post(
        "/recipes",
        json={
            "title": "Waffles",
            "ingredients": ["200 g flour", "2 eggs", "1.5 cup milk", "pinch of salt"],
            "tags": ["breakfast"],
        },
    )
    rid = r.json()["id"]

    res = client.get(f"/recipes/{rid}/scaled?factor=2")
    assert res.status_code == 200
    data = res.json()
    assert data["scale_factor"] == 2
    assert "400 g flour" in data["ingredients"]
    assert "4 eggs" in data["ingredients"]
    assert "3 cup milk" in data["ingredients"]
    assert "pinch of salt" in data["ingredients"]


def test_scale_ingredients_invalid_factor():
    r = client.post("/recipes", json={"title": "Tea", "ingredients": ["1 teabag"]})
    rid = r.json()["id"]
    res = client.get(f"/recipes/{rid}/scaled?factor=-1")
    assert res.status_code == 422  # pydantic/fastapi validation error gt=0

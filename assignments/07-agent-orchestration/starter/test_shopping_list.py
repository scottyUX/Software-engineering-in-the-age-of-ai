from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def _make(title, ingredients):
    r = client.post("/recipes", json={"title": title, "ingredients": ingredients})
    assert r.status_code == 200
    return r.json()["id"]


def test_merges_and_dedupes_in_order():
    a = _make("A", ["flour", "milk", "eggs"])
    b = _make("B", ["eggs", "sugar", "flour"])
    r = client.get(f"/shopping-list?ids={a},{b}")
    assert r.status_code == 200
    body = r.json()
    assert body["recipe_ids"] == [a, b]
    assert body["ingredients"] == ["flour", "milk", "eggs", "sugar"]
    assert body["count"] == 4


def test_order_follows_requested_ids():
    a = _make("A", ["flour"])
    b = _make("B", ["salt"])
    r = client.get(f"/shopping-list?ids={b},{a}")
    assert r.json()["ingredients"] == ["salt", "flour"]


def test_case_and_whitespace_insensitive_keeps_first_spelling():
    a = _make("A", ["  Olive   Oil ", "Salt"])
    b = _make("B", ["olive oil", "SALT", "salt  "])
    r = client.get(f"/shopping-list?ids={a},{b}")
    assert r.json()["ingredients"] == ["Olive Oil", "Salt"]


def test_blank_ingredients_dropped():
    a = _make("A", ["", "   ", "rice"])
    r = client.get(f"/shopping-list?ids={a}")
    assert r.json()["ingredients"] == ["rice"]


def test_recipe_without_ingredients():
    a = _make("Empty", [])
    r = client.get(f"/shopping-list?ids={a}")
    assert r.status_code == 200
    assert r.json() == {"recipe_ids": [a], "ingredients": [], "count": 0}


def test_duplicate_ids_counted_once():
    a = _make("A", ["flour"])
    r = client.get(f"/shopping-list?ids={a},{a}, {a}")
    assert r.status_code == 200
    assert r.json()["recipe_ids"] == [a]
    assert r.json()["ingredients"] == ["flour"]


def test_unknown_id_404_names_missing():
    a = _make("A", ["flour"])
    missing = a + 100000
    r = client.get(f"/shopping-list?ids={a},{missing}")
    assert r.status_code == 404
    assert str(missing) in r.json()["detail"]


def test_missing_or_empty_ids_400():
    for url in ["/shopping-list", "/shopping-list?ids=", "/shopping-list?ids=%20"]:
        r = client.get(url)
        assert r.status_code == 400, url
        assert "ids" in r.json()["detail"]


def test_malformed_ids_400():
    a = _make("A", ["flour"])
    for bad in ["abc", f"{a},x", f"{a},,{a}", f"{a},", "-1", "0", "1.5", f"{a};{a}", "²", "١"]:
        r = client.get("/shopping-list", params={"ids": bad})
        assert r.status_code == 400, bad
        assert "invalid recipe id" in r.json()["detail"]

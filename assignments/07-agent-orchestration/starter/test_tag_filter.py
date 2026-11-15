"""Tests for GET /recipes?tag=... (task 2: tag filter).

Every test creates its own recipes with tags made unique by a uuid, and only
asserts on those recipes, so results do not depend on ids or rows from other tests.
"""
import uuid

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def _uniq(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


def _create(title: str, tags: list[str]) -> int:
    r = client.post("/recipes", json={"title": title, "ingredients": [], "tags": tags})
    assert r.status_code == 200
    return r.json()["id"]


def _ids(params: dict | None = None) -> list[int]:
    r = client.get("/recipes", params=params)
    assert r.status_code == 200
    return [rec["id"] for rec in r.json()]


def test_filter_returns_only_recipes_with_tag():
    tag = _uniq("breakfast")
    other = _uniq("dinner")
    a = _create("Pancakes", [tag])
    b = _create("Omelette", [other, tag])
    c = _create("Steak", [other])

    r = client.get("/recipes", params={"tag": tag})
    assert r.status_code == 200
    body = r.json()
    assert [rec["id"] for rec in body] == [a, b]  # ordered by id, like the unfiltered list
    assert all(tag in rec["tags"] for rec in body)
    assert c not in [rec["id"] for rec in body]


def test_filtered_items_have_same_shape_as_unfiltered():
    tag = _uniq("shape")
    rid = _create("Porridge", [tag])
    filtered = client.get("/recipes", params={"tag": tag}).json()
    unfiltered = [rec for rec in client.get("/recipes").json() if rec["id"] == rid]
    assert filtered == unfiltered


def test_no_match_returns_empty_list():
    _create("Something", [_uniq("present")])
    r = client.get("/recipes", params={"tag": _uniq("absent")})
    assert r.status_code == 200
    assert r.json() == []


def test_without_tag_returns_all_recipes_as_before():
    a = _create("Untagged", [])
    b = _create("Tagged", [_uniq("x")])
    ids = _ids()
    assert a in ids and b in ids
    assert ids == sorted(ids)


def test_empty_or_whitespace_tag_means_no_filter():
    a = _create("Untagged", [])
    b = _create("Tagged", [_uniq("y")])
    for value in ["", "   "]:
        ids = _ids({"tag": value})
        assert a in ids and b in ids
    assert _ids({"tag": ""}) == _ids()


def test_match_is_case_insensitive():
    base = _uniq("brunch")
    rid = _create("Mixed case", [base.upper()])
    assert rid in _ids({"tag": base.lower()})
    assert rid in _ids({"tag": base.title()})


def test_surrounding_whitespace_is_ignored():
    base = _uniq("lunch")
    stored_padded = _create("Padded stored", [f"  {base} "])
    stored_clean = _create("Clean stored", [base])
    ids = _ids({"tag": f"  {base}  "})
    assert stored_padded in ids and stored_clean in ids


def test_substring_of_another_tag_does_not_match():
    base = _uniq("break")
    longer = _create("Longer tag", [f"{base}fast"])
    exact = _create("Exact tag", [base])
    assert _ids({"tag": base}) == [exact]
    assert _ids({"tag": f"{base}fast"}) == [longer]
    # a prefix of the stored tag matches nothing
    assert _ids({"tag": base[:-2]}) == []

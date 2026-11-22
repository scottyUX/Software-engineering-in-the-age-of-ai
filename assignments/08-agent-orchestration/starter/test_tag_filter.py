"""Tests for GET /recipes?tag=... (Task 2: tag filter)."""

import uuid

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def _uniq(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def test_tag_filter_returns_only_matching():
    tag1 = _uniq("breakfast")
    tag2 = _uniq("dinner")
    r1 = client.post("/recipes", json={"title": "Eggs", "tags": [tag1]})
    r2 = client.post("/recipes", json={"title": "Steak", "tags": [tag2]})
    assert r1.status_code == 200 and r2.status_code == 200

    res = client.get(f"/recipes?tag={tag1}")
    assert res.status_code == 200
    titles = [rec["title"] for rec in res.json()]
    assert "Eggs" in titles
    assert "Steak" not in titles


def test_tag_filter_case_insensitive_and_whitespace():
    tag = _uniq("Dessert")
    client.post("/recipes", json={"title": "Cake", "tags": [f"  {tag.upper()}  "]})

    res = client.get(f"/recipes?tag={tag.lower()}")
    assert res.status_code == 200
    titles = [rec["title"] for rec in res.json()]
    assert "Cake" in titles


def test_tag_filter_no_substring_matching():
    prefix = _uniq("quick")
    exact = prefix
    superset = f"{prefix}-snack"
    client.post("/recipes", json={"title": "A", "tags": [exact]})
    client.post("/recipes", json={"title": "B", "tags": [superset]})

    res = client.get(f"/recipes?tag={exact}")
    assert res.status_code == 200
    titles = [rec["title"] for rec in res.json()]
    assert "A" in titles
    assert "B" not in titles


def test_tag_filter_empty_or_whitespace_returns_all():
    client.post("/recipes", json={"title": "Sample"})
    all_res = client.get("/recipes").json()
    empty_tag_res = client.get("/recipes?tag=").json()
    ws_tag_res = client.get("/recipes?tag=%20").json()

    assert len(all_res) == len(empty_tag_res)
    assert len(all_res) == len(ws_tag_res)

import pytest
from fastapi.testclient import TestClient

import main
from main import app

client = TestClient(app)


def test_shorten_and_redirect():
    r = client.post("/shorten", json={"url": "https://example.com"})
    assert r.status_code == 200
    code = r.json()["code"]
    assert code
    r2 = client.get(f"/{code}", follow_redirects=False)
    assert r2.status_code == 307
    assert r2.headers["location"] == "https://example.com"


def test_rejects_bad_url():
    r = client.post("/shorten", json={"url": "ftp://nope"})
    assert r.status_code == 400


def test_unknown_code_404():
    r = client.get("/does-not-exist", follow_redirects=False)
    assert r.status_code == 404


# --- Task 1: custom alias -------------------------------------------------


def test_alias_used_as_code_and_redirects():
    r = client.post("/shorten", json={"url": "https://example.com/a", "alias": "my-link"})
    assert r.status_code == 200
    assert r.json() == {"code": "my-link", "short_url": "/my-link"}
    r2 = client.get("/my-link", follow_redirects=False)
    assert r2.status_code == 307
    assert r2.headers["location"] == "https://example.com/a"


def test_alias_taken_returns_409_and_keeps_original():
    client.post("/shorten", json={"url": "https://first.example", "alias": "taken"})
    r = client.post("/shorten", json={"url": "https://second.example", "alias": "taken"})
    assert r.status_code == 409
    r2 = client.get("/taken", follow_redirects=False)
    assert r2.headers["location"] == "https://first.example"


def test_alias_with_bad_url_is_still_rejected():
    r = client.post("/shorten", json={"url": "ftp://nope", "alias": "valid-alias"})
    assert r.status_code == 400


@pytest.mark.parametrize("alias", ["", "ab", "x" * 33, "has/slash", "has space", "query?x=1", "docs", "Docs"])
def test_alias_invalid_returns_400(alias):
    r = client.post("/shorten", json={"url": "https://example.com", "alias": alias})
    assert r.status_code == 400


def test_generated_code_skips_existing_alias(monkeypatch):
    # Patch encode() only to make the next generated code predictable;
    # the assertions below stay on HTTP behavior.
    monkeypatch.setattr(main, "encode", lambda n: f"code{n}")
    client.post("/shorten", json={"url": "https://alias.example", "alias": "code2"})
    r = client.post("/shorten", json={"url": "https://auto.example"})
    assert r.status_code == 200
    code = r.json()["code"]
    assert code != "code2"
    assert client.get(f"/{code}", follow_redirects=False).headers["location"] == "https://auto.example"
    assert client.get("/code2", follow_redirects=False).headers["location"] == "https://alias.example"

import uuid
from fastapi.testclient import TestClient

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


def test_shorten_with_custom_alias():
    alias = uuid.uuid4().hex
    r = client.post("/shorten", json={"url": "https://example.com", "alias": alias})
    assert r.status_code == 200
    assert r.json()["code"] == alias
    assert r.json()["short_url"] == f"/{alias}"
    r2 = client.get(f"/{alias}", follow_redirects=False)
    assert r2.status_code == 307
    assert r2.headers["location"] == "https://example.com"


def test_custom_alias_conflict_returns_409():
    alias = uuid.uuid4().hex
    r1 = client.post("/shorten", json={"url": "https://example.com", "alias": alias})
    assert r1.status_code == 200
    r2 = client.post("/shorten", json={"url": "https://other.com", "alias": alias})
    assert r2.status_code == 409


def test_custom_alias_invalid_returns_400():
    for invalid_alias in ["", "a/b", "has space", "a" * 33, "abc\n"]:
        r = client.post("/shorten", json={"url": "https://example.com", "alias": invalid_alias})
        assert r.status_code == 400


def test_custom_alias_reserved_returns_409():
    for reserved in ["shorten", "docs", "redoc", "openapi.json"]:
        r = client.post("/shorten", json={"url": "https://example.com", "alias": reserved})
        assert r.status_code == 409


def test_generated_code_collision_with_alias(tmp_path, monkeypatch):
    # Regression test for F3: alias claims a future generated code (e.g. encode(2)).
    db_file = tmp_path / "links.db"
    monkeypatch.setattr("main.DB_PATH", db_file)
    from main import init_db, encode
    init_db()

    # row_id 2 will generate encode(2). Let's claim encode(2) as an alias first (row_id 1).
    target_code = encode(2)
    r1 = client.post("/shorten", json={"url": "https://example.com", "alias": target_code})
    assert r1.status_code == 200

    # Now shorten without alias.
    # row_id 1 is taken by alias. Next insert gets row_id 2, which would generate encode(2).
    # But encode(2) is already taken by row_id 1. With collision handling, it should retry and succeed.
    r2 = client.post("/shorten", json={"url": "https://example.org"})
    assert r2.status_code == 200
    data = r2.json()
    assert data["code"] != target_code

    # Verify redirection works for both
    r3 = client.get(f"/{target_code}", follow_redirects=False)
    assert r3.status_code == 307
    assert r3.headers["location"] == "https://example.com"

    r4 = client.get(f"/{data['code']}", follow_redirects=False)
    assert r4.status_code == 307
    assert r4.headers["location"] == "https://example.org"



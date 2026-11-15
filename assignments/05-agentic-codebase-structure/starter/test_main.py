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


def test_custom_alias_success():
    alias = "my-custom-doc"
    r = client.post("/shorten", json={"url": "https://docs.python.org", "alias": alias})
    assert r.status_code == 200
    assert r.json()["code"] == alias
    r2 = client.get(f"/{alias}", follow_redirects=False)
    assert r2.status_code == 307
    assert r2.headers["location"] == "https://docs.python.org"


def test_custom_alias_collision_409():
    alias = "duplicate-alias"
    r1 = client.post("/shorten", json={"url": "https://first.com", "alias": alias})
    assert r1.status_code == 200

    # Second attempt with same alias must return 409 Conflict
    r2 = client.post("/shorten", json={"url": "https://second.com", "alias": alias})
    assert r2.status_code == 409
    assert "already in use" in r2.json()["detail"].lower()

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

def test_create_short_url_custom_slug_success():
    response = client.post("/shorten", json={"url": "https://example.com", "custom_slug": "my-custom-link"})
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "my-custom-link"

def test_create_short_url_custom_slug_conflict():
    client.post("/shorten", json={"url": "https://example.com", "custom_slug": "taken-slug"})
    response = client.post("/shorten", json={"url": "https://another.com", "custom_slug": "taken-slug"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Custom slug already in use"
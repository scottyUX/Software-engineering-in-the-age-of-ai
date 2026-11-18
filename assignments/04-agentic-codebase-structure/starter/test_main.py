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


def test_custom_alias_conflict():
    """Edge Case: Test that providing an already taken alias returns 409."""
    # Create the first alias
    client.post("/shorten", json={"url": "https://first.com", "alias": "taken"})
    
    # Try to use the same alias again
    response = client.post(
        "/shorten", 
        json={"url": "https://second.com", "alias": "taken"}
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Alias already in use"

def test_custom_alias_invalid_url():
    """Edge Case: Test that a bad URL is rejected even if an alias is provided."""
    response = client.post(
        "/shorten", 
        json={"url": "ftp://invalid-url.com", "alias": "bad-url-test"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "url must start with http:// or https://"



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


def shorten(url):
    return client.post("/shorten", json={"url": url}).json()["code"]


def test_stats_new_link_has_zero_clicks():
    code = shorten("https://example.com/stats-new")
    r = client.get(f"/stats/{code}")
    assert r.status_code == 200
    assert r.json() == {"url": "https://example.com/stats-new", "clicks": 0}


def test_stats_counts_each_redirect():
    code = shorten("https://example.com/stats-count")
    client.get(f"/{code}", follow_redirects=False)
    client.get(f"/{code}", follow_redirects=False)
    assert client.get(f"/stats/{code}").json()["clicks"] == 2


def test_stats_counts_only_its_own_link():
    code = shorten("https://example.com/stats-own")
    other = shorten("https://example.com/stats-other")
    client.get(f"/{other}", follow_redirects=False)
    assert client.get(f"/stats/{code}").json()["clicks"] == 0


def test_stats_does_not_count_as_click():
    code = shorten("https://example.com/stats-view")
    client.get(f"/stats/{code}")
    client.get(f"/stats/{code}")
    assert client.get(f"/stats/{code}").json()["clicks"] == 0


def test_stats_unknown_code_returns_404():
    r = client.get("/stats/does-not-exist")
    assert r.status_code == 404
    assert r.json() == {"detail": "unknown code"}

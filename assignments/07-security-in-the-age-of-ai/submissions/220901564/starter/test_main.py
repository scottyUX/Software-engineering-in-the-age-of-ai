from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

import main
from main import app

client = TestClient(app)


def test_search_books():
    r = client.get("/books", params={"q": "Python"})
    assert r.status_code == 200
    assert any("Python" in b["title"] for b in r.json())


def test_get_book():
    r = client.get("/books/1")
    assert r.status_code == 200
    assert "title" in r.json()


def test_search_with_apostrophe():
    response = client.get("/books", params={"q": "Reader's Guide"})
    assert response.status_code == 200
    assert response.json() == []


def test_add_and_list_reviews():
    client.post("/reviews", json={"book_id": 1, "text": "Great read"})
    r = client.get("/reviews/1")
    assert r.status_code == 200
    assert "Great read" in r.json()


@pytest.mark.parametrize(
    ("model_output", "status", "result"),
    [
        ('{"index": 1}', 200, {"summary": "The examples are clear."}),
        ("Unexpected model output", 502, {"detail": "Invalid summary selection"}),
        ('{"index": 2}', 502, {"detail": "Invalid summary selection"}),
        ('{"index": true}', 502, {"detail": "Invalid summary selection"}),
        ('{"index": 0, "text": "Extra"}', 502, {"detail": "Invalid summary selection"}),
    ],
)
def test_summary_model_output(monkeypatch, model_output, status, result):
    model_response = Mock()
    model_response.json.return_value = {"response": model_output}
    monkeypatch.setattr(main.requests, "post", Mock(return_value=model_response))

    response = client.post(
        "/summarize-review", json={"text": "I read this book. The examples are clear."}
    )

    assert response.status_code == status
    assert response.json() == result

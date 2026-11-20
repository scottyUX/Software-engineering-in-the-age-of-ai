import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_create_and_list_habit():
    r = client.post("/habits", json={"name": "Read 20 minutes"})
    assert r.status_code == 200
    hid = r.json()["id"]
    r2 = client.get("/habits")
    assert r2.status_code == 200
    assert any(h["id"] == hid for h in r2.json())


def test_checkin_flow():
    hid = client.post("/habits", json={"name": "Stretch"}).json()["id"]
    r = client.post(f"/habits/{hid}/checkin", json={"day": "2026-09-22"})
    assert r.status_code == 200
    r2 = client.get(f"/habits/{hid}/checkins")
    assert r2.json() == ["2026-09-22"]


def test_checkin_unknown_habit_404():
    r = client.post("/habits/99999/checkin", json={"day": "2026-09-22"})
    assert r.status_code == 404


def error_messages(response):
    return " ".join(error["msg"] for error in response.json()["detail"])


@pytest.mark.parametrize(
    "name", ["", "   ", "\t\n", "\u00a0", "\u200b", "\x00", "\ufe0f", "\u0301"]
)
def test_blank_habit_name_is_rejected(name):
    r = client.post("/habits", json={"name": name})
    assert r.status_code == 422
    assert "name must not be empty" in error_messages(r)


@pytest.mark.parametrize("name", ["日本語", "Oku 📚", "📚", "❤️", "é"])
def test_visible_names_are_accepted(name):
    r = client.post("/habits", json={"name": name})
    assert r.status_code == 200
    assert r.json()["name"] == name


def test_habit_name_is_stored_trimmed():
    r = client.post("/habits", json={"name": "  Read  "})
    assert r.status_code == 200
    assert r.json()["name"] == "Read"


@pytest.mark.parametrize(
    "day",
    ["", "hello", "2026/09/22", "22-09-2026", "2026-13-01", "2026-02-30", "20260922", "2026-W39-2"],
)
def test_malformed_day_is_rejected_and_not_stored(day):
    hid = client.post("/habits", json={"name": "Stretch"}).json()["id"]
    r = client.post(f"/habits/{hid}/checkin", json={"day": day})
    assert r.status_code == 422
    assert "YYYY-MM-DD" in error_messages(r)
    assert client.get(f"/habits/{hid}/checkins").json() == []


def test_leap_day_is_accepted():
    hid = client.post("/habits", json={"name": "Stretch"}).json()["id"]
    r = client.post(f"/habits/{hid}/checkin", json={"day": "2024-02-29"})
    assert r.status_code == 200
    assert r.json()["day"] == "2024-02-29"


def test_malformed_day_on_unknown_habit_is_still_a_validation_error():
    r = client.post("/habits/99999/checkin", json={"day": "hello"})
    assert r.status_code == 422

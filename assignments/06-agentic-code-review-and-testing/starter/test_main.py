from datetime import date, timedelta

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


# --- Feature 1: Validation Tests ---
def test_validation_rejects_empty_habit_name():
    r = client.post("/habits", json={"name": "   "})
    assert r.status_code == 400
    assert "empty" in r.json()["detail"].lower()


def test_validation_rejects_malformed_day_checkin():
    hid = client.post("/habits", json={"name": "Drink Water"}).json()["id"]
    r = client.post(f"/habits/{hid}/checkin", json={"day": "not-a-date"})
    assert r.status_code == 400
    assert "malformed" in r.json()["detail"].lower()


# --- Feature 2: Streak Tests ---
def test_streak_calculation():
    hid = client.post("/habits", json={"name": "Meditation"}).json()["id"]
    today = date.today()

    # Initial streak is 0
    r0 = client.get(f"/habits/{hid}/streak")
    assert r0.status_code == 200
    assert r0.json()["streak"] == 0

    # Checkin today and yesterday -> streak = 2
    client.post(
        f"/habits/{hid}/checkin", json={"day": (today - timedelta(days=1)).isoformat()}
    )
    client.post(f"/habits/{hid}/checkin", json={"day": today.isoformat()})

    r = client.get(f"/habits/{hid}/streak")
    assert r.status_code == 200
    assert r.json()["streak"] == 2


def test_streak_unknown_habit_404():
    r = client.get("/habits/88888/streak")
    assert r.status_code == 404


# --- Feature 3: Summary Tests ---
def test_weekly_summary():
    hid = client.post("/habits", json={"name": "Workout"}).json()["id"]
    today = date.today()
    client.post(f"/habits/{hid}/checkin", json={"day": today.isoformat()})
    client.post(
        f"/habits/{hid}/checkin", json={"day": (today - timedelta(days=2)).isoformat()}
    )
    r = client.get(f"/habits/{hid}/summary")
    assert r.status_code == 200
    assert r.json()["last_7_days_checkins"] == 2

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


# --- Streak Tests ---


def test_streak_empty_habit():
    hid = client.post("/habits", json={"name": "Meditation"}).json()["id"]
    r = client.get(f"/habits/{hid}/streak")
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "streak": 0}


def test_streak_checked_in_today_and_yesterday():
    today = date.today()
    yesterday = today - timedelta(days=1)
    hid = client.post("/habits", json={"name": "Coding"}).json()["id"]
    client.post(f"/habits/{hid}/checkin", json={"day": yesterday.isoformat()})
    client.post(f"/habits/{hid}/checkin", json={"day": today.isoformat()})

    r = client.get(f"/habits/{hid}/streak")
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "streak": 2}


def test_streak_alive_from_yesterday():
    yesterday = date.today() - timedelta(days=1)
    hid = client.post("/habits", json={"name": "Journaling"}).json()["id"]
    client.post(f"/habits/{hid}/checkin", json={"day": yesterday.isoformat()})

    r = client.get(f"/habits/{hid}/streak")
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "streak": 1}


def test_streak_broken():
    two_days_ago = date.today() - timedelta(days=2)
    hid = client.post("/habits", json={"name": "Guitar"}).json()["id"]
    client.post(f"/habits/{hid}/checkin", json={"day": two_days_ago.isoformat()})

    r = client.get(f"/habits/{hid}/streak")
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "streak": 0}


def test_streak_deduplicates_same_day():
    today = date.today()
    hid = client.post("/habits", json={"name": "Hydrate"}).json()["id"]
    client.post(f"/habits/{hid}/checkin", json={"day": today.isoformat()})
    client.post(f"/habits/{hid}/checkin", json={"day": today.isoformat()})

    r = client.get(f"/habits/{hid}/streak")
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "streak": 1}


def test_streak_unknown_habit_404():
    r = client.get("/habits/99999/streak")
    assert r.status_code == 404
    assert r.json()["detail"] == "unknown habit"

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


# --- Weekly Summary Tests ---


def test_weekly_summary_empty():
    hid = client.post("/habits", json={"name": "Reading"}).json()["id"]
    r = client.get(f"/habits/{hid}/summary")
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "checkins_last_7_days": 0}


def test_weekly_summary_within_last_7_days():
    today = date.today()
    day3 = today - timedelta(days=3)
    day6 = today - timedelta(days=6)
    hid = client.post("/habits", json={"name": "Exercise"}).json()["id"]
    client.post(f"/habits/{hid}/checkin", json={"day": day6.isoformat()})
    client.post(f"/habits/{hid}/checkin", json={"day": day3.isoformat()})
    client.post(f"/habits/{hid}/checkin", json={"day": today.isoformat()})

    r = client.get(f"/habits/{hid}/summary")
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "checkins_last_7_days": 3}


def test_weekly_summary_excludes_older_than_7_days():
    today = date.today()
    day8 = today - timedelta(days=8)
    hid = client.post("/habits", json={"name": "Piano"}).json()["id"]
    client.post(f"/habits/{hid}/checkin", json={"day": day8.isoformat()})

    r = client.get(f"/habits/{hid}/summary")
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "checkins_last_7_days": 0}


def test_weekly_summary_deduplicates_same_day():
    today = date.today()
    hid = client.post("/habits", json={"name": "Floss"}).json()["id"]
    client.post(f"/habits/{hid}/checkin", json={"day": today.isoformat()})
    client.post(f"/habits/{hid}/checkin", json={"day": today.isoformat()})

    r = client.get(f"/habits/{hid}/summary")
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "checkins_last_7_days": 1}


def test_weekly_summary_unknown_habit_404():
    r = client.get("/habits/99999/summary")
    assert r.status_code == 404
    assert r.json()["detail"] == "unknown habit"

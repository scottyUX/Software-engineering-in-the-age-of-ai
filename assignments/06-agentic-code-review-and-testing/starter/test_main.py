from datetime import date

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


# --- Validation Tests (Task 2) ---


def test_validation_empty_habit_name_422():
    for bad_name in ["", "   ", "\t\n", "\u200b", "​"]:
        r = client.post("/habits", json={"name": bad_name})
        assert r.status_code == 422


def test_validation_malformed_day_422():
    hid = client.post("/habits", json={"name": "Meditate"}).json()["id"]
    invalid_days = [
        "not-a-date",
        "2026-02-30",  # Invalid date in February
        "2026-13-45",  # Invalid month
        "20260922",  # Missing hyphens
        "2026-9-22",  # Missing leading zero
        "2026/09/22",  # Slashes instead of hyphens
        "yesterday",
        "",
    ]
    for bad_day in invalid_days:
        r = client.post(f"/habits/{hid}/checkin", json={"day": bad_day})
        assert r.status_code == 422


# --- Streak Tests (Task 1) ---


def test_streak_today():
    hid = client.post("/habits", json={"name": "Water plants"}).json()["id"]
    today = date.today().isoformat()
    client.post(f"/habits/{hid}/checkin", json={"day": today})
    r = client.get(f"/habits/{hid}/streak")
    assert r.status_code == 200
    assert r.json()["streak"] == 1


def test_streak_unknown_habit_404():
    r = client.get("/habits/99999/streak")
    assert r.status_code == 404


def test_streak_consecutive_days():
    hid = client.post("/habits", json={"name": "Coding"}).json()["id"]
    # Check in for 3 consecutive days: Nov 4, Nov 5, Nov 6
    client.post(f"/habits/{hid}/checkin", json={"day": "2026-11-04"})
    client.post(f"/habits/{hid}/checkin", json={"day": "2026-11-05"})
    client.post(f"/habits/{hid}/checkin", json={"day": "2026-11-06"})
    # Also add duplicate check-in on Nov 6 to test deduplication
    client.post(f"/habits/{hid}/checkin", json={"day": "2026-11-06"})

    r = client.get(f"/habits/{hid}/streak?today=2026-11-06")
    assert r.status_code == 200
    assert r.json()["streak"] == 3


def test_streak_preserved_from_yesterday():
    hid = client.post("/habits", json={"name": "Gym"}).json()["id"]
    # Checked in yesterday (Nov 5), but not yet today (Nov 6)
    client.post(f"/habits/{hid}/checkin", json={"day": "2026-11-04"})
    client.post(f"/habits/{hid}/checkin", json={"day": "2026-11-05"})

    r = client.get(f"/habits/{hid}/streak?today=2026-11-06")
    assert r.status_code == 200
    assert r.json()["streak"] == 2


def test_streak_broken_gap():
    hid = client.post("/habits", json={"name": "Reading"}).json()["id"]
    # Checked in 3 days ago (Nov 3), skipped Nov 4 and 5
    client.post(f"/habits/{hid}/checkin", json={"day": "2026-11-03"})

    r = client.get(f"/habits/{hid}/streak?today=2026-11-06")
    assert r.status_code == 200
    assert r.json()["streak"] == 0


def test_streak_invalid_today_param():
    hid = client.post("/habits", json={"name": "Run"}).json()["id"]
    r = client.get(f"/habits/{hid}/streak?today=invalid-date")
    assert r.status_code == 400

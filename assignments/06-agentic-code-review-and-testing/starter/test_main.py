from datetime import date, timedelta

import main
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

FIXED_TODAY = date(2026, 9, 25)


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    test_db = tmp_path / "test_habits.db"
    monkeypatch.setattr(main, "DB_PATH", test_db)
    main.init_db()


@pytest.fixture
def mock_today(monkeypatch):
    monkeypatch.setattr(main, "get_today", lambda: FIXED_TODAY)
    return FIXED_TODAY


def test_create_and_list_habit():
    r = client.post("/habits", json={"name": "Read 20 minutes"})
    assert r.status_code == 200
    hid = r.json()["id"]
    r2 = client.get("/habits")
    assert r2.status_code == 200
    assert any(h["id"] == hid for h in r2.json())


def test_checkin_flow():
    r_habit = client.post("/habits", json={"name": "Stretch"})
    assert r_habit.status_code == 200
    hid = r_habit.json()["id"]
    r = client.post(f"/habits/{hid}/checkin", json={"day": "2026-09-22"})
    assert r.status_code == 200
    r2 = client.get(f"/habits/{hid}/checkins")
    assert r2.json() == ["2026-09-22"]


def test_checkin_unknown_habit_404():
    r = client.post("/habits/99999/checkin", json={"day": "2026-09-22"})
    assert r.status_code == 404


def test_streak_no_checkins(mock_today):
    r_habit = client.post("/habits", json={"name": "Exercise"})
    assert r_habit.status_code == 200
    hid = r_habit.json()["id"]
    r = client.get(f"/habits/{hid}/streak")
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "streak": 0}


def test_streak_one_checkin_today(mock_today):
    r_habit = client.post("/habits", json={"name": "Exercise"})
    assert r_habit.status_code == 200
    hid = r_habit.json()["id"]
    r_checkin = client.post(
        f"/habits/{hid}/checkin", json={"day": mock_today.isoformat()}
    )
    assert r_checkin.status_code == 200
    r = client.get(f"/habits/{hid}/streak")
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "streak": 1}


def test_streak_multiple_consecutive_days(mock_today):
    r_habit = client.post("/habits", json={"name": "Exercise"})
    assert r_habit.status_code == 200
    hid = r_habit.json()["id"]
    for offset in range(3):
        day_str = (mock_today - timedelta(days=offset)).isoformat()
        r_checkin = client.post(f"/habits/{hid}/checkin", json={"day": day_str})
        assert r_checkin.status_code == 200
    r = client.get(f"/habits/{hid}/streak")
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "streak": 3}


def test_streak_gap_in_sequence(mock_today):
    r_habit = client.post("/habits", json={"name": "Exercise"})
    assert r_habit.status_code == 200
    hid = r_habit.json()["id"]
    days = [
        mock_today.isoformat(),
        (mock_today - timedelta(days=1)).isoformat(),
        (mock_today - timedelta(days=3)).isoformat(),
    ]
    for d in days:
        r_checkin = client.post(f"/habits/{hid}/checkin", json={"day": d})
        assert r_checkin.status_code == 200
    r = client.get(f"/habits/{hid}/streak")
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "streak": 2}


def test_streak_yesterday_only(mock_today):
    r_habit = client.post("/habits", json={"name": "Exercise"})
    assert r_habit.status_code == 200
    hid = r_habit.json()["id"]
    yesterday_str = (mock_today - timedelta(days=1)).isoformat()
    r_checkin = client.post(f"/habits/{hid}/checkin", json={"day": yesterday_str})
    assert r_checkin.status_code == 200
    r = client.get(f"/habits/{hid}/streak")
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "streak": 0}


def test_streak_duplicate_checkins(mock_today):
    r_habit = client.post("/habits", json={"name": "Exercise"})
    assert r_habit.status_code == 200
    hid = r_habit.json()["id"]
    today_str = mock_today.isoformat()
    yesterday_str = (mock_today - timedelta(days=1)).isoformat()
    for day_str in (today_str, today_str, yesterday_str, yesterday_str):
        r_checkin = client.post(f"/habits/{hid}/checkin", json={"day": day_str})
        assert r_checkin.status_code == 200
    r = client.get(f"/habits/{hid}/streak")
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "streak": 2}


def test_streak_unknown_habit_404():
    r = client.get("/habits/99999/streak")
    assert r.status_code == 404
    assert r.json()["detail"] == "unknown habit"


def test_streak_ignores_future_checkins(mock_today):
    r_habit = client.post("/habits", json={"name": "Exercise"})
    assert r_habit.status_code == 200
    hid = r_habit.json()["id"]
    tomorrow_str = (mock_today + timedelta(days=1)).isoformat()
    today_str = mock_today.isoformat()
    r_future = client.post(f"/habits/{hid}/checkin", json={"day": tomorrow_str})
    assert r_future.status_code == 200
    r_today = client.post(f"/habits/{hid}/checkin", json={"day": today_str})
    assert r_today.status_code == 200
    r = client.get(f"/habits/{hid}/streak")
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "streak": 1}


def test_streak_habit_isolation(mock_today):
    r_h1 = client.post("/habits", json={"name": "Habit 1"})
    assert r_h1.status_code == 200
    h1_id = r_h1.json()["id"]

    r_h2 = client.post("/habits", json={"name": "Habit 2"})
    assert r_h2.status_code == 200
    h2_id = r_h2.json()["id"]

    today_str = mock_today.isoformat()
    yesterday_str = (mock_today - timedelta(days=1)).isoformat()

    # Habit 1: checked in today and yesterday (streak = 2)
    r1 = client.post(f"/habits/{h1_id}/checkin", json={"day": today_str})
    assert r1.status_code == 200
    r2 = client.post(f"/habits/{h1_id}/checkin", json={"day": yesterday_str})
    assert r2.status_code == 200

    # Habit 2: checked in yesterday only (streak = 0)
    r3 = client.post(f"/habits/{h2_id}/checkin", json={"day": yesterday_str})
    assert r3.status_code == 200

    streak_h1 = client.get(f"/habits/{h1_id}/streak")
    assert streak_h1.status_code == 200
    assert streak_h1.json() == {"habit_id": h1_id, "streak": 2}

    streak_h2 = client.get(f"/habits/{h2_id}/streak")
    assert streak_h2.status_code == 200
    assert streak_h2.json() == {"habit_id": h2_id, "streak": 0}

    # Now check in Habit 2 today as well; Habit 2 streak becomes 2, Habit 1 remains 2
    r4 = client.post(f"/habits/{h2_id}/checkin", json={"day": today_str})
    assert r4.status_code == 200

    streak_h1_after = client.get(f"/habits/{h1_id}/streak")
    assert streak_h1_after.status_code == 200
    assert streak_h1_after.json() == {"habit_id": h1_id, "streak": 2}

    streak_h2_after = client.get(f"/habits/{h2_id}/streak")
    assert streak_h2_after.status_code == 200
    assert streak_h2_after.json() == {"habit_id": h2_id, "streak": 2}


def test_streak_date_min_boundary_no_overflow(monkeypatch):
    test_today = date(1, 1, 2)
    monkeypatch.setattr(main, "get_today", lambda: test_today)
    r_habit = client.post("/habits", json={"name": "Ancient Habit"})
    assert r_habit.status_code == 200
    hid = r_habit.json()["id"]

    r1 = client.post(f"/habits/{hid}/checkin", json={"day": test_today.isoformat()})
    assert r1.status_code == 200
    r2 = client.post(f"/habits/{hid}/checkin", json={"day": date.min.isoformat()})
    assert r2.status_code == 200

    r = client.get(f"/habits/{hid}/streak")
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "streak": 2}


def test_streak_compact_iso_dates(mock_today):
    r_habit = client.post("/habits", json={"name": "Exercise"})
    assert r_habit.status_code == 200
    hid = r_habit.json()["id"]

    today_compact = mock_today.strftime("%Y%m%d")
    yesterday_compact = (mock_today - timedelta(days=1)).strftime("%Y%m%d")

    r1 = client.post(f"/habits/{hid}/checkin", json={"day": today_compact})
    assert r1.status_code == 200
    r2 = client.post(f"/habits/{hid}/checkin", json={"day": yesterday_compact})
    assert r2.status_code == 200

    r = client.get(f"/habits/{hid}/streak")
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "streak": 2}


def test_streak_mixed_date_representations(mock_today):
    r_habit = client.post("/habits", json={"name": "Exercise"})
    assert r_habit.status_code == 200
    hid = r_habit.json()["id"]

    today_iso = mock_today.isoformat()
    today_compact = mock_today.strftime("%Y%m%d")
    yesterday_iso = (mock_today - timedelta(days=1)).isoformat()
    two_days_ago_compact = (mock_today - timedelta(days=2)).strftime("%Y%m%d")

    r1 = client.post(f"/habits/{hid}/checkin", json={"day": today_compact})
    assert r1.status_code == 200
    r2 = client.post(f"/habits/{hid}/checkin", json={"day": today_iso})
    assert r2.status_code == 200
    r3 = client.post(f"/habits/{hid}/checkin", json={"day": yesterday_iso})
    assert r3.status_code == 200
    r4 = client.post(f"/habits/{hid}/checkin", json={"day": two_days_ago_compact})
    assert r4.status_code == 200

    r = client.get(f"/habits/{hid}/streak")
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "streak": 3}


def test_streak_malformed_stored_dates_ignored(mock_today):
    r_habit = client.post("/habits", json={"name": "Exercise"})
    assert r_habit.status_code == 200
    hid = r_habit.json()["id"]

    for bad_day in ["invalid-date", "", "not-a-date", "2026-99-99", "2026-02-30"]:
        r_bad = client.post(f"/habits/{hid}/checkin", json={"day": bad_day})
        assert r_bad.status_code == 200

    r_streak_zero = client.get(f"/habits/{hid}/streak")
    assert r_streak_zero.status_code == 200
    assert r_streak_zero.json() == {"habit_id": hid, "streak": 0}

    r_valid = client.post(
        f"/habits/{hid}/checkin", json={"day": mock_today.isoformat()}
    )
    assert r_valid.status_code == 200

    r_streak_one = client.get(f"/habits/{hid}/streak")
    assert r_streak_one.status_code == 200
    assert r_streak_one.json() == {"habit_id": hid, "streak": 1}

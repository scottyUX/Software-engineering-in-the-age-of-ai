from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

import main
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


# Streak tests pin "today" so they cannot flake when the run crosses midnight.
TODAY = date(2026, 3, 2)


@pytest.fixture(autouse=True)
def fixed_today(monkeypatch):
    monkeypatch.setattr(main, "today", lambda: TODAY)


def _days_ago(n: int) -> str:
    return (TODAY - timedelta(days=n)).isoformat()


def _new_habit(name: str = "Streak habit") -> int:
    return client.post("/habits", json={"name": name}).json()["id"]


def test_streak_no_checkins_is_zero():
    hid = _new_habit()
    r = client.get(f"/habits/{hid}/streak")
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "streak": 0}


def test_streak_counts_consecutive_days_ending_today():
    hid = _new_habit()
    for n in (0, 1, 2):
        client.post(f"/habits/{hid}/checkin", json={"day": _days_ago(n)})
    assert client.get(f"/habits/{hid}/streak").json()["streak"] == 3


def test_streak_stops_at_gap():
    hid = _new_habit()
    for n in (0, 1, 3, 4):
        client.post(f"/habits/{hid}/checkin", json={"day": _days_ago(n)})
    assert client.get(f"/habits/{hid}/streak").json()["streak"] == 2


def test_streak_zero_when_today_missing():
    hid = _new_habit()
    for n in (1, 2):
        client.post(f"/habits/{hid}/checkin", json={"day": _days_ago(n)})
    assert client.get(f"/habits/{hid}/streak").json()["streak"] == 0


def test_streak_duplicate_checkins_count_once():
    hid = _new_habit()
    for n in (0, 0, 1):
        client.post(f"/habits/{hid}/checkin", json={"day": _days_ago(n)})
    assert client.get(f"/habits/{hid}/streak").json()["streak"] == 2


def test_streak_ignores_other_habits():
    hid = _new_habit()
    other = _new_habit("Other")
    client.post(f"/habits/{other}/checkin", json={"day": _days_ago(0)})
    assert client.get(f"/habits/{hid}/streak").json()["streak"] == 0


def test_streak_crosses_month_boundary():
    # TODAY is 2026-03-02, so this run covers 2026-02-27 .. 2026-03-02
    hid = _new_habit()
    for day in ("2026-02-27", "2026-02-28", "2026-03-01", "2026-03-02"):
        client.post(f"/habits/{hid}/checkin", json={"day": day})
    assert client.get(f"/habits/{hid}/streak").json()["streak"] == 4


def test_streak_ignores_future_checkins():
    hid = _new_habit()
    for n in (-1, 0):
        client.post(f"/habits/{hid}/checkin", json={"day": _days_ago(n)})
    assert client.get(f"/habits/{hid}/streak").json()["streak"] == 1


def test_streak_unknown_habit_404():
    r = client.get("/habits/99999/streak")
    assert r.status_code == 404


@pytest.mark.parametrize("name", ["", "   ", "\t\n"])
def test_create_habit_rejects_blank_name(name):
    r = client.post("/habits", json={"name": name})
    assert r.status_code == 422
    assert "habit name must not be empty" in r.text


def test_create_habit_strips_name():
    r = client.post("/habits", json={"name": "  Walk  "})
    assert r.status_code == 200
    assert r.json()["name"] == "Walk"


def test_create_habit_missing_name_422():
    r = client.post("/habits", json={})
    assert r.status_code == 422


@pytest.mark.parametrize(
    "day,message",
    [
        ("", "YYYY-MM-DD"),
        ("yesterday", "YYYY-MM-DD"),
        ("22-09-2026", "YYYY-MM-DD"),
        ("2026-9-22", "YYYY-MM-DD"),
        ("20260922", "YYYY-MM-DD"),
        ("2026-09-22T10:00:00", "YYYY-MM-DD"),
        (" 2026-09-22", "YYYY-MM-DD"),
        ("٢٠٢٦-٠٩-٢٢", "YYYY-MM-DD"),
        ("2026-13-01", "not a valid calendar date"),
        ("2026-02-30", "not a valid calendar date"),
    ],
)
def test_checkin_rejects_malformed_day(day, message):
    hid = client.post("/habits", json={"name": "Meditate"}).json()["id"]
    r = client.post(f"/habits/{hid}/checkin", json={"day": day})
    assert r.status_code == 422
    assert message in r.text
    assert client.get(f"/habits/{hid}/checkins").json() == []


def test_checkin_accepts_leap_day():
    hid = client.post("/habits", json={"name": "Journal"}).json()["id"]
    r = client.post(f"/habits/{hid}/checkin", json={"day": "2028-02-29"})
    assert r.status_code == 200


def test_streak_cannot_be_fooled_by_a_compact_date():
    # CodeRabbit (PR #1): "20260302" used to be stored as-is and never matched the
    # ISO day in the streak. Validation now rejects it, so it cannot silently not count.
    hid = _new_habit()
    assert client.post(f"/habits/{hid}/checkin", json={"day": "20260302"}).status_code == 422
    assert client.post(f"/habits/{hid}/checkin", json={"day": "1772409600"}).status_code == 422
    client.post(f"/habits/{hid}/checkin", json={"day": TODAY.isoformat()})
    assert client.get(f"/habits/{hid}/streak").json()["streak"] == 1

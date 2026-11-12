from datetime import date

import pytest
from fastapi import HTTPException

import main


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "habits.db")
    main.init_db()


def test_create_and_list_habit():
    created = main.create_habit(main.HabitIn(name="Read 20 minutes"))
    assert any(h["id"] == created["id"] for h in main.list_habits())


def test_checkin_flow():
    habit_id = main.create_habit(main.HabitIn(name="Stretch"))["id"]
    main.add_checkin(habit_id, main.CheckinIn(day="2026-09-22"))
    assert main.list_checkins(habit_id) == ["2026-09-22"]


def test_checkin_unknown_habit_404():
    with pytest.raises(HTTPException) as error:
        main.add_checkin(99999, main.CheckinIn(day="2026-09-22"))
    assert error.value.status_code == 404


def test_weekly_summary_counts_inclusive_seven_day_window():
    habit_id = main.create_habit(main.HabitIn(name="Practice piano"))["id"]
    for day in ["2026-09-16", "2026-09-18", "2026-09-22", "2026-09-15"]:
        main.add_checkin(habit_id, main.CheckinIn(day=day))

    result = main.weekly_summary(habit_id, today=date(2026, 9, 22))

    assert result == {
        "habit_id": habit_id,
        "start": "2026-09-16",
        "end": "2026-09-22",
        "count": 3,
    }


def test_weekly_summary_unknown_habit_404():
    with pytest.raises(HTTPException) as error:
        main.weekly_summary(99999, today=date(2026, 9, 22))
    assert error.value.status_code == 404

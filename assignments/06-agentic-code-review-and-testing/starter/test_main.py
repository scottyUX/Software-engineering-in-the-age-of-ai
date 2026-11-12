import pytest
from fastapi import HTTPException

import main


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "habits.db")
    main.init_db()


def test_create_and_list_habit():
    created = main.create_habit(main.HabitIn(name="Read 20 minutes"))
    assert created["name"] == "Read 20 minutes"
    assert any(h["id"] == created["id"] for h in main.list_habits())


def test_checkin_flow():
    habit_id = main.create_habit(main.HabitIn(name="Stretch"))["id"]
    result = main.add_checkin(habit_id, main.CheckinIn(day="2026-09-22"))
    assert result == {"habit_id": habit_id, "day": "2026-09-22"}
    assert main.list_checkins(habit_id) == ["2026-09-22"]


def test_checkin_unknown_habit_404():
    with pytest.raises(HTTPException) as error:
        main.add_checkin(99999, main.CheckinIn(day="2026-09-22"))
    assert error.value.status_code == 404


def test_empty_habit_name_is_rejected_and_trimmed_names_are_saved():
    with pytest.raises(HTTPException) as error:
        main.create_habit(main.HabitIn(name="   "))
    assert error.value.status_code == 422
    assert error.value.detail == "name must not be empty"

    created = main.create_habit(main.HabitIn(name="  Walk  "))
    assert created["name"] == "Walk"


@pytest.mark.parametrize("day", ["2026-13-01", "2026/09/22", "not-a-date", "2026-9-2"])
def test_malformed_checkin_day_is_rejected(day):
    habit_id = main.create_habit(main.HabitIn(name="Journal"))["id"]
    with pytest.raises(HTTPException) as error:
        main.add_checkin(habit_id, main.CheckinIn(day=day))
    assert error.value.status_code == 422
    assert error.value.detail == "day must be an ISO date in YYYY-MM-DD format"

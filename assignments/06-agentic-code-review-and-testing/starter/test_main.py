from contextlib import closing

import main
import pytest
from fastapi.testclient import TestClient
from main import app, get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    test_db = tmp_path / "test_habits.db"
    monkeypatch.setattr(main, "DB_PATH", test_db)
    main.init_db()
    yield test_db


def test_create_and_list_habit():
    r = client.post("/habits", json={"name": "Read 20 minutes"})
    assert r.status_code == 200
    hid = r.json()["id"]
    r2 = client.get("/habits")
    assert r2.status_code == 200
    assert any(h["id"] == hid for h in r2.json())


def test_create_habit_valid_names():
    # Standard valid name
    r = client.post("/habits", json={"name": "Drink water"})
    assert r.status_code == 200
    assert r.json()["name"] == "Drink water"

    # Name with surrounding whitespace should be trimmed
    r2 = client.post("/habits", json={"name": "  Meditate  "})
    assert r2.status_code == 200
    assert r2.json()["name"] == "Meditate"


def test_create_habit_empty_name():
    r = client.post("/habits", json={"name": ""})
    assert r.status_code == 422
    errors = r.json().get("detail", [])
    assert any("empty or whitespace-only" in err.get("msg", "") for err in errors)


@pytest.mark.parametrize(
    "whitespace_name",
    [
        " ",
        "   ",
        "\t",
        "\n",
        " \t \n ",
    ],
)
def test_create_habit_whitespace_only_names(whitespace_name):
    r = client.post("/habits", json={"name": whitespace_name})
    assert r.status_code == 422
    errors = r.json().get("detail", [])
    assert any("empty or whitespace-only" in err.get("msg", "") for err in errors)


@pytest.mark.parametrize(
    "invalid_payload",
    [
        {},
        {"name": None},
        {"name": 123},
        {"name": 45.67},
        {"name": True},
        {"name": ["Read"]},
        {"name": {"title": "Read"}},
    ],
)
def test_create_habit_invalid_input_types(invalid_payload):
    r = client.post("/habits", json=invalid_payload)
    assert r.status_code == 422
    assert "detail" in r.json()


def test_rejected_habit_does_not_persist():
    # Attempt invalid habit creations
    client.post("/habits", json={"name": ""})
    client.post("/habits", json={"name": "   "})
    client.post("/habits", json={})
    client.post("/habits", json={"name": None})
    client.post("/habits", json={"name": 999})

    # Verify no records in API
    r_list = client.get("/habits")
    assert r_list.status_code == 200
    assert r_list.json() == []

    # Verify directly in SQLite database
    with closing(get_db()) as conn:
        count = conn.execute("SELECT COUNT(*) FROM habits").fetchone()[0]
        assert count == 0


def test_checkin_flow():
    hid = client.post("/habits", json={"name": "Stretch"}).json()["id"]
    r = client.post(f"/habits/{hid}/checkin", json={"day": "2026-09-22"})
    assert r.status_code == 200
    r2 = client.get(f"/habits/{hid}/checkins")
    assert r2.json() == ["2026-09-22"]


@pytest.mark.parametrize(
    "valid_date",
    [
        "2026-09-22",
        "2024-02-29",  # Leap year
        "2026-01-01",  # Start of year
        "2026-12-31",  # End of year
    ],
)
def test_checkin_valid_dates(valid_date):
    hid = client.post("/habits", json={"name": "Cardio"}).json()["id"]
    r = client.post(f"/habits/{hid}/checkin", json={"day": valid_date})
    assert r.status_code == 200
    assert r.json() == {"habit_id": hid, "day": valid_date}


@pytest.mark.parametrize(
    "invalid_format",
    [
        "hello",
        "2026/09/22",
        "2026-9-2",
        "22-09-2026",
        "20260922",
        "2026-09-22T00:00:00",
        "2026-09-22 00:00:00",
        " 2026-09-22 ",
        "",
    ],
)
def test_checkin_invalid_date_formats(invalid_format):
    hid = client.post("/habits", json={"name": "Yoga"}).json()["id"]
    r = client.post(f"/habits/{hid}/checkin", json={"day": invalid_format})
    assert r.status_code == 422
    errors = r.json().get("detail", [])
    assert any("strict YYYY-MM-DD format" in err.get("msg", "") for err in errors)


@pytest.mark.parametrize(
    "unicode_date",
    [
        # Non-ASCII digits in year
        "\uff12\uff10\uff12\uff16-09-22",  # Full-width: ２０２６-09-22
        "\u0662\u0660\u0662\u0666-09-22",  # Arabic-Indic: ٢٠٢٦-09-22
        "\u0968\u0966\u0968\u096c-09-22",  # Devanagari: २०२६-09-22
        # Non-ASCII digits in month
        "2026-\uff10\uff19-22",  # Full-width: 2026-０９-22
        "2026-\u0660\u0669-22",  # Arabic-Indic: 2026-٠٩-22
        # Non-ASCII digits in day
        "2026-09-\uff12\uff12",  # Full-width: 2026-09-２２
        "2026-09-\u0662\u0662",  # Arabic-Indic: 2026-09-٢٢
    ],
)
def test_checkin_rejects_non_ascii_unicode_digits(unicode_date):
    hid = client.post("/habits", json={"name": "Pilates"}).json()["id"]
    r = client.post(f"/habits/{hid}/checkin", json={"day": unicode_date})
    assert r.status_code == 422
    errors = r.json().get("detail", [])
    assert any("strict YYYY-MM-DD format" in err.get("msg", "") for err in errors)


@pytest.mark.parametrize(
    "impossible_date",
    [
        "2026-13-45",
        "2026-02-30",
        "2026-02-29",  # 2026 is not a leap year
        "2026-04-31",  # April only has 30 days
        "2026-00-10",  # Month 00
        "2026-05-00",  # Day 00
    ],
)
def test_checkin_impossible_dates(impossible_date):
    hid = client.post("/habits", json={"name": "Cycling"}).json()["id"]
    r = client.post(f"/habits/{hid}/checkin", json={"day": impossible_date})
    assert r.status_code == 422
    errors = r.json().get("detail", [])
    assert any("Invalid calendar date" in err.get("msg", "") for err in errors)


@pytest.mark.parametrize(
    "invalid_payload",
    [
        {},
        {"day": None},
        {"day": 20260922},
        {"day": 2026.09},
        {"day": True},
        {"day": ["2026-09-22"]},
        {"day": {"date": "2026-09-22"}},
    ],
)
def test_checkin_invalid_input_types(invalid_payload):
    hid = client.post("/habits", json={"name": "Running"}).json()["id"]
    r = client.post(f"/habits/{hid}/checkin", json=invalid_payload)
    assert r.status_code == 422
    assert "detail" in r.json()


def test_rejected_checkin_does_not_persist():
    hid = client.post("/habits", json={"name": "Meditation"}).json()["id"]

    # Attempt rejected check-ins
    client.post(f"/habits/{hid}/checkin", json={"day": "hello"})
    client.post(f"/habits/{hid}/checkin", json={"day": "2026-02-30"})
    client.post(f"/habits/{hid}/checkin", json={"day": "2026-13-45"})
    client.post(f"/habits/{hid}/checkin", json={})
    client.post(f"/habits/{hid}/checkin", json={"day": None})
    client.post(f"/habits/{hid}/checkin", json={"day": 12345})

    # Verify via API
    r = client.get(f"/habits/{hid}/checkins")
    assert r.status_code == 200
    assert r.json() == []

    # Verify directly in SQLite database
    with closing(get_db()) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM checkins WHERE habit_id = ?", (hid,)
        ).fetchone()[0]
        assert count == 0


def test_checkin_unknown_habit_404():
    r = client.post("/habits/99999/checkin", json={"day": "2026-09-22"})
    assert r.status_code == 404

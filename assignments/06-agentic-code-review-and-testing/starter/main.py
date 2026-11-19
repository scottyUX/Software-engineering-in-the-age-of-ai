"""Habit Tracker — starter app for Week 6.

A tiny FastAPI service for habits and daily check-ins. You'll add features on
branches, open PRs, and compare your manual review with an AI reviewer.

Run:
    pip install -r requirements.txt
    uvicorn main:app --reload
Test:
    pytest
"""

import re
import sqlite3
from contextlib import closing
from datetime import date, timedelta
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator

DB_PATH = Path(__file__).parent / "habits.db"

app = FastAPI(title="Habit Tracker")


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with closing(get_db()) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS habits (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS checkins (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                day      TEXT NOT NULL,
                FOREIGN KEY (habit_id) REFERENCES habits (id)
            )""")
        conn.commit()


init_db()


# [0-9], not \d: \d also matches non-ASCII digits such as "٢", which fromisoformat rejects.
ISO_DAY_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


class HabitIn(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("habit name must not be empty")
        return v


class CheckinIn(BaseModel):
    day: str  # ISO date, e.g. "2026-09-22"

    @field_validator("day")
    @classmethod
    def day_is_iso_date(cls, v: str) -> str:
        # Require exactly YYYY-MM-DD so stored days sort and compare as strings.
        if not ISO_DAY_RE.fullmatch(v):
            raise ValueError("day must be a date in YYYY-MM-DD format, e.g. 2026-09-22")
        try:
            date.fromisoformat(v)
        except ValueError:
            raise ValueError(f"day {v!r} is not a valid calendar date") from None
        return v


@app.post("/habits")
def create_habit(habit: HabitIn):
    with closing(get_db()) as conn:
        cur = conn.execute("INSERT INTO habits (name) VALUES (?)", (habit.name,))
        conn.commit()
        return {"id": cur.lastrowid, "name": habit.name}


@app.get("/habits")
def list_habits():
    with closing(get_db()) as conn:
        rows = conn.execute("SELECT id, name FROM habits ORDER BY id").fetchall()
    return [dict(r) for r in rows]


@app.post("/habits/{habit_id}/checkin")
def add_checkin(habit_id: int, checkin: CheckinIn):
    with closing(get_db()) as conn:
        habit = conn.execute("SELECT id FROM habits WHERE id = ?", (habit_id,)).fetchone()
        if habit is None:
            raise HTTPException(status_code=404, detail="unknown habit")
        conn.execute("INSERT INTO checkins (habit_id, day) VALUES (?, ?)", (habit_id, checkin.day))
        conn.commit()
    return {"habit_id": habit_id, "day": checkin.day}


@app.get("/habits/{habit_id}/checkins")
def list_checkins(habit_id: int):
    with closing(get_db()) as conn:
        rows = conn.execute(
            "SELECT day FROM checkins WHERE habit_id = ? ORDER BY day", (habit_id,)
        ).fetchall()
    return [r["day"] for r in rows]


def today() -> date:
    """Current local date; a separate function so tests can override it."""
    return date.today()


@app.get("/habits/{habit_id}/streak")
def get_streak(habit_id: int):
    """Count consecutive days with a check-in, ending today.

    "Today" is the server's local date. If today has no check-in the streak is 0.
    Duplicate check-ins on the same day count once (the set below removes them).
    """
    with closing(get_db()) as conn:
        habit = conn.execute("SELECT id FROM habits WHERE id = ?", (habit_id,)).fetchone()
        if habit is None:
            raise HTTPException(status_code=404, detail="unknown habit")
        rows = conn.execute("SELECT day FROM checkins WHERE habit_id = ?", (habit_id,)).fetchall()
    days = {r["day"] for r in rows}
    streak = 0
    current = today()
    while current.isoformat() in days:
        streak += 1
        current -= timedelta(days=1)
    return {"habit_id": habit_id, "streak": streak}

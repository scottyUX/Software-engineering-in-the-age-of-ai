"""Habit Tracker — starter app for Week 6.

A tiny FastAPI service for habits and daily check-ins. You'll add features on
branches, open PRs, and compare your manual review with an AI reviewer.

Run:
    pip install -r requirements.txt
    uvicorn main:app --reload
Test:
    pytest
"""

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


class HabitIn(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("name must be a string")
        v = v.strip()
        if not v or not any(c.isprintable() and not c.isspace() for c in v):
            raise ValueError("habit name cannot be empty or whitespace only")
        return v


class CheckinIn(BaseModel):
    day: str  # ISO date, strictly YYYY-MM-DD

    @field_validator("day")
    @classmethod
    def validate_day(cls, v: str) -> str:
        if not isinstance(v, str) or len(v) != 10:
            raise ValueError("day must be formatted strictly as YYYY-MM-DD")
        try:
            parsed = date.fromisoformat(v)
            if parsed.isoformat() != v:
                raise ValueError("day must be formatted strictly as YYYY-MM-DD")
        except ValueError:
            raise ValueError(f"invalid calendar date: {v}")
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
        habit = conn.execute(
            "SELECT id FROM habits WHERE id = ?", (habit_id,)
        ).fetchone()
        if habit is None:
            raise HTTPException(status_code=404, detail="unknown habit")
        conn.execute(
            "INSERT INTO checkins (habit_id, day) VALUES (?, ?)",
            (habit_id, checkin.day),
        )
        conn.commit()
    return {"habit_id": habit_id, "day": checkin.day}


@app.get("/habits/{habit_id}/checkins")
def list_checkins(habit_id: int):
    with closing(get_db()) as conn:
        rows = conn.execute(
            "SELECT day FROM checkins WHERE habit_id = ? ORDER BY day", (habit_id,)
        ).fetchall()
    return [r["day"] for r in rows]


@app.get("/habits/{habit_id}/streak")
def get_streak(habit_id: int, today: str | None = None):
    # Determine reference date
    if today:
        try:
            ref_date = date.fromisoformat(today)
        except ValueError:
            raise HTTPException(
                status_code=400, detail="today must be in YYYY-MM-DD format"
            )
    else:
        ref_date = date.today()

    with closing(get_db()) as conn:
        habit = conn.execute(
            "SELECT id FROM habits WHERE id = ?", (habit_id,)
        ).fetchone()
        if habit is None:
            raise HTTPException(status_code=404, detail="unknown habit")

        # Distinct check-in days
        rows = conn.execute(
            "SELECT DISTINCT day FROM checkins WHERE habit_id = ?",
            (habit_id,),
        ).fetchall()

    checked_days = set()
    for r in rows:
        try:
            checked_days.add(date.fromisoformat(r["day"]))
        except ValueError:
            continue

    if not checked_days:
        return {"habit_id": habit_id, "streak": 0}

    # Streak counts consecutive days ending on ref_date (if checked in today)
    # or ending on yesterday (if not checked in yet today, streak is preserved).
    if ref_date in checked_days:
        cursor = ref_date
    elif (ref_date - timedelta(days=1)) in checked_days:
        cursor = ref_date - timedelta(days=1)
    else:
        return {"habit_id": habit_id, "streak": 0}

    streak = 0
    while cursor in checked_days:
        streak += 1
        cursor -= timedelta(days=1)

    return {"habit_id": habit_id, "streak": streak}

"""Habit Tracker — validation feature for Week 6."""

import sqlite3
from contextlib import closing
from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DB_PATH = Path(__file__).parent / "habits.db"

app = FastAPI(title="Habit Tracker")


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with closing(get_db()) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS habits (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS checkins (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                day      TEXT NOT NULL,
                FOREIGN KEY (habit_id) REFERENCES habits (id)
            )"""
        )
        conn.commit()


init_db()


class HabitIn(BaseModel):
    name: str


class CheckinIn(BaseModel):
    day: str


def normalized_habit_name(name: str) -> str:
    value = name.strip()
    if not value:
        raise HTTPException(status_code=422, detail="name must not be empty")
    return value


def normalized_day(day: str) -> str:
    value = day.strip()
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail="day must be an ISO date in YYYY-MM-DD format",
        ) from exc
    if parsed.isoformat() != value:
        raise HTTPException(
            status_code=422,
            detail="day must be an ISO date in YYYY-MM-DD format",
        )
    return value


@app.post("/habits")
def create_habit(habit: HabitIn):
    name = normalized_habit_name(habit.name)
    with closing(get_db()) as conn:
        cur = conn.execute("INSERT INTO habits (name) VALUES (?)", (name,))
        conn.commit()
        return {"id": cur.lastrowid, "name": name}


@app.get("/habits")
def list_habits():
    with closing(get_db()) as conn:
        rows = conn.execute("SELECT id, name FROM habits ORDER BY id").fetchall()
    return [dict(r) for r in rows]


@app.post("/habits/{habit_id}/checkin")
def add_checkin(habit_id: int, checkin: CheckinIn):
    day = normalized_day(checkin.day)
    with closing(get_db()) as conn:
        habit = conn.execute("SELECT id FROM habits WHERE id = ?", (habit_id,)).fetchone()
        if habit is None:
            raise HTTPException(status_code=404, detail="unknown habit")
        conn.execute("INSERT INTO checkins (habit_id, day) VALUES (?, ?)", (habit_id, day))
        conn.commit()
    return {"habit_id": habit_id, "day": day}


@app.get("/habits/{habit_id}/checkins")
def list_checkins(habit_id: int):
    with closing(get_db()) as conn:
        rows = conn.execute(
            "SELECT day FROM checkins WHERE habit_id = ? ORDER BY day", (habit_id,)
        ).fetchall()
    return [r["day"] for r in rows]

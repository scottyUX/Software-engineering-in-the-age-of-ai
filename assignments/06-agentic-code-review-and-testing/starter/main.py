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
from datetime import date, datetime, timedelta
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


class CheckinIn(BaseModel):
    day: str  # ISO date, e.g. "2026-09-22"


@app.post("/habits")
def create_habit(habit: HabitIn):
    clean_name = habit.name.strip()
    if not clean_name:
        raise HTTPException(status_code=400, detail="Habit name must not be empty")

    with closing(get_db()) as conn:
        cur = conn.execute("INSERT INTO habits (name) VALUES (?)", (clean_name,))
        conn.commit()
        return {"id": cur.lastrowid, "name": clean_name}


@app.get("/habits")
def list_habits():
    with closing(get_db()) as conn:
        rows = conn.execute("SELECT id, name FROM habits ORDER BY id").fetchall()
    return [dict(r) for r in rows]


@app.post("/habits/{habit_id}/checkin")
def add_checkin(habit_id: int, checkin: CheckinIn):
    # Validate day format (YYYY-MM-DD)
    try:
        parsed_date = datetime.strptime(checkin.day.strip(), "%Y-%m-%d").date()
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=400,
            detail="Malformed day value. Must be ISO format YYYY-MM-DD",
        )

    with closing(get_db()) as conn:
        habit = conn.execute(
            "SELECT id FROM habits WHERE id = ?", (habit_id,)
        ).fetchone()
        if habit is None:
            raise HTTPException(status_code=404, detail="unknown habit")

        day_str = parsed_date.isoformat()
        # Avoid duplicate checkins on the same day for same habit
        conn.execute(
            "INSERT OR IGNORE INTO checkins (habit_id, day) VALUES (?, ?)",
            (habit_id, day_str),
        )
        conn.commit()
    return {"habit_id": habit_id, "day": day_str}


@app.get("/habits/{habit_id}/checkins")
def list_checkins(habit_id: int):
    with closing(get_db()) as conn:
        rows = conn.execute(
            "SELECT day FROM checkins WHERE habit_id = ? ORDER BY day",
            (habit_id,),
        ).fetchall()
    return [r["day"] for r in rows]


@app.get("/habits/{habit_id}/streak")
def get_streak(habit_id: int):
    with closing(get_db()) as conn:
        habit = conn.execute(
            "SELECT id FROM habits WHERE id = ?", (habit_id,)
        ).fetchone()
        if habit is None:
            raise HTTPException(status_code=404, detail="unknown habit")

        rows = conn.execute(
            "SELECT DISTINCT day FROM checkins WHERE habit_id = ? ORDER BY day DESC",
            (habit_id,),
        ).fetchall()

    if not rows:
        return {"habit_id": habit_id, "streak": 0}

    checkin_dates = set()
    for r in rows:
        try:
            checkin_dates.add(datetime.strptime(r["day"], "%Y-%m-%d").date())
        except ValueError:
            continue

    today = date.today()
    # If checked in today, count starts from today; if not, check if streak ended yesterday
    if today in checkin_dates:
        current = today
    elif (today - timedelta(days=1)) in checkin_dates:
        current = today - timedelta(days=1)
    else:
        return {"habit_id": habit_id, "streak": 0}

    streak = 0
    while current in checkin_dates:
        streak += 1
        current -= timedelta(days=1)

    return {"habit_id": habit_id, "streak": streak}


@app.get("/habits/{habit_id}/summary")
def get_summary(habit_id: int):
    with closing(get_db()) as conn:
        habit = conn.execute(
            "SELECT id FROM habits WHERE id = ?", (habit_id,)
        ).fetchone()
        if habit is None:
            raise HTTPException(status_code=404, detail="unknown habit")

        since_date = (date.today() - timedelta(days=7)).isoformat()
        row = conn.execute(
            "SELECT COUNT(DISTINCT day) as cnt FROM checkins WHERE habit_id = ? AND day >= ?",
            (habit_id, since_date),
        ).fetchone()

    count = row["cnt"] if row else 0
    return {"habit_id": habit_id, "last_7_days_checkins": count}

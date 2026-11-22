"""Link Shortener — starter app for Week 5.

A deliberately tiny FastAPI service you will make *agent-native*. Run it, read it,
then use your coding agent (Antigravity by default) plus the tasks in docs/TASKS.md.

Run:
    pip install -r requirements.txt
    uvicorn main:app --reload
Test:
    pytest
"""
import re
import sqlite3
import string
from contextlib import closing
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

DB_PATH = Path(__file__).parent / "links.db"
ALPHABET = string.ascii_letters + string.digits
RESERVED_ALIASES = {"shorten", "docs", "redoc", "openapi.json"}
ALIAS_REGEX = re.compile(r"^[A-Za-z0-9_-]{1,32}$")

app = FastAPI(title="Link Shortener")


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with closing(get_db()) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS links (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE,
                url  TEXT NOT NULL
            )"""
        )
        conn.commit()


init_db()


def encode(n: int) -> str:
    """Base62-encode a row id into a short code."""
    base = len(ALPHABET)
    if n == 0:
        return ALPHABET[0]
    chars = []
    while n > 0:
        n, r = divmod(n, base)
        chars.append(ALPHABET[r])
    return "".join(reversed(chars))


class ShortenRequest(BaseModel):
    url: str
    alias: str | None = None


@app.post("/shorten")
def shorten(req: ShortenRequest):
    if not req.url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="url must start with http:// or https://")
    if req.alias is not None:
        if req.alias in RESERVED_ALIASES:
            raise HTTPException(status_code=409, detail="alias already taken")
        if not ALIAS_REGEX.fullmatch(req.alias):
            raise HTTPException(status_code=400, detail="invalid alias")
    with closing(get_db()) as conn:
        if req.alias:
            try:
                conn.execute("INSERT INTO links (code, url) VALUES (?, ?)", (req.alias, req.url))
                conn.commit()
            except sqlite3.IntegrityError:
                raise HTTPException(status_code=409, detail="alias already taken")
            code = req.alias
        else:
            cur = conn.execute("INSERT INTO links (url) VALUES (?)", (req.url,))
            row_id = cur.lastrowid
            k = 0
            while True:
                code = encode(row_id + k)
                try:
                    conn.execute("UPDATE links SET code = ? WHERE id = ?", (code, row_id))
                    conn.commit()
                    break
                except sqlite3.IntegrityError:
                    k += 1
    return {"code": code, "short_url": f"/{code}"}


@app.get("/{code}")
def redirect(code: str):
    with closing(get_db()) as conn:
        row = conn.execute("SELECT url FROM links WHERE code = ?", (code,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="unknown code")
    return RedirectResponse(url=row["url"], status_code=307)

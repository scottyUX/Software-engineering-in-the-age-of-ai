import sqlite3
import string
from typing import Optional
from contextlib import closing
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

DB_PATH = Path(__file__).parent / "links.db"
ALPHABET = string.ascii_letters + string.digits

app = FastAPI(title="Link Shortener")

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            url TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn

def encode(num: int) -> str:
    if num == 0:
        return ALPHABET[0]
    arr = []
    base = len(ALPHABET)
    while num:
        num, rem = divmod(num, base)
        arr.append(ALPHABET[rem])
    arr.reverse()
    return "".join(arr)

class ShortenRequest(BaseModel):
    url: str
    custom_slug: Optional[str] = None

@app.post("/shorten")
def shorten(req: ShortenRequest):
    if not req.url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="url must start with http:// or https://")
    
    with closing(get_db()) as conn:
        if req.custom_slug:
            existing = conn.execute("SELECT code FROM links WHERE code = ?", (req.custom_slug,)).fetchone()
            if existing:
                raise HTTPException(status_code=400, detail="Custom slug already in use")
            code = req.custom_slug
            cur = conn.execute("INSERT INTO links (url) VALUES (?)", (req.url,))
            row_id = cur.lastrowid
            conn.execute("UPDATE links SET code = ? WHERE id = ?", (code, row_id))
        else:
            cur = conn.execute("INSERT INTO links (url) VALUES (?)", (req.url,))
            row_id = cur.lastrowid
            code = encode(row_id)
            conn.execute("UPDATE links SET code = ? WHERE id = ?", (code, row_id))

        conn.commit()
        return {"code": code, "short_url": f"/{code}"}

@app.get("/{code}")
def redirect(code: str):
    with closing(get_db()) as conn:
        row = conn.execute("SELECT url FROM links WHERE code = ?", (code,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="unknown code")
        return RedirectResponse(url=row["url"], status_code=307)
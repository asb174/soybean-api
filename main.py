from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    conn = sqlite3.connect("soybean.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS entries ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "weight REAL, "
        "date TEXT)"
    )
    conn.commit()
    conn.close()

init_db()

class WeightEntry(BaseModel):
    weight: float
    date: str

@app.get("/")
def read_root():
        return {"message": "Hello, Soybean"}

@app.post("/entries")
def create_entry(entry: WeightEntry):
    conn = get_db()
    conn.execute(
        "INSERT INTO entries (weight, date) VALUES (?, ?)",
        (entry.weight, entry.date),
    )
    conn.commit()
    conn.close()
    return entry

@app.get("/entries")
def get_entries():
    conn = get_db()
    rows = conn.execute("SELECT * FROM entries").fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.put("/entries/{entry_id}")
def update_entry(entry_id: int, entry: WeightEntry):
    conn = get_db()
    conn.execute(
        "UPDATE entries SET weight = ?, date = ? WHERE id = ?",
        (entry.weight, entry.date, entry_id),
    )
    conn.commit()
    conn.close()
    return {"id": entry_id, "weight": entry.weight, "date": entry.date}

@app.delete("/entries/{entry_id}")
def delete_entry(entry_id: int):
    conn = get_db()
    conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()
    return {"message": f"Entry {entry_id} deleted"}
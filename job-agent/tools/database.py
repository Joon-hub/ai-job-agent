"""SQLite store for job listings."""
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional

DB_PATH = Path(__file__).parent.parent / "data" / "jobs.db"


def _conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    with _conn() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                url      TEXT UNIQUE,
                title    TEXT,
                company  TEXT,
                location TEXT,
                description TEXT,
                source   TEXT,
                score    REAL DEFAULT 0,
                applied  INTEGER DEFAULT 0,
                seen     INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS cv_outputs (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                job_url    TEXT,
                file_path  TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)


def save_jobs(jobs: List[Dict]) -> int:
    """Insert new jobs, skip duplicates. Returns count of new rows."""
    new_count = 0
    with _conn() as con:
        for j in jobs:
            try:
                con.execute(
                    "INSERT INTO jobs (url, title, company, location, description, source) VALUES (?,?,?,?,?,?)",
                    (j["url"], j["title"], j["company"], j["location"], j["description"], j["source"]),
                )
                new_count += 1
            except sqlite3.IntegrityError:
                pass  # already exists
    return new_count


def get_unseen_jobs(limit: int = 20) -> List[Dict]:
    with _conn() as con:
        con.row_factory = sqlite3.Row
        rows = con.execute(
            "SELECT * FROM jobs WHERE seen=0 ORDER BY score DESC, created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def update_score(job_id: int, score: float):
    with _conn() as con:
        con.execute("UPDATE jobs SET score=? WHERE id=?", (score, job_id))


def mark_seen(job_ids: List[int]):
    with _conn() as con:
        con.executemany("UPDATE jobs SET seen=1 WHERE id=?", [(i,) for i in job_ids])


def save_cv_output(job_url: str, file_path: str):
    with _conn() as con:
        con.execute("INSERT INTO cv_outputs (job_url, file_path) VALUES (?,?)", (job_url, file_path))

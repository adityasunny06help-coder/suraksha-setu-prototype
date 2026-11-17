"""SQLite access — path env-configurable, failure par graceful.

- SS_DB_PATH env sabse pehle (tests + Vercel par /tmp ke liye).
- Default: backend/data/suraksha.db (local dev).
- Default path fail ho (serverless par read-only FS) to /tmp fallback.
- Woh bhi fail ho to None — app bina DB ke chalti hai (alerts fresh fetch,
  counters best-effort skip). DB kabhi request ko crash nahi karti.
"""
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

BASE = Path(__file__).resolve().parent


def _candidates():
    env = os.environ.get("SS_DB_PATH")
    if env:
        yield env
    yield str(BASE / "data" / "suraksha.db")
    yield "/tmp/suraksha-setu.db"


def connect():
    seen = set()
    for path in _candidates():
        if path in seen:
            continue
        seen.add(path)
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(path)
            conn.executescript((BASE / "schema.sql").read_text(encoding="utf-8"))
            conn.commit()
            return conn
        except Exception:
            continue
    return None


def bump_counter(is_danger):
    """Anonymous daily counter — user ka text yahan KABHI nahi aata."""
    conn = connect()
    if conn is None:
        return
    try:
        today = datetime.now(ZoneInfo("Asia/Kolkata")).date().isoformat()
        conn.execute(
            "INSERT INTO daily_counters(date, total_scans, danger_count) VALUES(?, 1, ?) "
            "ON CONFLICT(date) DO UPDATE SET total_scans = total_scans + 1, danger_count = danger_count + ?",
            (today, 1 if is_danger else 0, 1 if is_danger else 0),
        )
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()

"""Vercel serverless entrypoint.

Vercel ka Python runtime /api ke neeche wali files ko serverless functions
banata hai aur ASGI `app` ko uthata hai. Asli app backend/main.py me hai —
ye file sirf use import karti hai taaki local (uvicorn) aur Vercel par
EK HI code chale. Routing: vercel.json /api/* ko yahan rewrite karta hai.

SQLite Vercel par: SS_DB_PATH env se path badal sakte ho; default local
path fail ho to db.py /tmp par girta hai, woh bhi fail ho to app bina DB
ke chalti hai (alerts fresh fetch, counters best-effort).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))

from main import app  # noqa: E402,F401 — Vercel isi `app` ko serve karta hai

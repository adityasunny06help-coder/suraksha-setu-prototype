"""Suraksha Setu v4 — FastAPI backend.

Endpoints:
  GET  /api/health  — liveness
  POST /api/check   — Python engine se analysis + RDAP domain-age (LIVE signal)
  GET  /api/alerts  — live scam-alert headlines (RSS + SQLite cache)

Privacy: scan ka user-text kahin store NAHI hota — sirf anonymous daily
counters (db.bump_counter) badhte hain. SSRF discipline: user ka URL
server se kabhi fetch nahi hota; sirf domain ka RDAP record dekha jata hai.
"""
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import alerts as alerts_mod
import db
import engine
import rdap

app = FastAPI(title="Suraksha Setu API", version="4.0")

# CORS sirf local dev origins ke liye — production me frontend same-origin hai (Vercel/Pages+backend alag ho to origin yahan jodo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080", "http://127.0.0.1:8080",
        "http://localhost:8000", "http://127.0.0.1:8000",
        "http://localhost:3000", "http://127.0.0.1:3000",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class CheckIn(BaseModel):
    input: str = Field(..., min_length=1, max_length=4000)


def _norm_reasons(reasons):
    out = []
    for r in reasons[:7]:
        if isinstance(r, (list, tuple)):
            out.append({"points": r[0], "text": r[1]})
        else:
            out.append({"points": 0, "text": r})
    return out


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "4.0", "time": datetime.now(timezone.utc).isoformat()}


@app.post("/api/check")
def check(body: CheckIn):
    text = body.input.strip()
    now = datetime.now(timezone.utc).isoformat()
    if not text:
        return {"score": 0, "kind": "Empty", "reasons": [], "domain": None,
                "domain_age": None, "checked_at": now}
    result = engine.scan(text)
    dom = engine.extract_domain(text)
    age = None
    if dom:
        raw_age = rdap.domain_age(dom["registrable"])
        if raw_age is not None:
            pts, note = rdap.risk_points(raw_age)
            age = dict(raw_age)
            age["risk_points"] = pts
            age["note"] = note
    db.bump_counter(result["score"] >= 85)
    b = engine.band(result["score"])
    return {
        "score": result["score"],
        "band": b["label"],
        "band_class": b["css"],
        "guidance": b["guidance"],
        "kind": result.get("kind"),
        "reasons": _norm_reasons(result["reasons"]),
        "domain": ({"host": dom["host"], "registrable": dom["registrable"], "official": dom["official"]} if dom else None),
        "domain_age": age,
        "checked_at": now,
    }


@app.get("/api/alerts")
def get_alerts():
    return alerts_mod.get_alerts()

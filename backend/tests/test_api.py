import importlib.util
import os
import sqlite3

from fastapi.testclient import TestClient

import main

client = TestClient(main.app)

FAKE_AGE = {"found": True, "registered_on": "2025-08-11", "age_days": 99,
            "source": "rdap.org", "fetched_at": "2026-11-18T00:00:00+00:00"}
FAKE_NOT_FOUND = {"found": False, "registered_on": None, "age_days": None,
                  "source": "rdap.org", "fetched_at": "2026-11-18T00:00:00+00:00"}


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_check_official_with_mocked_rdap(monkeypatch):
    monkeypatch.setattr(main.rdap, "domain_age", lambda d: dict(FAKE_AGE))
    r = client.post("/api/check", json={"input": "https://www.sbi.bank.in"})
    j = r.json()
    assert r.status_code == 200
    assert j["score"] == 0
    assert j["domain"]["host"] == "www.sbi.bank.in"
    assert j["domain_age"]["age_days"] == 99


def test_check_scam_link_rdap_not_found(monkeypatch):
    monkeypatch.setattr(main.rdap, "domain_age", lambda d: dict(FAKE_NOT_FOUND))
    r = client.post("/api/check", json={"input": "https://sbi-kyc-verify.top/login"})
    j = r.json()
    assert j["score"] == 85
    assert j["domain_age"]["found"] is False
    assert j["domain_age"]["risk_points"] == 20


def test_check_rdap_unavailable_degrades(monkeypatch):
    monkeypatch.setattr(main.rdap, "domain_age", lambda d: None)
    r = client.post("/api/check", json={"input": "9876543210"})
    j = r.json()
    assert r.status_code == 200 and j["score"] == 30 and j["domain_age"] is None


def test_check_rdap_exception_never_500(monkeypatch):
    # Deep-review Round 2: RDAP enrichment khud exception phenke to bhi
    # main jawab 500 nahi hona chahiye — signal gayab, score engine ka.
    def boom(d):
        raise RuntimeError("rdap exploded")
    monkeypatch.setattr(main.rdap, "domain_age", boom)
    r = client.post("/api/check", json={"input": "https://www.sbi.bank.in"})
    assert r.status_code == 200
    j = r.json()
    assert j["score"] == 0 and j["domain_age"] is None


def test_check_validation():
    assert client.post("/api/check", json={"input": ""}).status_code == 422
    assert client.post("/api/check", json={"input": "x" * 4001}).status_code == 422
    assert client.post("/api/check", json={}).status_code == 422


def test_privacy_no_user_text_in_db():
    marker = "ZXQWUNIQUE789"
    client.post("/api/check", json={"input": "message " + marker + " share otp batao"})
    dbfile = os.environ["SS_DB_PATH"]
    with open(dbfile, "rb") as f:
        assert marker.encode() not in f.read()
    rows = sqlite3.connect(dbfile).execute("SELECT total_scans FROM daily_counters").fetchall()
    assert rows and rows[0][0] >= 1


def test_vercel_entrypoint_imports_and_serves():
    root = os.path.join(os.path.dirname(__file__), "..", "..")
    spec = importlib.util.spec_from_file_location("vercel_index", os.path.join(root, "api", "index.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    c = TestClient(mod.app)
    assert c.get("/api/health").json()["status"] == "ok"

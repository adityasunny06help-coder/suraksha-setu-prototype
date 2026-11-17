"""RDAP domain-age lookup — v4 ka ekmatra LIVE signal (server side).

SSRF discipline: user ke diye URL ko server KABHI fetch nahi karta.
Sirf registrable domain ka RDAP record (https://rdap.org/domain/<domain>)
dekha jata hai — woh bhi registry ke server se, user ki site se nahi.

Result SQLite me 24h cache hota hai (public data hai). RDAP fail/timeout
ho to None — caller bina is signal ke jawab deta hai.
"""
from datetime import datetime, timezone

from db import connect
from net import make_client

CACHE_TTL_HOURS = 24


def parse_rdap(data):
    """RDAP JSON se registration date (ISO string) nikalo — pure function, testable."""
    for e in (data or {}).get("events") or []:
        if e.get("eventAction") == "registration":
            return e.get("eventDate")
    return None


def _cache_get(domain):
    conn = connect()
    if conn is None:
        return None
    try:
        row = conn.execute(
            "SELECT found, registered_on, fetched_at FROM rdap_cache WHERE domain = ?", (domain,)
        ).fetchone()
        if not row:
            return None
        found, registered_on, fetched_at = row
        age_h = (datetime.now(timezone.utc) - datetime.fromisoformat(fetched_at)).total_seconds() / 3600
        if age_h > CACHE_TTL_HOURS:
            return None
        out = {"found": bool(found), "registered_on": registered_on, "source": "rdap.org", "fetched_at": fetched_at}
        if registered_on:
            reg_dt = datetime.fromisoformat(registered_on)
            out["age_days"] = (datetime.now(timezone.utc) - reg_dt).days
        else:
            out["age_days"] = None
        return out
    except Exception:
        return None
    finally:
        conn.close()


def _cache_put(domain, found, registered_on_iso, fetched_at):
    conn = connect()
    if conn is None:
        return
    try:
        conn.execute(
            "INSERT INTO rdap_cache(domain, found, registered_on, fetched_at) VALUES(?, ?, ?, ?) "
            "ON CONFLICT(domain) DO UPDATE SET found = excluded.found, registered_on = excluded.registered_on, fetched_at = excluded.fetched_at",
            (domain, 1 if found else 0, registered_on_iso, fetched_at),
        )
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()


def _endpoints(domain):
    """RDAP endpoints koshish ke kram me. rdap.org bootstrap pehle;
    .com/.net par Verisign direct fallback (audit finding: rdap.org ka
    Verisign redirect kuch networks par slow/flaky hota hai, direct chal jata hai)."""
    eps = [("https://rdap.org/domain/" + domain, "rdap.org")]
    tld = domain.rsplit(".", 1)[-1] if "." in domain else ""
    if tld in ("com", "net"):
        eps.append(("https://rdap.verisign.com/" + tld + "/v1/domain/" + domain, "rdap.verisign.com"))
    return eps


def domain_age(domain):
    """{found, registered_on, age_days, source, fetched_at} ya None (lookup fail)."""
    if not domain:
        return None
    cached = _cache_get(domain)
    if cached:
        return cached
    now = datetime.now(timezone.utc)
    fetched_at = now.isoformat()
    client = make_client(timeout=8.0)
    if client is None:
        return None
    try:
        with client:
            for url, source in _endpoints(domain):
                try:
                    r = client.get(url)
                except Exception:
                    continue  # agla endpoint try karo
                if r.status_code == 404:
                    # Registry ne saaf kaha: koi record nahi — ye khud ek signal hai
                    out = {"found": False, "registered_on": None, "age_days": None, "source": source, "fetched_at": fetched_at}
                    _cache_put(domain, False, None, fetched_at)
                    return out
                if r.status_code != 200:
                    continue
                reg = parse_rdap(r.json())
                if not reg:
                    continue
                reg_dt = datetime.fromisoformat(reg.replace("Z", "+00:00"))
                out = {
                    "found": True,
                    "registered_on": reg_dt.date().isoformat(),
                    "age_days": (now - reg_dt).days,
                    "source": source,
                    "fetched_at": fetched_at,
                }
                _cache_put(domain, True, reg_dt.isoformat(), fetched_at)
                return out
        return None
    except Exception:
        return None


def risk_points(age):
    """Domain-age se advisory risk points (ye /api/check ke main score me
    NAHI judte — alag signal ke roop me dikhte hain, parity gate safe rahe)."""
    if not age:
        return 0, ""
    if not age.get("found"):
        return 20, "RDAP me is domain ka registration record nahi mila — bana hi nahi ya turant bana hua nakli domain ho sakta hai"
    d = age.get("age_days")
    if d is None:
        return 0, ""
    if d < 30:
        return 25, "Domain sirf " + str(d) + " din purana hai — itne naye domain par bank/login page lagbhag hamesha scam hota hai"
    if d < 180:
        return 10, "Domain " + str(d) + " din purana hai — kaafi naya hai, extra savdhani rakho"
    return 0, "Domain " + str(d) + " din purana hai — umar ke hisaab se theek hai"

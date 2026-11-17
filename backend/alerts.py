"""Live scam-alert headlines — keyless RSS, SQLite cache, stale honesty.

Feed chunav (18 Nov 2026 ko sandbox se verify — AUDIT-V4.md me record):
- PIB RSS: LIVE (200, asal RSS). Aam sarkari feed hai, isliye cyber/fraud
  keywords se filter hoti hai.
- Google News RSS (cyber fraud India search): LIVE (200). Query-scoped hai,
  isliye bina filter ke latest headlines.
- CERT-In ke RSS patterns (/Rssfeed.xml, /rss.xml): asal RSS NAHI mile —
  dono homepage HTML laute. Record karke chhoda gaya.
- RBI ke RSS patterns (/Rssfeeds/pressreleases.xml): 404. Record hai.

Cache 30 min taza rehta hai. Fetch fail ho to purana cache `stale: true`
ke saath jata hai — fetched_at hamesha asal fetch ka time hota hai,
response ka time NAHI (fetched_at honesty rule).
"""
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from db import connect
from net import make_client

TTL_SECONDS = 1800

KEYWORDS = ["cyber", "scam", "fraud", "upi", "phishing", "digital arrest",
            "cybercrime", "online fraud", "साइबर", "धोखाधड़ी", "धोखाधडी", "ठगी"]

FEEDS = [
    {"source": "PIB (Press Information Bureau)",
     "url": "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3",
     "keywords": KEYWORDS},
    {"source": "Google News — Cyber Fraud India",
     "url": "https://news.google.com/rss/search?q=cyber+fraud+scam+india+when:7d&hl=en-IN&gl=IN&ceid=IN:en",
     "keywords": None},
]


def parse_feed(xml_bytes, source, keywords):
    """RSS XML -> [{source, title, link, published_at}] — pure function, testable.
    Kharab XML par exception — caller per-feed isolation se sambhalta hai."""
    root = ET.fromstring(xml_bytes)
    items = []
    for it in root.iter("item"):
        title = " ".join((it.findtext("title") or "").split())
        link = (it.findtext("link") or "").strip()
        if not title or not link.startswith("http"):
            continue
        if keywords and not any(k in title.lower() for k in keywords):
            continue
        pub = None
        raw_pub = it.findtext("pubDate")
        if raw_pub:
            try:
                pub = parsedate_to_datetime(raw_pub).isoformat()
            except Exception:
                pub = None
        items.append({"source": source, "title": title, "link": link, "published_at": pub})
    return items


def _fetch_feed(feed):
    client = make_client(timeout=10.0)
    if client is None:
        raise RuntimeError("http client unavailable")
    with client:
        r = client.get(feed["url"])
    if r.status_code != 200:
        raise RuntimeError("feed HTTP " + str(r.status_code))
    return parse_feed(r.content, feed["source"], feed["keywords"])


def _status(source, ok, count, fetched_at):
    conn = connect()
    if conn is None:
        return
    try:
        conn.execute(
            "INSERT INTO feed_status(source, ok, item_count, fetched_at) VALUES(?, ?, ?, ?) "
            "ON CONFLICT(source) DO UPDATE SET ok = excluded.ok, item_count = excluded.item_count, fetched_at = excluded.fetched_at",
            (source, ok, count, fetched_at),
        )
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()


def _save_feed(source, items, fetched_at):
    conn = connect()
    if conn is None:
        return
    try:
        conn.execute("DELETE FROM alerts_cache WHERE source = ?", (source,))
        conn.executemany(
            "INSERT INTO alerts_cache(source, title, link, published_at, fetched_at) VALUES(?, ?, ?, ?, ?)",
            [(source, i["title"], i["link"], i["published_at"], fetched_at) for i in items],
        )
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()


def _read_cache():
    conn = connect()
    if conn is None:
        return [], None
    try:
        rows = conn.execute(
            "SELECT source, title, link, published_at, fetched_at FROM alerts_cache"
        ).fetchall()
        if not rows:
            return [], None
        items = [{"source": r[0], "title": r[1], "link": r[2], "published_at": r[3]} for r in rows]
        items.sort(key=lambda x: x["published_at"] or "", reverse=True)
        return items, max(r[4] for r in rows)
    except Exception:
        return [], None
    finally:
        conn.close()


def get_alerts():
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    cached_items, cached_at = _read_cache()
    if cached_items and cached_at:
        age = (now - datetime.fromisoformat(cached_at)).total_seconds()
        if age < TTL_SECONDS:
            return {"items": cached_items[:10], "fetched_at": cached_at, "stale": False}
    any_ok = False
    for feed in FEEDS:
        try:
            items = _fetch_feed(feed)
            _save_feed(feed["source"], items, now_iso)
            _status(feed["source"], 1, len(items), now_iso)
            any_ok = True
        except Exception:
            _status(feed["source"], 0, 0, now_iso)
    if any_ok:
        items, fetched = _read_cache()
        return {"items": items[:10], "fetched_at": fetched or now_iso, "stale": False}
    if cached_items:
        return {"items": cached_items[:10], "fetched_at": cached_at, "stale": True}
    return {"items": [], "fetched_at": None, "stale": True}

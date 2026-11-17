import pytest

import alerts

RSS = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>Test</title>
<item><title>Big cyber fraud busted in Delhi</title><link>https://example.com/a</link><pubDate>Mon, 17 Nov 2026 10:00:00 GMT</pubDate></item>
<item><title>Monsoon session begins in Parliament</title><link>https://example.com/b</link><pubDate>Mon, 17 Nov 2026 09:00:00 GMT</pubDate></item>
</channel></rss>"""


def test_parse_feed_keyword_filter():
    items = alerts.parse_feed(RSS, "PIB (Press Information Bureau)", alerts.KEYWORDS)
    assert len(items) == 1 and "fraud" in items[0]["title"]


def test_parse_feed_no_filter():
    items = alerts.parse_feed(RSS, "Google News", None)
    assert len(items) == 2
    assert items[0]["published_at"] is not None


def test_parse_feed_bad_xml_raises():
    # Per-feed isolation isi par nirbhar hai: kharab feed exception degi,
    # get_alerts use pakad kar doosri feed ko chalne dega
    with pytest.raises(Exception):
        alerts.parse_feed(b"<rss><channel><item>", "x", None)


def _down(feed):
    raise RuntimeError("feed down")


def test_get_alerts_all_down_empty_cache(monkeypatch):
    monkeypatch.setattr(alerts, "_fetch_feed", _down)
    out = alerts.get_alerts()
    assert out["items"] == [] and out["stale"] is True and out["fetched_at"] is None


def test_get_alerts_one_feed_down_other_survives(monkeypatch):
    def fetch(feed):
        if "PIB" in feed["source"]:
            raise RuntimeError("pib down")
        return alerts.parse_feed(RSS, feed["source"], feed["keywords"])
    monkeypatch.setattr(alerts, "_fetch_feed", fetch)
    out = alerts.get_alerts()
    assert out["stale"] is False
    assert len(out["items"]) == 2
    assert out["fetched_at"] is not None

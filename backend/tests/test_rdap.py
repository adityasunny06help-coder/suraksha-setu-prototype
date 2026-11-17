import rdap

RDAP_JSON = {"events": [{"eventAction": "registration", "eventDate": "1997-09-15T04:00:00Z"},
                        {"eventAction": "expiration", "eventDate": "2028-09-14T04:00:00Z"}]}


class FakeResp:
    def __init__(self, status, data=None):
        self.status_code = status
        self._data = data

    def json(self):
        return self._data


class FakeClient:
    def __init__(self, resp):
        self._resp = resp

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def get(self, url):
        return self._resp


def test_parse_rdap():
    assert rdap.parse_rdap(RDAP_JSON) == "1997-09-15T04:00:00Z"
    assert rdap.parse_rdap({}) is None
    assert rdap.parse_rdap(None) is None


def test_domain_age_found(monkeypatch):
    monkeypatch.setattr(rdap, "make_client", lambda timeout=8.0: FakeClient(FakeResp(200, RDAP_JSON)))
    out = rdap.domain_age("google.com")
    assert out["found"] is True
    assert out["registered_on"] == "1997-09-15"
    assert out["age_days"] > 10000


def test_domain_age_not_found(monkeypatch):
    monkeypatch.setattr(rdap, "make_client", lambda timeout=8.0: FakeClient(FakeResp(404)))
    out = rdap.domain_age("sbi-kyc-verify.top")
    assert out["found"] is False and out["age_days"] is None


def test_domain_age_client_unavailable(monkeypatch):
    monkeypatch.setattr(rdap, "make_client", lambda timeout=8.0: None)
    assert rdap.domain_age("example.com") is None


class RoutingClient:
    """rdap.org par 500, Verisign par 200 — fallback ka saboot."""
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def get(self, url):
        if "rdap.org" in url:
            return FakeResp(500)
        return FakeResp(200, RDAP_JSON)


def test_domain_age_verisign_fallback(monkeypatch):
    monkeypatch.setattr(rdap, "make_client", lambda timeout=8.0: RoutingClient())
    out = rdap.domain_age("google.com")
    assert out["found"] is True and out["source"] == "rdap.verisign.com"


def test_endpoints_order():
    eps = rdap._endpoints("google.com")
    assert eps[0][1] == "rdap.org" and eps[1][1] == "rdap.verisign.com"
    assert len(rdap._endpoints("sbi.bank.in")) == 1


def test_risk_points():
    assert rdap.risk_points(None)[0] == 0
    assert rdap.risk_points({"found": False})[0] == 20
    assert rdap.risk_points({"found": True, "age_days": 5})[0] == 25
    assert rdap.risk_points({"found": True, "age_days": 90})[0] == 10
    assert rdap.risk_points({"found": True, "age_days": 900})[0] == 0

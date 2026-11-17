"""Cross-language parity gate: Python engine == JavaScript engine.
6 built-in samples ke scores dono me bilkul wahi: 85/0/85/85/30/0."""
import engine


def test_six_samples_parity():
    for sample, expected in zip(engine.SAMPLES, engine.EXPECTED_SCORES):
        r = engine.scan(sample)
        assert r is not None, sample
        assert r["score"] == expected, sample


def test_official_apk_no_contradiction():
    # v3.1 fix: official domain par hard rules nahi chalte — score 0 ke saath
    # "+85 APK" jaisi contradictory reason nahi aani chahiye
    r = engine.scan("https://www.sbi.bank.in/yono.apk")
    assert r["score"] == 0
    assert all((x[0] if isinstance(x, (list, tuple)) else 0) == 0 for x in r["reasons"])


def test_email_is_not_upi():
    # v3.1 fix: email ko UPI samajh kar phantom handle reason nahi chipakni chahiye
    r = engine.scan("abc@gmail.com")
    assert r["score"] == 0
    texts = [x[1] if isinstance(x, (list, tuple)) else x for x in r["reasons"]]
    assert not any("Handle '@gmai" in t for t in texts)


def test_lookalike_upi_handle_hard():
    r = engine.scan("sbirefund@okhdfcbnak")
    assert r["score"] == 85


def test_extract_domain():
    d = engine.extract_domain("https://www.sbi.bank.in/path")
    assert d["registrable"] == "sbi.bank.in" and d["official"] is True
    assert engine.extract_domain("koi link nahi hai isme") is None
    assert engine.extract_domain("http://192.168.1.1/login") is None

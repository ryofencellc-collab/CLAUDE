import base64
import json

import pandas as pd
import pytest

from edge import live21 as L


@pytest.fixture
def key_pem():
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    k = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = k.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    return k, pem.decode()


def test_signature_verifies_with_public_key(key_pem):
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    k, pem = key_pem
    h = L.Kalshi("kid", pem)._headers("POST", "/trade-api/v2/portfolio/orders?x=1")
    msg = (h["KALSHI-ACCESS-TIMESTAMP"] + "POST" + "/trade-api/v2/portfolio/orders").encode()   # query excluded
    k.public_key().verify(base64.b64decode(h["KALSHI-ACCESS-SIGNATURE"]), msg,
                          padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH),
                          hashes.SHA256())
    assert h["KALSHI-ACCESS-KEY"] == "kid"


def test_order_is_post_only_99c_limit_buy():
    b = L.order_body("KXBTC15M-X", "no", 1000)
    assert b["action"] == "buy" and b["type"] == "limit" and b["post_only"] is True
    assert b["no_price"] == 99 and "yes_price" not in b and b["count"] == 1000
    assert b["client_order_id"].startswith("r21-")


def test_sizing_and_risk_rules():
    st = {"pause_until": 0.0, "half_until": 0.0, "day": "", "day_start_balance": 1000.0, "day_loss": 0.0,
          "open": None, "results": []}
    now = 1_000_000.0
    assert L.size_for(1000.0, st, now) == 959                    # 95% of balance at 99c
    assert L.size_for(50_000.0, st, now) == L.MAX_CONTRACTS        # capped
    L.record_result(st, now, -950.0)
    assert L.blocked(st, now + 60, 1000.0) is not None              # paused 24 h (and daily stop)
    st["day_loss"] = 0.0
    assert L.blocked(st, now + 25 * 3600, 1000.0) is None           # pause over
    assert L.size_for(1000.0, st, now + 25 * 3600) == 959 // 2     # half size for 7 days
    assert L.size_for(1000.0, st, now + 9 * 86400) == 959


def test_daily_stop():
    st = {"pause_until": 0.0, "half_until": 0.0, "day": "d", "day_start_balance": 1000.0, "day_loss": 120.0,
           "open": None, "results": []}
    assert L.blocked(st, 0.0, 1000.0) == "daily loss limit"


def test_dry_step_places_once_and_cancels_when_undecided(monkeypatch, tmp_path):
    monkeypatch.setattr(L, "LOG", tmp_path / "log.csv")
    monkeypatch.setattr(L, "STOP", tmp_path / "STOP")
    now = pd.Timestamp("2026-11-04 12:10", tz="UTC")
    market = {"ticker": "KXBTC15M-26NOV041215-15", "strike_type": "greater_or_equal", "floor_strike": 100.0,
              "cap_strike": None, "_close": pd.Timestamp("2026-11-04 12:15", tz="UTC")}
    monkeypatch.setattr(L, "decide", lambda now: (market, "KXBTC15M", "yes", 7.0, 101.0))
    monkeypatch.setattr(L.sig, "queue_ahead", lambda t, s: 500.0)
    st = {"pause_until": 0.0, "half_until": 0.0, "day": "", "day_start_balance": 0.0, "day_loss": 0.0, "open": None, "results": []}
    api = L.Kalshi(None, None)
    L.step(api, st, "DRY", now)
    assert st["open"]["ticker"] == market["ticker"] and st["open"]["count"] == 1000
    L.step(api, st, "DRY", now)                                         # one position at a time
    assert len(pd.read_csv(tmp_path / "log.csv").query("event == 'place'")) == 1
    monkeypatch.setattr(L, "still_decided", lambda o, now: False)
    L.step(api, st, "DRY", now + pd.Timedelta(seconds=30))
    assert st["open"]["cancelled"] is True


def test_summary_reads_settled_pnl(monkeypatch, tmp_path):
    monkeypatch.setattr(L, "LOG", tmp_path / "log.csv")
    L.log("DRY", "place", "T1", "yes", 1000)
    L.log("DRY", "settled", "T1", "yes", 1000, detail="result=yes pnl=9.82")
    L.log("DRY", "settled", "T2", "no", 0, detail="result=no pnl=0.00")
    text = L.summary()
    assert "$+9.82" in text and "Settled markets / with fills | 2 / 1" in text

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
    monkeypatch.setattr(L, "decide", lambda now: (market, "KXBTC15M", "yes", 7.0, 101.0, 500.0))
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



class FakeApi:
    """Stands in for Kalshi in LIVE-mode tests: records calls, can be told to fail."""
    def __init__(self, resting=(), positions=(), fail_buy=False):
        self.authed, self._resting, self._positions, self.fail_buy = True, list(resting), list(positions), fail_buy
        self.cancelled, self.bought = [], []

    def balance_usd(self):
        return 1000.0

    def resting(self):
        return self._resting

    def positions(self):
        return self._positions

    def buy(self, ticker, side, count, cents=99):
        if self.fail_buy:
            raise RuntimeError("post-only would cross")
        self.bought.append((ticker, side, count))
        return {"order_id": "oid-1", "status": "resting"}

    def cancel(self, order_id):
        self.cancelled.append(order_id)


def fresh():
    return {"pause_until": 0.0, "half_until": 0.0, "day": "", "day_start_balance": 0.0, "day_loss": 0.0, "open": None, "results": []}


MARKET = {"ticker": "KXXRP15M-X", "strike_type": "greater_or_equal", "floor_strike": 1.0, "cap_strike": None,
          "_close": pd.Timestamp("2026-11-04 12:15", tz="UTC")}


def test_decide_takes_shortest_queue(monkeypatch):
    a = ({**MARKET, "ticker": "KXBTC15M-A"}, "KXBTC15M", "yes", 9.0, 1.0)
    b = ({**MARKET, "ticker": "KXXRP15M-B"}, "KXXRP15M", "no", 7.0, 1.0)
    monkeypatch.setattr(L, "candidates", lambda now: [a, b])
    monkeypatch.setattr(L.sig, "queue_ahead", lambda t, s: {"KXBTC15M-A": 480000.0, "KXXRP15M-B": 300.0}[t])
    pick = L.decide(pd.Timestamp("2026-11-04 12:10", tz="UTC"))
    assert pick[0]["ticker"] == "KXXRP15M-B" and pick[-1] == 300.0


def test_live_tracks_order_and_redacts_balance(monkeypatch, tmp_path):
    monkeypatch.setattr(L, "LOG", tmp_path / "log.csv")
    monkeypatch.setattr(L, "STATE", tmp_path / "state.json")
    monkeypatch.setattr(L, "STOP", tmp_path / "STOP")
    monkeypatch.setattr(L, "decide", lambda now: (MARKET, "KXXRP15M", "yes", 7.0, 1.05, 200.0))
    api, st = FakeApi(), fresh()
    L.step(api, st, "LIVE", pd.Timestamp("2026-11-04 12:10", tz="UTC"))
    assert api.bought == [("KXXRP15M-X", "yes", 959)] and st["open"]["order_id"] == "oid-1"
    assert pd.read_csv(tmp_path / "log.csv")["balance"].isna().all()       # never written in LIVE


def test_rejected_order_leaves_nothing_tracked(monkeypatch, tmp_path):
    monkeypatch.setattr(L, "LOG", tmp_path / "log.csv")
    monkeypatch.setattr(L, "STOP", tmp_path / "STOP")
    monkeypatch.setattr(L, "decide", lambda now: (MARKET, "KXXRP15M", "yes", 7.0, 1.05, 200.0))
    api, st = FakeApi(fail_buy=True), fresh()
    with pytest.raises(RuntimeError):
        L.step(api, st, "LIVE", pd.Timestamp("2026-11-04 12:10", tz="UTC"))
    assert st["open"] is None


def test_open_position_blocks_new_orders(monkeypatch, tmp_path):
    monkeypatch.setattr(L, "LOG", tmp_path / "log.csv")
    monkeypatch.setattr(L, "STOP", tmp_path / "STOP")
    monkeypatch.setattr(L, "decide", lambda now: (MARKET, "KXXRP15M", "yes", 7.0, 1.05, 200.0))
    api, st = FakeApi(positions=[{"ticker": "OLD", "position": 500}]), fresh()
    L.step(api, st, "LIVE", pd.Timestamp("2026-11-04 12:10", tz="UTC"))
    assert api.bought == [] and st["open"] is None


def test_sweep_cancels_only_untracked_orders_of_ours(monkeypatch, tmp_path):
    monkeypatch.setattr(L, "LOG", tmp_path / "log.csv")
    api = FakeApi(resting=[{"order_id": "keep", "client_order_id": "r21-a"}, {"order_id": "stray", "client_order_id": "r21-b"},
                           {"order_id": "manual", "client_order_id": "my-own-order"}])
    st = fresh()
    st["open"] = {"order_id": "keep"}
    L.sweep_strays(api, st, "LIVE")
    assert api.cancelled == ["stray"]                                    # never touches orders the bot did not place


def test_rebuild_risk_from_settlements():
    class A:
        def recent_settlement_pnls(self, since):
            return [(1000.0, 9.8), (2000.0, -951.0)]
    st = fresh()
    L.rebuild_risk(A(), st, 2500.0)
    assert st["pause_until"] == 2000.0 + 24 * 3600 and st["half_until"] == 2000.0 + 24 * 3600 + 7 * 86400


def test_num_parses_cents_dollars_and_fixed_point():
    assert L.num({"balance": 123456}, "balance", scale=0.01) == 1234.56
    assert L.num({"count_fp": "250.00"}, "count_fp", "count") == 250.0
    assert L.num({"count": 7}, "count_fp", "count") == 7.0
    assert L.num({}, "x") == 0.0

import numpy as np
import pandas as pd

from edge import paper21 as p


class R:
    def __init__(self, j):
        self.status_code, self._j = 200, j

    def json(self):
        return self._j


def row(**kw):
    base = dict(ticker="T", series="KXBTCD", side="yes", strike=100.0, close_utc="2026-10-30T12:00:00+00:00",
                placed_utc="2026-10-30T11:50:00+00:00", z_at_place=7.0, spot_at_place=110.0, queue_ahead=500.0,
                seen=0.0, filled=0.0, status="open", cancelled_utc="", result="", pnl=np.nan, settled_utc="")
    base.update(kw)
    return pd.DataFrame([base])[p.COLS]


def test_z_sign_and_size():
    now, close = pd.Timestamp("2026-10-30 11:55", tz="UTC"), pd.Timestamp("2026-10-30 12:00", tz="UTC")
    assert p.z_for(101.0, 0.0005, 100.0, close, now) > 6
    assert p.z_for(99.0, 0.0005, 100.0, close, now) < -6


def test_cancel_when_z_drops_and_fill_after_queue(monkeypatch):
    now = pd.Timestamp("2026-10-30 11:55", tz="UTC")
    monkeypatch.setattr(p, "spot_and_vol", lambda prod, now: (100.01, 0.002))   # z near 0: no longer decided
    monkeypatch.setattr(p, "seen_since", lambda t, s, a, b: 800.0)
    led = p.watch(row(), now, count_fills=True)
    assert led.at[0, "status"] == "cancelled" and led.at[0, "filled"] == 300


def test_settle_win_and_loss(monkeypatch):
    now = pd.Timestamp("2026-10-30 12:05", tz="UTC")
    monkeypatch.setattr(p, "seen_since", lambda t, s, a, b: 1500.0)
    monkeypatch.setattr(p.wx, "_get", lambda url, params=None: R({"market": {"result": "yes"}}))
    led = p.watch(row(), now, count_fills=True)
    assert led.at[0, "status"] == "won" and led.at[0, "filled"] == 1000
    assert abs(led.at[0, "pnl"] - (1000 * 0.01 - p.r15._maker_fee(1000, 0.99))) < 1e-9
    monkeypatch.setattr(p.wx, "_get", lambda url, params=None: R({"market": {"result": "no"}}))
    led = p.watch(row(), now, count_fills=True)
    assert led.at[0, "status"] == "lost" and led.at[0, "pnl"] < -989
    assert "Paper profit" in p.summary(led, now)

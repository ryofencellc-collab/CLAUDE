import pandas as pd

from edge import paper18 as p


class R:
    def __init__(self, j):
        self.status_code, self._j = 200, j

    def json(self):
        return self._j


def test_queue_ahead_counts_only_99c_and_up(monkeypatch):
    book = {"orderbook_fp": {"no_dollars": [["0.9700", "50"], ["0.9900", "300"], ["0.9950", "20"]]}}
    monkeypatch.setattr(p.wx, "_get", lambda url, params=None: R(book))
    assert p.queue_ahead("T", "no") == 320
    assert p.queue_ahead("T", "yes") == 0


def test_eligible_volume_only_losing_side_takers_after_placement(monkeypatch):
    tr = pd.DataFrame({"time": pd.to_datetime(["2026-07-01 17:00", "2026-07-01 18:05", "2026-07-01 18:06",
                                               "2026-07-01 18:07"], utc=True),
                       "taker_side": ["yes", "yes", "no", "yes"], "count": [100, 40, 70, 30],
                       "yes_price": [0.01, 0.01, 0.01, 0.03], "no_price": [0.99, 0.99, 0.99, 0.97]})
    monkeypatch.setattr(p.r15, "trades", lambda t: tr)
    # before placement, our own side's takers, and fills below our 99c bid are excluded
    assert p.eligible_volume("T", "no", pd.Timestamp("2026-07-01 18:00", tz="UTC")) == 40


def _ledger(queue):
    return pd.DataFrame([dict(ticker="T", series="S", city="c", date="2026-07-01", side="no",
                              known_utc="2026-07-01T18:00:00+00:00", placed_utc="2026-07-01T18:00:00+00:00",
                              queue_ahead=queue, eligible_seen=0.0, fillable=0.0, filled=0.0, status="open",
                              result="", pnl=float("nan"), settled_utc="")])[p.COLS]


def test_fill_waits_for_queue_and_settles(monkeypatch):
    monkeypatch.setattr(p, "eligible_volume", lambda t, s, since: 1300.0)
    now = pd.Timestamp("2026-07-02 12:00", tz="UTC")
    monkeypatch.setattr(p.wx, "_get", lambda url, params=None: R({"market": {"result": ""}}))
    led = p.update(_ledger(1000.0), now)
    assert led.at[0, "fillable"] == 300 and led.at[0, "filled"] == 300 and led.at[0, "status"] == "open"
    monkeypatch.setattr(p.wx, "_get", lambda url, params=None: R({"market": {"result": "no"}}))
    led = p.update(_ledger(1000.0), now)
    assert led.at[0, "status"] == "won"
    assert abs(led.at[0, "pnl"] - (300 * 0.01 - p.r15._maker_fee(300, 0.99))) < 1e-9
    monkeypatch.setattr(p.wx, "_get", lambda url, params=None: R({"market": {"result": "yes"}}))
    led = p.update(_ledger(1000.0), now)
    assert led.at[0, "status"] == "lost" and led.at[0, "pnl"] < -290


def test_order_cap_and_no_fill_behind_queue(monkeypatch):
    monkeypatch.setattr(p, "eligible_volume", lambda t, s, since: 5000.0)
    monkeypatch.setattr(p.wx, "_get", lambda url, params=None: R({"market": {"result": "no"}}))
    led = p.update(_ledger(0.0), pd.Timestamp("2026-07-02", tz="UTC"))
    assert led.at[0, "filled"] == p.ORDER and led.at[0, "fillable"] == 5000
    led = p.update(_ledger(9000.0), pd.Timestamp("2026-07-02", tz="UTC"))
    assert led.at[0, "filled"] == 0 and led.at[0, "pnl"] == 0
    assert "Paper profit" in p.summary(led, pd.Timestamp("2026-07-02", tz="UTC"))


def test_event_ticker_format():
    assert p._event_ticker("KXHIGHNY", pd.Timestamp("2026-07-04")) == "KXHIGHNY-26JUL04"

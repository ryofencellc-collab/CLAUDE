import pandas as pd
from edge import fav


def test_favourite_side_detection():
    assert fav.favourite({"yes_bid_dollars": "0.90", "yes_ask_dollars": "0.92", "yes_bid_size_fp": "50"}) == ("yes", 0.90, 50.0)
    assert fav.favourite({"yes_bid_dollars": "0.05", "yes_ask_dollars": "0.12", "yes_ask_size_fp": "70"}) == ("no", 0.88, 70.0)
    assert fav.favourite({"yes_bid_dollars": "0.50", "yes_ask_dollars": "0.52"}) is None
    assert fav.favourite({"yes_bid_dollars": "0.97", "yes_ask_dollars": "0.98"}) is None


def test_fill_behind_queue_then_settle(tmp_path, monkeypatch):
    monkeypatch.setattr(fav, "DONE", str(tmp_path / "done.csv"))
    now = pd.Timestamp("2026-11-10T12:00:00Z")
    o = fav.new_order({"ticker": "S-E-T", "event_ticker": "S-E", "close_time": "2026-11-10T20:00:00Z"}, "yes", 0.90, 100.0, "Sports", now)
    assert o["q"] == 222
    # a taker buys NO at 10c (hits YES bids at 90c): 150 contracts, 100 ahead of us -> we get 50
    fav.lip.apply_trades(o, [{"created_time": "1", "taker_side": "no", "yes_price_dollars": "0.90", "count_fp": "150"}])
    assert o["inv_yes"] == 50
    st = {"orders": [o], "last": now.timestamp()}
    monkeypatch.setattr(fav, "get", lambda path, params=None: {"market": {"result": "yes"}} if path.startswith("markets/") and "trades" not in path else {"trades": []})
    fav.step(st, now)
    d = pd.read_csv(tmp_path / "done.csv")
    assert st["orders"] == [] and abs(d.pnl.iloc[0] - (50 * 0.10 - o["fees"])) < 1e-9

import pandas as pd
from edge import round28 as R


def test_queue_and_side_from_the_market_listing():
    m = {"yes_bid_dollars": "0.0000", "no_bid_dollars": "0.9900", "yes_ask_dollars": "0.0100", "yes_ask_size_fp": "39286.27"}
    assert R.decided_side(m) == ("no", 0.99) and R.queue_99(m, "no") == 39286.27
    m = {"yes_bid_dollars": "0.9800", "yes_bid_size_fp": "500.00", "no_bid_dollars": "0.0100"}
    assert R.decided_side(m) == ("yes", 0.98) and R.queue_99(m, "yes") == 0.0      # nothing at 99c yet
    assert R.decided_side({"yes_bid_dollars": "0.6", "no_bid_dollars": "0.35"})[0] is None


def test_settle_is_fifo_behind_the_queue(monkeypatch, tmp_path):
    led = pd.DataFrame([dict(series="S", ticker="T", side="no", close_utc="2026-11-07T12:00:00+00:00",
                             joined_utc="2026-11-07T11:00:00+00:00", best_bid=0.99, queue=300.0, reach=None, filled=None,
                             result="", pnl=None, settled_utc="")])

    class Resp:
        status_code = 200

        def json(self):
            return {"market": {"result": "no"}}
    monkeypatch.setattr(R.wx, "_get", lambda url, params=None: Resp())
    monkeypatch.setattr(R, "flow_after", lambda t, s, since: 1000.0)
    out = R.settle_pass(led, pd.Timestamp("2026-11-07T13:00", tz="UTC"))
    assert out.at[0, "filled"] == 700.0 and abs(out.at[0, "pnl"] - (7.0 - R.r15._maker_fee(700, 0.99))) < 1e-9
    assert "Total paper P&L" in R.summary(out, pd.Timestamp("2026-11-07T13:00", tz="UTC"))


def test_an_empty_new_market_is_not_decided():
    assert R.decided_side({"yes_bid_dollars": "0.0000", "no_bid_dollars": "1.0000", "yes_ask_dollars": "0.0000"})[0] is None
    assert R.decided_side({"yes_bid_dollars": "1.0000", "no_bid_dollars": "0.0000", "yes_ask_dollars": "1.0000"})[0] is None
    assert R.decided_side({"yes_bid_dollars": "0.0000", "no_bid_dollars": "0.9900", "yes_ask_dollars": "0.0100"})[0] == "no"

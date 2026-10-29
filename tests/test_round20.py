import pandas as pd

from edge import round20 as r


def test_fills_pnl_and_longshot_wins():
    tr = pd.DataFrame({"time": pd.to_datetime(["2026-07-01 10:00", "2026-07-01 10:05", "2026-07-01 10:10"], utc=True),
                       "taker_side": ["yes", "no", "yes"], "count": [400.0, 400.0, 400.0],
                       "yes_price": [0.01, 0.99, 0.5], "no_price": [0.99, 0.01, 0.5]})
    f = r.fills({"ticker": "T", "result": "no", "close_time": "2026-07-01T10:15:00Z"}, tr)
    assert len(f) == 2                                    # the 50c trade is not a long shot
    assert abs(f["pnl"].iloc[0] - (100 * 0.01 - 0.02)) < 1e-9 and not f["won_longshot"].iloc[0]
    assert f["won_longshot"].iloc[1] and f["pnl"].iloc[1] < -99
    assert list(f["min_to_close"]) == [15.0, 10.0]


def test_tiny_fills_earn_nothing_after_fee():
    tr = pd.DataFrame({"time": pd.to_datetime(["2026-07-01 10:00"], utc=True), "taker_side": ["yes"], "count": [4.0],
                       "yes_price": [0.01], "no_price": [0.99]})
    f = r.fills({"ticker": "T", "result": "no", "close_time": "2026-07-01T10:15:00Z"}, tr)
    assert f["pnl"].iloc[0] <= 0                          # 1 contract at 25%: 1c profit, 1c fee

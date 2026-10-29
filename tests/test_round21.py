import numpy as np
import pandas as pd

from edge import round21 as r


def test_zscores_use_last_completed_minute():
    idx = pd.date_range("2026-07-01 10:00", periods=120, freq="1min", tz="UTC")
    spot = pd.Series(100 * np.exp(np.cumsum(np.r_[0, np.tile([0.001, -0.001], 59), 0.001])), index=idx)
    t = pd.Series(pd.to_datetime(["2026-07-01 11:59:30"], utc=True))
    s, z = r.zscores(spot, t, strike=90.0, close=pd.Timestamp("2026-07-01 12:05", tz="UTC"))
    assert s[0] == spot.iloc[-1] and z[0] > 10           # far above the strike with 5.5 minutes left


def test_book_caps_contracts_per_market_and_scores_losses():
    f = pd.DataFrame({"ticker": ["A", "A", "B"], "time": pd.to_datetime(["2026-07-01 10:00", "2026-07-01 10:01", "2026-07-01 10:00"], utc=True),
                      "px": [0.01, 0.01, 0.02], "count": [3000.0, 3000.0, 400.0], "won_longshot": [False, False, True],
                      "z_for_us": [5.0, 5.0, 4.0], "weight": [1, 1, 1]})
    b = r.book(f, 3.0).set_index(["ticker", "time"]).sort_index()
    assert list(b["n"]) == [750.0, 250.0, 100.0]           # 25% share, 1,000 per market cap
    assert b["pnl"].iloc[2] < -97 and b["pnl"].iloc[0] > 7
    assert len(r.book(f, 4.5)) == 2

import pandas as pd

from edge import round15 as r


def obs(vals, start="2026-07-01 05:00"):
    idx = pd.date_range(start, periods=len(vals), freq="60min", tz="UTC")
    return pd.Series(vals, index=idx, dtype=float)


def test_decided_respects_margins():
    o = obs([70, 75, 80, 81.5, 82, 79])
    # "greater than 80" needs a running high of 82 (80 + 1 + 1 margin)
    side, known = r.decided({"strike_type": "greater", "floor_strike": 80}, o)
    assert side == "yes" and known == o.index[4] + r.DELAY
    assert r.decided({"strike_type": "greater", "floor_strike": 81}, o) is None
    # "less than 81" is dead once the high reaches 82
    side, known = r.decided({"strike_type": "less", "cap_strike": 81}, o)
    assert side == "no" and known == o.index[4] + r.DELAY
    # "between 78 and 79" is dead once the high reaches 81
    side, known = r.decided({"strike_type": "between", "floor_strike": 78, "cap_strike": 79}, o)
    assert side == "no" and known == o.index[3] + r.DELAY


def test_climate_day_is_local_standard_time():
    a, b = r.climate_day(pd.Timestamp("2026-07-01"), "America/New_York")
    assert a == pd.Timestamp("2026-07-01 05:00", tz="UTC") and b - a == pd.Timedelta(days=1)
    a, _ = r.climate_day(pd.Timestamp("2026-07-01"), "America/Phoenix")
    assert a == pd.Timestamp("2026-07-01 07:00", tz="UTC")


def test_opportunities_only_after_decision_and_correct_pnl():
    known = pd.Timestamp("2026-07-01 18:00", tz="UTC")
    tr = pd.DataFrame({"time": pd.to_datetime(["2026-07-01 17:59", "2026-07-01 18:05", "2026-07-01 18:06",
                                               "2026-07-01 18:07"], utc=True),
                       "taker_side": ["no", "no", "yes", "no"], "count": [10, 10, 10, 10],
                       "yes_price": [0.5, 0.1, 0.1, 0.02], "no_price": [0.5, 0.9, 0.9, 0.98]})
    out = r.opportunities({"ticker": "T"}, "no", known, tr, correct=True)
    assert len(out) == 1 and out[0]["price"] == 0.9            # before-decision, wrong-side and >97c excluded
    assert 0 < out[0]["profit_25"] < out[0]["profit_100"]
    wrong = r.opportunities({"ticker": "T"}, "no", known, tr, correct=False)
    assert wrong[0]["profit_100"] < 0

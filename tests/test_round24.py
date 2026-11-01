import numpy as np
import pandas as pd

from edge import round24 as r


def spot():
    idx = pd.date_range("2026-10-20 14:00", periods=24, freq="5min", tz="UTC") + pd.Timedelta(minutes=5)
    return pd.Series(6800 * np.exp(np.cumsum(np.tile([0.0005, -0.0005], 12))), index=idx)


def test_decided_sides_by_strike_type():
    s = spot()
    close = pd.Timestamp("2026-10-20 16:10", tz="UTC")
    t = pd.Series(pd.to_datetime(["2026-10-20 16:04"], utc=True))
    _, zy, zn = r.z_side({"strike_type": "greater", "floor_strike": 6700}, s, t, close)
    assert zy[0] > 6 and zn[0] < -6
    _, zy, zn = r.z_side({"strike_type": "between", "floor_strike": 6900, "cap_strike": 6950}, s, t, close)
    assert zn[0] > 6                                   # far outside the range: NO is decided
    _, zy, _ = r.z_side({"strike_type": "less", "cap_strike": 6900}, s, t, close)
    assert zy[0] > 6


def test_stale_bar_gives_no_z():
    s = spot()
    t = pd.Series(pd.to_datetime(["2026-10-20 18:00"], utc=True))     # an hour after the last bar
    _, zy, zn = r.z_side({"strike_type": "greater", "floor_strike": 6700}, s, t, pd.Timestamp("2026-10-20 20:00", tz="UTC"))
    assert np.isnan(zy[0]) and np.isnan(zn[0])

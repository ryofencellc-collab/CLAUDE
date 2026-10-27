import numpy as np
import pandas as pd

from edge import gates


def fake_panel(planted: bool, seed=0, n=10):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2019-06-01", "2025-12-31", freq="D")
    cols = [f"C{i}" for i in range(n - 1)] + ["BTC"]
    fund = pd.DataFrame(rng.normal(0, 1e-4, (len(idx), n)), index=idx, columns=cols)
    noise = rng.normal(0, 0.02, (len(idx), n))
    if planted:  # coins whose crowd is short (7d funding < 0) rise the next day, others fall
        f7 = fund.rolling(7, min_periods=5).mean().shift(1).fillna(0).to_numpy()
        noise = noise + np.where(f7 < 0, 0.004, -0.003)
    px = pd.DataFrame(100 * np.exp(np.cumsum(noise, axis=0)), index=idx, columns=cols)
    return {"spot_close": px, "spot_qv": pd.DataFrame(1e8, index=idx, columns=cols),
            "perp_close": px * (1 + rng.normal(0, 1e-3, px.shape)), "funding": fund}


def test_gates_fail_on_noise():
    p = fake_panel(planted=False)
    oos, turn, log = gates.walk_forward(p)
    v = gates.verdict(oos, turn, p["spot_close"]["BTC"])
    assert not v["pass"], v


def test_gates_find_planted_edge():
    p = fake_panel(planted=True)
    oos, turn, log = gates.walk_forward(p)
    v = gates.verdict(oos, turn, p["spot_close"]["BTC"])
    assert all("funding_negative" in r["gates"] or "funding_below_90d_median" in r["gates"] for r in log), log
    assert v["pass"], v

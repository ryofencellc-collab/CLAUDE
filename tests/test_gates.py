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


def fake_stocks(planted: bool, seed=1, n=6):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2007-06-01", "2024-12-31")
    cols = [f"E{i}" for i in range(n)]
    vix = pd.Series(20 * np.exp(np.cumsum(rng.normal(0, 0.05, len(idx)))), index=idx)
    vix3m = vix * np.exp(rng.normal(0, 0.08, len(idx)))
    noise = rng.normal(0, 0.012, (len(idx), n))
    if planted:  # calm term structure (VIX < VIX3M) today -> up tomorrow, else down
        calm = (vix < vix3m).shift(1).fillna(False).to_numpy()[:, None]
        noise = noise + np.where(calm, 0.002, -0.0015)
    px = pd.DataFrame(100 * np.exp(np.cumsum(noise, axis=0)), index=idx, columns=cols)
    walk = lambda s: pd.Series(100 * np.exp(np.cumsum(rng.normal(0, 0.01, len(idx)))), index=idx)
    macro = pd.DataFrame({"^VIX": vix, "^VIX3M": vix3m, "^IRX": walk(0), "HYG": walk(0), "IEF": walk(0),
                          "TLT": walk(0), "SPY": px.mean(axis=1)})
    return {"spot_close": px, "spot_qv": pd.DataFrame(1.0, index=idx, columns=cols)}, macro


def _stock_run(planted):
    p, macro = fake_stocks(planted)
    lib = gates.library(gates.stock_base_gates(p["spot_close"], macro))
    oos, turn, log = gates.walk_forward(p, mkt=gates.STOCKS, lib=lib)
    return gates.verdict(oos, turn, macro["SPY"], 265, 252), log


def test_stock_gates_fail_on_noise():
    v, _ = _stock_run(False)
    assert not v["pass"], v


def test_stock_gates_find_planted_edge():
    v, log = _stock_run(True)
    assert all("vix_contango" in r["gates"] for r in log), log
    assert v["pass"], v

"""Smoke test on synthetic random-walk data: pipeline runs and finds no edge."""
import numpy as np
import pandas as pd

import run_research as rr
from edge.strategies import crypto, etf


def fake_crypto(seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2018-01-01", "2026-09-30", freq="D")
    coins = ["BTC", "ETH", "SOL", "XRP", "ADA", "DOGE", "LTC"]
    r = pd.DataFrame(rng.normal(0, 0.04, (len(idx), len(coins))), idx, coins)
    spot = 100 * (1 + r).cumprod()
    spot.loc[:"2020-06-01", "SOL"] = np.nan  # late listing
    perp = spot * (1 + rng.normal(0, 0.001, spot.shape))
    fund = pd.DataFrame(rng.normal(0, 0.0003, spot.shape), idx, coins).loc["2019-09-10":]
    qv = pd.DataFrame(1e8, idx, coins).where(spot.notna())
    return {"spot_close": spot, "spot_qv": qv, "perp_close": perp, "funding": fund}


def fake_etf(seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2005-01-03", "2026-09-30")
    t = ["SPY", "QQQ", "IWM", "TLT", "GLD", "SVXY", "VXX"]
    close = 100 * (1 + pd.DataFrame(rng.normal(0, 0.012, (len(idx), len(t))), idx, t)).cumprod()
    close.loc[:"2011-10-01", "SVXY"] = np.nan
    opn = close.shift(1) * (1 + rng.normal(0, 0.004, close.shape))
    vix = pd.Series(18 + rng.normal(0, 3, len(idx)), idx)
    close["^VIX"], close["^VIX3M"], close["^IRX"] = vix, vix * 1.05, 4.0
    return {"close": close, "open": opn}


def test_pipeline_finds_nothing_on_noise():
    panels = {"crypto": fake_crypto(), "etf": fake_etf()}
    trials, streams = rr.evaluate(panels)
    n_expected = sum(len(g) for m in (crypto, etf) for _, g in m.FAMILIES.values())
    assert len(trials) == n_expected
    assert trials[["is_sharpe", "oos_sharpe"]].notna().all().all()
    verdict = rr.judge(trials, streams)
    assert verdict["passed"].sum() == 0, verdict


def test_null_builders_run():
    from edge import null
    rr.evaluate({"crypto": null.crypto(fake_crypto(), 1), "etf": null.etf(fake_etf(), 1)})


def test_pipeline_detects_planted_edge():
    """Power check: give BTC persistent trends; btc_trend must pass."""
    p = fake_crypto(2)
    rng = np.random.default_rng(2)
    idx = p["spot_close"].index
    regime = np.sign(np.sin(np.arange(len(idx)) / 40))  # ~4-month up/down swings
    r = 0.006 * regime + rng.normal(0, 0.02, len(idx))
    p["spot_close"]["BTC"] = 100 * np.cumprod(1 + r)
    trials, streams = rr.evaluate({"crypto": p, "etf": fake_etf()})
    v = rr.judge(trials, streams).set_index("family")
    assert v.loc["btc_trend", "passed"], v.loc["btc_trend"]

import numpy as np
import pandas as pd

from edge import gates, round13


def fake(seed=11):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2007-01-01", "2025-12-31")
    n = len(round13.ASSETS)
    vols = np.array([0.011] * (n - 2) + [0.04, 0.05])
    r = rng.normal(0, 1, (len(idx), n)) * vols
    px = pd.DataFrame(100 * np.exp(np.cumsum(r, axis=0)), index=idx, columns=round13.ASSETS)
    px.loc[:"2014-09-15", "BTC-USD"] = np.nan
    px.loc[:"2017-11-09", "ETH-USD"] = np.nan
    return px


def test_round13_noise_fails():
    px = fake()
    oos, turn, _ = round13.walk_forward(px)
    assert not gates.verdict(oos, turn, px["SPY"], 269, 252)["pass"]


def test_round13_no_leverage_and_causal():
    px = fake()
    trend_w = round13.round11.weights(px[round13.ETFS], round13.TREND_CFG)
    sleeves = {n: round13.crypto_sleeve(px, n) for n in (50, 100)}
    for c in round13.configs():
        w = round13.combine(px, c, trend_w, sleeves)
        assert (w.sum(axis=1) <= 1 + 1e-9).all() and (w >= -1e-12).all().all()
    cut = px.index[3500]
    q = px.loc[:cut]
    c = dict(core="volman", sma=50, alpha=0.3, beta=0.4)
    a = round13.combine(q, c, round13.round11.weights(q[round13.ETFS], round13.TREND_CFG),
                        {n: round13.crypto_sleeve(q, n) for n in (50, 100)})
    b = round13.combine(px, c, trend_w, sleeves).loc[:cut]
    assert np.allclose(a.to_numpy(), b.to_numpy())

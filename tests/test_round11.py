import numpy as np
import pandas as pd

from edge import gates, round11

COLS = round11.ETFS + [round11.BTC]


def fake(planted: bool, seed=5):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2007-01-01", "2025-12-31")
    n = len(COLS)
    vols = np.array([0.012] * (n - 1) + [0.04])
    r = rng.normal(0, 1, (len(idx), n)) * vols
    if planted:  # persistent regimes: each asset drifts up or down for long stretches
        regime = np.sign(np.sin(np.arange(len(idx))[:, None] / 180.0 + rng.uniform(0, 6, n)))
        r = r + regime * vols * 0.12
    px = pd.DataFrame(100 * np.exp(np.cumsum(r, axis=0)), index=idx, columns=COLS)
    px.loc[:"2014-09-15", round11.BTC] = np.nan
    return px


def test_round11_noise_fails():
    px = fake(False)
    oos, turn, _ = round11.walk_forward(px)
    assert not gates.verdict(oos, turn, px["SPY"], 267, 252)["pass"]


def test_round11_planted_trend_passes():
    px = fake(True)
    oos, turn, log = round11.walk_forward(px)
    v = gates.verdict(oos, turn, px["SPY"], 267, 252)
    assert v["pass"], (v, log)


def test_round11_no_leverage_and_causal():
    px = fake(True)
    c = dict(trend="sma100", target_vol=0.12, btc=True)
    w = round11.weights(px, c)
    assert (w.sum(axis=1) <= 1 + 1e-9).all() and (w >= 0).all().all()
    cut = px.index[3000]
    assert np.allclose(round11.weights(px.loc[:cut], c).to_numpy(), w.loc[:cut].to_numpy())

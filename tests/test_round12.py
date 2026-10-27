import numpy as np
import pandas as pd

from edge import gates, round12


def fake(planted: bool, seed=7):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2014-06-01", "2025-12-31")
    vols = np.array([0.011, 0.04, 0.05])
    r = rng.normal(0, 1, (len(idx), 3)) * vols
    if planted:  # crypto trends persist for months
        regime = np.sign(np.sin(np.arange(len(idx))[:, None] / 120.0 + np.array([0, 1, 2])))
        r[:, 1:] = r[:, 1:] + regime[:, 1:] * vols[1:] * 0.15
    px = pd.DataFrame(100 * np.exp(np.cumsum(r, axis=0)), index=idx, columns=round12.ASSETS)
    px.loc[:"2014-09-15", "BTC-USD"] = np.nan
    px.loc[:"2017-11-09", "ETH-USD"] = np.nan
    return px


def test_round12_noise_fails():
    px = fake(False)
    oos, turn, _ = round12.walk_forward(px)
    assert not gates.verdict(oos, turn, px["SPY"], 268, 252)["pass"]


def test_round12_no_leverage_and_causal():
    px = fake(True)
    for c in round12.configs():
        w = round12.weights(px, c)
        assert (w.sum(axis=1) <= 1 + 1e-9).all() and (w >= 0).all().all()
    c = dict(core="volman", sma=50, alpha=0.3)
    w = round12.weights(px, c)
    cut = px.index[2000]
    assert np.allclose(round12.weights(px.loc[:cut], c).to_numpy(), w.loc[:cut].to_numpy())


def test_round12_planted_crypto_trend_beats_spy():
    px = fake(True)
    oos, turn, log = round12.walk_forward(px)
    v = gates.verdict(oos, turn, px["SPY"], 268, 252)
    assert v["checks"]["beats_benchmark_sharpe"] and v["sharpe"] > 1.0, (v, log)

import numpy as np
import pandas as pd

from edge import gates, round10


def fake(planted: bool, seed=3, n=8):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2019-06-01", "2026-06-30", freq="D")
    cols = ["BTC", "ETH"] + [f"C{i}" for i in range(n - 2)]
    r = rng.normal(0, 0.03, (len(idx), n))
    px = pd.DataFrame(100 * np.exp(np.cumsum(r, axis=0)), index=idx, columns=cols)
    if planted:  # uptrend regime persists: when BTC is above its SMA 100 tomorrow drifts up, else down
        out = np.zeros_like(r)
        p = 100 * np.ones(n)
        hist = [p.copy()]
        for t in range(1, len(idx)):
            h = np.array(hist[-100:])[:, 0]
            up = h[-1] > h.mean() if len(h) >= 100 else True
            out[t] = r[t] + (0.004 if up else -0.004)
            p = p * np.exp(out[t])
            hist.append(p.copy())
        px = pd.DataFrame(np.array(hist), index=idx, columns=cols)
    return {"spot_close": px, "spot_qv": pd.DataFrame(1e9, index=idx, columns=cols)}


def test_round10_noise_fails():
    p = fake(False)
    oos, turn, _ = round10.walk_forward(p)
    assert not gates.verdict(oos, turn, p["spot_close"]["BTC"], 266, 365)["pass"]


def test_round10_planted_trend_passes():
    p = fake(True)
    oos, turn, log = round10.walk_forward(p)
    v = gates.verdict(oos, turn, p["spot_close"]["BTC"], 266, 365)
    assert v["pass"], (v, log)


def test_round10_weights_never_exceed_one_and_are_causal():
    p = fake(True)
    c = dict(universe="all", regime=100, coin_gate=True, target_vol=0.3)
    w = round10.weights(p, c)
    assert (w.sum(axis=1) <= 1 + 1e-9).all()
    cut = p["spot_close"].index[1500]
    q = {k: v.loc[:cut] for k, v in p.items()}  # future data removed must not change past weights
    assert np.allclose(round10.weights(q, c).to_numpy(), w.loc[:cut].to_numpy())

"""Round 10: crypto trend gate with a volatility risk limit (PROTOCOL_ROUND10.md)."""
from itertools import product

import numpy as np
import pandas as pd

from edge.backtest import run

COST = 0.001
PERIODS = 365
START = pd.Timestamp("2019-10-01")
FIRST_TEST = pd.Timestamp("2021-01-01")
MIN_USD = 5e6


def configs() -> list[dict]:
    return [dict(universe=u, regime=r, coin_gate=g, target_vol=v)
            for u, r, g, v in product(("BTC", "BTC+ETH", "top5", "all"), (50, 100, 200), (False, True),
                                      (0.20, 0.30, 0.40))]


def cfg_id(c: dict) -> str:
    return f"{c['universe']}-sma{c['regime']}-{'gate' if c['coin_gate'] else 'nogate'}-vol{int(c['target_vol'] * 100)}"


def universe_mask(p: dict, name: str) -> pd.DataFrame:
    px = p["spot_close"]
    qv = p["spot_qv"].reindex(index=px.index, columns=px.columns)
    liquid = (qv.rolling(30, min_periods=20).median() >= MIN_USD) & px.notna()
    if name in ("BTC", "BTC+ETH"):
        keep = ["BTC"] if name == "BTC" else ["BTC", "ETH"]
        return liquid & pd.DataFrame({c: c in keep for c in px.columns}, index=px.index)
    if name == "top5":
        rank = qv.rolling(30, min_periods=20).mean().where(liquid).rank(axis=1, ascending=False)
        return rank <= 5
    return liquid


def weights(p: dict, c: dict) -> pd.DataFrame:
    """Target weights at each close (causal: only data up to that close)."""
    px = p["spot_close"]
    rets = px.pct_change(fill_method=None)
    uni = universe_mask(p, c["universe"])
    btc = px["BTC"]
    regime = btc > btc.rolling(c["regime"]).mean()
    m = uni & pd.DataFrame(np.repeat(regime.to_numpy()[:, None], px.shape[1], axis=1), index=px.index,
                           columns=px.columns)
    if c["coin_gate"]:
        m = m & (px > px.rolling(50).mean())
    w = m.astype(float)
    w = w.div(w.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    # risk limit: scale the book by target vol / realised vol of the equal-weight universe basket
    basket = rets.where(uni).mean(axis=1)
    vol = basket.rolling(20, min_periods=15).std() * np.sqrt(PERIODS)
    scale = (c["target_vol"] / vol).clip(upper=1.0).fillna(0.0)
    return w.mul(scale, axis=0)


def walk_forward(p: dict) -> tuple[pd.Series, pd.Series, list[dict]]:
    px = p["spot_close"]
    rets = px.pct_change(fill_method=None)
    idx = px.index
    W = {cfg_id(c): weights(p, c) for c in configs()}
    R = {k: run(w, rets, COST).returns for k, w in W.items()}
    stitched = pd.DataFrame(0.0, index=idx, columns=px.columns)
    log, d = [], FIRST_TEST
    while d <= idx[-1]:
        end = d + pd.DateOffset(months=6)
        train = (idx >= START) & (idx < d)
        sh = {k: (r[train].mean() / r[train].std() * np.sqrt(PERIODS)) if r[train].std() > 0 else -9
              for k, r in R.items()}
        best = max(sh, key=sh.get)
        block = (idx >= d) & (idx < end)
        stitched.loc[block] = W[best].loc[block].to_numpy()
        log.append({"refit": d.date().isoformat(), "chosen": best, "train_sharpe": round(float(sh[best]), 2)})
        print(f"  refit {d.date()}: {best} (train Sharpe {sh[best]:.2f})", flush=True)
        d = end
    res = run(stitched, rets, COST)
    oos = idx >= FIRST_TEST
    return res.returns[oos], res.turnover[oos], log

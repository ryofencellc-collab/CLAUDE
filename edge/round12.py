"""Round 12: stock core plus a crypto trend sleeve (PROTOCOL_ROUND12.md)."""
from itertools import product

import numpy as np
import pandas as pd

PERIODS = 252
START = pd.Timestamp("2014-10-01")
FIRST_TEST = pd.Timestamp("2016-01-01")
ASSETS = ["SPY", "BTC-USD", "ETH-USD"]
COINS = ["BTC-USD", "ETH-USD"]
COSTS = {"SPY": 0.0002, "BTC-USD": 0.001, "ETH-USD": 0.001}
SLEEVE_VOL = 0.40
CORE_VOL = 0.15


def configs() -> list[dict]:
    return [dict(core=c, sma=n, alpha=a)
            for c, n, a in product(("hold", "volman", "trend200"), (50, 100), (0.10, 0.20, 0.30))]


def cfg_id(c: dict) -> str:
    return f"{c['core']}-sma{c['sma']}-crypto{int(c['alpha'] * 100)}"


def weights(px: pd.DataFrame, c: dict) -> pd.DataFrame:
    """Target weights at each close, causal; gross exposure <= 1."""
    rets = px.pct_change(fill_method=None)
    spy = px["SPY"]
    if c["core"] == "hold":
        core = pd.Series(1.0, index=px.index).where(spy.notna(), 0.0)
    elif c["core"] == "volman":
        vol = rets["SPY"].rolling(20, min_periods=15).std() * np.sqrt(PERIODS)
        core = (CORE_VOL / vol).clip(upper=1.0).fillna(0.0)
    else:
        sma = spy.rolling(200).mean()
        core = ((spy > sma) & sma.notna()).astype(float)
    coins = px[COINS]
    sma = coins.rolling(c["sma"]).mean()
    on = (coins > sma) & sma.notna()
    sleeve = on.astype(float).div(on.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    bvol = rets[COINS].where(on).mean(axis=1).rolling(20, min_periods=15).std() * np.sqrt(PERIODS)
    scale = (SLEEVE_VOL / bvol).clip(upper=1.0).fillna(0.0)
    sleeve = sleeve.mul(scale, axis=0)
    W = pd.DataFrame(0.0, index=px.index, columns=px.columns)
    W["SPY"] = (1 - c["alpha"]) * core
    W[COINS] = c["alpha"] * sleeve
    return W


def backtest(W: pd.DataFrame, px: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    rets = px.pct_change(fill_method=None).fillna(0.0)
    held = W.shift(1).fillna(0.0)
    gross = (held * rets).sum(axis=1)
    dturn = held.diff().abs().fillna(held.abs())
    cost = (dturn * pd.Series(COSTS)[px.columns]).sum(axis=1)
    return gross - cost, dturn.sum(axis=1)


def walk_forward(px: pd.DataFrame) -> tuple[pd.Series, pd.Series, list[dict]]:
    idx = px.index
    W = {cfg_id(c): weights(px, c) for c in configs()}
    R = {k: backtest(w, px)[0] for k, w in W.items()}
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
    net, turn = backtest(stitched, px)
    oos = idx >= FIRST_TEST
    return net[oos], turn[oos], log

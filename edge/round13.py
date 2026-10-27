"""Round 13: stock core + multi-asset trend sleeve + crypto trend sleeve (PROTOCOL_ROUND13.md)."""
from itertools import product

import numpy as np
import pandas as pd

from edge import round11, round12

PERIODS = 252
START = pd.Timestamp("2007-07-01")
FIRST_TEST = pd.Timestamp("2012-01-01")
ETFS = round11.ETFS
COINS = round12.COINS
ASSETS = ETFS + COINS
COSTS = {**{t: 0.0002 for t in ETFS}, **{c: 0.001 for c in COINS}}
TREND_CFG = dict(trend="sma100", target_vol=0.08, btc=False)


def configs() -> list[dict]:
    return [dict(core=c, sma=n, alpha=a, beta=b)
            for c, n, a, b in product(("hold", "volman"), (50, 100), (0.10, 0.20, 0.30), (0.20, 0.40))]


def cfg_id(c: dict) -> str:
    return f"{c['core']}-sma{c['sma']}-crypto{int(c['alpha'] * 100)}-trend{int(c['beta'] * 100)}"


def core_weight(px: pd.DataFrame, mode: str) -> pd.Series:
    if mode == "hold":
        return pd.Series(1.0, index=px.index).where(px["SPY"].notna(), 0.0)
    vol = px["SPY"].pct_change(fill_method=None).rolling(20, min_periods=15).std() * np.sqrt(PERIODS)
    return (round12.CORE_VOL / vol).clip(upper=1.0).fillna(0.0)


def crypto_sleeve(px: pd.DataFrame, n: int) -> pd.DataFrame:
    coins = px[COINS]
    rets = coins.pct_change(fill_method=None)
    sma = coins.rolling(n).mean()
    on = (coins > sma) & sma.notna()
    sleeve = on.astype(float).div(on.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    bvol = rets.where(on).mean(axis=1).rolling(20, min_periods=15).std() * np.sqrt(PERIODS)
    return sleeve.mul((round12.SLEEVE_VOL / bvol).clip(upper=1.0).fillna(0.0), axis=0)


def combine(px: pd.DataFrame, c: dict, trend_w: pd.DataFrame, sleeves: dict) -> pd.DataFrame:
    W = pd.DataFrame(0.0, index=px.index, columns=px.columns)
    W["SPY"] += (1 - c["alpha"] - c["beta"]) * core_weight(px, c["core"])
    W[ETFS] += c["beta"] * trend_w[ETFS]
    W[COINS] += c["alpha"] * sleeves[c["sma"]]
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
    trend_w = round11.weights(px[ETFS], TREND_CFG)
    sleeves = {n: crypto_sleeve(px, n) for n in (50, 100)}
    W = {cfg_id(c): combine(px, c, trend_w, sleeves) for c in configs()}
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

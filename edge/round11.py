"""Round 11: multi-asset trend with risk balancing (PROTOCOL_ROUND11.md)."""
from itertools import product

import numpy as np
import pandas as pd

PERIODS = 252
START = pd.Timestamp("2007-07-01")
FIRST_TEST = pd.Timestamp("2012-01-01")
ETFS = ["SPY", "EFA", "EEM", "TLT", "IEF", "GLD", "DBC", "VNQ"]
BTC = "BTC-USD"
COSTS = {**{t: 0.0002 for t in ETFS}, BTC: 0.001}


def configs() -> list[dict]:
    return [dict(trend=t, target_vol=v, btc=b)
            for t, v, b in product(("sma50", "sma100", "sma200", "mom252"), (0.08, 0.10, 0.12), (True, False))]


def cfg_id(c: dict) -> str:
    return f"{c['trend']}-vol{int(c['target_vol'] * 100)}-{'btc' if c['btc'] else 'nobtc'}"


def trend(px: pd.DataFrame, rule: str) -> pd.DataFrame:
    if rule == "mom252":
        s = px.pct_change(252, fill_method=None)
        return (s > 0) & s.notna()
    n = int(rule[3:])
    sma = px.rolling(n).mean()
    return (px > sma) & sma.notna()


def weights(px: pd.DataFrame, c: dict) -> pd.DataFrame:
    """Target weights at each close, causal."""
    cols = list(px.columns) if c["btc"] else [x for x in px.columns if x != BTC]
    p = px[cols]
    rets = p.pct_change(fill_method=None)
    on = trend(p, c["trend"])
    vol = rets.rolling(60, min_periods=40).std() * np.sqrt(PERIODS)
    raw = (on / vol).where(on & vol.notna(), 0.0).fillna(0.0)
    W = pd.DataFrame(0.0, index=px.index, columns=px.columns)
    R = rets.to_numpy()
    raw_np = raw.to_numpy()
    for t in range(60, len(px)):
        w = raw_np[t]
        if w.sum() <= 0:
            continue
        window = R[t - 59:t + 1]
        ok = ~np.isnan(window).any(axis=0)
        w = np.where(ok, w, 0.0)
        if w.sum() <= 0:
            continue
        cov = np.cov(window[:, ok], rowvar=False) * PERIODS
        wk = w[ok]
        port_vol = float(np.sqrt(max(wk @ np.atleast_2d(cov) @ wk, 1e-12)))
        w = w * (c["target_vol"] / port_vol)
        gross = w.sum()
        if gross > 1.0:
            w = w / gross
        W.iloc[t, [W.columns.get_loc(x) for x in cols]] = w
    return W


def backtest(W: pd.DataFrame, px: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """Weights at close t earn t+1; per-asset costs on turnover."""
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

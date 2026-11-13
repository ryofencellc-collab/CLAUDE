"""Strategy registry for the factory. Each entry: name -> (market, batch, fn(data) -> weights DataFrame).
Batch 1 added 2026-11-13 (before running): classic documented anomalies and rotations not yet tested here."""
from __future__ import annotations
import numpy as np, pandas as pd

REG: dict = {}


def strat(name, market, batch):
    def deco(fn):
        REG[name] = (market, batch, fn)
        return fn
    return deco


def month_end_mask(idx):
    s = pd.Series(idx, index=idx)
    return s.groupby([idx.year, idx.month]).transform("max") == s


def topk_monthly(score: pd.DataFrame, ok: pd.DataFrame, frac=0.1, k=None, largest=True, every="M"):
    mask = month_end_mask(score.index) if every == "M" else (score.index.weekday == 4)
    sc = score.where(ok)
    w = pd.DataFrame(np.nan, index=score.index, columns=score.columns)
    for t in score.index[mask]:
        row = sc.loc[t].dropna()
        if len(row) < 20:
            continue
        n = k or max(1, int(len(row) * frac))
        pick = row.nlargest(n).index if largest else row.nsmallest(n).index
        v = pd.Series(0.0, index=score.columns); v[pick] = 1.0 / n
        w.loc[t] = v
    return w.ffill().fillna(0.0)


# ------------------------------------------------------------ stocks (cross-sectional, long-only, top decile)
@strat("XS momentum 12-1 (top 10%)", "stocks", 1)
def _(d): return topk_monthly(d["C"].shift(21) / d["C"].shift(252) - 1, d["ok"])

@strat("XS momentum 6-1 (top 10%)", "stocks", 1)
def _(d): return topk_monthly(d["C"].shift(21) / d["C"].shift(126) - 1, d["ok"])

@strat("Short-term reversal (weekly losers, 10%)", "stocks", 1)
def _(d): return topk_monthly(d["C"] / d["C"].shift(5) - 1, d["ok"], largest=False, every="W")

@strat("Low volatility (lowest 10% 60d vol)", "stocks", 1)
def _(d): return topk_monthly(d["C"].pct_change(fill_method=None).rolling(60).std(), d["ok"], largest=False)

@strat("52-week-high proximity (top 10%)", "stocks", 1)
def _(d): return topk_monthly(d["C"] / d["C"].rolling(252).max(), d["ok"])

@strat("Anti-lottery (lowest monthly max daily return, 10%)", "stocks", 1)
def _(d): return topk_monthly(d["C"].pct_change(fill_method=None).rolling(21).max(), d["ok"], largest=False)

@strat("Momentum + low vol (rank sum, top 10%)", "stocks", 1)
def _(d):
    m = (d["C"].shift(21) / d["C"].shift(252) - 1).rank(axis=1, pct=True)
    v = d["C"].pct_change(fill_method=None).rolling(60).std().rank(axis=1, pct=True, ascending=False)
    return topk_monthly(m + v, d["ok"])

@strat("Momentum 12-1, top 20 names only", "stocks", 1)
def _(d): return topk_monthly(d["C"].shift(21) / d["C"].shift(252) - 1, d["ok"], k=20)


# ------------------------------------------------------------ ETFs / SPY
def one(d, col, pos):  # pos: Series of target weight for one ticker
    w = pd.DataFrame(0.0, index=d["E"].index, columns=d["E"].columns); w[col] = pos.reindex(w.index).fillna(0.0); return w

@strat("Turn-of-month SPY (last 4 + first 3 days)", "etfs", 1)
def _(d):
    idx = d["E"].index; s = pd.Series(range(len(idx)), index=idx)
    g = s.groupby([idx.year, idx.month]); pos_in = s - g.transform("min"); pos_end = g.transform("max") - s
    # weight decided at t applies from t+1's close... so mark the day before the window
    win = ((pos_in <= 2) | (pos_end <= 3)).astype(float).shift(-2).fillna(0)
    return one(d, "SPY", win)

@strat("Sell in May: SPY Nov-Apr, IEF May-Oct", "etfs", 1)
def _(d):
    idx = d["E"].index; w = pd.DataFrame(0.0, index=idx, columns=d["E"].columns)
    winter = pd.Series(idx.month.isin([11, 12, 1, 2, 3, 4]), index=idx).astype(float)
    w["SPY"], w["IEF"] = winter, 1 - winter; return w

@strat("Dual momentum GEM (SPY/EFA by 12m, else AGG)", "etfs", 1)
def _(d):
    E = d["E"]; r12 = E / E.shift(252) - 1; me = month_end_mask(E.index)
    w = pd.DataFrame(np.nan, index=E.index, columns=E.columns)
    for t in E.index[me]:
        v = pd.Series(0.0, index=E.columns)
        if r12.loc[t, ["SPY", "EFA"]].isna().any(): continue
        best = "SPY" if r12.loc[t, "SPY"] >= r12.loc[t, "EFA"] else "EFA"
        v["AGG" if r12.loc[t, "SPY"] < r12.loc[t, "BIL"] else best] = 1.0
        w.loc[t] = v
    return w.ffill().fillna(0.0)

@strat("Sector rotation (top 3 SPDR sectors by 3m return)", "etfs", 1)
def _(d):
    secs = [c for c in ("XLK", "XLF", "XLE", "XLV", "XLY", "XLP", "XLI", "XLB", "XLU", "XLRE", "XLC") if c in d["E"].columns]
    sc = (d["E"][secs] / d["E"][secs].shift(63) - 1)
    me = month_end_mask(sc.index); w = pd.DataFrame(np.nan, index=sc.index, columns=d["E"].columns)
    for t in sc.index[me]:
        row = sc.loc[t].dropna()
        if len(row) < 5: continue
        v = pd.Series(0.0, index=d["E"].columns); v[row.nlargest(3).index] = 1 / 3; w.loc[t] = v
    return w.ffill().fillna(0.0)

@strat("Volatility-managed SPY (15% vol target, max 1.5x)", "etfs", 1)
def _(d):
    r = d["E"]["SPY"].pct_change(fill_method=None); vol = r.rolling(21).std() * np.sqrt(252)
    return one(d, "SPY", (0.15 / vol).clip(upper=1.5))

@strat("2x SPY above 200-day average, else cash", "etfs", 1)
def _(d):
    s = d["E"]["SPY"]; return one(d, "SPY", 2.0 * (s > s.rolling(200).mean()).astype(float))

@strat("SPY above 200-day average, else IEF", "etfs", 1)
def _(d):
    s = d["E"]["SPY"]; up = (s > s.rolling(200).mean()).astype(float)
    w = one(d, "SPY", up); w["IEF"] = 1 - up; return w


# ------------------------------------------------------------ crypto
@strat("Crypto XS momentum: top 5 of 30 by 30d return, weekly", "crypto", 1)
def _(d): return topk_monthly(d["X"] / d["X"].shift(30) - 1, d["X"].notna() & d["X"].shift(60).notna(), k=5, every="W")

@strat("Crypto: BTC+ETH 50/200 golden cross, else cash", "crypto", 1)
def _(d):
    X = d["X"][["BTC", "ETH"]]; on = (X.rolling(50).mean() > X.rolling(200).mean()).astype(float) / 2
    return on.reindex(columns=d["X"].columns, fill_value=0.0)

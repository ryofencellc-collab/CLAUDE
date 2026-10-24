"""Synthetic 'no-edge' panels for the sanity check.

Each return-like series is demeaned and its values reshuffled in time, using
one global date permutation so cross-asset relationships on a given day are
roughly kept while any time-series structure (trend, mean reversion,
predictive signals) is destroyed. Any strategy that passes on this data is
evidence the pipeline itself is biased.
"""
import numpy as np
import pandas as pd


def _shuffle(df: pd.DataFrame, rank: pd.Series, demean: bool) -> pd.DataFrame:
    out = df.copy()
    r = rank.reindex(df.index)
    for c in df.columns:
        valid = df[c].notna()
        vals = df.loc[valid, c].to_numpy()
        vals = vals[np.argsort(r[valid].to_numpy())]
        out.loc[valid, c] = vals - vals.mean() if demean else vals
    return out


def _rebuild(rets: pd.DataFrame, like: pd.DataFrame) -> pd.DataFrame:
    px = (1 + rets.fillna(0)).cumprod() * like.bfill().iloc[0]
    return px.where(like.notna())


def crypto(p, seed):
    rng = np.random.default_rng(seed)
    spot = p["spot_close"]
    rank = pd.Series(rng.permutation(len(spot)), index=spot.index)
    sret = spot.pct_change(fill_method=None)
    basis = (p["perp_close"].pct_change(fill_method=None) - sret).reindex(columns=p["perp_close"].columns)
    s_null = _shuffle(sret, rank, True)
    b_null = _shuffle(basis, rank, True)
    perp_ret = s_null.reindex(columns=basis.columns) + b_null
    return {
        "spot_close": _rebuild(s_null, spot),
        "spot_qv": p["spot_qv"],
        "perp_close": _rebuild(perp_ret, p["perp_close"]),
        "funding": _shuffle(p["funding"], rank, True),
    }


def etf(p, seed):
    rng = np.random.default_rng(seed)
    c, o = p["close"], p["open"]
    rank = pd.Series(rng.permutation(len(c)), index=c.index)
    levels = ["^VIX", "^VIX3M", "^IRX"]
    tradable = [x for x in c.columns if x not in levels]
    cret = _shuffle(c[tradable].pct_change(fill_method=None), rank, True)
    close = _rebuild(cret, c[tradable])
    on = _shuffle(o[tradable] / c[tradable].shift(1) - 1, rank, True)
    opn = close.shift(1) * (1 + on)
    lv = _shuffle(c[levels], rank, False)
    return {"close": pd.concat([close, lv], axis=1), "open": opn}

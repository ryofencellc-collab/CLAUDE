"""Round 8 backtests: copy 13F portfolios, copy House stock purchases (PROTOCOL_ROUND8.md).

Inputs are the frames from edge/copytrade.py plus a wide price table
(adjusted closes, columns = Yahoo tickers, must include SPY). Every
strategy returns a daily net return series; callers compare it to SPY.
"""
import numpy as np
import pandas as pd

COST = 0.0005          # per side, on turnover
DEV_END = pd.Timestamp("2021-12-31")
SEALED_START = pd.Timestamp("2022-01-01")


def next_session(dates: pd.DatetimeIndex, d) -> pd.Timestamp | None:
    """First trading day strictly after d (we trade at that day's close)."""
    i = dates.searchsorted(pd.Timestamp(d), side="right")
    return dates[i] if i < len(dates) else None


# ------------------------------------------------------------------ 13F

def portfolios_13f(h: pd.DataFrame, n: int, weight: str, select: str) -> list[tuple[pd.Timestamp, dict]]:
    """One target portfolio per filing of a single fund: [(filed, {ticker: w})]."""
    out, prev = [], None
    for (filed, acc), g in h.dropna(subset=["ticker"]).groupby(["filed", "accession"], sort=True):
        full = g.groupby("ticker", as_index=False)[["value", "shares"]].sum()
        g = full
        if select == "added" and prev is not None:
            old = prev.set_index("ticker")["shares"]
            g = full[full["shares"] > full["ticker"].map(old).fillna(0) * 1.0001]  # new or bigger share count
        prev = full
        g = g.sort_values("value", ascending=False).head(n)
        if g.empty or g["value"].sum() <= 0:
            out.append((pd.Timestamp(filed), {}))
            continue
        w = g["value"] / g["value"].sum() if weight == "value" else pd.Series(1 / len(g), index=g.index)
        out.append((pd.Timestamp(filed), dict(zip(g["ticker"], w))))
    return out


def consensus_portfolios(h: pd.DataFrame, n: int) -> list[tuple[pd.Timestamp, dict]]:
    """After each filing by any fund: the n stocks most often in funds' latest top-20s, equal weight."""
    latest, out = {}, []
    h = h.dropna(subset=["ticker"])
    for filed, day in h.groupby("filed", sort=True):
        for cik, g in day.groupby("cik"):
            latest[cik] = set(g["ticker"])
        counts = pd.Series([t for s in latest.values() for t in s]).value_counts()
        counts = counts[counts >= 2]
        pick = list(counts.head(n).index)
        out.append((pd.Timestamp(filed), {t: 1 / len(pick) for t in pick} if pick else {}))
    return out


_CACHE = {}


def _returns(px: pd.DataFrame):
    """Daily returns as a numpy array (NaN where unpriced) plus a column lookup, cached per frame."""
    key = id(px)
    if key not in _CACHE:
        _CACHE.clear()
        _CACHE[key] = (px.pct_change(fill_method=None).to_numpy(), {c: j for j, c in enumerate(px.columns)},
                       px.notna().to_numpy())
    return _CACHE[key]


def run_portfolios(ports: list[tuple[pd.Timestamp, dict]], px: pd.DataFrame) -> pd.Series:
    """Buy each target at the close after its date, let weights drift, pay cost on turnover.
    Names with no price on the entry day are dropped and the rest re-weighted (none left:
    SPY). A name that stops trading is held as flat cash. NaN before the first portfolio."""
    dates = px.index
    R, col, has = _returns(px)
    sched = {}
    for d, w in ports:
        i = dates.searchsorted(pd.Timestamp(d), side="right")
        if i < len(dates):
            sched[i] = w  # same-session duplicates: last filing wins
    out = np.full(len(dates), np.nan)
    starts = sorted(sched)
    prev_w = None  # drifted weights at the end of the previous segment, {ticker: w}
    for k, i0 in enumerate(starts):
        i1 = starts[k + 1] if k + 1 < len(starts) else len(dates) - 1
        w = {t: v for t, v in sched[i0].items() if t in col and has[i0, col[t]]}
        tot = sum(w.values())
        w = {t: v / tot for t, v in w.items()} if w and tot > 0 else {"SPY": 1.0}
        if prev_w is None:
            turn = 1.0
        else:
            keys = set(w) | set(prev_w)
            turn = sum(abs(w.get(t, 0) - prev_w.get(t, 0)) for t in keys)
        out[i0] = (0.0 if np.isnan(out[i0]) else out[i0]) - COST * turn
        names = list(w)
        wv = np.array([w[t] for t in names])
        seg = np.nan_to_num(R[i0 + 1:i1 + 1][:, [col[t] for t in names]], nan=0.0)
        if len(seg):
            growth = np.cumprod(1 + seg, axis=0) * wv
            val = growth.sum(axis=1)
            out[i0 + 1:i1 + 1] = np.diff(np.concatenate([[1.0], val])) / np.concatenate([[1.0], val[:-1]])
            prev_w = dict(zip(names, growth[-1] / val[-1]))
        else:
            prev_w = w
    return pd.Series(out, index=dates)


def average_series(series: list[pd.Series]) -> pd.Series:
    return pd.concat(series, axis=1).mean(axis=1, skipna=True)


# ------------------------------------------------------------------ Congress

def congress_events(c: pd.DataFrame, px: pd.DataFrame, assets=("ST",), min_amount=0.0,
                    max_delay=None, members=None) -> pd.DataFrame:
    e = c[(c["type"] == "P") & c["asset_type"].isin(assets)].copy()
    e["ticker"] = e["ticker"].str.replace(".", "-", regex=False)
    if min_amount:
        e = e[e["amount_low"].fillna(0) >= min_amount]
    e["delay"] = (e["filed"] - e["tx_date"]).dt.days
    if max_delay is not None:
        e = e[e["delay"].between(0, max_delay)]
    if members is not None:
        e = e[e["last"].str.lower().isin([m.lower() for m in members])]
    e = e[e["ticker"].isin(px.columns)]
    dates = px.index
    e["entry"] = [next_session(dates, d) for d in e["filed"]]
    return e.dropna(subset=["entry"]).drop_duplicates(["ticker", "entry", "member"])


def run_events(e: pd.DataFrame, px: pd.DataFrame, hold: int) -> pd.Series:
    """Equal weight across open positions; each held `hold` sessions from the entry close.
    No open positions: SPY. Cost: each entry and exit trades 1/n of the book."""
    dates = px.index
    R, col, _ = _returns(px)
    T = len(dates)
    i0 = dates.get_indexer(pd.DatetimeIndex(e["entry"]))
    i1 = np.minimum(i0 + hold, T - 1)
    j = np.array([col[t] for t in e["ticker"]], dtype=int)
    diff = np.zeros((T + 1, R.shape[1]))
    np.add.at(diff, (i0 + 1, j), 1)          # held over sessions i0+1 .. i1
    np.add.at(diff, (i1 + 1, j), -1)
    C = np.cumsum(diff, axis=0)[:T]
    n = C.sum(axis=1)
    held = (C * np.nan_to_num(R, nan=0.0)).sum(axis=1)
    spy = np.nan_to_num(R[:, col["SPY"]], nan=0.0)
    out = np.where(n > 0, held / np.maximum(n, 1), spy)
    trades = np.bincount(i0, minlength=T) + np.bincount(i1, minlength=T)
    book = np.maximum(np.concatenate([n[1:], n[-1:]]), 1)   # positions held over the next session
    out = out - COST * trades / book
    first = i0.min() if len(i0) else T
    out[:first] = np.nan
    return pd.Series(out, index=dates)


# ------------------------------------------------------------------ scoring

def score(r: pd.Series, spy_r: pd.Series) -> dict:
    r = r.dropna()
    x = (r - spy_r.reindex(r.index)).dropna()
    if len(x) < 60 or x.std() == 0:
        return dict(days=len(x))
    cum = (1 + x).cumprod()
    yrs = len(r) / 252
    eq = (1 + r).prod()
    spy_eq = (1 + spy_r.reindex(r.index).fillna(0)).prod()
    return dict(start=r.index[0].date().isoformat(), end=r.index[-1].date().isoformat(), days=len(x),
                cagr=eq ** (1 / yrs) - 1, spy_cagr=spy_eq ** (1 / yrs) - 1,
                excess_ann=x.mean() * 252, ir=x.mean() / x.std() * np.sqrt(252),
                excess_mdd=float((cum / cum.cummax() - 1).min()),
                beat_spy_months=float(((1 + x).resample("ME").prod() > 1).mean()),
                usd_1000=1000 * eq, usd_1000_spy=1000 * spy_eq)

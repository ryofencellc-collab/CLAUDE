"""Intraday NQ engine: 1-minute bars, New York time, one position at a time.

Fill rules (conservative, fixed in PROTOCOL_ROUND2.md):
  * a signal on bar i's close is filled at bar i+1's open
  * stop/target are checked on every bar from the entry bar on; if both lie
    inside one bar the stop is assumed hit first; a gap through the stop
    fills at the bar's open
  * any open trade is closed at the close of its window's last bar
"""
from pathlib import Path

import numba
import numpy as np
import pandas as pd

CACHE = Path(__file__).resolve().parent.parent / "data"
COST_PTS = 1.25  # round trip, index points


def load_nq(directory: Path = CACHE / "histdata") -> pd.DataFrame:
    """Read HistData ASCII M1 files into New York-time 1-minute bars.

    HistData timestamps are fixed EST (UTC-5) with no daylight saving.
    """
    files = sorted(directory.glob("DAT_ASCII_NSXUSD_M1_*.csv"))
    if not files:
        raise FileNotFoundError(f"no HistData CSVs in {directory}")
    df = pd.concat(pd.read_csv(f, sep=";", header=None,
                               names=["ts", "open", "high", "low", "close", "vol"]) for f in files)
    est = pd.to_datetime(df["ts"], format="%Y%m%d %H%M%S")
    ny = (est + pd.Timedelta(hours=5)).dt.tz_localize("UTC").dt.tz_convert("America/New_York")
    df.index = ny.dt.tz_localize(None).to_numpy()
    df = df[~df.index.duplicated()].sort_index()[["open", "high", "low", "close"]]
    return df[df["high"] > df["low"]]  # drop flat/no-trade minutes


@numba.njit(cache=True)
def _simulate(o, h, l, c, win, last, sig, sdist, sabs, rr, max_per_win, cost):
    n = len(o)
    out_i = np.empty(n, np.int64)
    out_r = np.empty(n, np.float64)
    out_pts = np.empty(n, np.float64)
    k = 0
    pos = 0
    pending = 0
    p_sdist = 0.0
    p_sabs = np.nan
    p_rr = 0.0
    entry = stop = tgt = risk = 0.0
    cur_win = -1
    p_win = -1
    trades_in_win = 0
    entry_i = 0
    for i in range(n):
        if win[i] != cur_win:
            cur_win = win[i]
            trades_in_win = 0
        if pending != 0 and win[i] != p_win:
            pending = 0  # data gap: never carry a signal into another window
        if pending != 0:
            entry = o[i]
            if np.isnan(p_sabs):
                risk = p_sdist
                stop = entry - pending * risk
            else:
                stop = p_sabs
                risk = (entry - stop) * pending
            if risk > 0:
                tgt = entry + pending * p_rr * risk
                pos = pending
                entry_i = i
                trades_in_win += 1
            pending = 0
        if pos != 0:
            exit_px = np.nan
            if pos == 1:
                if l[i] <= stop:
                    exit_px = min(o[i], stop)
                elif h[i] >= tgt:
                    exit_px = max(o[i], tgt) if i > entry_i else tgt
            else:
                if h[i] >= stop:
                    exit_px = max(o[i], stop)
                elif l[i] <= tgt:
                    exit_px = min(o[i], tgt) if i > entry_i else tgt
            if np.isnan(exit_px) and last[i]:
                exit_px = c[i]
            if not np.isnan(exit_px):
                pts = (exit_px - entry) * pos - cost
                out_i[k] = entry_i
                out_pts[k] = pts
                out_r[k] = pts / risk
                k += 1
                pos = 0
        if pos == 0 and sig[i] != 0 and win[i] >= 0 and not last[i] and trades_in_win < max_per_win:
            pending = sig[i]
            p_win = win[i]
            p_sdist = sdist[i]
            p_sabs = sabs[i]
            p_rr = rr[i]
    return out_i[:k], out_r[:k], out_pts[:k]


def simulate(bars: pd.DataFrame, win, last, sig, sdist, sabs, rr,
             max_per_win: int, cost: float | None = None) -> pd.DataFrame:
    cost = COST_PTS if cost is None else cost
    a = lambda x: np.ascontiguousarray(np.asarray(x, dtype=np.float64))
    idx, r, pts = _simulate(a(bars["open"]), a(bars["high"]), a(bars["low"]), a(bars["close"]),
                            np.asarray(win, np.int64), np.asarray(last, np.bool_),
                            np.asarray(sig, np.int64), a(sdist), a(sabs), a(rr),
                            max_per_win, float(cost))
    return pd.DataFrame({"time": bars.index[idx], "R": r, "pts": pts})


# ---------------------------------------------------------------- windows

WINDOWS = {"am": (9 * 60 + 30, 11 * 60), "pm": (14 * 60, 15 * 60),
           "asia": (20 * 60, 21 * 60 + 30), "rth": (9 * 60 + 30, 16 * 60)}


def window_ids(bars: pd.DataFrame, names: list[str]):
    """Window id per bar (-1 outside), last-bar flag, minutes since window start, window open."""
    mod = (bars.index.hour * 60 + bars.index.minute).to_numpy()
    day = (bars.index.normalize().asi8 // 86_400_000_000_000).astype(np.int64)
    win = np.full(len(bars), -1, np.int64)
    since = np.full(len(bars), -1, np.int64)
    for j, name in enumerate(names):
        s, e = WINDOWS[name]
        m = (mod >= s) & (mod < e)
        win[m] = day[m] * 8 + j
        since[m] = mod[m] - s
    w = pd.Series(win, index=bars.index)
    last = (w != w.shift(-1)).to_numpy() & (win >= 0)
    first_open = bars["open"].groupby(win).transform("first").to_numpy()
    fv = np.where(win >= 0, first_open, np.nan)
    # a window only counts if its first bar is at the window's start minute
    started = pd.Series(since, index=bars.index).groupby(win).transform("min").to_numpy() == 0
    win = np.where(started, win, -1)
    return win, last & started, since, fv


# ---------------------------------------------------------------- strategies

def jj_fair_value(bars, windows, stops, disp, L, phases, max_per_win=3):
    names = {"am": ["am"], "am+pm": ["am", "pm"], "asia": ["asia"]}[windows]
    win, last, since, fv = window_ids(bars, names)
    o, h, l, c = (bars[k] for k in ("open", "high", "low", "close"))
    rng = h - l
    avg = rng.rolling(20).mean().shift(1)
    bull = (c > o) & ((o - l) < 0.2 * rng) & (rng >= disp * avg) & (c > h.rolling(L).max().shift(1))
    bear = (c < o) & ((h - o) < 0.2 * rng) & (rng >= disp * avg) & (c < l.rolling(L).min().shift(1))
    cont = since < 15
    above = c.to_numpy() > fv
    below = c.to_numpy() < fv
    long_ok = np.zeros(len(bars), bool)
    short_ok = np.zeros(len(bars), bool)
    if phases in ("both", "continuation"):
        long_ok |= cont & above
        short_ok |= cont & below
    if phases in ("both", "reversion"):
        long_ok |= ~cont & below
        short_ok |= ~cont & above
    sig = np.where(bull.to_numpy() & long_ok, 1, np.where(bear.to_numpy() & short_ok, -1, 0))
    sig = np.where(win >= 0, sig, 0)
    if stops == "regime":
        tr = pd.concat([rng, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
        atr = tr.rolling(14).mean().to_numpy()
        sdist = np.where(atr > 20, 50.0, np.where(atr >= 7, 25.0, 16.5))
    else:
        sdist = np.full(len(bars), 25.0)
    n = len(bars)
    return simulate(bars, win, last, sig, sdist, np.full(n, np.nan), np.full(n, 1.5), max_per_win)


def orb(bars, n, k):
    win, last, since, fv = window_ids(bars, ["rth"])
    o, h, l, c = (bars[x].to_numpy() for x in ("open", "high", "low", "close"))
    s_win = pd.Series(win)
    in_or = (since >= 0) & (since < n)
    hi = pd.Series(np.where(in_or, h, np.nan)).groupby(s_win).cummax().to_numpy()
    lo = pd.Series(np.where(in_or, l, np.nan)).groupby(s_win).cummin().to_numpy()
    at_end = since == n - 1
    direction = np.sign(c - fv)
    sig = np.where(at_end & (win >= 0), direction, 0).astype(np.int64)
    sabs = np.where(sig == 1, lo, np.where(sig == -1, hi, np.nan))
    rr = np.full(len(bars), np.inf if k == "eod" else float(k))
    return simulate(bars, win, last, sig, np.zeros(len(bars)), sabs, rr, max_per_win=1)


FAMILIES = {
    "jj_fair_value": (jj_fair_value, [
        dict(windows=w, stops=s, disp=d, L=L, phases=p)
        for w in ("am", "am+pm", "asia") for s in ("regime", "fixed")
        for d in (1.0, 1.5) for L in (5, 10) for p in ("both", "continuation", "reversion")]),
    "orb": (orb, [dict(n=n, k=k) for n in (5, 15, 30) for k in (1.5, 3, 10, "eod")]),
}


def trade_stats(t: pd.DataFrame, days: pd.DatetimeIndex) -> dict:
    """Owner-requested 'prints money' stats plus the ones that actually decide.

    days = every trading day in the segment, so flat days count as zero.
    """
    if t.empty:
        return dict(trades=0, win_rate=0.0, avg_R=0.0, profit_factor=0.0, green_days=0.0,
                    total_R=0.0, max_dd_R=0.0, sharpe=0.0)
    traded = t.groupby(t["time"].dt.normalize())["R"].sum()
    daily = traded.reindex(days.union(traded.index), fill_value=0.0)  # Sunday-evening sessions too
    eq = daily.cumsum()
    gains, losses = t.loc[t["R"] > 0, "R"].sum(), -t.loc[t["R"] < 0, "R"].sum()
    return dict(
        trades=len(t),
        win_rate=float((t["R"] > 0).mean()),
        avg_R=float(t["R"].mean()),
        profit_factor=float(gains / losses) if losses > 0 else float("inf"),
        green_days=float((traded > 0).mean()),  # share of days traded that ended green
        total_R=float(daily.sum()),
        max_dd_R=float((eq - eq.cummax()).min()),
        sharpe=float(daily.mean() / daily.std() * np.sqrt(252)) if daily.std() > 0 else 0.0,
    )

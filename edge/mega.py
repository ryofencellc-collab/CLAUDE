"""Round 56 engine (PROTOCOL_ROUND56.md): enumerate ~80k intraday configurations per market."""
import itertools
import numba
import numpy as np
import pandas as pd

ENTRIES = list(range(5, 381, 5))                       # bar index from 09:30: 09:35 ... 15:50 (76)
HOLDS = [5, 15, 30, 60, 120, 240, 999]
STOPS = [0.0, 0.001, 0.0025, 0.005, 0.01]
SIGNALS = ["gap", "since_open", "last5", "last15", "last30", "last60", "last120", "prev_day", "prev_5d", "prev_20d"]
FILTERS = ["none", "big_med", "big_q75", "big_q90", "hi_range", "lo_range", "mon", "tue", "wed", "thu", "fri", "trend_up", "trend_dn",
           "gap_up", "gap_dn", "month_end"]


@numba.njit(cache=True)
def trade_returns(O, H, L, C, e, hold, stop):
    """Long and short returns per day for entry at O[:, e], exit after `hold` bars (or 389), optional % stop."""
    D = O.shape[0]; rl = np.full(D, np.nan); rs = np.full(D, np.nan)
    x = min(e + hold, 390) - 1
    for d in range(D):
        p0 = O[d, e]
        if not (p0 > 0):
            continue
        outl = C[d, x]; outs = C[d, x]
        if stop > 0:
            sl = p0 * (1 - stop); ss = p0 * (1 + stop); hitl = False; hits = False
            for j in range(e, x + 1):
                if not hitl and L[d, j] <= sl:
                    outl = min(O[d, j], sl) if j > e else sl; hitl = True
                if not hits and H[d, j] >= ss:
                    outs = max(O[d, j], ss) if j > e else ss; hits = True
                if hitl and hits:
                    break
        rl[d] = outl / p0 - 1; rs[d] = 1 - outs / p0
    return rl, rs


def signal(M, name, e):
    O, C = M["o"], M["c"]; pc = M["prev_close"]; last = C[:, e - 1]
    if name == "gap": return O[:, 0] / pc - 1
    if name == "since_open": return last / O[:, 0] - 1
    if name.startswith("last"):
        k = int(name[4:]); return last / C[:, max(e - 1 - k, 0)] - 1
    if name == "prev_day": return pc / np.r_[np.nan, pc[:-1]] - 1
    if name == "prev_5d": return pc / np.r_[np.full(5, np.nan), pc[:-5]] - 1
    if name == "prev_20d": return pc / np.r_[np.full(20, np.nan), pc[:-20]] - 1
    raise ValueError(name)


def filt(M, name, sig):
    D = len(M["days"]); wd = M["days"].weekday
    a = pd.Series(np.abs(sig))
    if name == "none": return np.ones(D, bool)
    if name == "big_med": return np.abs(sig) >= a.shift(1).rolling(250, min_periods=120).median().to_numpy()
    if name == "big_q75": return np.abs(sig) >= a.shift(1).rolling(250, min_periods=120).quantile(0.75).to_numpy()
    if name == "big_q90": return np.abs(sig) >= a.shift(1).rolling(250, min_periods=120).quantile(0.90).to_numpy()
    if name == "gap_up": return M["o"][:, 0] > M["prev_close"]
    if name == "gap_dn": return M["o"][:, 0] < M["prev_close"]
    if name == "month_end":
        d = pd.Series(M["days"]); last = d.groupby([d.dt.year, d.dt.month]).transform("max")
        rank = d.groupby([d.dt.year, d.dt.month]).rank(ascending=False)
        return (rank <= 3).to_numpy()
    if name == "hi_range": return M["prev_rng"] >= M["rng_med"]
    if name == "lo_range": return M["prev_rng"] < M["rng_med"]
    if name in ("mon", "tue", "wed", "thu", "fri"): return wd == ["mon", "tue", "wed", "thu", "fri"].index(name)
    if name == "trend_up": return M["prev_close"] > M["prev_sma20"]
    if name == "trend_dn": return M["prev_close"] < M["prev_sma20"]
    raise ValueError(name)


def period_stats(r, masks):
    out = []
    for m in masks:
        v = r[m & np.isfinite(r)]
        n = len(v)
        if n < 30:
            out += [n, np.nan, np.nan]; continue
        sd = v.std()
        out += [n, v.mean() * 1e4, v.mean() / sd * np.sqrt(n) if sd > 0 else np.nan]
    return out


def run_market(M, cost_bp, market, cuts):
    """cuts = (search_end, select_end) timestamps. Returns a DataFrame with stats for the three periods."""
    days = M["days"]
    masks = [days < cuts[0], (days >= cuts[0]) & (days < cuts[1]), days >= cuts[1]]
    O, H, L, C = (np.ascontiguousarray(M[k]) for k in ("o", "h", "l", "c"))
    rows = []
    for e in ENTRIES:
        sigs = {s: signal(M, s, e) for s in SIGNALS}
        fl = {(s, f): filt(M, f, sigs[s]) & np.isfinite(sigs[s]) & (sigs[s] != 0) for s in SIGNALS for f in FILTERS}
        for hold, stop in itertools.product(HOLDS, STOPS):
            rl, rs = trade_returns(O, H, L, C, e, hold, stop)
            rl = rl - cost_bp / 1e4; rs = rs - cost_bp / 1e4
            for s in SIGNALS:
                sg = np.sign(sigs[s])
                for mode in ("mom", "rev"):
                    dirn = sg if mode == "mom" else -sg
                    r = np.where(dirn > 0, rl, rs)
                    for f in FILTERS:
                        st = period_stats(r, [fl[(s, f)] & m for m in masks])
                        rows.append((market, e, s, mode, f, hold, stop, *st))
    cols = ["market", "entry_bar", "signal", "mode", "filter", "hold", "stop"] + \
           [f"{p}_{k}" for p in ("search", "select", "final") for k in ("n", "bp", "t")]
    return pd.DataFrame(rows, columns=cols)


def shortlist(T, k=20, per_market=5):
    s = T[(T.search_bp > 0) & (T.search_t >= 2) & (T.select_bp > 0) & (T.select_t >= 2)].copy()
    s["min_t"] = np.minimum(s.search_t, s.select_t)
    s = s.sort_values("min_t", ascending=False).drop_duplicates(["market", "signal", "entry_bar"])
    out = s.groupby("market").head(per_market).sort_values("min_t", ascending=False).head(k)
    return out, len(s)


def verdict(S):
    return S.assign(PASS=(S.final_bp > 0) & (S.final_t >= 2.81) & (S.final_n >= 100))


def bar_time(e):
    m = 570 + e; return f"{m // 60:02d}:{m % 60:02d}"

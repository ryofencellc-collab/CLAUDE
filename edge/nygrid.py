"""Round 53 engine (PROTOCOL_ROUND53.md): day-matrix NY session bars + numba kernels for entries, exits and prop scoring."""
from __future__ import annotations
import numba
import numpy as np
import pandas as pd

N_BARS = 390


def day_matrix(bars: pd.DataFrame) -> dict:
    """Pivot 1-minute NY-time bars into (days x 390) RTH arrays plus per-day context."""
    idx = bars.index
    tod = idx.hour * 60 + idx.minute
    rth = bars[(tod >= 570) & (tod < 960)]
    t = rth.index.hour * 60 + rth.index.minute - 570
    day = rth.index.normalize()
    days = pd.Index(sorted(set(day)))
    D = len(days); pos = days.get_indexer(day)
    M = {k: np.full((D, N_BARS), np.nan) for k in ("o", "h", "l", "c")}
    for k, col in (("o", "open"), ("h", "high"), ("l", "low"), ("c", "close")):
        M[k][pos, t] = rth[col].to_numpy()
    cnt = np.isfinite(M["c"]).sum(axis=1)
    keep = cnt >= 380
    for k in M:  # forward-fill small gaps inside the session
        df = pd.DataFrame(M[k][keep]).ffill(axis=1).bfill(axis=1); M[k] = df.to_numpy()
    days = days[keep]
    c_last = M["c"][:, -1]
    prev_close = np.r_[np.nan, c_last[:-1]]
    prev_hi = np.r_[np.nan, M["h"].max(axis=1)[:-1]]; prev_lo = np.r_[np.nan, M["l"].min(axis=1)[:-1]]
    rng = M["h"].max(axis=1) - M["l"].min(axis=1)
    prev_rng = np.r_[np.nan, rng[:-1]]
    rng_med = pd.Series(prev_rng).rolling(60, min_periods=30).median().to_numpy()
    sma20 = pd.Series(c_last).rolling(20, min_periods=15).mean().to_numpy()
    prev_sma20 = np.r_[np.nan, sma20[:-1]]
    # overnight range: 18:00 previous calendar day -> 09:29
    on = bars[(tod >= 1080) | (tod < 570)]
    on_key = (on.index + pd.Timedelta(hours=6)).normalize()
    g = on.groupby(on_key)
    on_hi = g["high"].max().reindex(days).to_numpy(); on_lo = g["low"].min().reindex(days).to_numpy()
    return dict(days=days, o=M["o"], h=M["h"], l=M["l"], c=M["c"], prev_close=prev_close, prev_hi=prev_hi, prev_lo=prev_lo,
                prev_rng=prev_rng, rng_med=rng_med, prev_sma20=prev_sma20, on_hi=on_hi, on_lo=on_lo)


@numba.njit(cache=True)
def walk(o, h, l, c, i0, side, stop, tgt, last):
    """Return exit price for a trade entered at o[i0] (one day's bars)."""
    for j in range(i0, last + 1):
        if side > 0:
            if l[j] <= stop:
                return min(o[j], stop) if j > i0 else stop
            if tgt == tgt and h[j] >= tgt:
                return max(o[j], tgt) if j > i0 else tgt
        else:
            if h[j] >= stop:
                return max(o[j], stop) if j > i0 else stop
            if tgt == tgt and l[j] <= tgt:
                return min(o[j], tgt) if j > i0 else tgt
    return c[last]


@numba.njit(cache=True)
def entries(fam, p, O, H, L, C, prev_close, prev_hi, prev_lo, on_hi, on_lo, flat):
    """Per day: (entry bar, side, structural stop) for one entry family; entry bar -1 = no trade."""
    D = O.shape[0]
    ent = np.full(D, -1); side = np.zeros(D); sstop = np.full(D, np.nan)
    for d in range(D):
        o = O[d]; h = H[d]; l = L[d]; c = C[d]
        if fam == 0 or fam == 1:            # ORB / OR-fade, p = range minutes
            n = int(p); hi = h[:n].max(); lo = l[:n].min(); broke = 0
            for k in range(n, flat):
                if fam == 0:
                    if c[k] > hi or c[k] < lo:
                        ent[d] = k + 1; side[d] = 1.0 if c[k] > hi else -1.0; sstop[d] = lo if c[k] > hi else hi; break
                else:
                    if broke == 0 and (c[k] > hi or c[k] < lo):
                        broke = 1 if c[k] > hi else -1
                    elif broke != 0 and lo <= c[k] <= hi:
                        ent[d] = k + 1; side[d] = -broke
                        ext = h[n:k + 1].max() if broke > 0 else l[n:k + 1].min()
                        sstop[d] = ext; break
        elif fam == 2 or fam == 3:          # gap fill / gap-and-go, p = gap fraction
            pc = prev_close[d]
            if pc != pc: continue
            gap = o[0] / pc - 1
            if abs(gap) < p: continue
            if fam == 2:
                ent[d] = 1; side[d] = -1.0 if gap > 0 else 1.0
            else:
                k = 15
                if (gap > 0 and c[k - 1] > o[0]) or (gap < 0 and c[k - 1] < o[0]):
                    ent[d] = k; side[d] = 1.0 if gap > 0 else -1.0
        elif fam == 4:                      # first-hour trend, p = threshold
            mv = c[59] / o[0] - 1
            if abs(mv) >= p:
                ent[d] = 60; side[d] = 1.0 if mv > 0 else -1.0
        elif fam == 5 or fam == 6:          # prior-day / overnight level breakout
            hi = prev_hi[d] if fam == 5 else on_hi[d]; lo = prev_lo[d] if fam == 5 else on_lo[d]
            if hi != hi or lo != lo: continue
            for k in range(5, flat):
                if c[k] > hi or c[k] < lo:
                    if k == 5 and (c[4] > hi or c[4] < lo):
                        break               # already outside at the start: not a breakout today
                    ent[d] = k + 1; side[d] = 1.0 if c[k] > hi else -1.0; sstop[d] = lo if c[k] > hi else hi; break
        elif fam == 7:                      # power hour, p = threshold
            mv = c[329] / o[0] - 1
            if abs(mv) >= p:
                ent[d] = 330; side[d] = 1.0 if mv > 0 else -1.0
        elif fam == 8:                      # stretch fade vs 30-bar average, p = threshold
            for k in range(30, flat):
                m = c[k - 30:k].mean()
                dev = c[k] / m - 1
                if abs(dev) >= p:
                    ent[d] = k + 1; side[d] = -1.0 if dev > 0 else 1.0; sstop[d] = np.nan; break
        if ent[d] >= flat:
            ent[d] = -1
    return ent, side, sstop


@numba.njit(cache=True)
def run_config(O, H, L, C, ent, side, sstop, stop_mode, stop_pct, rr, flat, tgt_override):
    """Exit price, entry price and risk (points) per day; nan when no trade."""
    D = O.shape[0]
    e_px = np.full(D, np.nan); x_px = np.full(D, np.nan); risk = np.full(D, np.nan)
    for d in range(D):
        i0 = ent[d]
        if i0 < 0: continue
        e = O[d, i0]; s = side[d]
        if stop_mode == 0:
            st = sstop[d]
            if st != st: continue
        else:
            st = e * (1 - s * stop_pct)
        r = (e - st) * s
        if r <= 0: continue
        tgt = np.nan
        if tgt_override[d] == tgt_override[d]:
            tgt = tgt_override[d]
            if (tgt - e) * s <= 0: continue
        elif rr > 0:
            tgt = e + s * rr * r
        x_px[d] = walk(O[d], H[d], L[d], C[d], i0, s, st, tgt, flat - 1)
        e_px[d] = e; risk[d] = r
    return e_px, x_px, risk


@numba.njit(cache=True)
def prop_sim(daily, starts):
    """Prop evaluation from each start index: target +3000, trailing floor (peak-2000, capped at 0 once peak >= 2000),
    daily loss -1000 fails, 60 days max. Returns pass flag and days used; plus first funded month's profit if passed."""
    n = len(starts); passed = np.zeros(n); used = np.zeros(n); funded = np.zeros(n)
    T = len(daily)
    for a in range(n):
        s = starts[a]; bal = 0.0; peak = 0.0; k = 0
        status = 0
        while k < 60 and s + k < T:
            v = daily[s + k]; bal += v; k += 1
            if v <= -1000: status = -1; break
            if bal >= 3000: status = 1; break
            if bal > peak: peak = bal
            if bal <= min(peak - 2000.0, 0.0): status = -1; break
        used[a] = k
        if status == 1:
            passed[a] = 1
            fb = 0.0; fpk = 0.0; alive = True
            j = s + k
            for m in range(21):
                if j + m >= T: break
                v = daily[j + m]; fb += v
                if fb > fpk: fpk = fb
                if v <= -1000 or fb <= min(fpk - 2000.0, 0.0):
                    alive = False; break
            funded[a] = max(fb, 0.0) * 0.9 if alive else 0.0
    return passed, used, funded

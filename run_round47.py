"""Round 47 (PROTOCOL_ROUND47.md): rules from community Claude trading skills, rebuilt and backtested."""
import math, os
import numpy as np, pandas as pd

D = "data/r38"
COST = 0.001
DEV0, SPLIT, END = pd.Timestamp("2015-01-01"), pd.Timestamp("2022-01-01"), pd.Timestamp("2026-11-01")


def load():
    O, H, L, C, V = (pd.read_pickle(f"{D}/stocks_{k}.pkl").astype(float) for k in "OHLCV")
    cols = C.columns
    O, H, L, V = (x.reindex(index=C.index, columns=cols) for x in (O, H, L, V))
    R = pd.read_pickle(f"{D}/stocks_R.pkl").astype(float).reindex(index=C.index, columns=cols) if os.path.exists(f"{D}/stocks_R.pkl") else C
    dv = (R * V).rolling(20, min_periods=15).mean()
    ok = (R >= 10) & (dv >= 20e6)
    return O, H, L, C, V, ok


def signals(O, H, L, C, V, ok):
    rng = (H - L).replace(0, np.nan); ibs = (C - L) / rng
    ch = C / C.shift(1) - 1
    s = {}
    s["S1"] = ok & (ch >= 0.04) & (V > V.shift(1)) & (V >= 1e5) & (ibs >= 0.7) & (ch.shift(1) <= 0.02)
    sma50, sma200 = C.rolling(50, min_periods=40).mean(), C.rolling(200, min_periods=150).mean()
    s["S2"] = ok & (C > sma50) & (sma50 > sma200) & (C <= 0.92 * H.rolling(20).max()) & (L < L.shift(1)) & (C > L.shift(1)) \
        & (ibs >= 0.7) & (V >= 1.2 * V.rolling(20).mean().shift(1))
    s["S3"] = ok & (O / C.shift(1) - 1 >= 0.05) & (V >= 3 * V.rolling(50, min_periods=30).mean().shift(1)) & (C >= O)
    rank = V / V.rolling(50, min_periods=30).mean().shift(1)
    return s, rank


def trade(o, h, l, c, i, stop, hold, target_r=None):
    """Enter at o[i+1]; exit on stop (gap -> open), optional +R target, else close of day i+hold."""
    n = len(c)
    if i + 1 >= n or not np.isfinite(o[i + 1]):
        return None
    e = o[i + 1]
    risk = e - stop
    if not np.isfinite(stop) or risk <= 0:
        return None
    tgt = e + target_r * risk if target_r else None
    for j in range(i + 1, min(i + hold, n - 1) + 1):
        if not np.isfinite(l[j]):
            return None
        if l[j] <= stop:
            px = min(o[j], stop) if j > i + 1 else stop
            return px / e - 1 - 2 * COST, j
        if tgt is not None and h[j] >= tgt:
            px = max(o[j], tgt) if j > i + 1 else tgt
            return px / e - 1 - 2 * COST, j
    j = min(i + hold, n - 1)
    return c[j] / e - 1 - 2 * COST, j


VARIANTS = {"S1a momentum burst, 3 days": ("S1", "low", 3, None), "S1b momentum burst, 5 days": ("S1", "low", 5, None),
            "S2 exhaustion hammer, 2R / 10 days": ("S2", "low", 10, 2.0),
            "S3a earnings-gap drift, 20 days": ("S3", "low", 20, None), "S3b earnings-gap drift, 60 days": ("S3", "low", 60, None)}


def run_variant(name, O, H, L, C, sig, rank):
    key, _, hold, tr = VARIANTS[name]
    S = sig[key]
    idx = C.index
    rows = []
    for col in S.columns[S.any(axis=0).to_numpy()]:
        o, h, l, c = (x[col].to_numpy() for x in (O, H, L, C))
        for i in np.flatnonzero(S[col].to_numpy()):
            r = trade(o, h, l, c, i, l[i], hold, tr)
            if r is None:
                continue
            rows.append((idx[i], col, r[0], idx[r[1]], rank[col].iloc[i]))
    return pd.DataFrame(rows, columns=["date", "sym", "ret", "exit", "rank"])


def clustered_t(t):
    g = t.groupby("date").ret.sum(); n = t.groupby("date").size()
    m = t.ret.mean(); resid = g - m * n
    se = math.sqrt((resid ** 2).sum()) / len(t) if len(t) else np.nan
    return m / se if se and se > 0 else np.nan


def portfolio(t, a, b, per=5, w=0.10, cap=10):
    t = t[(t.date >= a) & (t.date < b)].sort_values(["date", "rank"], ascending=[True, False])
    t = t.groupby("date").head(per)
    days = pd.bdate_range(a, b)
    eq, open_, pnl = 1.0, [], pd.Series(0.0, index=days)
    for d, x in t.groupby("date"):
        open_ = [e for e in open_ if e > d]
        for _, r in x.iterrows():
            if len(open_) >= cap:
                break
            open_.append(r.exit)
            if r.exit in pnl.index:
                pnl[r.exit] += w * r.ret
    curve = (1 + pnl).cumprod()
    yrs = (b - a).days / 365.25
    cagr = curve.iloc[-1] ** (1 / yrs) - 1
    sh = pnl.mean() / pnl.std() * math.sqrt(252) if pnl.std() > 0 else 0
    return cagr, sh, (curve / curve.cummax() - 1).min()


def s5():
    import yfinance as yf
    x = yf.download("SPY", start="2014-01-01", auto_adjust=True, progress=False)
    c, v = x["Close"].squeeze(), x["Volume"].squeeze()
    c.index = pd.to_datetime(c.index).tz_localize(None); v.index = c.index
    ret = c.pct_change().fillna(0)
    low25 = c.rolling(25).min()
    dist = ((ret <= -0.002) & (v > v.shift(1))).astype(int)
    pos, inv, day1 = np.zeros(len(c)), False, None
    for i in range(26, len(c)):
        if not inv:
            if c.iloc[i - 1] <= low25.iloc[i - 1] and ret.iloc[i] > 0:
                day1 = i
            if day1 is not None and i - day1 >= 3 and ret.iloc[i] >= 0.0125 and v.iloc[i] > v.iloc[i - 1]:
                inv, day1 = True, None
        else:
            if dist.iloc[i - 24:i + 1].sum() >= 5:
                inv = False
        pos[i] = 1.0 if inv else 0.0
    strat = pd.Series(pos, index=c.index).shift(1).fillna(0) * ret - pd.Series(pos, index=c.index).diff().abs().fillna(0) * COST
    out = []
    for nm, r in (("S5 FTD/distribution timing", strat), ("SPY buy-and-hold", ret)):
        for per, a, b in (("dev", DEV0, SPLIT), ("holdout", SPLIT, END)):
            y = r[(r.index >= a) & (r.index < b)]
            eq = (1 + y).cumprod(); yrs = (b - a).days / 365.25
            out.append(dict(rule=nm, period=per, CAGR=f"{eq.iloc[-1] ** (1 / yrs) - 1:.1%}", Sharpe=round(y.mean() / y.std() * math.sqrt(252), 2),
                            worst_drop=f"{(eq / eq.cummax() - 1).min():.1%}", in_market=f"{(y != 0).mean():.0%}"))
    return pd.DataFrame(out)


def main():
    O, H, L, C, V, ok = load()
    sig, rank = signals(O, H, L, C, V, ok)
    rows, passed = [], []
    for name in VARIANTS:
        t = run_variant(name, O, H, L, C, sig, rank)
        dv, ho = t[(t.date >= DEV0) & (t.date < SPLIT)], t[t.date >= SPLIT]
        pc, ps, pdd = portfolio(t, SPLIT, END)
        dc, dsh, _ = portfolio(t, DEV0, SPLIT)
        row = dict(rule=name, dev_trades=len(dv), dev_mean=f"{dv.ret.mean():.2%}", hold_trades=len(ho), hold_mean=f"{ho.ret.mean():.2%}",
                   hold_t=round(clustered_t(ho), 2), hold_win=f"{(ho.ret > 0).mean():.0%}", dev_port_CAGR=f"{dc:.1%}",
                   hold_port_CAGR=f"{pc:.1%}", hold_port_Sharpe=round(ps, 2), hold_port_drop=f"{pdd:.1%}")
        ok_ = ho.ret.mean() >= 0.003 and clustered_t(ho) >= 3 and dv.ret.mean() > 0 and pc >= 0.15 and ps >= 1
        row["PASS"] = "YES" if ok_ else ""
        rows.append(row); passed += [name] if ok_ else []
        print(row, flush=True)
    out = ["# Round 47: strategies from community Claude trading skills (rebuilt, not their code)", "",
           "Rules: [PROTOCOL_ROUND47.md](../PROTOCOL_ROUND47.md). US stocks, real price ≥ $10, $20M/day; 0.10%/side; dev 2015–2021, holdout 2022→.", "",
           pd.DataFrame(rows).to_markdown(index=False), ""]
    try:
        out += ["## S5 O'Neil market timing on SPY", "", s5().to_markdown(index=False), ""]
    except Exception as e:
        out.append(f"S5 failed: {e!r}")
    out.append(f"**Passing: {', '.join(passed) or 'none'}.**")
    open("reports/ROUND47.md", "w").write("\n".join(out) + "\n"); print("\n".join(out))


if __name__ == "__main__":
    main()

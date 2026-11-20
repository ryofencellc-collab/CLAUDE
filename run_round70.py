"""Round 70 (PROTOCOL_ROUND70.md): Kalshi S&P 4pm markets vs SPXW 0DTE option-implied probabilities.  Usage: smoke | collect | report"""
import glob, math, os, pickle, sys
import numpy as np, pandas as pd

ET = "America/New_York"
MARGINS = [0.02, 0.03, 0.05, 0.08]
DEV_END = "2026-11-13"
OUT = "data/r70"; os.makedirs(OUT, exist_ok=True)


def fee(p):
    return np.ceil(0.07 * p * (1 - p) * 100 - 1e-9) / 100


# ---------------------------------------------------------------- Kalshi
def kalshi_threshold(m):
    """(lo, hi) such that YES <=> lo <= S_close < hi."""
    st = m.get("strike_type"); f = m.get("floor_strike"); c = m.get("cap_strike")
    if st in ("greater", "greater_or_equal"): return (math.ceil(float(f) - 1e-6) if st == "greater" else float(f) + 0.0099, np.inf)
    if st == "less": return (-np.inf, float(c))
    if st == "between": return (float(f), float(c) + 0.0001)
    return None


def collect():
    from edge import round20 as r20, round31 as r31
    days = sorted(os.path.basename(p) for p in glob.glob("data/odte/2*"))
    a, b = pd.Timestamp(days[0], tz="UTC"), pd.Timestamp(days[-1], tz="UTC") + pd.Timedelta(days=2)
    ms = []
    for s in ("KXINXU", "KXINX"):
        for m in r20.markets(s, a, b):
            if not m["event_ticker"].endswith("H1600"): continue
            d = pd.Timestamp(m["close_time"]).tz_convert(ET).date().isoformat()
            th = kalshi_threshold(m)
            if d in days and th: ms.append(dict(series=s, ticker=m["ticker"], day=d, lo=th[0], hi=th[1], y=float(m["result"] == "yes"), open_time=m["open_time"], close_time=m["close_time"]))
    M = pd.DataFrame(ms); print("markets", len(M), M.groupby(["series", "day"]).size().to_dict(), flush=True)
    from edge import weather as wx
    qs = []
    for i, r in enumerate(M.itertuples()):
        a_ = pd.Timestamp(r.day + " 09:55", tz=ET); b_ = pd.Timestamp(r.close_time)
        x = wx._get(f"{wx.KALSHI}/series/{r.series}/markets/{r.ticker}/candlesticks",
                    {"start_ts": int(a_.timestamp()), "end_ts": int(b_.timestamp()), "period_interval": 1})
        if x is not None and x.status_code == 200:
            qs.append(r31.parse_candles(r.ticker, x.json().get("candlesticks")))
        if i % 100 == 0: print("candles", i, len(M), sum(len(q) for q in qs), flush=True)
    Q = pd.concat(qs, ignore_index=True) if qs else pd.DataFrame()
    print("candles", len(Q), flush=True)
    pickle.dump((M, Q), open(f"{OUT}/kalshi.pkl", "wb"))


# ---------------------------------------------------------------- options -> digitals
def digitals(day):
    """DataFrame index = minute (ET), columns = strike grid, values = P(S_close >= K)."""
    from edge import odte_score as O
    x = O.load_day(day, "SPXW")
    x = x[(x.bid > 0) & (x.ask >= x.bid)].copy(); x["mid"] = (x.bid + x.ask) / 2; x["t"] = x.t.dt.floor("min")
    out = {}
    for t, g in x.groupby("t"):
        c = g[g.cp == "C"].groupby("K").mid.mean(); p = g[g.cp == "P"].groupby("K").mid.mean()
        Ks = np.arange(math.floor(g.K.min() / 5) * 5, math.ceil(g.K.max() / 5) * 5 + 5, 5.0)
        dc = (c.reindex(Ks - 5).to_numpy() - c.reindex(Ks + 5).to_numpy()) / 10
        dp = 1 - (p.reindex(Ks + 5).to_numpy() - p.reindex(Ks - 5).to_numpy()) / 10
        D = np.nanmean(np.vstack([dc, dp]), axis=0)
        out[t] = pd.Series(np.clip(D, 0, 1), index=Ks)
    D = pd.DataFrame(out).T.sort_index()
    return D.apply(lambda r: r.interpolate(limit_area="inside"), axis=1)


def d_at(Drow, K):
    if not np.isfinite(K): return 1.0 if K < 0 else 0.0
    ks = Drow.dropna()
    if len(ks) < 4 or K < ks.index.min() or K > ks.index.max():
        return 1.0 if len(ks) and K < ks.index.min() else (0.0 if len(ks) and K > ks.index.max() else np.nan)
    return float(np.interp(K, ks.index.to_numpy(float), ks.to_numpy(float)))


def panel(M, Q, Dmaps):
    """Long table: one row per market-minute with Kalshi bid/ask and fair value S (same minute) and L (15 min older)."""
    Q = Q.copy(); Q["t"] = pd.to_datetime(Q.t, utc=True).dt.tz_convert(ET).dt.floor("min")
    Q = Q[(Q.t.dt.hour * 60 + Q.t.dt.minute >= 600) & (Q.t.dt.hour * 60 + Q.t.dt.minute <= 945)]
    J = Q.merge(M[["ticker", "day", "lo", "hi", "y", "series"]], on="ticker")
    rows = []
    for day, g in J.groupby("day"):
        D = Dmaps.get(day)
        if D is None or D.empty: continue
        for lag, col in ((0, "fS"), (15, "fL")):
            idx = D.index.get_indexer(g.t - pd.Timedelta(minutes=lag), method="pad")
            vals = []
            for k, (lo, hi) in zip(idx, zip(g.lo, g.hi)):
                if k < 0: vals.append(np.nan); continue
                r = D.iloc[k]; vals.append(d_at(r, lo) - d_at(r, hi))
            g = g.assign(**{col: vals})
        rows.append(g)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


# ---------------------------------------------------------------- strategy
def trades(P, col, m):
    P = P[(P.bid > 0) & (P.ask > 0.02) & (P.ask < 0.98) & P[col].notna()].sort_values("t")
    ey = P[col] - P.ask - fee(P.ask); no_px = 1 - P.bid; en = (1 - P[col]) - no_px - fee(no_px)
    P = P.assign(ey=ey, en=en)
    sig = P[(P.ey >= m) | (P.en >= m)]
    first = sig.groupby("ticker").head(1)
    yes = first.ey >= first.en
    px = np.where(yes, first.ask, 1 - first.bid)
    pnl = np.where(yes, first.y - first.ask - fee(first.ask), (1 - first.y) - (1 - first.bid) - fee(1 - first.bid))
    return first.assign(side=np.where(yes, "yes", "no"), px=px, pnl=pnl, fair=np.where(yes, first[col], 1 - first[col]))


def tstat(x):
    x = np.asarray(x, float); return x.mean() / x.std(ddof=1) * math.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else float("nan")


def analyze(P):
    dev = P[P.day <= DEV_END]; ho = P[P.day > DEV_END]; res = {}
    for col in ("fS", "fL"):
        G = pd.DataFrame([dict(m=m, dev_n=len(T), dev_total=T.pnl.sum(), dev_mean=T.pnl.mean() if len(T) else np.nan) for m in MARGINS for T in [trades(dev, col, m)]])
        mb = float(G.sort_values("dev_total", ascending=False).iloc[0].m) if G.dev_n.sum() else MARGINS[-1]
        H = trades(ho, col, mb)
        byday = H.groupby("day").pnl.sum()
        mid = (H.ask + H.bid) / 2 if len(H) else pd.Series(dtype=float)
        yv = np.where(H.side == "yes", H.y, 1 - H.y) if len(H) else np.array([])
        km = np.where(H.side == "yes", mid, 1 - mid) if len(H) else np.array([])
        bf, bk = (float(np.mean((H.fair - yv) ** 2)), float(np.mean((km - yv) ** 2))) if len(H) else (np.nan, np.nan)
        ok = len(H) > 2 and H.pnl.sum() > 0 and tstat(H.pnl) >= 2 and (byday > 0).sum() >= 3 and bf < bk
        res[col] = dict(grid=G, m=mb, H=H, n=len(H), total=H.pnl.sum(), mean=H.pnl.mean() if len(H) else np.nan, t=tstat(H.pnl), days_pos=int((byday > 0).sum()),
                        n_days=len(byday), byday=byday, brier_opt=bf, brier_kalshi=bk, PASS=bool(ok))
    return res


# ---------------------------------------------------------------- calibration
def synthetic(planted, seed=11, ndays=9):
    rng = np.random.default_rng(seed); Ms, Qs, Dm = [], [], {}
    days = ["2026-11-09", "2026-11-10", "2026-11-11", "2026-11-12", "2026-11-13", "2026-11-16", "2026-11-17", "2026-11-18", "2026-11-19"][:ndays]
    from scipy.stats import norm
    for day in days:
        S0, sd = 7500.0, 60.0; ST = S0 + rng.normal(0, sd)
        mins = pd.date_range(pd.Timestamp(day + " 10:00", tz=ET), pd.Timestamp(day + " 15:45", tz=ET), freq="1min")
        Ks = np.arange(7200, 7805, 5.0)
        path = S0 + np.cumsum(rng.normal(0, sd / math.sqrt(len(mins) + 15), len(mins)))
        path = path + (ST - path[-1]) * np.linspace(0, 1, len(mins)) ** 2      # bridge to the close
        rem = sd * np.sqrt(np.linspace(1, 1 / len(mins), len(mins)))
        Dtrue = 1 - norm.cdf((Ks[None, :] - path[:, None]) / rem[:, None])
        Dm[day] = pd.DataFrame(np.clip(Dtrue + rng.normal(0, 0.005, Dtrue.shape), 0, 1), index=mins, columns=Ks)
        for j, K in enumerate(Ks[::2]):
            tk = f"S-{day}-{K}"; y = float(ST >= K)
            Ms.append(dict(series="SYN", ticker=tk, day=day, lo=K, hi=np.inf, y=y))
            p = Dtrue[:, 2 * j]
            mid = p + (0.06 * (0.5 - p) / 0.5 if planted else 0) + rng.normal(0, 0.01, len(p))
            half = rng.uniform(0.01, 0.02, len(p))
            Qs.append(pd.DataFrame(dict(ticker=tk, t=mins.tz_convert("UTC"), bid=np.clip(np.round(mid - half, 2), 0, 1), ask=np.clip(np.round(mid + half, 2), 0, 1))))
    return pd.DataFrame(Ms), pd.concat(Qs), Dm


def smoke():
    out = {}
    for planted in (True, False):
        for seed in (11, 12, 13):
            M, Q, Dm = synthetic(planted, seed)
            r = analyze(panel(M, Q, Dm))
            out[(planted, seed)] = r["fS"]["PASS"]
            print("planted" if planted else "null", seed, "PASS", r["fS"]["PASS"], "n", r["fS"]["n"], "total", round(r["fS"]["total"], 2), "t", round(r["fS"]["t"], 2), "m", r["fS"]["m"], "days+", r["fS"]["days_pos"])
    assert all(out[(True, s)] for s in (11, 12, 13)) and not any(out[(False, s)] for s in (11, 12, 13)), "calibration failed"
    print("smoke OK")


# ---------------------------------------------------------------- report
def report():
    M, Q = pickle.load(open(f"{OUT}/kalshi.pkl", "rb"))
    Dm = {d: digitals(d) for d in sorted(M.day.unique())}
    P = panel(M, Q, Dm)
    P["mid"] = (P.bid + P.ask) / 2
    res = analyze(P)
    passed = res["fL"]["PASS"]
    V = P[(P.bid > 0) & (P.ask < 0.98) & (P.ask > 0.02) & P.fS.notna()]
    cal = V.groupby(pd.cut(V.mid, [0, .1, .3, .5, .7, .9, 1])).agg(rows=("y", "size"), kalshi_mid=("mid", "mean"), option_fair=("fS", "mean"), outcome=("y", "mean")).round(3)
    gap = V.assign(gap=(V.mid - V.fS).abs(), hour=V.t.dt.hour).groupby("hour").gap.agg(["count", "mean", "median"]).round(3)
    out = ["# Round 70: Kalshi S&P 4pm markets vs the SPXW 0DTE option chain", "", "Rules: [PROTOCOL_ROUND70.md](../PROTOCOL_ROUND70.md).", "",
           f"Markets: {len(M):,} ({M.groupby('series').size().to_dict()}) over {M.day.nunique()} days; market-minutes with a fair value: {len(V):,}.", "",
           f"**Verdict (variant L, live-feasible 15-min-old option data): {'PASS → live paper tracker' if passed else 'FAIL'}.**", ""]
    for col, lab in (("fS", "S: same-minute option fair value (upper bound)"), ("fL", "L: 15-minute-old option fair value (what free data allows)")):
        r = res[col]
        out += [f"## {lab}", "", f"Margin chosen on dev: {r['m']}. Holdout: {r['n']} trades, total ${r['total']:+.2f} per 1-contract set, mean {r['mean']:+.4f}, t {r['t']:.2f}, "
                f"positive days {r['days_pos']}/{r['n_days']}, Brier option {r['brier_opt']:.4f} vs Kalshi {r['brier_kalshi']:.4f}. PASS: {r['PASS']}.", "",
                r["grid"].round(4).to_markdown(index=False), "", "Holdout by day:", "", r["byday"].round(2).to_frame("pnl").to_markdown(), ""]
        if len(r["H"]):
            out += ["Holdout by side:", "", r["H"].groupby("side").pnl.agg(["count", "mean", "sum"]).round(3).to_markdown(), ""]
    out += ["## Calibration by Kalshi mid band (all market-minutes)", "", cal.to_markdown(), "", "## |Kalshi mid − option fair| by hour", "", gap.to_markdown(), ""]
    open("reports/ROUND70.md", "w").write("\n".join(out) + "\n"); print("\n".join(out[:30]))


if __name__ == "__main__":
    {"smoke": smoke, "collect": collect, "report": report}[sys.argv[1]]()

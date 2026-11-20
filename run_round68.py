"""Round 68 (PROTOCOL_ROUND68.md): catalyst dissection of 0DTE straddle hits and flops.  Usage: report"""
import json, math, sys
import numpy as np, pandas as pd
import run_round67 as r67

C2P, K = r67.C2P, r67.K
SPLIT = r67.SPLIT
NY = "America/New_York"
TIER1, TIER2 = ["cpi", "jobs", "fomc"], ["ppi", "retail", "gdp", "pce"]
KALSHI = {"cpi": ["KXCPI", "KXCPIYOY"], "jobs": ["KXPAYROLLS", "KXU3"], "gdp": ["KXGDP"], "ppi": ["KXUSPPI"], "retail": ["KXUSRETAIL"],
          "pce": ["KXPCEHEAD"], "claims": ["KXJOBLESSCLAIMS", "KXJOBLESS"], "fomc": ["KXFEDDECISION", "KXFED"]}
MEGA = ["NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "AVGO"]
CAL = json.load(open("data/r66_cal.json"))


# ---------------------------------------------------------------- calendars
def kalshi_calendar():
    from edge import round20 as r20
    a, b = pd.Timestamp("2021-06-01", tz="UTC"), pd.Timestamp.now(tz="UTC") + pd.Timedelta(days=1)
    rows = []
    for typ, series in KALSHI.items():
        for s in series:
            try: ms = r20.markets(s, a, b)
            except Exception as e: print("kalshi", s, e, flush=True); continue
            for m in ms:
                c = pd.Timestamp(m["close_time"]).tz_convert(NY)
                if c.hour >= 16:      # old-style markets closed the evening before the release
                    day = (c.normalize().tz_localize(None) + pd.offsets.BDay(1)); t = "14:00" if typ == "fomc" else "08:30"
                else:
                    rel = c + pd.Timedelta(minutes=1); day = rel.normalize().tz_localize(None); t = rel.strftime("%H:%M")
                rows.append(dict(type=typ, day=day, time=t, series=s))
    C = pd.DataFrame(rows).drop_duplicates(["type", "day"])
    try:
        from edge.factory_strats import fomc_dates
        fd = pd.to_datetime(fomc_dates()).normalize()
        C = pd.concat([C, pd.DataFrame(dict(type="fomc", day=fd, time="14:00", series="fed.gov"))]).drop_duplicates(["type", "day"])
    except Exception as e:
        print("fomc site failed", e)
    return C


def earnings():
    import yfinance as yf
    rows = []
    for t in MEGA:
        try: e = yf.Ticker(t).get_earnings_dates(limit=40)
        except Exception as ex: print("earnings", t, ex); continue
        for ts in e.index:
            ts = pd.Timestamp(ts).tz_convert(NY)
            day = ts.normalize().tz_localize(None)
            if ts.hour >= 16: day = day + pd.offsets.BDay(1)
            elif ts.hour >= 10: continue          # intraday reports are rare; ignore
            rows.append(dict(ticker=t, day=day))
    return pd.DataFrame(rows).drop_duplicates()


# ---------------------------------------------------------------- minute data
def minutes():
    """NY-naive 1-minute closes: HistData SPXUSD (incl. pre-market), then Yahoo ^GSPC (session) + ES=F (pre-market) for later days."""
    from edge.intraday import load_nq
    h = load_nq(pair="SPXUSD")["close"]
    last = h.index.max().normalize()
    import yfinance as yf
    def y(t):
        out = []
        end = pd.Timestamp.now(tz=NY).normalize() + pd.Timedelta(days=1)
        for k in range(4):
            e = end - pd.Timedelta(days=7 * k); s = e - pd.Timedelta(days=7)
            try:
                d = yf.Ticker(t).history(start=s, end=e, interval="1m")["Close"]
                if len(d): out.append(d)
            except Exception as ex: print("yahoo 1m", t, ex)
        if not out: return pd.Series(dtype=float)
        x = pd.concat(out); x.index = x.index.tz_convert(NY).tz_localize(None); return x[~x.index.duplicated()].sort_index()
    g, es = y("^GSPC"), y("ES=F")
    g, es = g[g.index > last + pd.Timedelta(days=1)], es[es.index > last + pd.Timedelta(days=1)]
    print("minutes: histdata to", last.date(), "| yahoo", len(g), "gspc,", len(es), "es", flush=True)
    return h, g, es


def day_path(day, h, g, es):
    """(session closes 09:30..15:59 as Series, pre-market Series) for one day, or (None, None)."""
    d0 = pd.Timestamp(day)
    s = h[(h.index >= d0 + pd.Timedelta(hours=8)) & (h.index < d0 + pd.Timedelta(hours=16))]
    if len(s) > 300:
        return s[s.index >= d0 + pd.Timedelta(hours=9, minutes=30)], s[s.index < d0 + pd.Timedelta(hours=9, minutes=30)]
    sg = g[(g.index >= d0 + pd.Timedelta(hours=9, minutes=30)) & (g.index < d0 + pd.Timedelta(hours=16))]
    pe = es[(es.index >= d0 + pd.Timedelta(hours=8)) & (es.index < d0 + pd.Timedelta(hours=9, minutes=30))]
    return (sg, pe) if len(sg) > 300 else (None, None)


def at(s, hm):
    t = s.index[0].normalize() + pd.Timedelta(hours=int(hm[:2]), minutes=int(hm[3:]))
    x = s[s.index <= t]
    return float(x.iloc[-1]) if len(x) else float(s.iloc[0])


def a_curve(mins):
    return float(np.interp(mins, CAL["A_mins"], CAL["A"]))


ENTRY = ["10:05", "11:30", "13:00", "14:35"]
BUCKETS = [f"{9 + (30 + 30 * i) // 60:02d}:{(30 + 30 * i) % 60:02d}" for i in range(13)]


def intraday(d, sd, h, g, es):
    rows = {}
    for day, r in d.iterrows():
        s, pre = day_path(day, h, g, es)
        if s is None: continue
        p0, pc = float(s.iloc[0]), float(s.iloc[-1]); sg = np.sign(pc - p0) or 1.0
        scale = r.OPEN / p0; sdp = float(sd.loc[day])
        rec = {}
        for i, b in enumerate(BUCKETS):
            st = s.index[0].normalize() + pd.Timedelta(hours=9, minutes=30 + 30 * i); en = st + pd.Timedelta(minutes=30)
            a_, b_ = s[s.index < st], s[s.index < en]
            pa = float(a_.iloc[-1]) if len(a_) else p0; pb = float(b_.iloc[-1]) if len(b_) else pa
            rec["h" + b] = (pb - pa) * sg * scale / sdp
        five = s.resample("5min").last().dropna(); dm = five.diff().abs()
        if len(dm.dropna()):
            rec["max5_sd"] = float(dm.max() * scale / sdp); rec["max5_time"] = dm.idxmax().strftime("%H:%M")
        if pre is not None and len(pre) > 30:
            p829 = at(pre, "08:29"); p845 = at(pre, "08:45"); p929 = float(pre.iloc[-1])
            rec["r830_sd"] = abs(p845 - p829) * scale / sdp; rec["pre_sd"] = abs(p929 - p829) * scale / sdp
        lr = np.diff(np.log(s.to_numpy(float)))
        for T in ENTRY:
            t = s.index[0].normalize() + pd.Timedelta(hours=int(T[:2]), minutes=int(T[3:]))
            k = int((s.index <= t).sum()) - 1
            if k < 31: continue
            ST = float(s.iloc[k]) * scale; mins = 960 - (int(T[:2]) * 60 + int(T[3:]))
            rv = math.sqrt(float((lr[k - 30:k] ** 2).sum()) * 252 * 13); V = r.V1O / 100
            mult = min(max((max(rv, 1e-4) / V) ** 0.457, 0.3), 3.0)
            prem = ST * V * math.sqrt(mins / 390 / 252) * C2P * a_curve(mins) / a_curve(390) * mult
            rec["L" + T] = prem - abs(r.CLOSE - ST) - 0.6
            rec["morn" + T] = abs(ST - r.OPEN) / sdp
        rows[day] = rec
    return pd.DataFrame.from_dict(rows, orient="index")


# ---------------------------------------------------------------- report
def stats(x):
    x = pd.Series(x).dropna()
    return dict(n=len(x), mean=round(x.mean(), 2) if len(x) else np.nan, t=round(r67.tstat(x), 2), win=round((x > 0).mean(), 3) if len(x) else np.nan,
                worst=round(x.min(), 1) if len(x) else np.nan, total=round(x.sum(), 0))


def rule_eval(name, skip, A, idx):
    ho = np.asarray(idx >= SPLIT); a = A.to_numpy(float); keep = ~np.asarray(skip, bool)
    x = a[ho & keep]; pos = np.flatnonzero(ho & keep); hs = np.flatnonzero(ho); mid = hs[len(hs) // 2]
    eq = np.where(keep[ho], a[ho], 0.0)
    base = a[ho]
    r = dict(rule=name, skipped_all=int((~keep).sum()), ho_n=len(x), ho_mean=round(x.mean(), 2), ho_t=round(r67.tstat(x), 2), ho_maxdd=round(r67.maxdd(eq), 1),
             ho_h1=round(x[pos < mid].mean(), 2), ho_h2=round(x[pos >= mid].mean(), 2), base_mean=round(base.mean(), 2), base_maxdd=round(r67.maxdd(base), 1),
             dev_mean=round(a[~ho & keep].mean(), 2), dev_t=round(r67.tstat(a[~ho & keep]), 2))
    r["PASS"] = bool(r["ho_mean"] > 0 and r["ho_t"] >= 2.5 and r["ho_mean"] > r["base_mean"] and r["ho_maxdd"] <= r["base_maxdd"] and r["ho_h1"] > 0 and r["ho_h2"] > 0)
    return r


def report():
    d, cal67, src = r67.load()
    f, A, F, sd, prem = r67.features(d, cal67)
    f = f.iloc[25:]; idx = f.index; A = A.loc[idx]; d = d.loc[idx]; sd = sd.loc[idx]
    C = kalshi_calendar(); E = earnings()
    cov = C.groupby("type").day.agg(["min", "max", "count"])
    print(cov, flush=True)
    tags = pd.DataFrame(index=idx)
    for typ in KALSHI:
        sub = C[C.type == typ]
        tags[typ] = idx.isin(pd.DatetimeIndex(sub.day)).astype(int)
        tags.loc[idx < sub.day.min() if len(sub) else idx == idx, typ] = np.nan   # outside coverage
    tags["claims"] = np.maximum(tags["claims"].fillna(0), (idx.weekday == 3).astype(int))      # weekly, Thursdays 08:30
    ev_time = C.groupby("day").apply(lambda x: ",".join(sorted(f"{a}@{b}" for a, b in zip(x.type, x.time))))
    tags["events"] = pd.Series(idx, index=idx).map(ev_time).fillna("")
    big = E[E.ticker.isin(MEGA[:6])]
    tags["mega_er"] = idx.isin(pd.DatetimeIndex(big.day)).astype(int)
    tags["er_names"] = pd.Series(idx, index=idx).map(E.groupby("day").ticker.apply(lambda s: ",".join(sorted(set(s))))).fillna("")
    tags["tier1"] = tags[TIER1].fillna(0).max(axis=1); tags["tier2"] = tags[TIER2].fillna(0).max(axis=1)
    h, g, es = minutes()
    I = intraday(d, sd, h, g, es)
    X = tags.join(I).join(f[["vix1d", "v1_over_vix", "gap_bp", "weekday"]])
    X["A"] = A; X["move_sd"] = (d.CLOSE - d.OPEN).abs() / sd
    X["cat"] = np.select([X.fomc == 1, X.cpi == 1, X.jobs == 1, X.tier2 == 1, X.mega_er == 1, X.claims == 1],
                         ["FOMC", "CPI", "Jobs", "PPI/Retail/GDP/PCE", "Mega-cap earnings", "Jobless claims only"], "No scheduled catalyst")
    losses = -X.A.clip(upper=0)
    T1 = X.groupby("cat").agg(days=("A", "size"), v1_over_vix=("v1_over_vix", "mean"), vix1d=("vix1d", "mean"), move_sd=("move_sd", "mean"),
                              mean_A=("A", "mean"), flop_rate=("A", lambda s: (s <= 0).mean()), worst=("A", "min"),
                              share_of_losses=("A", lambda s: (-s.clip(upper=0)).sum() / losses.sum()), in_worst50=("A", lambda s: s.index.isin(X.A.nsmallest(50).index).sum())).round(3)
    T1 = T1.sort_values("days", ascending=False)
    hcols = [c for c in X.columns if c.startswith("h") and c[1:3].isdigit()]
    w50 = X.A.nsmallest(50).index
    prof = pd.DataFrame({"all days": X[hcols].mean(), "flop days": X.loc[X.A <= 0, hcols].mean(), "worst 50": X.loc[w50, hcols].mean(),
                         "hit days": X.loc[X.A > 0, hcols].mean()}).round(3)
    prof.index = [c[1:] for c in prof.index]
    has = X[hcols].notna().any(axis=1)
    X["damage_window"] = pd.Series(None, index=X.index, dtype=object)
    X.loc[has, "damage_window"] = X.loc[has, hcols].fillna(-99).idxmax(axis=1).str[1:]
    sched_window = X.loc[w50, "damage_window"].isin(["10:00", "14:00", "14:30"])
    T3 = X.loc[w50, ["A", "move_sd", "cat", "events", "er_names", "vix1d", "v1_over_vix", "gap_bp", "pre_sd", "damage_window", "max5_sd", "max5_time"]].round(2)
    T3.index = T3.index.date
    sched = (X.tier1 == 1) | (X.tier2 == 1) | (X.mega_er == 1)
    T4 = pd.DataFrame([dict(group="scheduled tier-1/2 release or mega-cap earnings", days=int(sched.sum()), share_days=round(sched.mean(), 3), share_losses=round(losses[sched].sum() / losses.sum(), 3),
                            share_worst50=round(sched.loc[w50].mean(), 3), mean_A=round(X.A[sched].mean(), 2), move_sd=round(X.move_sd[sched].mean(), 3)),
                       dict(group="no scheduled catalyst (claims-only included)", days=int((~sched).sum()), share_days=round((~sched).mean(), 3), share_losses=round(losses[~sched].sum() / losses.sum(), 3),
                            share_worst50=round((~sched).loc[w50].mean(), 3), mean_A=round(X.A[~sched].mean(), 2), move_sd=round(X.move_sd[~sched].mean(), 3))])
    # pre-registered rules
    e1 = X.tier1 == 1; e2 = e1 | (X.tier2 == 1); e3 = X.mega_er == 1; e4 = X.pre_sd >= 0.5
    R = pd.DataFrame([rule_eval("E1 skip CPI/jobs/FOMC", e1, X.A, idx), rule_eval("E2 skip tier-1 + PPI/retail/GDP/PCE", e2, X.A, idx),
                      rule_eval("E3 skip mega-cap earnings day", e3, X.A, idx), rule_eval("E4 skip if pre-open move ≥ 0.5σ", e4.fillna(False), X.A, idx),
                      rule_eval("E5 = E1 ∪ E3 ∪ E4", e1 | e3 | e4.fillna(False), X.A, idx)])
    passed = bool(R.PASS.any())
    L = pd.DataFrame([dict(entry="09:30 (A)", **stats(X.A))] + [dict(entry=T, **stats(X["L" + T])) for T in ENTRY if "L" + T in X])
    LW = pd.DataFrame([dict(entry=T, worst50_mean_open=round(X.loc[w50, "A"].mean(), 1), worst50_mean_late=round(X.loc[w50, "L" + T].mean(), 1),
                            morning_move_sd_worst50=round(X.loc[w50, "morn" + T].mean(), 2), morning_move_sd_all=round(X["morn" + T].mean(), 2)) for T in ENTRY if "L" + T in X])
    out = ["# Round 68: what is the catalyst behind 0DTE straddle flops?", "", "Rules: [PROTOCOL_ROUND68.md](../PROTOCOL_ROUND68.md).", "",
           f"Days: {len(idx):,} ({idx.min().date()} → {idx.max().date()}); with minute data: {len(I):,}. Straddle P&L in SPX points per 1-lot (×$100), as Round 67 (VIX1D-priced).", "",
           f"**Verdict on the pre-registered skip rules: {'PASS → real-quote forward test' if passed else 'FAIL'}.**", "",
           "## Release calendar coverage (Kalshi market close times)", "", cov.to_markdown(), "",
           "## T1. By catalyst (each day gets its most important tag)", "", T1.to_markdown(), "",
           "## T4. Scheduled vs unscheduled", "", T4.to_markdown(index=False), "",
           "## T2. When the damage happens: average signed contribution to |close − open| by half-hour (σ units)", "", prof.to_markdown(), "",
           f"Worst 50 days whose biggest-damage half-hour starts at a scheduled time (10:00, 14:00, 14:30): {int(sched_window.sum())}/50. "
           f"Damage-window counts (worst 50): " + ", ".join(f"{k} {v}" for k, v in X.loc[w50, 'damage_window'].value_counts().items()), "",
           "## Pre-registered skip rules (holdout ≥ 2024-08-12)", "", R.to_markdown(index=False), "",
           "## Late entry (model-priced, descriptive only — never a pass)", "", L.to_markdown(index=False), "", LW.to_markdown(index=False), "",
           "## T3. The 50 worst days", "", T3.to_markdown(), ""]
    open("reports/ROUND68.md", "w").write("\n".join(out) + "\n"); print("\n".join(out[:40]))
    X.to_csv("data/r68_days.csv")


if __name__ == "__main__":
    {"report": report}[sys.argv[1]]()

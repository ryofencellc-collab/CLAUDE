"""Round 67 (PROTOCOL_ROUND67.md): which days does selling 0DTE premium win, and why?  Usage: smoke | report"""
import glob, io, math, os, re, sys
import numpy as np, pandas as pd, requests

H = {"User-Agent": "Mozilla/5.0 (research)"}
K = math.sqrt(1 / 252); C2P = math.sqrt(2 / math.pi)
COST_A, COST_F, WING = 0.6, 1.2, 2.0
SPLIT = pd.Timestamp("2024-08-12")
QS = [10, 20, 30, 70, 80, 90]
BINARY = ["fomc", "fomc_eve", "cpi", "nfp", "opex", "monthend", "mon", "fri"]


# ---------------------------------------------------------------- data
def cboe(sym):
    r = requests.get(f"https://cdn.cboe.com/api/global/us_indices/daily_prices/{sym}_History.csv", headers=H, timeout=60); r.raise_for_status()
    d = pd.read_csv(io.StringIO(r.text)); d.columns = [c.strip().upper() for c in d.columns]
    d["DATE"] = pd.to_datetime(d["DATE"]); return d.set_index("DATE").sort_index()


def yhist(t):
    import yfinance as yf
    d = yf.Ticker(t).history(start="2010-01-01", auto_adjust=False)
    d.index = pd.to_datetime(d.index).tz_localize(None).normalize(); d.columns = [c.upper() for c in d.columns]
    return d[["OPEN", "HIGH", "LOW", "CLOSE"]]


def series(sym, ysym):
    try:
        d = cboe(sym)
        if {"OPEN", "CLOSE"} <= set(d.columns) and len(d) > 500 and (sym != "SPX" or (d.OPEN != d.CLOSE).mean() > 0.9):
            return d[["OPEN", "HIGH", "LOW", "CLOSE"]], "cboe"
    except Exception as e:
        print("cboe", sym, "failed:", e, flush=True)
    return yhist(ysym), "yahoo"


def bls_dates(kind):
    """Release dates from the BLS archive page file names (cpi_MMDDYYYY.htm / empsit_MMDDYYYY.htm)."""
    url = {"cpi": "https://www.bls.gov/bls/news-release/cpi.htm", "empsit": "https://www.bls.gov/bls/news-release/empsit.htm"}[kind]
    try:
        t = requests.get(url, headers={"User-Agent": "Mozilla/5.0 research-script"}, timeout=60).text
        ds = sorted({pd.Timestamp(f"{m[4:]}-{m[:2]}-{m[2:4]}") for m in re.findall(kind + r"_(\d{8})\.htm", t)})
        print(kind, "dates", len(ds), ds[:1], ds[-1:], flush=True)
        return ds if len(ds) > 30 else None
    except Exception as e:
        print("bls", kind, "failed:", e, flush=True); return None


def load():
    src = {}
    spx, src["SPX"] = series("SPX", "^GSPC"); v1, src["VIX1D"] = series("VIX1D", "^VIX1D")
    vx, src["VIX"] = series("VIX", "^VIX"); v9, src["VIX9D"] = series("VIX9D", "^VIX9D")
    d = spx.join(v1[["OPEN", "CLOSE"]].rename(columns={"OPEN": "V1O", "CLOSE": "V1C"}), how="inner")
    d = d.join(vx.CLOSE.rename("VIX"), how="left").join(v9.CLOSE.rename("V9"), how="left")
    d = d[(d.V1O > 1) & (d.V1C > 1)].dropna(subset=["OPEN", "CLOSE", "V1O"])
    from edge.factory_strats import fomc_dates
    try: fomc = set(pd.to_datetime(fomc_dates()).normalize())
    except Exception as e: print("fomc failed", e); fomc = None
    cal = dict(fomc=fomc, cpi=bls_dates("cpi"), nfp=bls_dates("empsit"))
    return d, cal, src


def outcomes(d):
    sd = d.OPEN * d.V1O / 100 * K
    prem = sd * C2P; mv = (d.CLOSE - d.OPEN).abs()
    A = prem - mv - COST_A
    w = WING * sd; z = w / sd
    wing = 2 * sd * (np.exp(-z * z / 2) / math.sqrt(2 * math.pi) - z * 0.5 * np.vectorize(math.erfc)(z / math.sqrt(2)))   # Bachelier OTM call=put at ±w
    F = prem - wing - mv + np.maximum(mv - w, 0) - COST_F
    return sd, prem, A, F


def features(d, cal):
    sd, prem, A, F = outcomes(d)
    pc = d.CLOSE.shift(1); f = pd.DataFrame(index=d.index)
    f["vix1d"] = d.V1O; f["vix_prev"] = d.VIX.shift(1); f["vix9d_prev"] = d.V9.shift(1)
    f["v1_over_vix"] = d.V1O / f.vix_prev; f["v9_over_vix"] = f.vix9d_prev / f.vix_prev; f["v1_chg"] = d.V1O / d.V1C.shift(1) - 1
    f["gap_bp"] = 1e4 * (d.OPEN / pc - 1); f["absgap_sd"] = (d.OPEN - pc).abs() / sd
    mvr = (d.CLOSE - d.OPEN).abs() / sd
    f["prev_move_sd"] = mvr.shift(1); f["prev_range_sd"] = ((d.HIGH - d.LOW) / sd).shift(1); f["prevA"] = A.shift(1)
    win = (A > 0).astype(int); grp = (win != win.shift()).cumsum(); streak = win.groupby(grp).cumcount() + 1
    f["win_streak"] = (streak * np.where(win == 1, 1, -1)).shift(1)
    f["move5_sd"] = mvr.rolling(5).mean().shift(1)
    f["trend20"] = 1e4 * (pc / d.CLOSE.rolling(20).mean().shift(1) - 1)
    f["dd252"] = 1e4 * (pc / d.CLOSE.rolling(252, min_periods=60).max().shift(1) - 1)
    f["vix_pct252"] = d.VIX.shift(1).rolling(252, min_periods=60).rank(pct=True)
    idx = d.index
    f["weekday"] = idx.weekday; f["mon"] = (idx.weekday == 0).astype(int); f["fri"] = (idx.weekday == 4).astype(int)
    f["opex"] = ((idx.weekday == 4) & (idx.day >= 15) & (idx.day <= 21)).astype(int)
    nxt = pd.Series(idx[1:].tolist() + [idx[-1] + pd.Timedelta(days=30)], index=idx)
    f["monthend"] = (nxt.dt.month != idx.month).astype(int).values
    if cal.get("fomc"):
        f["fomc"] = idx.isin(cal["fomc"]).astype(int); f["fomc_eve"] = pd.Series(f.fomc.values, index=idx).shift(-1).fillna(0).astype(int)
    for k in ("cpi", "nfp"):
        if cal.get(k): f[k] = idx.isin(pd.DatetimeIndex(cal[k])).astype(int)
    return f, A, F, sd, prem


# ---------------------------------------------------------------- search
def tstat(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    return x.mean() / x.std(ddof=1) * math.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else float("nan")


def maxdd(x):
    c = np.cumsum(np.nan_to_num(np.asarray(x, float))); return float((np.maximum.accumulate(np.concatenate([[0], c]))[1:] - c).max()) if len(c) else 0.0


def conds_for(f, dev):
    out = []
    for c in f.columns:
        if c in BINARY: out += [(c, "==", 1.0), (c, "==", 0.0)]
        elif c == "weekday": out += [(c, "==", float(w)) for w in range(5)] + [(c, "!=", float(w)) for w in range(5)]
        else:
            v = f.loc[dev, c].dropna()
            if len(v) < 50: continue
            for q in QS:
                thr = float(np.percentile(v, q)); out.append((c, ">=" if q >= 70 else "<=", thr))
                out.append((c, "<=" if q >= 70 else ">=", thr))    # also the complement side (keep the majority)
    return list(dict.fromkeys(out))


def mask(f, cond):
    c, op, thr = cond; x = f[c].to_numpy(float)
    with np.errstate(invalid="ignore"):
        m = {"==": x == thr, "!=": x != thr, ">=": x >= thr, "<=": x <= thr}[op]
    return m & np.isfinite(x)


def search(f, A, dev, min_frac=0.25, top_single=40):
    a = A.to_numpy(float); nd = dev.sum(); res = []
    conds = conds_for(f, dev); M = {c: mask(f, c) for c in conds}
    def ev(sig, m):
        k = m & dev
        if k.sum() < min_frac * nd: return None
        t = tstat(a[k]); res.append(dict(sig=sig, dev_n=int(k.sum()), dev_mean=float(np.nanmean(a[k])), dev_t=t)); return t
    singles = []
    for c in conds:
        t = ev((c,), M[c])
        if t is not None and t == t: singles.append((c, t))
    top = [c for c, _ in sorted(singles, key=lambda x: -x[1])[:top_single]]
    for i in range(len(top)):
        for j in range(i + 1, len(top)):
            if top[i][0] != top[j][0]: ev((top[i], top[j]), M[top[i]] & M[top[j]])
    R = pd.DataFrame(res).sort_values("dev_t", ascending=False)
    R["key"] = R.sig.map(lambda s: tuple(sorted(s))); R = R.drop_duplicates("key").drop(columns="key")
    return R


def evaluate(R, f, A, idx, ho, top=10):
    a = A.to_numpy(float); hs = np.flatnonzero(ho); mid = hs[len(hs) // 2]
    base = a[ho]; rows = []
    for r in R.head(top).itertuples():
        m = np.ones(len(a), bool)
        for c in r.sig: m &= mask(f, c)
        k = m & ho; x = a[k]; pos = np.flatnonzero(k)
        h1, h2 = x[pos < mid], x[pos >= mid]
        xs = np.where(m[ho], base, 0.0)    # filtered equity on the holdout calendar (0 on skipped days)
        rows.append(dict(rule=" AND ".join(f"{c} {op} {thr:.4g}" for c, op, thr in r.sig), dev_n=r.dev_n, dev_mean=round(r.dev_mean, 2), dev_t=round(r.dev_t, 2),
                         ho_n=int(k.sum()), ho_mean=round(float(x.mean()), 2) if len(x) else np.nan, ho_t=round(tstat(x), 2), ho_win=round(float((x > 0).mean()), 3) if len(x) else np.nan,
                         ho_worst=round(float(x.min()), 1) if len(x) else np.nan, ho_maxdd=round(maxdd(xs), 1), ho_h1=round(float(h1.mean()), 2) if len(h1) else np.nan,
                         ho_h2=round(float(h2.mean()), 2) if len(h2) else np.nan))
    H = pd.DataFrame(rows)
    bm, bdd = float(np.nanmean(base)), maxdd(base)
    if len(H):
        H["beats_base"] = H.ho_mean > bm
        H["ok"] = (H.ho_mean > 0) & (H.ho_t >= 2.5) & H.beats_base & (H.ho_maxdd <= bdd) & (H.ho_h1 > 0) & (H.ho_h2 > 0)
    return H, dict(n=int(ho.sum()), mean=round(bm, 2), t=round(tstat(base), 2), maxdd=round(bdd, 1), worst=round(float(np.nanmin(base)), 1))


def null_dist(f, A, dev, ho, n=50, seed=7):
    rng = np.random.default_rng(seed); best = []
    for i in range(n):
        k = int(rng.integers(60, 500)); g = f.copy()
        g[:] = np.roll(f.to_numpy(float), k, axis=0)
        R = search(g, A, dev); H, _ = evaluate(R, g, A, f.index, ho, top=10)
        best.append(float(np.nanmax(H.ho_t)) if len(H) else float("nan"))
        print("null", i, k, round(best[-1], 2), flush=True)
    return np.array(best)


def run(f, A, idx, n_null=50):
    dev = np.asarray(idx < SPLIT); ho = ~dev
    R = search(f, A, dev); H, base = evaluate(R, f, A, idx, ho)
    nd = null_dist(f, A, dev, ho, n_null); q95 = float(np.nanpercentile(nd, 95))
    H["above_null"] = H.ho_t > q95; H["PASS"] = H.ok & H.above_null
    return R, H, base, nd, q95


# ---------------------------------------------------------------- calibration
def synthetic(planted, n=1100, seed=3):
    rng = np.random.default_rng(seed); idx = pd.bdate_range("2022-05-16", periods=n)
    v1 = np.full(n, 14.0); sd = 4000 * v1 / 100 * K       # constant vol: the null world must hold no structure at all
    vn = np.clip(14 * np.exp(rng.normal(0, 0.3, n)), 6, 60)  # vol-index columns are pure noise
    lk = rng.normal(0, 0.35, n); kmul = np.exp(lk) / np.exp(0.35 ** 2 / 2) / 1.1     # 10% variance premium on average
    mv = np.abs(rng.normal(0, 1, n)) * sd * kmul
    O = np.full(n, 4000.0); C = O + mv * rng.choice([-1, 1], n)
    d = pd.DataFrame(dict(OPEN=O, HIGH=np.maximum(O, C) + 5, LOW=np.minimum(O, C) - 5, CLOSE=C, V1O=v1, V1C=v1, VIX=vn * 1.2, V9=vn * 1.1 * np.exp(rng.normal(0, 0.1, n))), index=idx)
    f, A, F, _, _ = features(d, {})
    f["signal"] = (lk + rng.normal(0, 0.6, n)) if planted else rng.normal(0, 1, n)
    return f, A, idx


def smoke(n_null=20):
    res = {}
    for planted in (True, False):
        f, A, idx = synthetic(planted)
        R, H, base, nd, q95 = run(f, A, idx, n_null)
        res[planted] = bool(H.PASS.any())
        print("planted" if planted else "null", "PASS any:", res[planted], "null q95", round(q95, 2)); print(H.head(5).to_string())
    assert res[True] and not res[False], "calibration failed"
    print("smoke OK")


# ---------------------------------------------------------------- real-quote cross-check
def real_check(d):
    try:
        from edge import odte_score as O
    except Exception as e:
        return f"real-quote check unavailable: {e}"
    rows = []
    for p in sorted(glob.glob("data/odte/2*")):
        day = os.path.basename(p); ts = pd.Timestamp(day)
        if ts not in d.index: continue
        try: x = O.load_day(day, "SPXW")
        except Exception: continue
        x = x[x.exp == day]
        if x.empty: continue
        t0 = x.t[x.t.dt.hour * 60 + x.t.dt.minute >= 571].min()
        g = x[x.t == t0]; S = float(g.spot.iloc[0]); Kc = g.K.iloc[(g.K - S).abs().argmin()]
        c = g[(g.K == Kc) & (g.cp == "C")]; pp = g[(g.K == Kc) & (g.cp == "P")]
        if c.empty or pp.empty: continue
        real = float((c.bid.iloc[0] + c.ask.iloc[0]) / 2 + (pp.bid.iloc[0] + pp.ask.iloc[0]) / 2)
        spread = float(c.ask.iloc[0] - c.bid.iloc[0] + pp.ask.iloc[0] - pp.bid.iloc[0])
        model = float(d.loc[ts, "OPEN"] * d.loc[ts, "V1O"] / 100 * K * C2P)
        rows.append(dict(day=day, time=str(t0.time()), spot=round(S, 1), real_mid=round(real, 2), real_spread=round(spread, 2), model=round(model, 2), ratio=round(real / model, 3)))
    if not rows: return "real-quote check: no overlapping recorded days."
    T = pd.DataFrame(rows)
    return (f"Real SPXW ATM straddle at the first snapshot ≥ 09:31 vs model premium (VIX1D open), {len(T)} days: median real/model {T.ratio.median():.3f}, "
            f"median real spread {T.real_spread.median():.2f} pt (model cost assumes 1.2 pt round-trip on entry ×½ = 0.6).\n\n" + T.to_markdown(index=False))


# ---------------------------------------------------------------- report
def why_tables(f, A, dev):
    out = []
    a = A
    for c in f.columns:
        x = f[c]
        if x.notna().sum() < 50: continue
        if c in BINARY or c == "weekday":
            g = a.groupby(x)
        else:
            try: g = a.groupby(pd.qcut(x, 5, duplicates="drop"))
            except Exception: continue
        t = g.agg(days="size", mean="mean", win=lambda s: (s > 0).mean(), worst="min").round(2)
        out += [f"**{c}**", "", t.to_markdown(), ""]
    return out


def hits_vs_flops(f, A, dev):
    """Per feature: average on hit days, flop days and the worst-10% flop days, in dev and in holdout separately.
    d = (hit mean - flop mean) / pooled sd; a real difference should keep its sign and size from dev to holdout."""
    rows = []; a = A.to_numpy(float)
    for c in f.columns:
        x = f[c].to_numpy(float); r = dict(feature=c)
        for lab, part in (("dev", dev), ("ho", ~dev)):
            ok = part & np.isfinite(x); h = ok & (a > 0); fl = ok & (a <= 0)
            big = ok & (a <= np.nanpercentile(a[part], 10))
            sdp = np.nanstd(x[ok]) or np.nan
            r[f"{lab}_hit"] = np.nanmean(x[h]); r[f"{lab}_flop"] = np.nanmean(x[fl]); r[f"{lab}_bigflop"] = np.nanmean(x[big])
            r[f"{lab}_d"] = (np.nanmean(x[h]) - np.nanmean(x[fl])) / sdp
        rows.append(r)
    T = pd.DataFrame(rows)
    T["same_sign"] = np.sign(T.dev_d) == np.sign(T.ho_d)
    return T.reindex(T.dev_d.abs().sort_values(ascending=False).index).round(3)


def report():
    d, cal, src = load()
    f, A, F, sd, prem = features(d, cal)
    f = f.iloc[25:]; A = A.loc[f.index]; F = F.loc[f.index]; d = d.loc[f.index]
    idx = f.index
    print("days", len(idx), idx.min().date(), idx.max().date(), "sources", src, "calendar", {k: (len(v) if v else None) for k, v in cal.items()}, flush=True)
    R, H, base, nd, q95 = run(f, A, idx)
    dev = np.asarray(idx < SPLIT); ho = ~dev
    # same filters on the iron fly (reported)
    HF, baseF = evaluate(R, f, F, idx, ho)
    passed = bool(H.PASS.any())
    out = ["# Round 67: which days does selling 0DTE premium win, and why?", "", "Rules: [PROTOCOL_ROUND67.md](../PROTOCOL_ROUND67.md).", "",
           f"Days: {len(idx):,} ({idx.min().date()} → {idx.max().date()}); dev < {SPLIT.date()} ({dev.sum()}), holdout {ho.sum()}. Sources: {src}. "
           f"Calendar: FOMC {'yes' if cal.get('fomc') else 'MISSING'}, CPI {'yes' if cal.get('cpi') else 'MISSING'}, jobs {'yes' if cal.get('nfp') else 'MISSING'}.",
           f"Filters searched: {len(R):,} (singles + pairs, each keeps ≥ 25% of dev days). Time-shift null (50 runs): 95th percentile of the best holdout t = {q95:.2f}.", "",
           f"**Verdict: {'PASS → real-quote forward test next' if passed else 'FAIL'}.**", "",
           f"Unfiltered short straddle (A), holdout: {base}. All days: mean {A.mean():.2f} pt, t {tstat(A):.2f}, win {(A > 0).mean():.1%}, worst {A.min():.1f}.",
           f"Unfiltered iron fly (F, wings ±{WING}σ, optimistic), holdout: {baseF}.", "",
           "## Top 10 dev filters on the holdout — short straddle (A, primary)", "", H.to_markdown(index=False), "",
           "## The same filters on the iron fly (F, defined risk; reported, not passed)", "", HF.to_markdown(index=False), "",
           "## Real quotes vs the model premium", "", real_check(d), "",
           "## Year by year (A, unfiltered)", "", A.groupby(A.index.year).agg(days="size", mean="mean", win=lambda s: (s > 0).mean(), worst="min", total="sum").round(2).to_markdown(), "",
           "## The 25 worst days (A) and what was known at the open", "",
           f.assign(A=A.round(1), move_sd=((d.CLOSE - d.OPEN).abs() / sd.loc[idx]).round(2)).loc[A.nsmallest(25).index,
               ["A", "move_sd", "vix1d", "vix_prev", "v1_over_vix", "gap_bp", "prev_move_sd", "move5_sd", "vix_pct252", "weekday"] + [c for c in ("fomc", "cpi", "nfp", "opex") if c in f]].round(3).to_markdown(), "",
           "## Hits vs flops: what was different on the morning of winning vs losing days", "",
           "d = (average on hit days − average on flop days) / spread of the feature. |d| ≥ 0.2 is a noticeable difference. A real pattern keeps its sign and size from dev to holdout.", "",
           hits_vs_flops(f, A, dev).to_markdown(index=False), "",
           "## Why: mean A by feature bucket (all days)", ""] + why_tables(f, A, dev)
    open("reports/ROUND67.md", "w").write("\n".join(out) + "\n"); print("\n".join(out[:16]))


if __name__ == "__main__":
    {"smoke": smoke, "report": report}[sys.argv[1]]()

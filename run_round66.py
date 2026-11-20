"""Round 66 (PROTOCOL_ROUND66.md): 0DTE "million ways" search on 14 years of S&P minutes, options priced by a model calibrated to real 0DTE quotes.
Usage: smoke | report"""
import json, math, os, sys, time
from statistics import NormalDist
import numpy as np, pandas as pd

N_ = NormalDist()
CAL = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "r66_cal.json")))
SLOTS = list(range(30, 361, 15))                      # minute index from 09:30 (0 = 09:31 close): 10:00 ... 15:30
LAST = 385                                           # 15:55
TYPES = [("C", 0.5), ("C", 0.3), ("C", 0.7), ("P", 0.5), ("P", 0.3), ("P", 0.7)]
TNAME = ["call ATM", "call OTM30", "call ITM70", "put ATM", "put OTM30", "put ITM70"]
PTS, SLS, HOLDS = [0.25, 0.5, 1.0, 2.0, None], [-0.25, -0.5, -0.75, None], [15, 30, 60, 120, None]
EXITS = [(p, s, h) for p in PTS for s in SLS for h in HOLDS]
FEE = 1.0
QS = [10, 20, 30, 70, 80, 90]


def Ncdf(x): return 0.5 * (1 + np.vectorize(math.erf)(x / math.sqrt(2))) if np.ndim(x) else 0.5 * (1 + math.erf(x / math.sqrt(2)))


try:
    from scipy.special import ndtr as Ncdf  # fast vectorized normal cdf
except Exception:
    pass


def iv_model(V, mins, z):
    return V * np.interp(mins, CAL["A_mins"], CAL["A"]) * np.interp(z, CAL["smile_z"], CAL["smile"])


def spread(mid):
    return np.interp(mid, CAL["spread_mid"], CAL["spread"])


def bs(S, K, T, iv, cp):
    T = np.maximum(T, 1e-9); v = iv * np.sqrt(T)
    d1 = (np.log(S / K) + 0.5 * v * v) / v; d2 = d1 - v
    if cp == "C": return S * Ncdf(d1) - K * Ncdf(d2)
    return K * Ncdf(-d2) - S * Ncdf(-d1)


# ---------------------------------------------------------------- data
def load_days(pair):
    from edge.intraday import load_nq
    b = load_nq(pair=pair)
    b = b.between_time("09:31", "16:00")
    out = {}
    for d, g in b.groupby(b.index.normalize()):
        if len(g) < 380: continue
        idx = pd.date_range(d + pd.Timedelta(hours=9, minutes=31), periods=390, freq="1min")
        c = g["close"].reindex(idx).ffill().bfill().to_numpy(float)
        out[d] = c
    return out


def load_vix(ticker, start="2011-06-01"):
    import yfinance as yf
    v = yf.Ticker(ticker).history(start=start, auto_adjust=False)["Close"]
    v.index = v.index.tz_localize(None).normalize()
    return v


# ---------------------------------------------------------------- features at slots
FEATS = ["ret1", "ret5", "ret15", "ret30", "ret60", "vs_open", "vs_high", "vs_low", "vs_orh", "vs_orl", "vs_mean", "rsi", "macd_h", "macd_slope",
         "ema9_21", "bb_pctb", "rv30", "rv_day", "rv_ratio", "min_since_high", "min_since_low", "gap", "prev_ret", "prev_range", "vix_prev",
         "vix_chg", "trend20", "dist_round", "min_to_close", "weekday"]


def ema(x, n):
    a = 2 / (n + 1); out = np.empty_like(x); out[0] = x[0]
    for i in range(1, len(x)): out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


def day_features(c, prev_close, prev_range, prev_ret, vix, vix5, trend20, wd, step=25.0):
    """c: 390 closes (09:31..16:00). Returns (len(SLOTS), len(FEATS)) using closes up to and including the slot's minute."""
    lr = np.diff(np.log(c), prepend=np.log(c[0]))
    d = np.diff(c, prepend=c[0]); up = np.clip(d, 0, None); dn = np.clip(-d, 0, None)
    au, ad = ema(up, 27), ema(dn, 27); rsi = 100 - 100 / (1 + au / np.where(ad == 0, np.nan, ad))
    macd = ema(c, 12) - ema(c, 26); mh = macd - ema(macd, 9)
    e9, e21 = ema(c, 9), ema(c, 21)
    cs = np.cumsum(c); orh, orl = c[:30].max(), c[:30].min()
    rows = []
    for s in SLOTS:
        x = c[: s + 1]; m20 = x[-20:].mean(); s20 = x[-20:].std() or np.nan
        r30 = math.sqrt((lr[s - 29: s + 1] ** 2).sum() * 252 * 13)
        rday = math.sqrt((lr[1: s + 1] ** 2).sum() * 252 * 390 / s)
        hi, lo = x.max(), x.min()
        rows.append([1e4 * (c[s] / c[s - 1] - 1), 1e4 * (c[s] / c[s - 5] - 1), 1e4 * (c[s] / c[s - 15] - 1), 1e4 * (c[s] / c[s - 30] - 1),
                     1e4 * (c[s] / c[max(s - 60, 0)] - 1), 1e4 * (c[s] / c[0] - 1), 1e4 * (c[s] / hi - 1), 1e4 * (c[s] / lo - 1),
                     1e4 * (c[s] / orh - 1), 1e4 * (c[s] / orl - 1), 1e4 * (c[s] / (cs[s] / (s + 1)) - 1), rsi[s], 1e4 * mh[s] / c[s],
                     1e4 * (mh[s] - mh[s - 5]) / c[s], 1e4 * (e9[s] / e21[s] - 1), (c[s] - (m20 - 2 * s20)) / (4 * s20),
                     r30, rday, r30 / rday if rday > 0 else np.nan, s - int(np.argmax(x)), s - int(np.argmin(x)),
                     1e4 * (c[0] / prev_close - 1) if prev_close else np.nan, prev_ret, prev_range, vix, vix - vix5, trend20,
                     (c[s] % step) / step - 0.5, 390 - s, wd])
    return np.array(rows, float)


# ---------------------------------------------------------------- option outcome table
def rv_path(c):
    """rv30 at every minute (same formula as the rv30 feature; shorter window before minute 30)."""
    lr2 = np.diff(np.log(c), prepend=np.log(c[0])) ** 2; cs = np.concatenate([[0.0], np.cumsum(lr2)])
    i = np.arange(len(c)); lo = np.maximum(i - 29, 1); n = np.maximum(i + 1 - lo, 1)
    return np.sqrt((cs[i + 1] - cs[lo]) * 252 * 390 / n)


def outcome_table(c, V, beta=0.0):
    """O[slot, type, exit] = P&L ($ per contract) for one day. beta > 0 (amendment 2): IV x (rv30_t / V)^beta."""
    mult = np.clip((np.maximum(rv_path(c), 1e-4) / V) ** beta, 0.3, 3.0) if beta else np.ones(len(c))
    O = np.full((len(SLOTS), len(TYPES), len(EXITS)), np.nan, np.float32)
    mins_all = 390 - np.arange(390)                     # minutes to 16:00 at each minute index (index 0 = 09:31 -> 389? use 390-i-1)
    mins_all = 389 - np.arange(390) + 1.0
    for si, s in enumerate(SLOTS):
        S0 = c[s]; T0 = mins_all[s] / (365 * 1440)
        atm_iv = float(iv_model(V, mins_all[s], 0.0)) * mult[s]
        j = np.arange(s, LAST + 1); Sj = c[j]; Tj = mins_all[j] / (365 * 1440)
        for ti, (cp, dl) in enumerate(TYPES):
            if dl == 0.5: K = S0
            else:
                target = dl if cp == "C" else 1 - dl
                d1 = N_.inv_cdf(target); v = atm_iv * math.sqrt(T0)
                K = S0 * math.exp(-d1 * v + 0.5 * v * v)
            z = np.log(K / Sj) / (V * np.sqrt(Tj))
            mid = bs(Sj, K, Tj, iv_model(V, mins_all[j], z) * mult[j], cp)
            sp = spread(mid)
            ask0 = mid[0] + sp[0] / 2
            if not (ask0 > 0.05): continue
            bid = np.maximum(mid - sp / 2, 0.0)
            r = bid[1:] / ask0 - 1; n = len(r)
            first = lambda cond: (int(np.argmax(cond)) if cond.any() else n)
            pti = [first(r >= p) if p is not None else n for p in PTS]
            sli = [first(r <= q) if q is not None else n for q in SLS]
            hi_ = [min(h, n) - 1 if h is not None else n - 1 for h in HOLDS]
            for ei, (pi, qi, hj) in enumerate([(a, b, h) for a in range(len(PTS)) for b in range(len(SLS)) for h in range(len(HOLDS))]):
                k = min(pti[pi], sli[qi], hi_[hj] if hi_[hj] >= 0 else 0, n - 1)
                O[si, ti, ei] = (bid[1 + k] - ask0) * 100 - 2 * FEE
    return O


def build_market(days, vix, label, planted=None, beta=0.0):
    ds = sorted(days); F, O, keep = [], [], []
    closes = {d: days[d][-1] for d in ds}
    t0 = time.time()
    for i, d in enumerate(ds):
        if i < 21: continue
        vp = vix[vix.index < d]
        if len(vp) < 6: continue
        V = float(vp.iloc[-1]) / 100; v5 = float(vp.iloc[-6:-1].mean()) / 100
        pc = closes[ds[i - 1]]; prev = days[ds[i - 1]]
        f = day_features(days[d], pc, 1e4 * (prev.max() - prev.min()) / pc, 1e4 * (pc / closes[ds[i - 2]] - 1), V * 100, v5 * 100,
                         1e4 * (pc / np.mean([closes[x] for x in ds[i - 20: i]]) - 1), pd.Timestamp(d).weekday())
        if planted is not None:
            c = days[d]; fut = np.array([np.sign(c[min(s + 30, 389)] - c[s]) for s in SLOTS])
            f = np.column_stack([f, fut + planted.normal(0, 1.0, len(SLOTS))])
        F.append(f); O.append(outcome_table(days[d], V, beta)); keep.append(d)
        if i % 250 == 0: print(label, i, len(ds), round(time.time() - t0), "s", flush=True)
    return np.array(keep), np.array(F, np.float32), np.array(O, np.float32)


# ---------------------------------------------------------------- search
def first_slot(mask):
    """mask (days, slots) -> first true slot per day, -1 if none."""
    any_ = mask.any(axis=1); return np.where(any_, mask.argmax(axis=1), -1)


def eval_signal(sl, O, B, rows):
    """sl: first slot per day; rows: bool day subset. Returns (n, mean_pnl[6,100], mean_ex, t_ex, sr_ex)."""
    d = np.flatnonzero(rows & (sl >= 0))
    if len(d) < 2: return len(d), None, None, None, None
    X = O[d, sl[d]]                                  # (n, 6, 100)
    Ex = X - B[sl[d]]
    m, mx = np.nanmean(X, axis=0), np.nanmean(Ex, axis=0); sd = np.nanstd(Ex, axis=0, ddof=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        sr = mx / sd; t = sr * math.sqrt(len(d))
    return len(d), m, mx, t, sr


def thresholds(F, rows):
    return np.nanpercentile(F[rows].reshape(-1, F.shape[2]), QS, axis=0)   # (6, nfeat)


def cond_mask(F, Q, j, qi):
    with np.errstate(invalid="ignore"):
        return F[:, :, j] <= Q[qi, j] if QS[qi] < 50 else F[:, :, j] >= Q[qi, j]


def search(F, O, dev, feats, min_trades=200):
    B = np.nanmean(O[dev], axis=0)                   # (slots, 6, 100) unconditional dev mean per slot
    Q = thresholds(F, dev)
    conds = [(j, qi) for j in range(F.shape[2]) for qi in range(len(QS))]
    singles = []; all_sr = []; res = []
    masks = {c: cond_mask(F, Q, *c) for c in conds}
    def run(sig, mask):
        sl = first_slot(mask); n, m, mx, t, sr = eval_signal(sl, O, B, dev)
        if m is None: return None
        all_sr.append(sr[np.isfinite(sr)].ravel())
        if n >= min_trades:
            ok = np.where(np.isfinite(t), t, -np.inf)
            for k in np.argsort(ok.ravel())[-5:]:
                ti, ei = np.unravel_index(k, ok.shape)
                res.append(dict(signal=sig, type=int(ti), exit=int(ei), dev_n=n, dev_mean=float(m[ti, ei]), dev_excess=float(mx[ti, ei]), dev_t=float(t[ti, ei]), dev_sr=float(sr[ti, ei])))
        return t if n >= min_trades else None
    run((), np.ones(F.shape[:2], bool))
    for c in conds:
        t = run((c,), masks[c])
        if t is not None:
            tt = np.where(np.isfinite(t), t, -np.inf)
            singles.append((c, float(tt[:3].max()), float(tt[3:].max())))
    n_pairs = 0
    for side in (1, 2):
        top = [c for c, *_ in sorted(singles, key=lambda x: -x[side])[:60]]
        for a in range(len(top)):
            for b in range(a + 1, len(top)):
                if top[a][0] == top[b][0]: continue
                run((top[a], top[b]), masks[top[a]] & masks[top[b]]); n_pairs += 1
    R = pd.DataFrame(res).sort_values("dev_t", ascending=False).drop_duplicates(["signal", "type", "exit"])
    all_sr = np.concatenate(all_sr) if all_sr else np.array([])
    return R, Q, B, all_sr, len(conds) + 1 + n_pairs


def signal_mask(F, Q, sig):
    m = np.ones(F.shape[:2], bool)
    for c in sig: m &= cond_mask(F, Q, *c)
    return m


def dsr(sr, n, all_sr, n_trials, skew=0.0, kurt=3.0):
    if n < 3 or not len(all_sr): return float("nan")
    v = float(np.var(all_sr)); g = 0.5772156649
    sr0 = math.sqrt(v) * ((1 - g) * N_.inv_cdf(1 - 1 / n_trials) + g * N_.inv_cdf(1 - 1 / (n_trials * math.e)))
    den = math.sqrt(max(1 - skew * sr + (kurt - 1) / 4 * sr * sr, 1e-9))
    return N_.cdf((sr - sr0) * math.sqrt(n - 1) / den)


def holdout(R, F, O, Q, days, ho, F2=None, O2=None, Q2=None, ho2=None, all_sr=None, n_trials=1, top=20):
    B = np.nanmean(O[ho], axis=0)
    mid = days[ho][len(days[ho]) // 2] if ho.any() else None
    rows = []
    for r in R.head(top).itertuples():
        sl = first_slot(signal_mask(F, Q, r.signal))
        d = np.flatnonzero(ho & (sl >= 0))
        X = O[d, sl[d], r.type, r.exit]; Ex = X - B[sl[d], r.type, r.exit]
        n = len(d); t = Ex.mean() / Ex.std(ddof=1) * math.sqrt(n) if n > 2 and Ex.std() > 0 else float("nan")
        h1 = Ex[days[d] < mid].mean() if (days[d] < mid).any() else float("nan"); h2 = Ex[days[d] >= mid].mean() if (days[d] >= mid).any() else float("nan")
        nq = float("nan")
        if F2 is not None:
            B2 = np.nanmean(O2[ho2], axis=0); sl2 = first_slot(signal_mask(F2, Q2, r.signal)); d2 = np.flatnonzero(ho2 & (sl2 >= 0))
            nq = float((O2[d2, sl2[d2], r.type, r.exit] - B2[sl2[d2], r.type, r.exit]).mean()) if len(d2) else float("nan")
        sr_h = float(Ex.mean() / Ex.std(ddof=1)) if n > 2 and Ex.std() > 0 else float("nan")
        sk = float(pd.Series(Ex).skew()) if n > 3 else 0.0; ku = float(pd.Series(Ex).kurt()) + 3 if n > 3 else 3.0
        rows.append(dict(signal=r.signal, type=TNAME[r.type], exit=EXITS[r.exit], dev_n=r.dev_n, dev_t=round(r.dev_t, 2), ho_n=n, ho_mean=round(float(X.mean()), 2) if n else np.nan,
                         ho_excess=round(float(Ex.mean()), 2) if n else np.nan, ho_t=round(t, 2), ho_h1=round(h1, 2), ho_h2=round(h2, 2), ndx_excess=round(nq, 2),
                         zsr=sr_h, zsk=sk, zku=ku, zok=bool(n > 0 and X.mean() > 0 and Ex.mean() > 0 and t >= 3.0 and h1 > 0 and h2 > 0 and nq > 0)))
    H = pd.DataFrame(rows)
    if len(H):   # amendment 1: deflated Sharpe over the holdout trials actually run (N = number tested), SR variance across them
        srs = H.zsr.to_numpy(float); srs = srs[np.isfinite(srs)]
        H["dsr"] = [round(dsr(r.zsr, r.ho_n, srs, max(len(H), 2), r.zsk, r.zku), 3) if r.zsr == r.zsr else np.nan for r in H.itertuples()]
        H["PASS"] = H.zok & (H.dsr >= 0.95)
        H = H.drop(columns=["zsr", "zsk", "zku", "zok"])
    return H


def describe(sig, feats, Q):
    if not sig: return "always"
    return " AND ".join(f"{feats[j]} {'<=' if QS[qi] < 50 else '>='} {Q[qi, j]:.4g} (p{QS[qi]})" for j, qi in sig)


# ---------------------------------------------------------------- synthetic calibration
def synth_days(n, seed):
    rng = np.random.default_rng(seed); out = {}
    for d in pd.bdate_range("2012-01-03", periods=n):
        out[d] = 4000 * np.exp(np.cumsum(rng.normal(0, 0.0007, 390)))
    return out


def smoke():
    vix = pd.Series(18.0, index=pd.bdate_range("2011-12-01", periods=900))
    res = {}
    for planted in (False, True):
        rng = np.random.default_rng(5)
        A = synth_days(500, 1); Bm = synth_days(500, 2)
        d1, F1, O1 = build_market(A, vix, "synA", rng if planted else None)
        d2, F2, O2 = build_market(Bm, vix, "synB", np.random.default_rng(6) if planted else None)
        feats = FEATS + (["planted"] if planted else [])
        if not planted:   # keep shapes equal for the null
            pass
        dev = np.arange(len(d1)) < len(d1) * 0.55; ho = ~dev
        dev2 = np.arange(len(d2)) < len(d2) * 0.55; ho2 = ~dev2
        R, Q, B, all_sr, nt = search(F1, O1, dev, feats, min_trades=60)
        Q2 = thresholds(F2, dev2)
        H = holdout(R, F1, O1, Q, d1, ho, F2, O2, Q2, ho2, all_sr, nt)
        res[planted] = H.PASS.any()
        print("planted" if planted else "null", "trials", nt, "PASS any:", H.PASS.any()); print(H.head(5).to_string())
    assert res[True] and not res[False], "calibration failed"
    print("smoke OK")


def report():
    out = ["# Round 66: 0DTE search, 14 years of S&P minutes, option prices calibrated to real 0DTE quotes", "", "Rules: [PROTOCOL_ROUND66.md](../PROTOCOL_ROUND66.md).", ""]
    mk = {}
    for name, pair, vt in (("SPX", "SPXUSD", "^VIX"), ("NDX", "NSXUSD", "^VXN")):
        days = load_days(pair); vix = load_vix(vt)
        dd, F, O = build_market(days, vix, name)
        np.savez_compressed(f"data/r66_{name}.npz", days=dd.astype("datetime64[ns]").astype(np.int64), F=F, O=O)
        mk[name] = (np.asarray(dd).astype("datetime64[ns]"), F, O); print(name, len(dd), "days", F.shape, O.shape, flush=True)
    d1, F1, O1 = mk["SPX"]; d2, F2, O2 = mk["NDX"]
    cut = np.datetime64("2020-01-01")
    dev, ho = d1 < cut, d1 >= cut; dev2, ho2 = d2 < cut, d2 >= cut
    t0 = time.time(); R, Q, B, all_sr, nt = search(F1, O1, dev, FEATS)
    n_cfg = nt * len(TYPES) * len(EXITS)
    print("search done", nt, "signals,", n_cfg, "configs,", round(time.time() - t0), "s", flush=True)
    Q2 = thresholds(F2, dev2)
    H = holdout(R, F1, O1, Q, d1, ho, F2, O2, Q2, ho2, all_sr, n_cfg)
    H.insert(0, "rule", [describe(s, FEATS, Q) for s in H.signal]); H = H.drop(columns="signal")
    # baselines (unconditional, every day at 10:00, best and worst type/exit) for context
    base = pd.DataFrame([dict(type=TNAME[k], exit=EXITS[e], dev_mean=round(float(np.nanmean(O1[dev, 0, k, e])), 2), ho_mean=round(float(np.nanmean(O1[ho, 0, k, e])), 2))
                         for k in range(len(TYPES)) for e in range(len(EXITS))]).sort_values("dev_mean", ascending=False)
    passed = bool(H.PASS.any())
    out += [f"Days: SPX {len(d1):,} ({pd.Timestamp(d1[0]).date()} → {pd.Timestamp(d1[-1]).date()}), NDX {len(d2):,}. Dev < 2020, holdout ≥ 2020.",
            f"Search: **{nt:,} signals × {len(TYPES)} option types × {len(EXITS)} exits = {n_cfg:,} configurations** (dev only).", "",
            f"**Verdict: {'PASS → real-quote check next' if passed else 'FAIL'}.** (Top 20 dev configurations tested once on the holdout; pass needs all five criteria.)", "",
            "## Top 20 dev configurations on the holdout", "", "Excess = P&L minus the same option/exit bought unconditionally at the same slot (cancels pricing-model level bias).", "",
            H.to_markdown(index=False), "",
            "## How the best dev configurations did on the holdout (distribution)", ""]
    big = holdout(R, F1, O1, Q, d1, ho, None, None, None, None, all_sr, n_cfg, top=500)
    out += [f"Top 500 dev configurations: holdout excess > 0 in {int((big.ho_excess > 0).sum())}/500; holdout t ≥ 2 in {int((big.ho_t >= 2).sum())}; t ≥ 3 in {int((big.ho_t >= 3).sum())}. "
            f"Median holdout t {big.ho_t.median():.2f} (dev median t {big.dev_t.median():.2f}).", "",
            "## Context: unconditional option buying at 10:00 (model prices; level not trusted, see protocol)", "", base.head(10).to_markdown(index=False), "", base.tail(5).to_markdown(index=False)]
    open("reports/ROUND66.md", "w").write("\n".join(out) + "\n"); print("\n".join(out[:12]))


def reprice():
    """Amendment 2: same dev search (original prices) -> same top 20 re-tested on holdout with IV reacting to rv30."""
    m1 = json.load(open("data/r66_m1.json")); cut = np.datetime64("2020-01-01")
    raw = {}
    for name, pair, vt in (("SPX", "SPXUSD", "^VIX"), ("NDX", "NSXUSD", "^VXN")):
        raw[name] = (load_days(pair), load_vix(vt))
    def market(beta):
        mk = {}
        for name in raw:
            dd, F, O = build_market(*raw[name], name, beta=beta); mk[name] = (np.asarray(dd).astype("datetime64[ns]"), F, O)
        return mk
    base = market(0.0); d1, F1, O1 = base["SPX"]; d2, F2, _ = base["NDX"]
    dev, ho = d1 < cut, d1 >= cut; dev2, ho2 = d2 < cut, d2 >= cut
    R, Q, B, all_sr, nt = search(F1, O1, dev, FEATS); n_cfg = nt * len(TYPES) * len(EXITS); Q2 = thresholds(F2, dev2)
    H0 = holdout(R, F1, O1, Q, d1, ho, F2, base["NDX"][2], Q2, ho2, all_sr, n_cfg)
    out = ["# Round 66 amendment 2: re-priced with IV reacting to intraday realized vol", "", "Rules: [PROTOCOL_ROUND66.md](../PROTOCOL_ROUND66.md), amendment 2.", "",
           f"M1 on real SPXW quotes ({m1['n']:,} ATM snapshots, {m1['days']} days): log(real IV / model IV) vs log(rv30 / VIXprev): beta {m1['beta']:.3f} (within-day {m1['beta_within_day']:.3f}), corr {m1['corr']:.2f}. "
           f"Real/model IV median by rv30 quintile: " + ", ".join(f"{k} → {v:.2f}" for k, v in m1["by_rv_bin"].items()) + ".", "",
           f"Original prices: {int(H0.PASS.sum())}/20 top dev configurations PASS (as in ROUND66.md).", ""]
    verdict = None
    for lab, beta in (("pooled beta (pre-registered verdict)", m1["beta"]), ("within-day beta (sensitivity only)", m1["beta_within_day"])):
        mk = market(beta); _, _, O1b = mk["SPX"]; _, _, O2b = mk["NDX"]
        H = holdout(R, F1, O1b, Q, d1, ho, F2, O2b, Q2, ho2, all_sr, n_cfg)
        H.insert(0, "rule", [describe(s, FEATS, Q) for s in H.signal]); H = H.drop(columns="signal")
        if verdict is None: verdict = "PASS → real-quote replay next" if H.PASS.any() else "FAIL (model artifact)"
        out += [f"## {lab}: beta = {beta:.3f} — {int(H.PASS.sum())}/20 PASS", "", H.to_markdown(index=False), ""]
    out.insert(4, f"**Verdict: {verdict}.**\n")
    open("reports/ROUND66_REPRICE.md", "w").write("\n".join(out) + "\n"); print("\n".join(out[:12]))


if __name__ == "__main__":
    {"smoke": smoke, "report": report, "reprice": reprice}[sys.argv[1]]()

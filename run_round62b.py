"""Round 62b (PROTOCOL_ROUND62.md, amendment 5): direction study on ~20+ days of Yahoo 1-minute data (SPY + market-wide context +
calendar). Targets: SPY forward 10/30/60-minute returns. Model: gradient-boosted trees, leave-one-day-out. Policies: shares long/short,
long only, short only; every 30-min slot vs >=60% vs >=70% confident; with/without walk-away. Baselines: always long / always short.
Null: labels circularly time-shifted within training days. `smoke` | `report`."""
import glob, math, os, sys
from datetime import time as dtime
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier

ET = "America/New_York"
MEGA = ["NVDA", "AAPL", "MSFT", "AMZN", "META", "GOOGL", "TSLA"]
FOMC = ["2026-09-16", "2026-10-28", "2026-12-09", "2027-01-27"]
HZ = [10, 30, 60]
SHARES, COST = 100, 0.01          # 100 SPY shares (~$74k), 1 cent per share each way


def third_friday(y, m):
    d = pd.Timestamp(year=y, month=m, day=1)
    fr = d + pd.Timedelta(days=(4 - d.weekday()) % 7)
    return fr + pd.Timedelta(days=14)


def calendar_feats(day):
    d = pd.Timestamp(day)
    ox = third_friday(d.year, d.month)
    if ox < d: ox = third_friday(d.year + (d.month == 12), d.month % 12 + 1)
    bd = pd.bdate_range(d, ox)
    nf = min((pd.Timestamp(x) - d).days for x in FOMC if pd.Timestamp(x) >= d) if any(pd.Timestamp(x) >= d for x in FOMC) else 99
    pf = min((d - pd.Timestamp(x)).days for x in FOMC if pd.Timestamp(x) <= d) if any(pd.Timestamp(x) <= d for x in FOMC) else 99
    month_days = pd.bdate_range(d.replace(day=1), d + pd.offsets.MonthEnd(0))
    pos = list(month_days).index(d) if d in month_days else -1
    return dict(bdays_to_opex=len(bd) - 1, opex_week=int(len(bd) - 1 <= 4), days_to_fomc=nf, days_since_fomc=pf,
                month_start=int(0 <= pos <= 1), month_end=int(pos >= len(month_days) - 2))


def load(day):
    C = pd.read_csv(f"data/ctx/{day}.csv.gz", index_col=0)
    C.index = pd.to_datetime(C.index, utc=True).tz_convert(ET)
    return C.sort_index().ffill()


def day_frame(day, prev_close, prev_range):
    C = load(day)
    S = C["SPY_close"].dropna(); S = S[(S.index.time >= dtime(9, 30)) & (S.index.time < dtime(16, 0))]
    if len(S) < 300: return None, None, None
    V = C["SPY_vol"].reindex(S.index).fillna(0)
    f = pd.DataFrame(index=S.index)
    for k in (1, 3, 5, 10, 30): f[f"ret{k}"] = S.pct_change(k) * 1e4
    f["vs_open"] = (S / S.iloc[0] - 1) * 1e4; f["vs_mean"] = (S / S.expanding().mean() - 1) * 1e4
    f["vs_high"] = (S / S.cummax() - 1) * 1e4; f["vs_low"] = (S / S.cummin() - 1) * 1e4
    orh, orl = S[S.index.time < dtime(10, 0)].max(), S[S.index.time < dtime(10, 0)].min()
    f["vs_orh"] = (S / orh - 1) * 1e4; f["vs_orl"] = (S / orl - 1) * 1e4
    f.loc[f.index.time < dtime(10, 0), ["vs_orh", "vs_orl"]] = np.nan          # range not known yet
    lo_t = S.cummin().eq(S).cumsum(); hi_t = S.cummax().eq(S).cumsum()
    f["min_since_low"] = [(t - S[:t].idxmin()).total_seconds() / 60 for t in S.index]
    f["min_since_high"] = [(t - S[:t].idxmax()).total_seconds() / 60 for t in S.index]
    f["dist_round"] = (S - (S / 5).round() * 5) / S * 1e4
    f["rv30"] = S.pct_change().rolling(30).std() * 1e4
    dl = S.diff(); up = dl.clip(lower=0).ewm(alpha=1 / 14).mean(); dn = (-dl.clip(upper=0)).ewm(alpha=1 / 14).mean()
    f["rsi"] = 100 - 100 / (1 + up / dn.replace(0, np.nan))
    f["ema9_21"] = (S.ewm(span=9).mean() - S.ewm(span=21).mean()) / S * 1e4
    macd = S.ewm(span=12).mean() - S.ewm(span=26).mean(); mh = macd - macd.ewm(span=9).mean()
    f["macd_h"] = mh / S * 1e4; f["macd_slope"] = mh.diff(3) / S * 1e4
    m20, s20 = S.rolling(20).mean(), S.rolling(20).std(); f["bb_pctb"] = (S - (m20 - 2 * s20)) / (4 * s20)
    vwap = (S * V).cumsum() / V.cumsum().replace(0, np.nan); f["vs_vwap_true"] = (S / vwap - 1) * 1e4
    f["spy_vol_rel15"] = V.rolling(15).sum() / (V.expanding().mean() * 15)
    f["min_to_close"] = [(16 * 60) - (t.hour * 60 + t.minute) for t in S.index]
    f["weekday"] = S.index.weekday
    def X(col): return C[col].reindex(S.index).ffill() if col in C else pd.Series(np.nan, index=S.index)
    vix = X("^VIX_close"); f["vix"] = vix
    for k in (5, 15, 30): f[f"vix_chg{k}"] = vix.diff(k)
    mret = {k: pd.concat([X(f"{m}_close").pct_change(k) * 1e4 for m in MEGA], axis=1) for k in (5, 15, 30)}
    for k in (5, 15, 30): f[f"mega_ret{k}"] = mret[k].mean(axis=1)
    f["mega_breadth15"] = (mret[15] > 0).mean(axis=1)
    for m in ("NVDA", "AAPL", "MSFT", "TSLA"): f[f"{m.lower()}_ret15"] = X(f"{m}_close").pct_change(15) * 1e4
    spy15 = S.pct_change(15) * 1e4
    f["mega_lead15"] = f.mega_ret15 - spy15
    f["qqq_vs_spy15"] = X("QQQ_close").pct_change(15) * 1e4 - spy15; f["iwm_vs_spy15"] = X("IWM_close").pct_change(15) * 1e4 - spy15
    f["tnx_chg30"] = X("^TNX_close").diff(30); f["dxy_chg30"] = X("DX-Y.NYB_close").pct_change(30) * 1e4
    f["btc_ret30"] = X("BTC-USD_close").pct_change(30) * 1e4
    f["tlt_ret15"] = X("TLT_close").pct_change(15) * 1e4; f["hyg_ret15"] = X("HYG_close").pct_change(15) * 1e4
    f["gap"] = (S.iloc[0] / prev_close - 1) * 1e4 if prev_close else np.nan
    f["prev_range"] = prev_range / prev_close * 1e4 if prev_close else np.nan
    for k, v in calendar_feats(day).items(): f[k] = v
    # features use bars that CLOSED before the decision: shift everything by one bar (decision at the next bar's open)
    f = f.shift(1)
    for h in HZ: f[f"fwd{h}"] = (S.shift(-h) / S - 1) * 1e4       # entry at this bar's close ~ next open
    f["px"] = S; f["px_fwd30"] = S.shift(-30)
    f["day"] = day; f["t"] = f.index
    f = f[(f.index.time >= dtime(9, 45)) & (f.index.time <= dtime(15, 30))]
    return f, S.iloc[-1], S.max() - S.min()


def build():
    days = sorted(os.path.basename(p)[:10] for p in glob.glob("data/ctx/2*.csv.gz"))
    out, pc, pr = [], None, None
    for d in days:
        f, pc2, pr2 = day_frame(d, pc, pr)
        if f is None: continue
        out.append(f); pc, pr = pc2, pr2
    return pd.concat(out, ignore_index=True)


SKIP = {"day", "t", "px", "px_fwd30"} | {f"fwd{h}" for h in HZ}


def feats(D): return [c for c in D.columns if c not in SKIP]


def oof(D, F, h, shift=False, seed=0):
    rng = np.random.default_rng(seed); P = []
    for hold in sorted(D.day.unique()):
        tr, te = D[(D.day != hold) & D[f"fwd{h}"].notna()].copy(), D[D.day == hold]
        if shift: tr[f"fwd{h}"] = tr.groupby("day")[f"fwd{h}"].transform(lambda s: np.roll(s.values, int(rng.integers(60, 240))))
        m = HistGradientBoostingClassifier(max_iter=150, learning_rate=0.05, max_leaf_nodes=15, l2_regularization=1.0, random_state=0)
        m.fit(tr[F], (tr[f"fwd{h}"] > 0).astype(int))
        P.append(te.assign(p_up=m.predict_proba(te[F])[:, 1]))
    return pd.concat(P, ignore_index=True)


def policy(P, h, mode, hi, lo, every, walk):
    rows = []
    for day, x in P.sort_values("t").groupby("day"):
        busy = None
        for r in x.itertuples():
            if busy is not None and r.t < busy: continue
            fr = getattr(r, f"fwd{h}")
            if fr != fr: continue
            if every: side = 1 if r.p_up >= 0.5 else -1
            else: side = 1 if r.p_up >= hi else (-1 if r.p_up <= lo else 0)
            if mode == "long_only" and side < 0: side = 0
            if mode == "short_only" and side > 0: side = 0
            if side == 0: continue
            pnl = side * fr / 1e4 * r.px * SHARES - 2 * COST * SHARES
            rows.append(dict(day=day, t=r.t, pnl=pnl)); busy = r.t + pd.Timedelta(minutes=h)
            if walk and pnl > 0: break
    return pd.DataFrame(rows, columns=["day", "t", "pnl"])


def summ(T):
    if T.empty: return dict(trades=0, total=0.0, win=np.nan, green="0/0", t=np.nan)
    dd = T.groupby("day").pnl.sum()
    return dict(trades=len(T), total=round(T.pnl.sum(), 0), win=round((T.pnl > 0).mean(), 2), green=f"{(dd > 0).sum()}/{len(dd)}",
                t=round(dd.mean() / dd.std() * math.sqrt(len(dd)), 2) if len(dd) > 2 and dd.std() > 0 else np.nan)


def analyze(D, n_null=10):
    F = feats(D); rows = []; nulls = {}
    for h in HZ:
        P = oof(D, F, h)
        for mode in ("long_short", "long_only", "short_only"):
            for sel, (hi, lo, every) in {"every slot": (0.5, 0.5, True), "≥60%": (0.6, 0.4, False), "≥70%": (0.7, 0.3, False)}.items():
                for walk in (False, True):
                    rows.append(dict(horizon=f"{h}m", policy=mode, selectivity=sel, walk_away=walk, **summ(policy(P, h, mode, hi, lo, every, walk))))
        # baselines on the same grid (a trade every h minutes)
        G = D[D[f"fwd{h}"].notna()].sort_values("t").assign(slot=lambda z: z.t.dt.floor(f"{h}min")).groupby(["day", "slot"]).head(1)
        for side, nm in ((1, "BASELINE always long"), (-1, "BASELINE always short")):
            T = G.assign(pnl=side * G[f"fwd{h}"] / 1e4 * G.px * SHARES - 2 * COST * SHARES)[["day", "t", "pnl"]]
            rows.append(dict(horizon=f"{h}m", policy=nm, selectivity="every slot", walk_away=False, **summ(T)))
        nulls[h] = [policy(oof(D, F, h, shift=True, seed=s), h, "long_short", 0.6, 0.4, False, False).pnl.sum() for s in range(n_null if h == 30 else 5)]
    return pd.DataFrame(rows), nulls


def smoke():
    D = build(); rng = np.random.default_rng(2)
    P = D.copy(); P["planted"] = P.fwd30 + rng.normal(0, P.fwd30.std() * 0.7, len(P))
    F = feats(P); pr = oof(P, F, 30)
    s = summ(policy(pr, 30, "long_short", 0.6, 0.4, False, False)); print("planted:", s)
    assert s["total"] > 0, "planted signal not exploited"
    print("smoke OK")


def report():
    D = build(); R, nulls = analyze(D)
    n = D.day.nunique()
    q = {h: float(np.percentile(v, 95)) for h, v in nulls.items()}
    best = {h: R[(R.horizon == f"{h}m") & ~R.policy.str.startswith("BASELINE")].total.max() for h in HZ}
    base = {h: R[(R.horizon == f"{h}m") & R.policy.str.startswith("BASELINE")].total.max() for h in HZ}
    out = ["# Round 62b: direction study on Yahoo 1-minute data (SPY + market-wide + calendar variables)", "",
           "Rules: [PROTOCOL_ROUND62.md](../PROTOCOL_ROUND62.md) amendment 5. 100 SPY shares per trade (~$74k), 1¢/share each way. Leave-one-day-out.",
           f"Days: **{n}** ({D.day.min()} → {D.day.max()}); minutes analysed: {len(D):,}; variables: {len(feats(D))}.", ""]
    for h in HZ:
        out.append(f"- {h}-min horizon: best model policy ${best[h]:,.0f} vs best no-model baseline ${base[h]:,.0f}; "
                   f"model ≥60% long/short ${R[(R.horizon == f'{h}m') & (R.policy == 'long_short') & (R.selectivity == '≥60%') & (~R.walk_away)].total.iloc[0]:,.0f} "
                   f"vs time-shift null 95th pct ${q[h]:,.0f}.")
    out += ["", R.sort_values("total", ascending=False).to_markdown(index=False)]
    open("reports/ROUND62B.md", "w").write("\n".join(out) + "\n"); print("\n".join(out[:12]))


if __name__ == "__main__":
    {"smoke": smoke, "report": report, "build": lambda: print(build().shape)}[sys.argv[1]]()

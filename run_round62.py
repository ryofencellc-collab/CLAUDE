"""Round 62 (PROTOCOL_ROUND62.md): every-variable analysis of 0DTE SPY/SPXW trades on recorded quotes.
`build` (feature + label tables) | `smoke` | `report`."""
import glob, math, os, sys
from datetime import time as dtime
import numpy as np, pandas as pd
from scipy.stats import spearmanr
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
from edge import odte_score as O

OUT = "data/r62"; os.makedirs(OUT, exist_ok=True)
ROUND = {"SPY": 5.0, "SPXW": 25.0}
TP, SL, HOLD = 1.50, 0.75, 30


def days():
    return sorted(os.path.basename(p) for p in glob.glob(os.path.join(O.DATA, "2*")) if pd.Timestamp(os.path.basename(p)).weekday() < 5)


def chain_at(d):
    """Dict t -> chain DataFrame (rows: cp, K, bid, ask, bid_size, ask_size, iv, delta, gamma, theo, volume, open_interest)."""
    return {t: g for t, g in d.groupby("t", sort=True)}


def atm_row(g, cp, S):
    x = g[(g.cp == cp) & (g.bid > 0) & (g.ask > 0)]
    if x.empty: return None
    return x.loc[(x.K - S).abs().idxmin()]


def trade_pnl(ts, chains, i, cp, root):
    """Buy ATM `cp` at snapshot i (ask), exit by X2 rules at the bid. Returns P&L per contract ($) or NaN."""
    t0 = ts[i]; g0 = chains[t0]; S = g0.spot.iloc[0]
    r = atm_row(g0, cp, S)
    if r is None: return np.nan
    K, paid = r.K, r.ask; mult, fee = O.SPEC[ROOT[0]]["mult"], O.SPEC[ROOT[0]]["fee"]
    for t in ts[i + 1:]:
        g = chains[t]; x = g[(g.cp == cp) & (g.K == K)]
        if x.empty: continue
        b = float(x.bid.iloc[0])
        if b >= TP * paid or (b <= SL * paid and b > 0) or (t - t0) >= pd.Timedelta(minutes=HOLD) or t.time() >= dtime(15, 45):
            return (b - paid) * mult - 2 * fee
    return np.nan


ROOT = ["SPY"]


def straddle_pnl(ts, chains, i, short=False):
    """Buy (or sell) the ATM straddle at snapshot i. Long: pay asks, exit at bids on +50% / -25% / 30 min / 15:45.
    Short: receive bids, buy back at asks when cost <= 50% of credit (take profit) or >= 125% (stop), or at 30 min / 15:45."""
    t0 = ts[i]; g0 = chains[t0]; S = g0.spot.iloc[0]
    c, p = atm_row(g0, "C", S), atm_row(g0, "P", S)
    if c is None or p is None: return np.nan
    mult, fee = O.SPEC[ROOT[0]]["mult"], O.SPEC[ROOT[0]]["fee"]
    open_px = (c.bid + p.bid) if short else (c.ask + p.ask)
    if open_px <= 0: return np.nan
    for t in ts[i + 1:]:
        g = chains[t]
        xc, xp = g[(g.cp == "C") & (g.K == c.K)], g[(g.cp == "P") & (g.K == p.K)]
        if xc.empty or xp.empty: continue
        if short:
            cost = float(xc.ask.iloc[0] + xp.ask.iloc[0])
            if cost <= 0.5 * open_px or cost >= 1.25 * open_px or (t - t0) >= pd.Timedelta(minutes=HOLD) or t.time() >= dtime(15, 45):
                return (open_px - cost) * mult - 4 * fee
        else:
            val = float(xc.bid.iloc[0] + xp.bid.iloc[0])
            if val >= TP * open_px or (val <= SL * open_px and val > 0) or (t - t0) >= pd.Timedelta(minutes=HOLD) or t.time() >= dtime(15, 45):
                return (val - open_px) * mult - 4 * fee
    return np.nan


MEGA = ["NVDA", "AAPL", "MSFT", "AMZN", "META", "GOOGL", "TSLA"]


def load_ctx(day):
    path = f"data/ctx/{day}.csv.gz"
    if not os.path.exists(path): return None
    C = pd.read_csv(path, index_col=0); C.index = pd.to_datetime(C.index, utc=True).tz_convert(O.ET)
    return C.sort_index().ffill()


def ctx_feats(C, t):
    """Market-wide variables from Yahoo 1-minute bars that CLOSED before t (bar stamped m closes at m+1)."""
    if C is None: return {}
    cut = t.floor("min") - pd.Timedelta(minutes=1)
    X = C[C.index <= cut]
    if len(X) < 31: return {}
    def chg(col, k, pct=True):
        if col not in X or X[col].iloc[-1 - k] != X[col].iloc[-1 - k]: return np.nan
        a, b = X[col].iloc[-1 - k], X[col].iloc[-1]
        return (b / a - 1) * 1e4 if pct else (b - a)
    f = {"vix": X["^VIX_close"].iloc[-1] if "^VIX_close" in X else np.nan}
    for k in (5, 15, 30): f[f"vix_chg{k}"] = chg("^VIX_close", k, pct=False)
    m15 = [chg(f"{m}_close", 15) for m in MEGA]; m5 = [chg(f"{m}_close", 5) for m in MEGA]; m30 = [chg(f"{m}_close", 30) for m in MEGA]
    f.update(mega_ret5=np.nanmean(m5), mega_ret15=np.nanmean(m15), mega_ret30=np.nanmean(m30),
             mega_breadth15=np.nanmean([v > 0 for v in m15 if v == v]) if any(v == v for v in m15) else np.nan,
             nvda_ret15=chg("NVDA_close", 15), aapl_ret15=chg("AAPL_close", 15), msft_ret15=chg("MSFT_close", 15), tsla_ret15=chg("TSLA_close", 15))
    spy15 = chg("SPY_close", 15)
    f.update(mega_lead15=f["mega_ret15"] - spy15, qqq_vs_spy15=chg("QQQ_close", 15) - spy15, iwm_vs_spy15=chg("IWM_close", 15) - spy15,
             tnx_chg30=chg("^TNX_close", 30, pct=False), dxy_chg30=chg("DX-Y.NYB_close", 30), btc_ret30=chg("BTC-USD_close", 30),
             tlt_ret15=chg("TLT_close", 15), hyg_ret15=chg("HYG_close", 15))
    sess = X[X.index.time >= dtime(9, 30)]
    if "SPY_vol" in sess and sess.SPY_vol.sum() > 0:
        vwap = (sess.SPY_close * sess.SPY_vol).sum() / sess.SPY_vol.sum()
        f["vs_vwap_true"] = (sess.SPY_close.iloc[-1] / vwap - 1) * 1e4
        v15 = sess.SPY_vol.tail(15).sum(); avg15 = sess.SPY_vol.mean() * 15
        f["spy_vol_rel15"] = v15 / avg15 if avg15 > 0 else np.nan
    return f


def build_day(day, root, prev):
    ROOT[0] = root
    d = O.load_day(day, root)
    if d.empty or d["t"].nunique() < O.MIN_SNAPS: return None, prev
    d = d[(d.t.dt.time >= dtime(9, 30)) & (d.t.dt.time <= dtime(15, 59))]
    chains = chain_at(d); ts = sorted(chains)
    sp = pd.Series({t: chains[t].spot.iloc[0] for t in ts}).sort_index()
    orng = sp[sp.index.time < dtime(10, 0)]; orh, orl = orng.max(), orng.min()
    dl = sp.diff(); up = dl.clip(lower=0).ewm(alpha=1 / 14).mean(); dn = (-dl.clip(upper=0)).ewm(alpha=1 / 14).mean()
    rsi = 100 - 100 / (1 + up / dn.replace(0, np.nan))
    macd = sp.ewm(span=12).mean() - sp.ewm(span=26).mean(); mh = macd - macd.ewm(span=9).mean()
    m20, s20 = sp.rolling(20).mean(), sp.rolling(20).std()
    rows = []
    feat_hist = []
    CTX = load_ctx(day)
    for i, t in enumerate(ts):
        if not (dtime(9, 45) <= t.time() < dtime(15, 30)): continue
        g = chains[t]; S = sp[t]
        past = sp[:t]
        f = dict(day=day, root=root, t=t, spot=S)
        for k in (1, 3, 5, 10, 30):
            f[f"ret{k}"] = (S / past.iloc[-1 - k] - 1) * 1e4 if len(past) > k else np.nan
        f.update(vs_open=(S / past.iloc[0] - 1) * 1e4, vs_mean=(S / past.mean() - 1) * 1e4, vs_high=(S / past.max() - 1) * 1e4,
                 vs_low=(S / past.min() - 1) * 1e4, vs_orh=(S / orh - 1) * 1e4, vs_orl=(S / orl - 1) * 1e4,
                 min_since_low=(t - past.idxmin()).total_seconds() / 60, min_since_high=(t - past.idxmax()).total_seconds() / 60,
                 dist_round=(S - round(S / ROUND[root]) * ROUND[root]) / S * 1e4,
                 rv30=past.pct_change().tail(30).std() * 1e4 if len(past) > 30 else np.nan,
                 rsi=rsi[t], ema9_21=(past.ewm(span=9).mean().iloc[-1] - past.ewm(span=21).mean().iloc[-1]) / S * 1e4,
                 macd_h=mh[t] / S * 1e4, macd_slope=(mh[t] - mh[:t].iloc[-4]) / S * 1e4 if len(past) > 4 else np.nan,
                 bb_pctb=(S - (m20[t] - 2 * s20[t])) / (4 * s20[t]) if s20[t] and s20[t] == s20[t] else np.nan,
                 min_to_close=(pd.Timestamp.combine(t.date(), dtime(16, 0)).tz_localize(t.tz) - t).total_seconds() / 60, weekday=t.weekday())
        ac, ap = atm_row(g, "C", S), atm_row(g, "P", S)
        if ac is None or ap is None: continue
        f.update(atm_iv=(ac.iv + ap.iv) / 2, atm_gamma=(ac.gamma + ap.gamma) / 2, atm_spread=(ac.ask - ac.bid + ap.ask - ap.bid) / 2,
                 atm_spread_pct=((ac.ask - ac.bid) / max(ac.ask, 0.01) + (ap.ask - ap.bid) / max(ap.ask, 0.01)) / 2,
                 imb_call=(ac.bid_size - ac.ask_size) / max(ac.bid_size + ac.ask_size, 1), imb_put=(ap.bid_size - ap.ask_size) / max(ap.bid_size + ap.ask_size, 1))
        live = g[(g.iv > 0)]
        c25 = live[live.cp == "C"].iloc[(live[live.cp == "C"].delta - 0.25).abs().argsort()[:1]]
        p25 = live[live.cp == "P"].iloc[(live[live.cp == "P"].delta + 0.25).abs().argsort()[:1]]
        f["skew25"] = float(p25.iv.iloc[0] - c25.iv.iloc[0]) if len(c25) and len(p25) else np.nan
        vc, vp = g[g.cp == "C"].volume.sum(), g[g.cp == "P"].volume.sum()
        f["pcr_vol"] = vp / max(vc, 1)
        f["pcr_oi"] = g[g.cp == "P"].open_interest.sum() / max(g[g.cp == "C"].open_interest.sum(), 1)
        oi = g.groupby("K").open_interest.sum(); f["dist_maxoi"] = (S - oi.idxmax()) / S * 1e4 if len(oi) else np.nan
        gam = (g.gamma * g.open_interest).groupby(g.K).sum(); f["dist_maxgamma"] = (S - gam.idxmax()) / S * 1e4 if len(gam) else np.nan
        sign = np.where(g.cp == "C", 1.0, -1.0); f["gex"] = float((g.gamma * g.open_interest * sign).sum() * S * S * 0.01 * 100 / 1e9)
        f["theta_proxy"] = (ac.theo + ap.theo) / 2
        f.update(ctx_feats(CTX, t))
        feat_hist.append((t, f["atm_iv"], f["pcr_vol"], vc, vp))
        h = [x for x in feat_hist if (t - x[0]) <= pd.Timedelta(minutes=15)]
        f["iv_chg15"] = f["atm_iv"] - h[0][1]; f["pcr_chg15"] = f["pcr_vol"] - h[0][2]
        f["vol15_call"], f["vol15_put"] = vc - h[0][3], vp - h[0][4]
        f["gap"] = (past.iloc[0] / prev["close"] - 1) * 1e4 if prev else np.nan
        f["prev_range"] = prev["range"] / prev["close"] * 1e4 if prev else np.nan
        # labels
        j = next((k for k in range(i, len(ts)) if (ts[k] - t) >= pd.Timedelta(minutes=30)), None)
        f["fwd30"] = (sp[ts[j]] / S - 1) * 1e4 if j is not None else np.nan
        f["pnl_call"] = trade_pnl(ts, chains, i, "C", root); f["pnl_put"] = trade_pnl(ts, chains, i, "P", root)
        f["pnl_straddle"] = straddle_pnl(ts, chains, i); f["pnl_short_straddle"] = straddle_pnl(ts, chains, i, short=True)
        shares = 100 if root == "SPY" else 10            # ~$74k notional either way (SPX ~10x SPY)
        f["pnl_shares_long"] = (sp[ts[j]] - S) * shares - 0.01 * shares * 2 if j is not None else np.nan
        f["pnl_shares_short"] = -(sp[ts[j]] - S) * shares - 0.01 * shares * 2 if j is not None else np.nan
        rows.append(f)
    return pd.DataFrame(rows), dict(close=sp.iloc[-1], range=sp.max() - sp.min())


FEATS = None


def build():
    allr = []
    for root in O.SPEC:
        prev = None
        for day in days():
            path = f"{OUT}/{root}_{day}.pkl"
            if os.path.exists(path):
                X, prev = pd.read_pickle(path)
            else:
                X, prev2 = build_day(day, root, prev)
                if X is None: continue
                prev = prev2; pd.to_pickle((X, prev), path)
            allr.append(X); print("built", root, day, len(X), flush=True)
    return pd.concat(allr, ignore_index=True)


def feat_cols(D):
    skip = {"day", "root", "t", "spot", "fwd30", "pnl_call", "pnl_put", "pnl_straddle", "pnl_short_straddle", "pnl_shares_long", "pnl_shares_short"}
    return [c for c in D.columns if c not in skip]


def univariate(D, F, n_null=100, seed=0):
    """Amendment 1: per-day Spearman IC vs a NULL built by circularly shifting the target within each day (60-240 min).
    Raw within-day ICs of level variables are biased (a pure random walk gives IC -0.36, t -7 for level vs forward change);
    the shifted null keeps that bias, so only excess over it counts. z = (mean IC - null mean) / null sd."""
    rng = np.random.default_rng(seed); out = []
    groups = [(k, x.reset_index(drop=True)) for k, x in D.groupby(["root", "day"])]
    for tgt in ("fwd30", "cp"):
        for c in F:
            real, null = [], np.zeros(n_null)
            per = []
            for _, x in groups:
                y = x.fwd30 if tgt == "fwd30" else (x.pnl_call - x.pnl_put)
                ok = x[c].notna() & y.notna()
                if ok.sum() < 40 or x[c][ok].nunique() < 4: continue
                xv, yv = x[c][ok].rank().values, y[ok].rank().values
                per.append((xv, yv))
            if len(per) < 3: continue
            ic = np.mean([np.corrcoef(a, b)[0, 1] for a, b in per])
            for k in range(n_null):
                null[k] = np.mean([np.corrcoef(a, np.roll(b, int(rng.integers(60, min(240, len(b) - 1))))) [0, 1] for a, b in per])
            out.append(dict(variable=c, target="fwd30" if tgt == "fwd30" else "call−put P&L", mean_IC=ic, null_mean=null.mean(),
                            excess=ic - null.mean(), z_vs_null=(ic - null.mean()) / null.std() if null.std() > 0 else np.nan, days=len(per)))
    U = pd.DataFrame(out)
    crit = float(__import__("scipy").stats.norm.ppf(1 - 0.025 / max(len(U), 1)))
    U["significant"] = U.z_vs_null.abs() >= crit
    return U.sort_values("z_vs_null", key=abs, ascending=False), crit


def tradable(D, F):
    """Amendment 2: per-variable TRADABLE test (unbiased; a martingale gives zero expected P&L whatever the feature).
    Dev = first half of days: median m of the variable, and whether 'above m' favours calls or puts (mean call−put P&L).
    Holdout = second half: every 30 min from 10:00 to 15:00, buy the favoured side; P&L at real bid/ask (X2)."""
    out = []
    grid = {dtime(h, m) for h in range(10, 15) for m in (0, 30)} | {dtime(15, 0)}
    for root, R in D.groupby("root"):
        dl = sorted(R.day.unique()); dev, ho = R[R.day.isin(dl[: len(dl) // 2])], R[R.day.isin(dl[len(dl) // 2:])]
        H = ho[[t.replace(second=0, microsecond=0).time() in grid or False for t in ho.t]]
        H = H.assign(slot=[t.replace(second=0, microsecond=0).floor("30min") for t in H.t]).sort_values("t").groupby(["day", "slot"]).head(1)
        for c in F:
            x = dev[[c, "pnl_call", "pnl_put"]].dropna()
            if len(x) < 100 or x[c].nunique() < 4: continue
            m = x[c].median(); diff = x.pnl_call - x.pnl_put
            hi_calls = diff[x[c] > m].mean() > diff[x[c] <= m].mean()
            h = H[[c, "pnl_call", "pnl_put", "day"]].dropna()
            if h.empty: continue
            take_call = (h[c] > m) == hi_calls
            pnl = np.where(take_call, h.pnl_call, h.pnl_put)
            dd = pd.Series(pnl, index=h.day.values).groupby(level=0).sum()
            out.append(dict(root=root, variable=c, rule=f"{'above' if hi_calls else 'below'} dev median → calls, else puts", holdout_trades=len(pnl),
                            holdout_total=pnl.sum(), per_trade=pnl.mean(), green_days=f"{(dd > 0).sum()}/{len(dd)}",
                            t=dd.mean() / dd.std() * math.sqrt(len(dd)) if len(dd) > 2 and dd.std() > 0 else np.nan))
        for side, nm in (("pnl_put", "BASELINE always puts"), ("pnl_call", "BASELINE always calls")):
            dd = H.groupby("day")[side].sum()
            out.append(dict(root=root, variable=nm, rule="no signal (trend tilt)", holdout_trades=len(H), holdout_total=H[side].sum(), per_trade=H[side].mean(),
                            green_days=f"{(dd > 0).sum()}/{len(dd)}", t=dd.mean() / dd.std() * math.sqrt(len(dd)) if len(dd) > 2 and dd.std() > 0 else np.nan))
    T = pd.DataFrame(out)
    base = T[T.variable.str.startswith("BASELINE")].groupby("root").holdout_total.max()
    T["beats_best_baseline"] = [r.holdout_total > base.get(r.root, np.inf) if not r.variable.startswith("BASELINE") else "" for r in T.itertuples()]
    return T.sort_values("holdout_total", ascending=False)


def lodo(D, F, label_shift=None, seed=0):
    """Leave-one-day-out: per root, predict P(fwd30 > 0); rule P>=.6 call, <=.4 put; one position at a time (30-min block)."""
    rng = np.random.default_rng(seed); trades = []
    for root, R in D.groupby("root"):
        dlist = sorted(R.day.unique())
        for hold in dlist:
            tr = R[(R.day != hold) & R.fwd30.notna()].copy()
            if label_shift:
                tr["fwd30"] = tr.groupby("day").fwd30.transform(lambda s: np.roll(s.values, int(rng.integers(60, 240))))
            te = R[R.day == hold]
            if tr.empty or te.empty: continue
            m = HistGradientBoostingClassifier(max_iter=150, learning_rate=0.05, max_leaf_nodes=15, l2_regularization=1.0, random_state=0)
            m.fit(tr[F], (tr.fwd30 > 0).astype(int))
            p = m.predict_proba(te[F])[:, 1]
            busy_until = None
            for (idx, r), pr in zip(te.iterrows(), p):
                if busy_until is not None and r.t < busy_until: continue
                side = "C" if pr >= 0.60 else ("P" if pr <= 0.40 else None)
                if side is None: continue
                pnl = r.pnl_call if side == "C" else r.pnl_put
                if pnl != pnl: continue
                trades.append(dict(root=root, day=hold, t=r.t, side=side, p=pr, pnl=pnl)); busy_until = r.t + pd.Timedelta(minutes=30)
    return pd.DataFrame(trades, columns=["root", "day", "t", "side", "p", "pnl"])


POLICIES = {   # name: (instrument for 'up' prediction, instrument for 'down' prediction)
    "options: calls up / puts down": ("pnl_call", "pnl_put"),
    "options: calls only (long only)": ("pnl_call", None),
    "options: puts only (short only)": (None, "pnl_put"),
    "shares: long up / short down": ("pnl_shares_long", "pnl_shares_short"),
    "shares: long only": ("pnl_shares_long", None),
}


def lodo_matrix(D, F):
    """Out-of-fold P(up) for every snapshot (leave-one-day-out), plus P(big move) for straddle policies."""
    P = []
    for root, R in D.groupby("root"):
        R = R.copy(); R["big"] = (R.fwd30.abs() > R.fwd30.abs().median()).astype(int)
        for hold in sorted(R.day.unique()):
            tr, te = R[(R.day != hold) & R.fwd30.notna()], R[R.day == hold]
            if tr.empty or te.empty: continue
            mk = lambda: HistGradientBoostingClassifier(max_iter=150, learning_rate=0.05, max_leaf_nodes=15, l2_regularization=1.0, random_state=0)
            m1 = mk().fit(tr[F], (tr.fwd30 > 0).astype(int)); m2 = mk().fit(tr[F], tr.big)
            P.append(te.assign(p_up=m1.predict_proba(te[F])[:, 1], p_big=m2.predict_proba(te[F])[:, 1]))
    return pd.concat(P, ignore_index=True)


def run_policy(P, up_col, dn_col, hi, lo, mode="dir", every=False, walk=False):
    rows = []
    for (root, day), x in P.sort_values("t").groupby(["root", "day"]):
        busy = None
        for r in x.itertuples():
            if busy is not None and r.t < busy: continue
            if mode == "dir":
                if every: col = up_col if r.p_up >= 0.5 else dn_col
                else: col = up_col if r.p_up >= hi else (dn_col if r.p_up <= lo else None)
            else:   # volatility: big move -> long straddle, quiet -> short straddle
                col = "pnl_straddle" if r.p_big >= hi else ("pnl_short_straddle" if r.p_big <= lo else None)
                if every: col = "pnl_straddle" if r.p_big >= 0.5 else "pnl_short_straddle"
            if col is None: continue
            v = getattr(r, col)
            if v != v: continue
            rows.append(dict(root=root, day=day, t=r.t, pnl=v)); busy = r.t + pd.Timedelta(minutes=30)
            if walk and v > 0: break
    return pd.DataFrame(rows, columns=["root", "day", "t", "pnl"])


def matrix(P):
    out = []
    pols = [(nm, u, d, "dir") for nm, (u, d) in POLICIES.items()] + [("straddles: buy if big move expected, sell if quiet", None, None, "vol")]
    for nm, u, d, mode in pols:
        for sel, (hi, lo, every) in {"every 30-min slot": (0.5, 0.5, True), "confident (≥60%)": (0.60, 0.40, False), "very confident (≥70%)": (0.70, 0.30, False)}.items():
            for walk in (False, True):
                T = run_policy(P, u, d, hi, lo, mode, every, walk)
                for root in sorted(P.root.unique()):
                    x = T[T.root == root]; s_ = summarize(x)
                    out.append(dict(policy=nm, selectivity=sel, walk_away=walk, root=root, trades=s_["trades"], total=round(s_["total"], 0) if s_["trades"] else 0,
                                    win=round(s_.get("win", np.nan), 2) if s_["trades"] else np.nan, green=s_.get("green"), t=round(s_["t"], 2) if s_["t"] == s_["t"] else np.nan))
    # no-model baselines on the same 30-min grid
    for root in sorted(P.root.unique()):
        G = P[P.root == root].sort_values("t").assign(slot=lambda z: z.t.dt.floor("30min")).groupby(["day", "slot"]).head(1)
        for col in ["pnl_call", "pnl_put", "pnl_straddle", "pnl_short_straddle", "pnl_shares_long", "pnl_shares_short"]:
            dd = G.groupby("day")[col].sum()
            out.append(dict(policy=f"BASELINE always {col.replace('pnl_', '')}", selectivity="every 30-min slot", walk_away=False, root=root, trades=int(G[col].notna().sum()),
                            total=round(G[col].sum(), 0), win=round((G[col] > 0).mean(), 2), green=f"{(dd > 0).sum()}/{len(dd)}",
                            t=round(dd.mean() / dd.std() * math.sqrt(len(dd)), 2) if dd.std() > 0 else np.nan))
    return pd.DataFrame(out)


def walk_first_win(T):
    keep = []
    for _, x in T.sort_values("t").groupby(["root", "day"]):
        for idx, r in x.iterrows():
            keep.append(idx)
            if r.pnl > 0: break
    return T.loc[keep]


def importance(D, F):
    out = []
    for root, R in D.groupby("root"):
        R = R[R.fwd30.notna()]; dl = sorted(R.day.unique())
        if len(dl) < 3: continue
        tr, te = R[R.day.isin(dl[:-2])], R[R.day.isin(dl[-2:])]
        m = HistGradientBoostingClassifier(max_iter=150, learning_rate=0.05, max_leaf_nodes=15, l2_regularization=1.0, random_state=0)
        m.fit(tr[F], (tr.fwd30 > 0).astype(int))
        pi = permutation_importance(m, te[F], (te.fwd30 > 0).astype(int), n_repeats=5, random_state=0, scoring="roc_auc")
        out.append(pd.Series(pi.importances_mean, index=F, name=root))
    return pd.concat(out, axis=1) if out else pd.DataFrame()


def summarize(T):
    if T.empty: return dict(trades=0, total=0, per_trade=np.nan, green=np.nan, t=np.nan)
    dd = T.groupby(["root", "day"]).pnl.sum()
    return dict(trades=len(T), total=T.pnl.sum(), per_trade=T.pnl.mean(), win=(T.pnl > 0).mean(), green=f"{(dd > 0).sum()}/{len(dd)}",
                t=dd.mean() / dd.std() * math.sqrt(len(dd)) if len(dd) > 2 and dd.std() > 0 else np.nan)


def smoke():
    D = build(); F = feat_cols(D)
    rng = np.random.default_rng(1)
    P = D.copy(); P["planted"] = P.fwd30 + rng.normal(0, P.fwd30.std() * 0.7, len(P)); P["noise"] = rng.normal(0, 1, len(P))
    Fp = F + ["planted", "noise"]
    imp = importance(P, Fp)
    top = imp.mean(axis=1).sort_values(ascending=False)
    print("planted importance rank:", list(top.index).index("planted") + 1, "noise rank:", list(top.index).index("noise") + 1, "of", len(top))
    assert list(top.index).index("planted") == 0, "planted variable not ranked first"
    Tp = lodo(P, Fp); print("planted model P&L", summarize(Tp))
    assert Tp.pnl.sum() > 0, "planted model did not profit"
    print("smoke OK")


def report():
    D = build(); F = feat_cols(D); n_days = D.day.nunique()
    U, crit = univariate(D, F)
    TR = tradable(D, F)
    T = lodo(D, F); W = walk_first_win(T) if len(T) else T
    nulls = [lodo(D, F, label_shift=True, seed=s).pnl.sum() for s in range(20)]
    imp = importance(D, F)
    M = matrix(lodo_matrix(D, F))
    s_all, s_walk = summarize(T), summarize(W)
    by_root = {r: summarize(T[T.root == r]) for r in T.root.unique()} if len(T) else {}
    q95 = float(np.percentile(nulls, 95))
    out = ["# Round 62: every-variable analysis of 0DTE trades (real recorded quotes)", "", "Rules: [PROTOCOL_ROUND62.md](../PROTOCOL_ROUND62.md).",
           f"Recorded days: **{n_days}** ({'INTERIM: pass needs 20 days' if n_days < 20 else 'scored'}); snapshots analysed: {len(D):,}; variables: {len(F)}.", "",
           "## A. Which variables predict? (per-day Spearman IC vs a time-shift null)", "",
           f"Each IC is compared with a null built from the same day's target shifted in time (raw within-day ICs of level variables are biased). "
           f"Bonferroni bar |z| ≥ {crit:.2f} over {len(U)} tests. Significant: **{int(U.significant.sum())}**.", "",
           U.head(30).round(3).to_markdown(index=False), "",
           "## A2. Tradable test per variable (learn direction on the first half of the days, trade the second half every 30 min, real bid/ask)", "",
           "This is the unbiased test. The table in A is descriptive only (its within-day ICs are inflated for level variables, see amendments).", "",
           f"Variables that beat the better of 'always puts' / 'always calls' on the same holdout: "
           f"SPY {int((TR[TR.root == 'SPY'].beats_best_baseline == True).sum())}, SPXW {int((TR[TR.root == 'SPXW'].beats_best_baseline == True).sum())}.", "",
           f"Variables profitable in holdout: SPY {int(((TR.root == 'SPY') & (TR.holdout_total > 0)).sum())}/{int((TR.root == 'SPY').sum())}, "
           f"SPXW {int(((TR.root == 'SPXW') & (TR.holdout_total > 0)).sum())}/{int((TR.root == 'SPXW').sum())}. "
           f"Profitable on BOTH roots: {', '.join(sorted(set(TR[(TR.root == 'SPY') & (TR.holdout_total > 0)].variable) & set(TR[(TR.root == 'SPXW') & (TR.holdout_total > 0)].variable))) or 'none'}.", "",
           TR.round(2).to_markdown(index=False), "",
           "## B. The algorithm (gradient-boosted trees on all variables, leave-one-day-out, real bid/ask, X2 exits)", "",
           f"All trades: {s_all}", "", f"Walk-away (stop after first winner): {s_walk}", "",
           "By root: " + "; ".join(f"{r}: {v}" for r, v in by_root.items()), "",
           f"Null (labels time-shifted, 20 runs): 95th percentile total ${q95:,.0f}; real total ${s_all['total']:,.0f} → "
           f"**{'beats' if s_all['total'] > q95 else 'does NOT beat'} the null**.", "",
           "## B2. Every instrument × selectivity × walk-away (model out-of-fold, leave-one-day-out) vs no-model baselines", "",
           "Instruments: options (calls/puts), calls only, puts only, shares long/short, shares long only, straddles (buy when a big move is predicted, sell when quiet). "
           "Selectivity: every 30-min slot, ≥60% confident, ≥70% confident. Walk-away = stop after the first winning trade of the day.", "",
           M.sort_values("total", ascending=False).to_markdown(index=False), "",
           "## C. Variable importance (permutation, last 2 days held out)", "",
           imp.assign(mean=imp.mean(axis=1)).sort_values("mean", ascending=False).head(20).round(4).to_markdown() if len(imp) else "n/a", "",
           "Gaps: no event calendar (Fed/CPI/OPEX), no true volume-weighted VWAP (feed has option volume, not SPY share volume)."]
    open("reports/ROUND62.md", "w").write("\n".join(out) + "\n"); print("\n".join(out))


if __name__ == "__main__":
    {"build": build, "smoke": smoke, "report": report}[sys.argv[1]]()

"""Round 61 (PROTOCOL_ROUND61.md): indicator-setup 0DTE scalps on recorded quotes. `smoke` | `report`."""
import glob, math, os, sys
from datetime import time as dtime
import numpy as np, pandas as pd
from statistics import NormalDist
from edge import odte_score as O

TRIG = ["R1", "R2", "V1", "E1", "M1", "B1", "B2"]
EXITS = {"X1": (1.25, 0.85, 10), "X2": (1.50, 0.75, 30), "X3": (None, None, 9999)}
N = NormalDist()


def indicators(sp):
    f = pd.DataFrame({"px": sp})
    dl = sp.diff(); up = dl.clip(lower=0).ewm(alpha=1 / 14).mean(); dn = (-dl.clip(upper=0)).ewm(alpha=1 / 14).mean()
    f["rsi"] = 100 - 100 / (1 + up / dn.replace(0, np.nan))
    f["mean"] = sp.expanding().mean()
    f["e9"], f["e21"] = sp.ewm(span=9).mean(), sp.ewm(span=21).mean()
    macd = sp.ewm(span=12).mean() - sp.ewm(span=26).mean(); f["mh"] = macd - macd.ewm(span=9).mean()
    m, s = sp.rolling(20).mean(), sp.rolling(20).std(); f["bl"], f["bu"] = m - 2 * s, m + 2 * s
    return f


def signal(trig, f, i):
    """+1 call, -1 put, 0 none, using rows i-1 and i only (known at snapshot i)."""
    a, b = f.iloc[i - 1], f.iloc[i]
    if trig == "R1": return 1 if b.rsi < 30 else (-1 if b.rsi > 70 else 0)
    if trig == "R2": return -1 if (a.rsi >= 40 > b.rsi) else (1 if (a.rsi <= 60 < b.rsi) else 0)
    if trig == "V1": return 1 if (a.px <= a["mean"] and b.px > b["mean"]) else (-1 if (a.px >= a["mean"] and b.px < b["mean"]) else 0)
    if trig == "E1": return 1 if (a.e9 <= a.e21 and b.e9 > b.e21) else (-1 if (a.e9 >= a.e21 and b.e9 < b.e21) else 0)
    if trig == "M1": return 1 if (a.mh <= 0 < b.mh) else (-1 if (a.mh >= 0 > b.mh) else 0)
    if trig == "B1": return 1 if b.px <= b.bl else (-1 if b.px >= b.bu else 0)
    if trig == "B2": return -1 if (a.px >= a.bl and b.px < b.bl) else (1 if (a.px <= a.bu and b.px > b.bu) else 0)
    return 0


def run_day(ss, spot, root, day, trig, ex):
    tp, sl, hold = EXITS[ex]; fee = O.SPEC[root]["fee"]; mult = O.SPEC[root]["mult"]
    sp = spot.sort_index(); sp = sp[sp.index.time >= dtime(9, 30)]
    f = indicators(sp); snaps = {t: g for t, g in ss}
    out, pos = [], None
    for i in range(1, len(f)):
        t = f.index[i]; g = snaps.get(t)
        if g is None: continue
        if pos:
            cp, K, paid, t0 = pos; bid = O.q(g, cp, K, "bid")
            hit = bid == bid and tp is not None and (bid >= tp * paid or bid <= sl * paid)
            if hit or (t - t0) >= pd.Timedelta(minutes=hold) or t.time() >= dtime(15, 45):
                bid = bid if bid == bid else 0.0
                out.append(dict(day=day, root=root, trig=trig, exit=ex, t_in=t0, cost=paid * mult, pnl=(bid - paid) * mult - 2 * fee)); pos = None
            continue
        if not (dtime(9, 45) <= t.time() < dtime(15, 30)): continue
        s = signal(trig, f, i)
        if s:
            cp = "C" if s > 0 else "P"; px = f.px.iloc[i]
            try: K = float(min(g.xs(cp, level="cp").index, key=lambda x: abs(x - px)))
            except KeyError: continue
            a = O.q(g, cp, K, "ask")
            if a == a and a > 0: pos = (cp, K, a, t)
    return out


def all_trades(days_iter):
    rows = []
    for day, root, ss, spot in days_iter:
        for trig in TRIG:
            for ex in EXITS:
                rows += run_day(ss, spot, root, day, trig, ex)
    return pd.DataFrame(rows, columns=["day", "root", "trig", "exit", "t_in", "cost", "pnl"])


def real_days():
    for day in sorted(os.path.basename(p) for p in glob.glob(os.path.join(O.DATA, "2*"))):
        if pd.Timestamp(day).weekday() >= 5: continue
        for root in O.SPEC:
            d = O.load_day(day, root)
            if d.empty or d["t"].nunique() < O.MIN_SNAPS: continue
            yield day, root, O.snaps(d), d.groupby("t")["spot"].first()


def walk_away(T, rule):
    """Apply a daily walk-away overlay to each (root, trig, exit, day) trade sequence, in entry order.
    W0 = take every signal; W1 = stop after the first winner; W2 = stop at day P&L >= +1x or <= -1x the day's first-trade cost; W3 = first trade only."""
    keep = []
    for _, x in T.sort_values("t_in").groupby(["root", "trig", "exit", "day"], sort=False):
        run = 0.0; unit = x.cost.iloc[0]
        for i, r in enumerate(x.itertuples()):
            keep.append(r.Index); run += r.pnl
            if rule == "W1" and r.pnl > 0: break
            if rule == "W2" and (run >= unit or run <= -unit): break
            if rule == "W3": break
    return T.loc[keep]


def score(T):
    days = sorted(T.day.unique()); half = days[len(days) // 2] if len(days) > 1 else None
    rows = []
    for (root, trig, ex), x in T.groupby(["root", "trig", "exit"]):
        dd = x.groupby("day").pnl.sum(); dev = dd[dd.index < half] if half else dd; ho = dd[dd.index >= half] if half else dd
        t = ho.mean() / ho.std() * math.sqrt(len(ho)) if len(ho) > 2 and ho.std() > 0 else np.nan
        rows.append(dict(root=root, trig=trig, exit=ex, trades=len(x), win=(x.pnl > 0).mean(), total=x.pnl.sum(), per_trade=x.pnl.mean(),
                         dev_total=dev.sum(), ho_total=ho.sum(), ho_t=t,
                         PASS=bool(len(days) >= 20 and ho.mean() > 0 and t >= 3 and dev.mean() > 0 and dev.sum() > 0 and ho.sum() > 0)))
    return pd.DataFrame(rows).sort_values("total", ascending=False), len(days)


def synthetic(planted, ndays=12, seed=3):
    """Days of 1-minute spot + BS-priced ATM-ish option quotes (2c spread)."""
    rng = np.random.default_rng(seed); out = []
    for k in range(ndays):
        day = (pd.Timestamp("2026-01-05") + pd.Timedelta(days=k)).strftime("%Y-%m-%d")
        idx = pd.date_range(f"{day} 09:30", periods=390, freq="min", tz=O.ET); sig = 0.15 / math.sqrt(252 * 390)
        px = [500.0]; r = []
        for i in range(1, 390):
            drift = 0.0
            if planted and len(px) > 15:
                s = pd.Series(px[-15:]); dl = s.diff(); u = dl.clip(lower=0).mean(); d_ = (-dl.clip(upper=0)).mean()
                rsi = 100 - 100 / (1 + u / d_) if d_ > 0 else 100
                if rsi < 30: drift = 6 * sig
                elif rsi > 70: drift = -6 * sig
            px.append(px[-1] * math.exp(drift + rng.normal(0, sig)))
        sp = pd.Series(px, index=idx); snaps = []
        for i, t in enumerate(idx):
            T = max((389 - i) / (252 * 390), 1e-6); S = sp.iloc[i]; rows = []
            for K in np.arange(round(S) - 3, round(S) + 4):
                d1 = (math.log(S / K) + 0.5 * 0.15 ** 2 * T) / (0.15 * math.sqrt(T)); d2 = d1 - 0.15 * math.sqrt(T)
                c = S * N.cdf(d1) - K * N.cdf(d2); p = c - S + K
                for cp, v in (("C", c), ("P", p)):
                    rows.append(dict(cp=cp, K=float(K), bid=max(round(v - 0.01, 2), 0.0), ask=round(v + 0.01, 2)))
            snaps.append((t, pd.DataFrame(rows).set_index(["cp", "K"])))
        out.append((day, "SPY", snaps, sp))
    return out


def smoke():
    for planted in (False, True):
        R, n = score(all_trades(synthetic(planted)))
        r1 = R[R.trig == "R1"].total.mean(); other = R[R.trig != "R1"].total.mean()
        print("planted" if planted else "null", "R1 mean total", round(r1, 1), "others", round(other, 1))
        if planted: assert r1 > 0 and r1 > other, "planted R1 edge not detected"
        else: assert R.total.max() < abs(R.total.min()) * 2, "null looks too profitable"
    print("smoke OK")


def report():
    T = all_trades(real_days()); R, n = score(T)
    W = []
    for rule in ["W0", "W1", "W2", "W3"]:
        X = T if rule == "W0" else walk_away(T, rule)
        for (root, trig, ex), x in X.groupby(["root", "trig", "exit"]):
            dd = x.groupby("day").pnl.sum()
            W.append(dict(rule=rule, root=root, trig=trig, exit=ex, trades=len(x), total=round(x.pnl.sum(), 0), green_days=f"{(dd > 0).sum()}/{len(dd)}"))
    WD = pd.DataFrame(W)
    piv = WD.pivot_table(index=["root", "trig", "exit"], columns="rule", values="total").reset_index()
    gd = WD.pivot_table(index=["root", "trig", "exit"], columns="rule", values="green_days", aggfunc="first").reset_index()
    piv = piv.merge(gd, on=["root", "trig", "exit"], suffixes=("", "_green"))
    out = ["# Round 61: indicator setups as 0DTE scalps on real recorded quotes", "", "Rules: [PROTOCOL_ROUND61.md](../PROTOCOL_ROUND61.md). 1 contract, ask in / bid out, fees.",
           f"Recorded days: **{n}** ({'INTERIM: pass test needs 20 days' if n < 20 else 'scored'}). Trades: {len(T):,}. Configurations with any trade: {len(R)}.", "",
           f"Profitable configurations: {int((R.total > 0).sum())} of {len(R)}. Passing: **{int(R.PASS.sum())}**.", "",
           R.round(2).to_markdown(index=False), "",
           "## Walk-away overlays (total $; green days / days)", "",
           "W0 = every signal; W1 = stop after the first winner; W2 = stop at day ±1× first-trade cost; W3 = first signal only.", "",
           piv.sort_values("W1", ascending=False).to_markdown(index=False)]
    open("reports/ROUND61.md", "w").write("\n".join(out) + "\n"); print("\n".join(out[:8]))


if __name__ == "__main__":
    {"smoke": smoke, "report": report}[sys.argv[1]]()

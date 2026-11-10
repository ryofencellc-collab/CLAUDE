"""Round 39b scorer (PROTOCOL_ROUND39.md): paper-trade the pre-registered 0DTE strategies on collected Cboe snapshots.

Fills: sell at bid, buy at ask, from the same snapshot. Commissions per contract per leg: SPY $0.65, SPX $1.50.
Settlement: the official close (Yahoo ^GSPC / SPY) when available, else the last snapshot's spot.
"""
from __future__ import annotations
import glob, os
from datetime import time as dtime
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "odte")
LEDGER = os.path.join(ROOT, "paper", "r39b_trades.csv")
REPORT = os.path.join(ROOT, "reports", "ROUND39B.md")
ET = ZoneInfo("America/New_York")
ENTRIES = [dtime(10, 0), dtime(11, 30), dtime(13, 0), dtime(14, 30)]
EXIT_LATE = dtime(15, 45)
SPEC = {"SPXW": dict(file="SPX", mult=100, fee=1.50, wing=25.0, yahoo="^GSPC"),
        "SPY": dict(file="SPY", mult=100, fee=0.65, wing=2.5, yahoo="SPY")}
MIN_SNAPS = int(0.6 * 390)


def load_day(day: str, root: str) -> pd.DataFrame:
    fs = glob.glob(os.path.join(DATA, day, f"{SPEC[root]['file']}_*.csv.gz"))
    if not fs:
        return pd.DataFrame()
    d = pd.concat((pd.read_csv(f) for f in fs), ignore_index=True)
    d = d[(d["root"] == root) & (d["exp"] == day)].copy()
    d["t"] = pd.to_datetime(d["ts_feed"]).dt.tz_localize("UTC").dt.tz_convert(ET)
    d = d[(d["t"].dt.date.astype(str) == day) & (d["t"].dt.time >= dtime(9, 0)) & (d["t"].dt.time <= dtime(16, 30))]
    return d.drop_duplicates(["ts_feed", "cp", "K"]).sort_values(["t", "cp", "K"])


def snaps(d: pd.DataFrame) -> list[tuple[pd.Timestamp, pd.DataFrame]]:
    return [(t, g.set_index(["cp", "K"])) for t, g in d.groupby("t", sort=True)]


def first_at(ss, tm):
    for t, g in ss:
        if t.time() >= tm:
            return t, g
    return None, None


def q(g, cp, K, side):
    try:
        v = float(g.loc[(cp, K), side])
    except KeyError:
        return np.nan
    return v if v > 0 else np.nan


def by_delta(g, cp, target):
    x = g.xs(cp, level="cp")
    x = x[(x["bid"] > 0) & (x["ask"] > 0)]
    if x.empty:
        return None
    return float((x["delta"].abs() - target).abs().idxmin())


def wing(g, cp, K, w):
    ks = np.array(sorted(g.xs(cp, level="cp").index))
    c = ks[ks <= K - w + 1e-9] if cp == "P" else ks[ks >= K + w - 1e-9]
    if not len(c):
        return None
    return float(c.max() if cp == "P" else c.min())


def spread_value(S, legs):
    """Expiry value of legs [(cp, K, +1 long / -1 short)] at settlement S, per 1 unit."""
    return sum(sgn * (max(K - S, 0) if cp == "P" else max(S - K, 0)) for cp, K, sgn in legs)


def close_cost(g, legs):
    """Cost to close now (buy back shorts at ask, sell longs at bid)."""
    v = 0.0
    for cp, K, sgn in legs:
        px = q(g, cp, K, "ask" if sgn < 0 else "bid")
        if np.isnan(px):
            return np.nan
        v += -sgn * px
    return v


def credit_of(g, legs):
    v = 0.0
    for cp, K, sgn in legs:
        px = q(g, cp, K, "bid" if sgn < 0 else "ask")
        if np.isnan(px):
            return np.nan
        v += -sgn * px
    return v


def credit_trade(name, root, day, entry, ss, legs_fn, S, stop=None):
    t0, g0 = first_at(ss, entry)
    if g0 is None:
        return None
    legs = legs_fn(g0)
    if not legs:
        return None
    cr = credit_of(g0, legs)
    if np.isnan(cr) or cr <= 0:
        return None
    sp = SPEC[root]
    exit_val, how = None, "expiry"
    if stop:
        for t, g in ss:
            if t <= t0:
                continue
            c = close_cost(g, legs)
            if not np.isnan(c) and c >= stop * cr:
                exit_val, how = c, f"stop {t:%H:%M}"
                break
    if exit_val is None:
        exit_val = -spread_value(S, legs)       # what the position costs us at expiry
    pnl = (cr - exit_val) * sp["mult"] - len(legs) * sp["fee"] * (1 if how == "expiry" else 2)
    return dict(day=day, strategy=name, root=root, entry=entry.strftime("%H:%M"), legs=str(legs), credit=round(cr, 3),
                exit=how, pnl=round(pnl, 2))


def condor(delta, w):
    def f(g):
        kp, kc = by_delta(g, "P", delta), by_delta(g, "C", delta)
        if kp is None or kc is None:
            return None
        lp, lc = wing(g, "P", kp, w), wing(g, "C", kc, w)
        if lp is None or lc is None:
            return None
        return [("P", kp, -1), ("P", lp, 1), ("C", kc, -1), ("C", lc, 1)]
    return f


def vertical(cp, delta, w):
    def f(g):
        k = by_delta(g, cp, delta)
        if k is None:
            return None
        l = wing(g, cp, k, w)
        return None if l is None else [(cp, k, -1), (cp, l, 1)]
    return f


def debit_exit(ss, t0, legs, root, S, target=None, floor=None, paid=None):
    """Sell a long position: first snapshot after t0 hitting target/floor (on bid), else 15:45 ET bid, else expiry."""
    for t, g in ss:
        if t <= t0:
            continue
        v = -close_cost(g, legs) if legs else np.nan   # value we can sell for now (bid of longs)
        if np.isnan(v):
            continue
        if target is not None and paid and (v >= target * paid or v <= floor * paid):
            return v, f"{'target' if v >= target * paid else 'floor'} {t:%H:%M}"
        if t.time() >= EXIT_LATE:
            return v, f"15:45 {t:%H:%M}"
    return spread_value(S, legs), "expiry"


def day_trades(day: str, root: str, S: float) -> list[dict]:
    d = load_day(day, root)
    if d.empty or d["t"].nunique() < MIN_SNAPS:
        return []
    ss = snaps(d)
    spot = d.groupby("t")["spot"].first()
    w, sp = SPEC[root]["wing"], SPEC[root]
    out = []
    t945, _ = first_at(ss, dtime(9, 45))
    for e in ENTRIES:
        for name, fn, stop in (("I1 condor 10d", condor(0.10, w), None), ("I2 condor 10d stop 2x", condor(0.10, w), 2.0),
                               ("I3 condor 20d", condor(0.20, w), None)):
            r = credit_trade(name, root, day, e, ss, fn, S, stop)
            if r: out.append(r)
        te, _ = first_at(ss, e)
        if te is not None and t945 is not None:
            up = spot[te] > spot[t945]
            r = credit_trade("T1 trend spread 15d", root, day, e, ss, vertical("P" if up else "C", 0.15, w), S)
            if r: out.append(r)
        # L1 long straddle at the money
        te, g = first_at(ss, e)
        if g is not None:
            k = float(min(g.xs("C", level="cp").index, key=lambda x: abs(x - spot[te])))
            legs = [("C", k, 1), ("P", k, 1)]
            paid = -credit_of(g, legs)
            if not np.isnan(paid) and paid > 0:
                v, how = debit_exit(ss, te, legs, root, S)
                out.append(dict(day=day, strategy="L1 long straddle", root=root, entry=e.strftime("%H:%M"), legs=str(legs),
                                credit=round(-paid, 3), exit=how, pnl=round((v - paid) * sp["mult"] - 2 * sp["fee"] * 2, 2)))
    # B1 opening-range breakout, one per day
    orng = spot[(spot.index.time >= dtime(9, 30)) & (spot.index.time < dtime(10, 0))]
    if len(orng) >= 10:
        hi, lo = orng.max(), orng.min()
        for t, g in ss:
            if t.time() < dtime(10, 0) or t.time() >= EXIT_LATE:
                continue
            s = spot[t]
            if s > hi or s < lo:
                cp = "C" if s > hi else "P"
                k = float(min(g.xs(cp, level="cp").index, key=lambda x: abs(x - s)))
                paid = q(g, cp, k, "ask")
                if np.isnan(paid):
                    break
                v, how = debit_exit(ss, t, [(cp, k, 1)], root, S, target=2.0, floor=0.5, paid=paid)
                out.append(dict(day=day, strategy="B1 OR breakout", root=root, entry=t.strftime("%H:%M"), legs=str([(cp, k, 1)]),
                                credit=round(-paid, 3), exit=how, pnl=round((v - paid) * sp["mult"] - 2 * sp["fee"], 2)))
                break
    return out


def settle_price(day: str, root: str, fallback: float) -> tuple[float, str]:
    try:
        import yfinance as yf
        x = yf.download(SPEC[root]["yahoo"], start=day, end=str(pd.Timestamp(day) + pd.Timedelta(days=1))[:10],
                        auto_adjust=False, progress=False)
        if len(x):
            c = x["Close"]
            return float(c.iloc[-1, 0] if getattr(c, "ndim", 1) == 2 else c.iloc[-1]), "official close"
    except Exception:
        pass
    return fallback, "last snapshot"


def lower90(x, n=4000, seed=0):
    x = np.asarray(x, float)
    if len(x) < 3:
        return np.nan
    rng = np.random.default_rng(seed)
    return float(np.quantile(rng.choice(x, (n, len(x))).mean(1), 0.05))


def main():
    days = sorted(os.path.basename(p) for p in glob.glob(os.path.join(DATA, "2*")))
    rows, notes = [], []
    for day in days:
        if pd.Timestamp(day).weekday() >= 5:
            continue
        for root in SPEC:
            d = load_day(day, root)
            if d.empty:
                continue
            n = d["t"].nunique()
            S, src = settle_price(day, root, float(d.sort_values("t")["spot"].iloc[-1]))
            tr = day_trades(day, root, S)
            notes.append(f"{day} {root}: {n} snapshots{' (excluded, < 60%)' if n < MIN_SNAPS else ''}, settle {S:.2f} ({src}), {len(tr)} trades")
            rows += tr
    T = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    T.to_csv(LEDGER, index=False)
    out = ["# Round 39b: 0DTE paper strategies on collected Cboe quotes", "",
           "Rules: [PROTOCOL_ROUND39.md](../PROTOCOL_ROUND39.md). Fills at bid/ask of the same snapshot; per-leg commissions; "
           "first score at 20 trading days, again at 40. P&L per 1 lot.", "", *[f"- {n}" for n in notes], ""]
    if T.empty:
        open(REPORT, "w").write("\n".join(out + ["No trades yet."]) + "\n"); print("\n".join(out)); return
    ndays = T["day"].nunique()
    g = []
    for (s, r), x in T.assign(entry=np.where(T.strategy.str.startswith("B1"), "-", T.entry)).groupby(["strategy", "root"]):
        for e, y in x.groupby("entry"):
            days_ = sorted(y["day"].unique()); half = days_[len(days_) // 2] if len(days_) > 1 else None
            g.append(dict(strategy=s, root=r, entry=e, trades=len(y), win=f"{(y.pnl > 0).mean():.0%}", mean=round(y.pnl.mean(), 2),
                          low90=round(lower90(y.pnl), 2), worst=round(y.pnl.min(), 2), total=round(y.pnl.sum(), 2),
                          h1=round(y[y.day < half].pnl.sum(), 2) if half else np.nan, h2=round(y[y.day >= half].pnl.sum(), 2) if half else np.nan))
    G = pd.DataFrame(g)
    out += [f"Trading days scored: **{ndays}** (verdict at 20).", "", G.to_markdown(index=False), "",
            "Pass (at ≥ 20 days): mean > 0 with 90% bootstrap lower bound > 0, both halves > 0, worst day ≥ −3× the mean credit/debit.", "",
            "## Daily P&L by strategy (all entries and both roots)", "",
            T.pivot_table(index="day", columns="strategy", values="pnl", aggfunc="sum").round(0).to_markdown()]
    open(REPORT, "w").write("\n".join(out) + "\n"); print("\n".join(out))


if __name__ == "__main__":
    main()

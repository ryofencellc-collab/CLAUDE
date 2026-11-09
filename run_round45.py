"""Round 45 (PROTOCOL_ROUND45.md): maker returns on Kalshi by category x price x time-to-close, event-clustered."""
import os, time
import numpy as np, pandas as pd
from edge import weather as wx
from edge import round20 as r20
from edge import round27 as r27

A, B, SPLIT = pd.Timestamp("2025-11-01", tz="UTC"), pd.Timestamp("2026-11-01", tz="UTC"), pd.Timestamp("2026-07-01", tz="UTC")
PER_SERIES, BUDGET = 80, float(os.environ.get("R45_BUDGET_MIN", "290")) * 60
OUT = "data/r45"; os.makedirs(OUT, exist_ok=True)
PB = [0.0, 0.05, 0.15, 0.30, 0.50, 0.70, 0.85, 0.95, 1.0]
PL = [".01-.05", ".05-.15", ".15-.30", ".30-.50", ".50-.70", ".70-.85", ".85-.95", ".95-.99"]
TB = [0, 1, 24, 168, 1e9]; TL = ["<1h", "1-24h", "1-7d", ">7d"]


def fnum(x, d=np.nan):
    try: return float(x)
    except (TypeError, ValueError): return d


def collect():
    path = f"{OUT}/trades.pkl"
    if os.path.exists(path): return pd.read_pickle(path)
    ser = r27.series_list(); print("series", len(ser), flush=True)
    meta = {s["ticker"]: (s.get("category") or "?", "maker" in str(s.get("fee_type") or "")) for s in ser}
    rng = np.random.default_rng(45); pairs = []
    t0 = time.time()
    for s in rng.permutation(list(meta)):
        if time.time() - t0 > BUDGET * 0.25: break
        ms = r20.markets(s, A, B)
        if ms:
            pick = rng.choice(len(ms), size=min(PER_SERIES, len(ms)), replace=False)
            pairs += [(s, ms[i]) for i in pick]
    print("market pairs", len(pairs), "listing took", round(time.time() - t0), "s", flush=True)
    rng.shuffle(pairs)
    cut = r27.cutoff(); rows = []
    for k, (s, m) in enumerate(pairs):
        if time.time() - t0 > BUDGET: break
        close = pd.to_datetime(m.get("close_time"), utc=True)
        for t in r27.trades(m["ticker"], close, cut, max_pages=5):
            side = t.get("taker_side")
            if side not in ("yes", "no"): continue
            px = fnum(t.get("yes_price_dollars"), fnum(t.get("yes_price"), np.nan) / 100)
            if not 0 < px < 1: continue
            rows.append((s, m.get("event_ticker") or m["ticker"].rsplit("-", 1)[0], m["ticker"], m["result"], close,
                         pd.Timestamp(t["created_time"]), side, px, fnum(t.get("count_fp") or t.get("count"), 0)))
        if k % 500 == 0:
            print(f"  {k}/{len(pairs)} markets, {len(rows)} trades, {time.time() - t0:.0f}s", flush=True)
        if k % 5000 == 4999:
            frame(rows, meta).to_pickle(path)        # checkpoint: a crash later never loses the download
    d = frame(rows, meta)
    d.to_pickle(path); return d


def frame(rows, meta):
    d = pd.DataFrame(rows, columns=["series", "event", "ticker", "result", "close", "ts", "taker", "p", "n"])
    d["category"] = d.series.map(lambda s: meta.get(s, ("?", False))[0])
    d["maker_fee"] = d.series.map(lambda s: meta.get(s, ("?", False))[1])
    return d


def prep(d):
    d = d[d.n > 0].copy()
    d["mside"] = np.where(d.taker == "yes", "no", "yes")
    d["x"] = np.where(d.mside == "yes", d.p, 1 - d.p)
    fee = np.where(d.maker_fee, 0.0175 * d.x * (1 - d.x), 0.0)
    d["pnl"] = d.n * ((d.result == d.mside).astype(float) - d.x - fee)
    d["risk"] = d.n * d.x
    d["hrs"] = (d.close - d.ts).dt.total_seconds() / 3600
    d["pb"] = pd.cut(d.x, PB, labels=PL); d["tb"] = pd.cut(d.hrs, TB, labels=TL, right=False)
    d["dev"] = d.close < SPLIT
    return d


def clustered(x):
    e = x.groupby("event")[["pnl", "risk"]].sum()
    if len(e) < 2 or e.risk.sum() <= 0: return dict(events=len(e), ret=np.nan, t=np.nan)
    ret = e.pnl.sum() / e.risk.sum()
    # ratio estimator SE via event-level residuals
    resid = e.pnl - ret * e.risk
    se = np.sqrt((resid ** 2).sum()) / e.risk.sum()
    return dict(events=len(e), ret=ret, t=ret / se if se > 0 else np.nan, contracts=round(x.n.sum()))


def main():
    d = prep(collect())
    out = ["# Round 45: where do Kalshi makers earn?", "",
           f"{d.ticker.nunique():,} markets, {d.event.nunique():,} events, {len(d):,} trades, {d.n.sum():,.0f} contracts, "
           f"{d.category.nunique()} categories. Dev closes < {SPLIT.date()}, holdout after.", ""]
    # calibration (sanity): realized YES frequency by YES trade price, contract-weighted
    cal = d.assign(yb=pd.cut(d.p, [0, .05, .1, .2, .3, .4, .5, .6, .7, .8, .9, .95, 1])).groupby("yb", observed=True).apply(
        lambda x: pd.Series({"avg_price": np.average(x.p, weights=x.n), "yes_rate": np.average(x.result == "yes", weights=x.n), "contracts": x.n.sum()}))
    out += ["## Calibration (all trades): price vs how often YES won", "", cal.round(3).to_markdown(), ""]
    allm = clustered(d); out += [f"All makers: return {allm['ret']:.2%} per dollar risked (t {allm['t']:.1f}).", ""]
    rows = []
    for (c, pb, tb), x in d.groupby(["category", "pb", "tb"], observed=True):
        dv, ho = clustered(x[x.dev]), clustered(x[~x.dev])
        rows.append(dict(category=c, maker_price=pb, time_left=tb, dev_events=dv["events"], dev_ret=dv["ret"], dev_t=dv["t"],
                         hold_events=ho["events"], hold_ret=ho["ret"], hold_t=ho["t"]))
    T = pd.DataFrame(rows)
    cand = T[(T.dev_events >= 100) & (T.dev_ret >= 0.03) & (T.dev_t >= 3)]
    T["pass"] = T.index.isin(cand.index) & (T.hold_events >= 30) & (T.hold_ret > 0) & (T.hold_t >= 2)
    f = lambda v: f"{v:.1%}" if pd.notna(v) else ""
    show = T.sort_values("dev_t", ascending=False).head(40).copy()
    for c in ("dev_ret", "hold_ret"): show[c] = show[c].map(f)
    out += [f"**Candidates on dev: {len(cand)}; pass on holdout: {int(T['pass'].sum())}** (of {len(T)} cells).", "",
            "## Top 40 cells by dev t-stat", "", show.round(2).to_markdown(index=False), ""]
    by = []
    for (c, pb), x in d.groupby(["category", "pb"], observed=True):
        a = clustered(x); by.append(dict(category=c, maker_price=pb, events=a["events"], ret=f(a["ret"]), t=round(a["t"], 1) if pd.notna(a["t"]) else ""))
    out += ["## Maker return by category × maker price (all periods)", "", pd.DataFrame(by).to_markdown(index=False)]
    open("reports/ROUND45.md", "w").write("\n".join(out) + "\n"); print("\n".join(out[:60]))


if __name__ == "__main__":
    main()

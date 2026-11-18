"""Round 57 (PROTOCOL_ROUND57.md): AAA gas nowcast vs Kalshi KXAAAGASD* markets. `collect` | `analyze` | `smoke`."""
import math, os, pickle, sys, time
import numpy as np, pandas as pd
from statistics import NormalDist
from edge import round27 as r27

PHI = NormalDist().cdf
OUT = "data/r57"; os.makedirs(OUT, exist_ok=True)
A, B = pd.Timestamp("2026-08-01", tz="UTC"), pd.Timestamp.now(tz="UTC")
SPLIT = pd.Timestamp("2026-10-20", tz="UTC")
VARIANTS = {"persist": 0, "mom3": 3, "mom7": 7}
EDGES = [0.05, 0.10, 0.15, 0.20]
ET = "America/New_York"


def fee(x):
    return math.ceil(0.07 * x * (1 - x) * 100 - 1e-9) / 100


def collect(budget_min=300):
    path = f"{OUT}/raw.pkl"
    if os.path.exists(path):
        return pickle.load(open(path, "rb"))
    ser = sorted(s["ticker"] for s in r27.series_list() if s["ticker"].startswith("KXAAAGASD"))
    print("series", len(ser), flush=True)
    cut = r27.cutoff(); mk, tr = [], {}; t0 = time.time()
    for s in ser:
        ms = r27.settled_markets(s, A, B, max_pages=20)
        for m in ms:
            mk.append(dict(series=s, ticker=m["ticker"], event=m["event_ticker"], K=float(m["floor_strike"]), close=m["close_time"],
                           value=float(str(m["expiration_value"]).replace(",", "")), result=m["result"], vol=float(m.get("volume_fp") or 0)))
        print(s, len(ms), round(time.time() - t0), flush=True)
    M = pd.DataFrame(mk)
    todo = M[M.vol > 0]
    print("markets", len(M), "with volume", len(todo), flush=True)
    for i, r in enumerate(todo.itertuples()):
        if time.time() - t0 > budget_min * 60:
            print("budget hit at", i, flush=True); break
        tr[r.ticker] = r27.trades(r.ticker, pd.Timestamp(r.close), cut, max_pages=5)
        if i % 500 == 0: print("trades", i, round(time.time() - t0), flush=True)
    pickle.dump((M, tr), open(path, "wb")); return M, tr


def build(M, tr):
    """One row per market: value history features, first ask-side trade per side after 12:00 ET on D-1."""
    M = M.copy(); M["close"] = pd.to_datetime(M.close, utc=True)
    M["day"] = M.close.dt.tz_convert(ET).dt.normalize().dt.tz_localize(None) + pd.Timedelta(days=1)   # the AAA date being predicted
    vals = M.groupby(["series", "day"]).value.first().reset_index().sort_values(["series", "day"])
    rows = []
    for s, g in vals.groupby("series"):
        g = g.set_index("day").value
        g = g[~g.index.duplicated()]
        full = g.reindex(pd.date_range(g.index.min(), g.index.max())).copy()       # gaps stay NaN
        d = full.diff()
        for day in g.index:
            prev = full.get(day - pd.Timedelta(days=1), np.nan)
            hist = d[d.index < day].dropna()
            hist = hist[hist.index >= day - pd.Timedelta(days=14)]
            row = dict(series=s, day=day, V=prev, sig=max(hist.tail(10).std(), 0.002) if len(hist.tail(10)) >= 5 else np.nan)
            for v, n in VARIANTS.items():
                row[f"mu_{v}"] = hist.tail(n).mean() if n and len(hist.tail(n)) == n else (0.0 if n == 0 else np.nan)
            rows.append(row)
    F = pd.DataFrame(rows)
    M = M.merge(F, on=["series", "day"], how="left")
    ya, na, cap_y, cap_n = [], [], [], []
    for r in M.itertuples():
        t = tr.get(r.ticker) or []
        start = (r.day - pd.Timedelta(days=1) + pd.Timedelta(hours=12)).tz_localize(ET).tz_convert("UTC")
        ts = sorted(t, key=lambda x: x["created_time"])
        y = next((x for x in ts if pd.Timestamp(x["created_time"]) >= start and x.get("taker_side") == "yes"), None)
        n = next((x for x in ts if pd.Timestamp(x["created_time"]) >= start and x.get("taker_side") == "no"), None)
        ya.append(float(y["yes_price_dollars"]) if y else np.nan); na.append(float(n["no_price_dollars"]) if n else np.nan)
        cap_y.append(float(y.get("count_fp") or 0) if y else 0.0); cap_n.append(float(n.get("count_fp") or 0) if n else 0.0)
    M["yes_ask"], M["no_ask"], M["cap_y"], M["cap_n"] = ya, na, cap_y, cap_n
    M["y"] = (M.result == "yes").astype(float)
    return M


def trades_for(M, variant, e):
    p = 1 - pd.Series([PHI(z) for z in ((M.K - M.V - M[f"mu_{variant}"]) / M.sig)], index=M.index)
    out = []
    for i, r in M.assign(p=p).dropna(subset=["p"]).iterrows():
        if r.yes_ask == r.yes_ask and 0.01 <= r.yes_ask <= 0.99 and r.p - r.yes_ask >= e:
            out.append(dict(day=r.day, series=r.series, side="yes", px=r.yes_ask, p=r.p, pnl=r.y - r.yes_ask - fee(r.yes_ask), cap=r.cap_y))
        elif r.no_ask == r.no_ask and 0.01 <= r.no_ask <= 0.99 and (1 - r.p) - r.no_ask >= e:
            out.append(dict(day=r.day, series=r.series, side="no", px=r.no_ask, p=1 - r.p, pnl=(1 - r.y) - r.no_ask - fee(r.no_ask), cap=r.cap_n))
    return pd.DataFrame(out, columns=["day", "series", "side", "px", "p", "pnl", "cap"])


def clustered_t(T):
    if len(T) < 5: return np.nan
    g = T.groupby("day").pnl.sum(); n = len(g)
    return g.mean() / g.std() * math.sqrt(n) if n > 2 and g.std() > 0 else np.nan


def brier(M, variant):
    x = M.dropna(subset=["V", "sig", f"mu_{variant}"]).copy()
    x["p"] = 1 - pd.Series([PHI(z) for z in ((x.K - x.V - x[f"mu_{variant}"]) / x.sig)], index=x.index)
    x["mkt"] = np.where(x.yes_ask == x.yes_ask, x.yes_ask, 1 - x.no_ask)
    x = x.dropna(subset=["mkt"])
    return ((x.p - x.y) ** 2).mean(), ((x.mkt - x.y) ** 2).mean(), len(x)


def analyze(M, label="real"):
    dev = M[M.day < SPLIT.tz_localize(None)]; ho = M[M.day >= SPLIT.tz_localize(None)]
    grid = []
    for v in VARIANTS:
        for e in EDGES:
            T = trades_for(dev, v, e)
            grid.append(dict(variant=v, edge=e, dev_trades=len(T), dev_mean=T.pnl.mean() if len(T) else np.nan, dev_t=clustered_t(T)))
    G = pd.DataFrame(grid); ok = G[G.dev_trades >= 30]
    if ok.empty:
        return dict(label=label, verdict="FAIL (no dev config with 30 trades)", grid=G)
    best = ok.sort_values("dev_mean", ascending=False).iloc[0]
    H = trades_for(ho, best.variant, best.edge)
    bm, bk, nb = brier(ho, best.variant)
    t = clustered_t(H); mean = H.pnl.mean() if len(H) else np.nan
    passed = len(H) >= 100 and mean > 0 and t >= 2.5 and bm < bk
    return dict(label=label, verdict="PASS" if passed else "FAIL", choice=f"{best.variant}, edge {best.edge}", grid=G, H=H,
                ho_trades=len(H), ho_mean=mean, ho_t=t, brier_model=bm, brier_mkt=bk, brier_n=nb,
                cap=H.cap.sum() if len(H) else 0)


def synthetic(planted, seed=0):
    """Fake gas world: trending daily values, strikes around V, prices = true prob (null) or trend-blind prob (planted), plus noise."""
    rng = np.random.default_rng(seed); rows = []
    days = pd.date_range("2026-08-15", "2026-11-15")
    for s in [f"S{i}" for i in range(30)]:
        v, trend = 3.5 + rng.normal(0, .3), 0.0
        for day in days:
            trend = 0.85 * trend + rng.normal(0, 0.004)
            dv = trend + rng.normal(0, 0.003); vn = v + dv
            for K in np.round(v + np.arange(-0.02, 0.021, 0.01), 4):
                true_p = 1 - PHI((K - v - trend) / 0.003)
                blind_p = 1 - PHI((K - v) / 0.006)
                q = blind_p if planted else true_p
                q = float(np.clip(q + rng.normal(0, 0.03), 0.02, 0.98))
                rows.append(dict(series=s, ticker=f"{s}-{day.date()}-{K}", event=f"{s}-{day.date()}", K=K,
                                 close=(day - pd.Timedelta(days=1)).tz_localize(ET).tz_convert("UTC") + pd.Timedelta(hours=23, minutes=59),
                                 value=round(vn, 4), result="yes" if vn > K else "no", vol=1.0, q=q))
            v = vn
    M = pd.DataFrame(rows); tr = {}
    for r in M.itertuples():
        t = (r.close - pd.Timedelta(hours=6)).isoformat()
        tr[r.ticker] = [dict(created_time=t, taker_side="yes", yes_price_dollars=str(round(min(r.q + 0.01, 0.99), 2)), count_fp="10"),
                        dict(created_time=t, taker_side="no", no_price_dollars=str(round(min(1 - r.q + 0.01, 0.99), 2)), count_fp="10")]
    return M.drop(columns="q"), tr


def report(res, M):
    out = ["# Round 57: AAA gas nowcast vs Kalshi daily gas markets", "", "Rules: [PROTOCOL_ROUND57.md](../PROTOCOL_ROUND57.md).", "",
           f"Markets: {len(M):,} settled ({M.series.nunique()} series, {M.day.min().date()} → {M.day.max().date()}); "
           f"with an ask-side trade after 12:00 ET: YES {M.yes_ask.notna().sum():,}, NO {M.no_ask.notna().sum():,}.", "",
           f"**Verdict: {res['verdict']}.**"]
    if "H" in res:
        out += [f"Dev choice: {res['choice']}. Holdout: {res['ho_trades']} trades, mean P&L {res['ho_mean']:+.3f} $/contract, day-clustered t {res['ho_t']:.2f}. "
                f"Brier: model {res['brier_model']:.4f} vs market {res['brier_mkt']:.4f} on {res['brier_n']} markets. "
                f"Contracts available at the trade prices: {res['cap']:,.0f}.", ""]
    out += ["## Dev grid", "", res["grid"].round(4).to_markdown(index=False), ""]
    if "H" in res and len(res["H"]):
        H = res["H"]
        out += ["## Holdout by series (top 15 by trades)", "", H.groupby("series").pnl.agg(["count", "mean", "sum"]).sort_values("count", ascending=False).head(15).round(3).to_markdown(), "",
                "## Holdout by side", "", H.groupby("side").pnl.agg(["count", "mean", "sum"]).round(3).to_markdown()]
    open("reports/ROUND57.md", "w").write("\n".join(out) + "\n"); print("\n".join(out[:8]))


def smoke():
    for planted in (True, False):
        M = build(*synthetic(planted)); r = analyze(M, "planted" if planted else "null")
        print(r["label"], r["verdict"], r.get("choice"), r.get("ho_trades"), round(r.get("ho_mean", np.nan) or np.nan, 3), round(r.get("ho_t", np.nan) or np.nan, 2))
        assert (r["verdict"] == "PASS") == planted, f"calibration failed on {r['label']}"
    print("smoke OK")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "smoke": smoke()
    elif cmd == "collect": collect(float(os.environ.get("R57_BUDGET_MIN", "300")))
    else:
        M = build(*collect()); M.to_pickle(f"{OUT}/built.pkl"); report(analyze(M), M)

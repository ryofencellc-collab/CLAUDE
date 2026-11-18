"""Round 58 (PROTOCOL_ROUND58.md): mention markets vs each word's own settlement record. `smoke` | `collect` | `analyze`."""
import math, os, pickle, re, sys, time
import numpy as np, pandas as pd
from edge import round27 as r27
from edge import round20 as r20
from run_round57 import fee

OUT = "data/r58"; os.makedirs(OUT, exist_ok=True)
A, B = pd.Timestamp("2025-01-01", tz="UTC"), pd.Timestamp.now(tz="UTC")
SPLIT = pd.Timestamp("2026-07-01", tz="UTC")
EDGES, NMINS = [0.05, 0.10, 0.15, 0.20, 0.30], [3, 5]


def wkey(s):
    return re.sub(r"\s+", "", str(s or "").lower())


def first_asks(ts, open_t):
    ts = sorted(ts or [], key=lambda x: x["created_time"])
    start = pd.Timestamp(open_t) + pd.Timedelta(hours=1)
    y = next((x for x in ts if pd.Timestamp(x["created_time"]) >= start and x.get("taker_side") == "yes"), None)
    n = next((x for x in ts if pd.Timestamp(x["created_time"]) >= start and x.get("taker_side") == "no"), None)
    return (float(y["yes_price_dollars"]) if y else np.nan, float(n["no_price_dollars"]) if n else np.nan)


def collect(budget_min=300):
    """Amendment 3: list markets (capped), compute word history first, then fetch trades ONLY for markets with n >= 3 earlier
    settlements, keeping just the two first-ask prices per market (no raw trades in memory). Checkpoints every 300 markets."""
    path = f"{OUT}/raw.pkl"
    if os.path.exists(path): return pickle.load(open(path, "rb"))
    S = pd.read_csv("probe/mention/series.csv")
    ser = list(S[S.volume > 0].sort_values("volume", ascending=False).ticker)
    cut = r27.cutoff(); t0 = time.time(); mk = []
    for s in ser:
        if time.time() - t0 > 0.35 * budget_min * 60:
            print("listing budget hit; series done:", ser.index(s), flush=True); break
        for m in r20.markets(s, A, B):
            mk.append(dict(series=s, ticker=m["ticker"], event=m["event_ticker"], word=wkey(m.get("yes_sub_title")), open=m.get("open_time"),
                           close=m["close_time"], result=m["result"], vol=float(m.get("volume_fp") or 0)))
    M = pd.DataFrame(mk).drop_duplicates("ticker"); print("markets", len(M), "series", M.series.nunique(), round(time.time() - t0), flush=True)
    M = history(M)
    todo = M[(M.n >= 3) & (M.vol > 0)]
    print("eligible markets (n>=3, traded):", len(todo), flush=True)
    asks = {}
    ck = f"{OUT}/asks_ckpt.pkl"
    if os.path.exists(ck): asks = pickle.load(open(ck, "rb"))
    for i, r in enumerate(todo.itertuples()):
        if r.ticker in asks: continue
        if time.time() - t0 > budget_min * 60: print("trade budget hit", i, flush=True); break
        asks[r.ticker] = first_asks(r27.trades(r.ticker, pd.Timestamp(r.close), cut, max_pages=5), r.open)
        if i % 300 == 0:
            pickle.dump(asks, open(ck, "wb")); print("trades", i, round(time.time() - t0), flush=True)
    pickle.dump((M, asks), open(path, "wb")); return M, asks


def history(M):
    M = M.copy(); M["close"] = pd.to_datetime(M.close, utc=True, format="ISO8601"); M["open"] = pd.to_datetime(M.open, utc=True, format="ISO8601")
    M["y"] = (M.result == "yes").astype(float)
    M["ev_close"] = M.event.map(M.groupby("event").close.max())
    M = M.sort_values("ev_close")
    pri, nn, hist = [], [], {}
    for r in M.itertuples():
        h = [y for c, y in hist.get((r.series, r.word), []) if c < r.open + pd.Timedelta(hours=1)]   # amendment 4: known at decision time
        pri.append((sum(h) + 1) / (len(h) + 2)); nn.append(len(h))
        hist.setdefault((r.series, r.word), []).append((r.ev_close, r.y))
    M["prior"], M["n"] = pri, nn
    return M


def build(M, tr):
    """tr: {ticker: (yes_ask, no_ask)} from collect, or {ticker: [trades]} from the synthetic smoke world."""
    if "prior" not in M.columns:
        M = history(M)
    ya, na = [], []
    for r in M.itertuples():
        v = tr.get(r.ticker)
        if isinstance(v, tuple): a = v
        elif v: a = first_asks(v, r.open)
        else: a = (np.nan, np.nan)
        ya.append(a[0]); na.append(a[1])
    M["yes_ask"], M["no_ask"] = ya, na
    return M


def trades_for(M, e, nmin):
    x = M[M.n >= nmin]; out = []
    for r in x.itertuples():
        if r.yes_ask == r.yes_ask and 0.01 <= r.yes_ask <= 0.99 and r.prior - r.yes_ask >= e:
            out.append(dict(event=r.event, series=r.series, side="yes", px=r.yes_ask, p=r.prior, y=r.y, pnl=r.y - r.yes_ask - fee(r.yes_ask)))
        elif r.no_ask == r.no_ask and 0.01 <= r.no_ask <= 0.99 and (1 - r.prior) - r.no_ask >= e:
            out.append(dict(event=r.event, series=r.series, side="no", px=r.no_ask, p=1 - r.prior, y=1 - r.y, pnl=(1 - r.y) - r.no_ask - fee(r.no_ask)))
    return pd.DataFrame(out, columns=["event", "series", "side", "px", "p", "y", "pnl"])


def ct(T):
    if len(T) < 5: return np.nan
    g = T.groupby("event").pnl.sum(); return g.mean() / g.std() * math.sqrt(len(g)) if len(g) > 2 and g.std() > 0 else np.nan


def analyze(M, label="real"):
    elig = M[(M.n >= 3) & (M.yes_ask.notna() | M.no_ask.notna())]
    split = elig.ev_close.median() if len(elig) else SPLIT          # amendment 1: data-shape split, no P&L
    dev, ho = M[M.ev_close < split], M[M.ev_close >= split]
    G = pd.DataFrame([dict(edge=e, nmin=n, dev_trades=len(T), dev_mean=T.pnl.mean() if len(T) else np.nan, dev_t=ct(T))
                      for e in EDGES for n in NMINS for T in [trades_for(dev, e, n)]])
    ok = G[G.dev_trades >= 50]
    if ok.empty: return dict(label=label, verdict="FAIL (no dev config with 50 trades)", grid=G)
    b = ok.sort_values("dev_mean", ascending=False).iloc[0]
    H = trades_for(ho, b.edge, int(b.nmin))
    bm = ((H.p - H.y) ** 2).mean() if len(H) else np.nan; bk = ((H.px - H.y) ** 2).mean() if len(H) else np.nan
    mean, t = (H.pnl.mean() if len(H) else np.nan), ct(H)
    ok_ = len(H) >= 100 and mean > 0 and t >= 2.5 and bm < bk
    return dict(label=label, verdict="PASS" if ok_ else "FAIL", choice=f"edge {b.edge}, n_min {int(b.nmin)}, split {split.date()}", grid=G, H=H, n=len(H), mean=mean, t=t, bm=bm, bk=bk)


def synthetic(planted, seed=1):
    rng = np.random.default_rng(seed); rows, tr = [], {}
    words = {f"w{i}": rng.beta(0.7, 0.7) for i in range(40)}
    for s in ["SA", "SB", "SC"]:
        for k, day in enumerate(pd.date_range("2025-02-01", "2026-11-01", freq="7D")):
            ev = f"{s}-{k}"; close = day.tz_localize("UTC")
            for w, p in rng.permutation(list(words.items()))[:15]:
                p = float(p); y = rng.random() < p
                q = 0.5 + 0.5 * (p - 0.5) if planted else p
                q = float(np.clip(q + rng.normal(0, 0.04), 0.03, 0.97)); tk = f"{ev}-{w}"
                rows.append(dict(series=s, ticker=tk, event=ev, word=w, open=(close - pd.Timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S.%fZ") if k % 2 else (close - pd.Timedelta(days=2)).isoformat(), close=close.isoformat(),
                                 result="yes" if y else "no", vol=1.0))
                t = (close - pd.Timedelta(days=1)).isoformat()
                tr[tk] = [dict(created_time=t, taker_side="yes", yes_price_dollars=str(round(min(q + 0.01, 0.99), 2))),
                          dict(created_time=t, taker_side="no", no_price_dollars=str(round(min(1 - q + 0.01, 0.99), 2)))]
    return pd.DataFrame(rows), tr


def report(res, M):
    out = ["# Round 58: mention markets vs each word's settlement record", "", "Rules: [PROTOCOL_ROUND58.md](../PROTOCOL_ROUND58.md).", "",
           f"Markets: {len(M):,} settled in {M.series.nunique()} series ({M.close.min().date()} → {M.close.max().date()}); with ≥ 3 earlier settlements of the same word: {(M.n >= 3).sum():,}.", "",
           f"**Verdict: {res['verdict']}.**"]
    if "H" in res:
        out += [f"Dev choice: {res['choice']}. Holdout: {res['n']} trades, mean P&L {res['mean']:+.3f} $/contract, event-clustered t {res['t']:.2f}. "
                f"Brier on traded markets: prior {res['bm']:.3f} vs price {res['bk']:.3f}.", ""]
    out += ["## Dev grid", "", res["grid"].round(4).to_markdown(index=False), ""]
    if "H" in res and len(res["H"]):
        H = res["H"]
        out += ["## Holdout by side", "", H.groupby("side").pnl.agg(["count", "mean", "sum"]).round(3).to_markdown(), "",
                "## Holdout by series (top 15)", "", H.groupby("series").pnl.agg(["count", "mean", "sum"]).sort_values("count", ascending=False).head(15).round(3).to_markdown(), "",
                "## Holdout by price band", "", H.assign(band=pd.cut(H.px, [0, .1, .3, .5, .7, .9, 1])).groupby("band", observed=True).pnl.agg(["count", "mean"]).round(3).to_markdown()]
    open("reports/ROUND58.md", "w").write("\n".join(out) + "\n"); print("\n".join(out[:8]))


def smoke():
    for planted in (True, False):
        r = analyze(build(*synthetic(planted)), "planted" if planted else "null")
        print(r["label"], r["verdict"], r.get("choice"), r.get("n"), r.get("mean"), r.get("t"))
        assert (r["verdict"] == "PASS") == planted, f"calibration failed on {r['label']}"
    print("smoke OK")


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "smoke": smoke()
    elif c == "collect": collect(float(os.environ.get("R58_BUDGET_MIN", "300")))
    else:
        M = build(*collect()); M.to_pickle(f"{OUT}/built.pkl"); report(analyze(M), M)

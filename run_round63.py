"""Round 63 (PROTOCOL_ROUND63.md): chart #1 markets — does the incumbent repeat more often than priced? `smoke` | `collect` | `analyze`."""
import math, os, pickle, sys, time
import numpy as np, pandas as pd
from edge import round27 as r27
from edge import round20 as r20
from run_round57 import fee
from run_round58 import wkey, first_asks, ct

OUT = "data/r63"; os.makedirs(OUT, exist_ok=True)
A, B = pd.Timestamp("2025-01-01", tz="UTC"), pd.Timestamp.now(tz="UTC")
SERIES = ["KXSPOTIFYD", "KXSPOTIFY2D", "KXSPOTIFYGLOBALD", "KXSPOTIFYW", "KXTOPSONG", "KXTOPALBUM",
          "KXNETFLIXRANKSHOW", "KXNETFLIXRANKMOVIE", "KXNETFLIXRANKSHOWRUNNERUP", "KXNETFLIXRANKMOVIERUNNERUP", "KXNETFLIXRANKMOVIEGLOBAL"]
EDGES, NMINS = [0.05, 0.10, 0.15, 0.20, 0.30], [5, 10]


def bucket(streak):
    return "1" if streak <= 1 else ("2-3" if streak <= 3 else "4+")


def incumbents(M):
    """One row per event: the incumbent's market, with the streak-bucket prior from events closed before the decision time."""
    M = M.copy()
    M["close"] = pd.to_datetime(M.close, utc=True, format="ISO8601"); M["open"] = pd.to_datetime(M.open, utc=True, format="ISO8601")
    out = []
    for s, x in M.groupby("series"):
        ev = x.groupby("event").agg(ev_close=("close", "max"), ev_open=("open", "min")).sort_values("ev_close")
        win = x[x.result == "yes"].groupby("event").word.first()
        ev["winner"] = ev.index.map(win)
        hist = []                     # (ev_close, winner) of earlier events, in close order
        recs = []                     # (ev_close, bucket, repeated) of earlier incumbent opportunities
        for e, r in ev.iterrows():
            dec = r.ev_open + pd.Timedelta(hours=1)
            past = [w for c, w in hist if c < dec]
            if past and past[-1] == past[-1]:
                inc = past[-1]; streak = 0
                for w in reversed(past):
                    if w == inc: streak += 1
                    else: break
                b = bucket(streak)
                h = [rep for c, bb, rep in recs if bb == b and c < dec]
                mk = x[(x.event == e) & (x.word == inc)]
                if len(mk) and r.winner == r.winner:
                    m = mk.iloc[0]
                    out.append(dict(series=s, event=e, ticker=m.ticker, word=inc, open=m.open, ev_close=r.ev_close, bucket=b, n=len(h),
                                    prior=(sum(h) + 1) / (len(h) + 2), y=float(m.result == "yes")))
                if r.winner == r.winner:
                    recs.append((r.ev_close, b, float(r.winner == inc)))
            hist.append((r.ev_close, r.winner))
    return pd.DataFrame(out)


def collect(budget_min=280):
    path = f"{OUT}/raw.pkl"
    if os.path.exists(path): return pickle.load(open(path, "rb"))
    t0 = time.time(); mk = []
    for s in SERIES:
        ms = r20.markets(s, A, B); print(s, len(ms), round(time.time() - t0), flush=True)
        mk += [dict(series=s, ticker=m["ticker"], event=m["event_ticker"], word=wkey(m.get("yes_sub_title")), open=m.get("open_time"),
                    close=m["close_time"], result=m["result"], vol=float(m.get("volume_fp") or 0)) for m in ms]
    M = pd.DataFrame(mk).drop_duplicates("ticker")
    I = incumbents(M); print("incumbent markets", len(I), flush=True)
    cut = r27.cutoff(); asks = {}
    for i, r in enumerate(I.itertuples()):
        if time.time() - t0 > budget_min * 60: print("trade budget hit", i, flush=True); break
        asks[r.ticker] = first_asks(r27.trades(r.ticker, pd.Timestamp(r.ev_close), cut, max_pages=5), r.open)
        if i % 200 == 0: print("trades", i, round(time.time() - t0), flush=True)
    pickle.dump((M, asks), open(path, "wb")); return M, asks


def build(M, tr):
    I = incumbents(M)
    ya, na = [], []
    for r in I.itertuples():
        v = tr.get(r.ticker)
        a = v if isinstance(v, tuple) else (first_asks(v, r.open) if v else (np.nan, np.nan))
        ya.append(a[0]); na.append(a[1])
    I["yes_ask"], I["no_ask"] = ya, na
    return I


def trades_for(I, e, nmin):
    out = []
    for r in I[I.n >= nmin].itertuples():
        if r.yes_ask == r.yes_ask and 0.01 <= r.yes_ask <= 0.99 and r.prior - r.yes_ask >= e:
            out.append(dict(event=r.event, series=r.series, bucket=r.bucket, side="yes", px=r.yes_ask, p=r.prior, y=r.y, pnl=r.y - r.yes_ask - fee(r.yes_ask)))
        elif r.no_ask == r.no_ask and 0.01 <= r.no_ask <= 0.99 and (1 - r.prior) - r.no_ask >= e:
            out.append(dict(event=r.event, series=r.series, bucket=r.bucket, side="no", px=r.no_ask, p=1 - r.prior, y=1 - r.y, pnl=(1 - r.y) - r.no_ask - fee(r.no_ask)))
    return pd.DataFrame(out, columns=["event", "series", "bucket", "side", "px", "p", "y", "pnl"])


def analyze(I, label="real"):
    elig = I[I.yes_ask.notna() | I.no_ask.notna()]
    if elig.empty: return dict(label=label, verdict="FAIL (no priced incumbent markets)", grid=pd.DataFrame())
    split = elig.ev_close.median()
    dev, ho = I[I.ev_close < split], I[I.ev_close >= split]
    G = pd.DataFrame([dict(edge=e, nmin=n, dev_trades=len(T), dev_mean=T.pnl.mean() if len(T) else np.nan, dev_t=ct(T))
                      for e in EDGES for n in NMINS for T in [trades_for(dev, e, n)]])
    ok = G[G.dev_trades >= 50]
    if ok.empty: return dict(label=label, verdict="FAIL (no dev config with 50 trades)", grid=G, split=split)
    b = ok.sort_values("dev_mean", ascending=False).iloc[0]
    H = trades_for(ho, b.edge, int(b.nmin))
    bm = ((H.p - H.y) ** 2).mean() if len(H) else np.nan; bk = ((H.px - H.y) ** 2).mean() if len(H) else np.nan
    mean, t = (H.pnl.mean() if len(H) else np.nan), ct(H)
    passed = len(H) >= 100 and mean > 0 and t >= 2.5 and bm < bk
    return dict(label=label, verdict="PASS" if passed else "FAIL", choice=f"edge {b.edge}, n_min {int(b.nmin)}, split {split.date()}",
                grid=G, H=H, n=len(H), mean=mean, t=t, bm=bm, bk=bk)


def synthetic(planted, seed=1):
    rng = np.random.default_rng(seed); rows, tr = [], {}
    P = {"1": 0.60, "2-3": 0.75, "4+": 0.85}
    for s in ["SA", "SB", "SC"]:
        inc, streak = "song0", 1; k_song = 1
        for k, day in enumerate(pd.date_range("2025-03-01", periods=300, freq="D")):
            ev = f"{s}-{k}"; op = day.tz_localize("UTC"); close = op + pd.Timedelta(hours=20)
            p = P[bucket(streak)]; rep = rng.random() < p
            others = [f"song{k_song + j}" for j in range(4)]
            winner = inc if rep else others[0]
            q = 0.5 + 0.5 * (p - 0.5) if planted else p
            q = float(np.clip(q + rng.normal(0, 0.03), 0.03, 0.97))
            for w in [inc] + others:
                tk = f"{ev}-{w}"
                rows.append(dict(series=s, ticker=tk, event=ev, word=w, open=op.isoformat(), close=close.isoformat(), result="yes" if w == winner else "no", vol=1.0))
                if w == inc:
                    t = (op + pd.Timedelta(hours=2)).isoformat()
                    tr[tk] = [dict(created_time=t, taker_side="yes", yes_price_dollars=str(round(min(q + 0.01, 0.99), 2))),
                              dict(created_time=t, taker_side="no", no_price_dollars=str(round(min(1 - q + 0.01, 0.99), 2)))]
            if rep: streak += 1
            else: inc, streak, k_song = winner, 1, k_song + 4
    return pd.DataFrame(rows), tr


def report(res, I, M):
    out = ["# Round 63: chart #1 markets — incumbent repeat rate vs price", "", "Rules: [PROTOCOL_ROUND63.md](../PROTOCOL_ROUND63.md).", "",
           f"Settled markets: {len(M):,} in {M.series.nunique()} series. Incumbent markets: {len(I):,}; priced: {int((I.yes_ask.notna() | I.no_ask.notna()).sum()):,}.", "",
           f"**Verdict: {res['verdict']}.**"]
    if "H" in res:
        out += [f"Dev choice: {res['choice']}. Holdout: {res['n']} trades, mean P&L {res['mean']:+.3f} $/contract, event-clustered t {res['t']:.2f}. "
                f"Brier on traded markets: prior {res['bm']:.3f} vs price {res['bk']:.3f}.", ""]
    if len(I):
        J = I.assign(mid=I.yes_ask.where(I.yes_ask.notna(), 1 - I.no_ask))
        out += ["## Descriptive: incumbent repeat rate vs first price, by series × streak bucket", "",
                J.groupby(["series", "bucket"]).agg(events=("y", "size"), repeat_rate=("y", "mean"), mean_yes_price=("mid", "mean")).round(3).to_markdown(), ""]
    if len(res.get("grid", [])):
        out += ["## Dev grid", "", res["grid"].round(4).to_markdown(index=False), ""]
    if "H" in res and len(res["H"]):
        H = res["H"]
        out += ["## Holdout by side", "", H.groupby("side").pnl.agg(["count", "mean", "sum"]).round(3).to_markdown(), "",
                "## Holdout by series", "", H.groupby("series").pnl.agg(["count", "mean", "sum"]).round(3).to_markdown(), "",
                "## Holdout by streak bucket", "", H.groupby("bucket").pnl.agg(["count", "mean", "sum"]).round(3).to_markdown()]
    open("reports/ROUND63.md", "w").write("\n".join(out) + "\n"); print("\n".join(out[:9]))


def smoke():
    for planted in (True, False):
        r = analyze(build(*synthetic(planted)), "planted" if planted else "null")
        print(r["label"], r["verdict"], r.get("choice"), r.get("n"), r.get("mean"), r.get("t"))
        assert (r["verdict"] == "PASS") == planted, f"calibration failed on {r['label']}"
    print("smoke OK")


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "smoke": smoke()
    elif c == "collect": collect(int(os.environ.get("R63_BUDGET_MIN", "280")))
    elif c == "analyze":
        M, asks = collect(); I = build(M, asks); report(analyze(I), I, M)

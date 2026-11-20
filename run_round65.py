"""Round 65 (PROTOCOL_ROUND65.md): hourly Polymarket -> Kalshi lead-lag on Fed decisions. `smoke` | `collect` | `analyze`."""
import json, math, os, pickle, re, sys, time
import numpy as np, pandas as pd, requests
from run_round57 import fee

OUT = "data/r65"; os.makedirs(OUT, exist_ok=True)
K = "https://api.elections.kalshi.com/trade-api/v2"; G = "https://gamma-api.polymarket.com"; C = "https://clob.polymarket.com"
GS, HS = [0.02, 0.03, 0.05, 0.08], [1, 3, 6, 24]
MON = {m: i for i, m in enumerate(["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"], 1)}


def get(u, p=None, tries=3):
    for i in range(tries):
        try:
            r = requests.get(u, params=p, timeout=40, headers={"User-Agent": "research-probe"})
            if r.status_code == 429: time.sleep(5 * (i + 1)); continue
            return r.json() if r.ok else None
        except Exception:
            time.sleep(2)
    return None


def poly_outcome(q):
    q = (q or "").lower()
    if "no change" in q: return "hold"
    if re.search(r"(decrease|cut).*(50|75|100)\+?", q): return "cut_big"
    if re.search(r"(decrease|cut).*25", q): return "cut25"
    if re.search(r"(increase|hike).*(50|75)\+?", q): return "hike_big"
    if re.search(r"(increase|hike).*25", q): return "hike25"
    return None


def kalshi_outcome(m):
    suf = m["ticker"].rsplit("-", 1)[-1]
    return {"H0": "hold", "C25": "cut25", "C26": "cut_big", "H25": "hike25", "H26": "hike_big"}.get(suf)


def num(x):
    if x is None: return np.nan
    try: return float(x)
    except Exception: return np.nan


def candle_px(c, side):
    d = c.get(side) or {}
    v = d.get("close_dollars")
    if v is not None: return num(v)
    v = d.get("close")
    return num(v) / 100 if v is not None else np.nan


def poly_history(tok, a, b, fidelity=60):
    """Amendment 2: resolved markets only answer startTs/endTs windows of <= 7 days (interval=all returns nothing after resolution)."""
    pts, t = {}, int(a.timestamp()); end = int(b.timestamp())
    while t < end:
        u = min(t + 7 * 86400 - 60, end)
        for x in (get(f"{C}/prices-history", {"market": tok, "startTs": t, "endTs": u, "fidelity": fidelity}) or {}).get("history", []):
            pts[int(x["t"])] = float(x["p"])
        t = u; time.sleep(0.2)
    return [{"t": k, "p": v} for k, v in sorted(pts.items())]


def collect():
    path = f"{OUT}/raw.pkl"
    if os.path.exists(path): return pickle.load(open(path, "rb"))
    from edge import round20 as r20
    pe = {}
    for tag in ["fed-rates", "fed", "economic-policy", "economy"]:
        for closed in ("true", "false"):
            for off in range(0, 2000, 100):
                e = get(f"{G}/events", {"tag_slug": tag, "closed": closed, "limit": 100, "offset": off})
                if not isinstance(e, list) or not e: break
                for x in e: pe[x["id"]] = x
    fed = [e for e in pe.values() if re.match(r"fed decision in", (e.get("title") or "").lower()) and float(e.get("volume") or 0) > 1e5]
    print("poly fed events", len(fed), flush=True)
    km = r20.markets("KXFEDDECISION", pd.Timestamp("2024-06-01", tz="UTC"), pd.Timestamp.now(tz="UTC") + pd.Timedelta(days=400))
    try:
        live = (get(f"{K}/markets", {"series_ticker": "KXFEDDECISION", "status": "open", "limit": 1000}) or {}).get("markets", [])
    except Exception:
        live = []
    km += live
    kev = {}
    for m in km:
        code = m["event_ticker"].split("-")[-1]
        mm = re.match(r"(\d\d)([A-Z]{3})", code)
        if mm and mm.group(2) in MON: kev.setdefault((2000 + int(mm.group(1)), MON[mm.group(2)]), []).append(m)
    print("kalshi meetings", sorted(kev), flush=True)
    pairs = []
    for e in fed:
        end = pd.Timestamp(e.get("endDate"))
        key = (end.year, end.month)
        if key not in kev:                                     # Polymarket endDate can fall just after the meeting day
            alt = (end - pd.Timedelta(days=3)); key = (alt.year, alt.month)
        if key not in kev: continue
        kout = {kalshi_outcome(m): m for m in kev[key] if kalshi_outcome(m)}
        for pm in e.get("markets", []):
            o = poly_outcome(pm.get("question"))
            if o not in kout: continue
            tok = json.loads(pm["clobTokenIds"])[0] if isinstance(pm.get("clobTokenIds"), str) else (pm.get("clobTokenIds") or [None])[0]
            if not tok: continue
            km_ = kout[o]; cl = pd.Timestamp(km_["close_time"]); op = pd.Timestamp(km_.get("open_time") or cl - pd.Timedelta(days=60))
            h = poly_history(tok, max(op, cl - pd.Timedelta(days=90)), min(cl, pd.Timestamp.now(tz="UTC")))
            cs = []
            st = int(max(op, cl - pd.Timedelta(days=90)).timestamp())
            for ep in (f"{K}/series/KXFEDDECISION/markets/{km_['ticker']}/candlesticks", f"{K}/historical/markets/{km_['ticker']}/candlesticks"):
                j = get(ep, {"start_ts": st, "end_ts": int(min(cl, pd.Timestamp.now(tz="UTC")).timestamp()), "period_interval": 60}) or {}
                cs = j.get("candlesticks", [])
                if cs: break
            pairs.append(dict(meeting=f"{key[0]}-{key[1]:02d}", outcome=o, ticker=km_["ticker"], result=km_.get("result"), close=cl,
                              poly=[(int(x["t"]), float(x["p"])) for x in h],
                              kal=[(int(c["end_period_ts"]), candle_px(c, "yes_bid"), candle_px(c, "yes_ask")) for c in cs]))
            print(key, o, len(h), "poly pts", len(cs), "kalshi candles", flush=True)
    pickle.dump(pairs, open(path, "wb")); return pairs


def frames(pairs, shift_h=0):
    """One frame per pair: hourly Kalshi bid/ask with the Polymarket price known >= 1 h before (optionally shifted)."""
    out = []
    for p in pairs:
        if not p["poly"] or not p["kal"]: continue
        P = pd.Series([v for _, v in p["poly"]], index=[t for t, _ in p["poly"]]).sort_index()
        Kf = pd.DataFrame(p["kal"], columns=["t", "bid", "ask"]).dropna().sort_values("t")
        if Kf.empty: continue
        look = Kf.t.to_numpy() - 3600 - shift_h * 3600
        idx = np.searchsorted(P.index.to_numpy(), look, side="right") - 1
        Kf["poly"] = np.where(idx >= 0, P.to_numpy()[np.maximum(idx, 0)], np.nan)
        res = 1.0 if p["result"] == "yes" else (0.0 if p["result"] == "no" else np.nan)
        out.append((p["meeting"], p["ticker"], Kf.reset_index(drop=True), res))
    return out


def trades(F, g, H):
    rows = []
    for meeting, tk, x, res in F:
        n = len(x); i = 0
        t, bid, ask, poly = x.t.to_numpy(), x.bid.to_numpy(), x.ask.to_numpy(), x.poly.to_numpy()
        while i < n:
            side = None
            if poly[i] == poly[i] and 0.01 <= ask[i] <= 0.99 and poly[i] - ask[i] >= g: side, px = "yes", ask[i]
            elif poly[i] == poly[i] and 0.01 <= bid[i] <= 0.99 and bid[i] - poly[i] >= g: side, px = "no", 1 - bid[i]
            if side is None: i += 1; continue
            j = np.searchsorted(t, t[i] + H * 3600)
            if j < n:
                ex = bid[j] if side == "yes" else 1 - ask[j]; pnl = ex - px - fee(px) - fee(ex)
            elif res == res:
                ex = res if side == "yes" else 1 - res; pnl = ex - px - fee(px); j = n
            else:
                break
            rows.append(dict(meeting=meeting, ticker=tk, side=side, px=px, pnl=pnl)); i = j
    return pd.DataFrame(rows, columns=["meeting", "ticker", "side", "px", "pnl"])


def ct(T):
    if len(T) < 5: return np.nan
    g = T.groupby("meeting").pnl.sum()
    return g.mean() / g.std() * math.sqrt(len(g)) if len(g) > 2 and g.std() > 0 else np.nan


def analyze(pairs, label="real"):
    F = frames(pairs)
    ms = sorted({m for m, *_ in F})
    if len(ms) < 4: return dict(label=label, verdict=f"FAIL (only {len(ms)} meetings with data)", grid=pd.DataFrame(), meetings=ms)
    cut = ms[len(ms) // 2]
    dev = [f for f in F if f[0] < cut]; ho = [f for f in F if f[0] >= cut]
    G = pd.DataFrame([dict(g=g, H=H, dev_trades=len(T), dev_mean=T.pnl.mean() if len(T) else np.nan, dev_t=ct(T))
                      for g in GS for H in HS for T in [trades(dev, g, H)]])
    ok = G[G.dev_trades >= 50]
    if ok.empty: return dict(label=label, verdict="FAIL (no dev config with 50 trades)", grid=G, meetings=ms)
    b = ok.sort_values("dev_mean", ascending=False).iloc[0]
    T = trades(ho, b.g, int(b.H))
    Fn = frames([p for p in pairs if p["meeting"] >= cut], shift_h=7 * 24)
    N = trades(Fn, b.g, int(b.H))
    mean, t, nm = (T.pnl.mean() if len(T) else np.nan), ct(T), (N.pnl.mean() if len(N) else -np.inf)
    passed = len(T) >= 100 and mean > 0 and t >= 2.5 and mean > nm
    return dict(label=label, verdict="PASS" if passed else "FAIL", choice=f"g {b.g}, H {int(b.H)} h, split at meeting {cut}", grid=G, T=T,
                n=len(T), mean=mean, t=t, null_mean=nm, null_n=len(N), meetings=ms)


def synthetic(planted, seed=0):
    rng = np.random.default_rng(seed); pairs = []
    for k in range(12):
        meeting = f"2025-{k + 1:02d}"; n = 24 * 40
        t0 = int(pd.Timestamp(f"2025-{k + 1:02d}-01", tz="UTC").timestamp()); ts = t0 + 3600 * np.arange(n)
        for o in ("hold", "cut25", "hike25"):
            true = 1 / (1 + np.exp(-np.cumsum(rng.normal(0, 0.15, n))))
            poly = true
            if planted: kal = np.concatenate([np.full(6, true[0]), true[:-6]])
            else: kal = 1 / (1 + np.exp(-np.cumsum(rng.normal(0, 0.15, n)))); poly = 1 / (1 + np.exp(-np.cumsum(rng.normal(0, 0.15, n))))
            res = "yes" if rng.random() < kal[-1] else "no"
            pairs.append(dict(meeting=meeting, outcome=o, ticker=f"S-{k}-{o}", result=res, close=None,
                              poly=list(zip(ts.tolist(), poly.tolist())),
                              kal=list(zip((ts + 3600).tolist(), np.clip(kal - 0.01, 0.01, 0.99).tolist(), np.clip(kal + 0.01, 0.01, 0.99).tolist()))))
    return pairs


def diagnostics(pairs):
    rows = []
    for p in pairs:
        K_ = pd.DataFrame(p["kal"], columns=["t", "bid", "ask"]) if p["kal"] else pd.DataFrame(columns=["t", "bid", "ask"])
        F = frames([p])
        x = F[0][2] if F else pd.DataFrame(columns=["poly", "bid", "ask"])
        mid = (x.bid + x.ask) / 2 if len(x) else pd.Series(dtype=float)
        rows.append(dict(meeting=p["meeting"], outcome=p["outcome"], ticker=p["ticker"], result=p["result"], poly_pts=len(p["poly"]), kal_candles=len(K_),
                         kal_with_bid_ask=int(K_[["bid", "ask"]].notna().all(axis=1).sum()) if len(K_) else 0, aligned=int(x.poly.notna().sum()) if len(x) else 0,
                         med_abs_gap=round(float((x.poly - mid).abs().median()), 4) if len(x) else np.nan,
                         med_spread=round(float((x.ask - x.bid).median()), 4) if len(x) else np.nan,
                         corr=round(float(x.poly.corr(mid)), 3) if len(x) > 5 else np.nan))
    return pd.DataFrame(rows)


def report(res, pairs):
    out = ["# Round 65: does Polymarket lead Kalshi on Fed decisions? (hourly)", "", "Rules: [PROTOCOL_ROUND65.md](../PROTOCOL_ROUND65.md).", "",
           f"Matched outcome pairs: {len(pairs)}; with both histories: {sum(1 for p in pairs if p['poly'] and p['kal'])}; meetings: {', '.join(res.get('meetings', []))}.", "",
           f"**Verdict: {res['verdict']}.**"]
    if "T" in res:
        out += [f"Dev choice: {res['choice']}. Holdout: {res['n']} trades, mean {res['mean']:+.4f} $/contract, meeting-clustered t {res['t']:.2f}. "
                f"Time-shift null (+7 days) mean {res['null_mean']:+.4f} on {res['null_n']} trades.", ""]
        if len(res["T"]):
            out += ["## Holdout by side", "", res["T"].groupby("side").pnl.agg(["count", "mean", "sum"]).round(4).to_markdown(), "",
                    "## Holdout by meeting", "", res["T"].groupby("meeting").pnl.agg(["count", "mean", "sum"]).round(4).to_markdown(), ""]
    if len(res.get("grid", [])): out += ["## Dev grid", "", res["grid"].round(4).to_markdown(index=False), ""]
    out += ["## Data diagnostics per matched pair", "", diagnostics(pairs).to_markdown(index=False)]
    open("reports/ROUND65.md", "w").write("\n".join(out) + "\n"); print("\n".join(out[:9]))


def smoke():
    for planted in (True, False):
        r = analyze(synthetic(planted), "planted" if planted else "null")
        print(r["label"], r["verdict"], r.get("choice"), r.get("n"), r.get("mean"), r.get("t"), r.get("null_mean"))
        assert (r["verdict"] == "PASS") == planted, f"calibration failed on {r['label']}"
    print("smoke OK")


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "smoke": smoke()
    elif c == "collect": collect()
    elif c == "analyze":
        P = collect(); report(analyze(P), P)

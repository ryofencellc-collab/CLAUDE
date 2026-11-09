"""Round 41 (PROTOCOL_ROUND41.md): is the 99c bid's losing flow predictable from the last few minutes of price?"""
import os, sys, time
import numpy as np, pandas as pd, requests
from edge import weather as wx
from edge import round20 as r20

A, B = pd.Timestamp("2026-05-01", tz="UTC"), pd.Timestamp("2026-11-09", tz="UTC")
HOLD = pd.Timestamp("2026-09-01", tz="UTC")
COINS = {"KXBTCD": "BTC-USD", "KXETHD": "ETH-USD"}
BUDGET = float(os.environ.get("R41_BUDGET_MIN", "110")) * 60  # per coin
OUT = "data/r41"; os.makedirs(OUT, exist_ok=True)
FEE_C = 100 * 0.0175 * 0.99 * 0.01


def candles(product):
    p = f"{OUT}/{product}.pkl"
    if os.path.exists(p):
        return pd.read_pickle(p)
    s, rows = requests.Session(), []
    t = A - pd.Timedelta(hours=3)
    while t < B:
        u = min(t + pd.Timedelta(minutes=300), B)
        for i in range(6):
            r = s.get(f"https://api.exchange.coinbase.com/products/{product}/candles",
                      params={"granularity": 60, "start": t.isoformat(), "end": u.isoformat()}, timeout=30)
            if r.status_code == 200:
                rows += r.json(); break
            time.sleep(2 ** i)
        t = u; time.sleep(0.12)
    d = pd.DataFrame(rows, columns=["t", "lo", "hi", "o", "c", "v"]).drop_duplicates("t").sort_values("t")
    c = pd.Series(d.c.values, index=pd.to_datetime(d.t, unit="s", utc=True) + pd.Timedelta(minutes=1))  # by END
    c = c.asfreq("1min").ffill(limit=5)
    c.to_pickle(p); return c


def trades(ticker, a, b):
    seen, out = set(), []
    for path in ("markets/trades", "historical/trades"):
        cursor = None
        for _ in range(20):
            p = {"ticker": ticker, "limit": 1000, "min_ts": int(a.timestamp()), "max_ts": int(b.timestamp()) + 1}
            if cursor: p["cursor"] = cursor
            r = wx._get(f"{wx.KALSHI}/{path}", p)
            if r is None or r.status_code != 200: break
            j = r.json()
            for t in j.get("trades", []):
                k = t.get("trade_id") or (t.get("created_time"), t.get("count_fp"))
                if k not in seen:
                    seen.add(k); out.append(t)
            cursor = j.get("cursor")
            if not cursor or not j.get("trades"): break
    return out


def run_coin(series, product):
    c = candles(product)
    lc = np.log(c); vol = lc.diff().rolling(60, min_periods=55).std()
    d1 = lc.diff() / vol; d5 = lc.diff(5) / vol
    ms = [m for m in r20.markets(series, A, B) if m.get("strike_type") in ("greater", "greater_or_equal")]
    print(series, "markets", len(ms), flush=True)
    ev = {}
    for m in ms:
        ev.setdefault(m["ticker"].rsplit("-", 1)[0], []).append(m)
    keys = sorted(ev); rng = np.random.default_rng(41); rng.shuffle(keys)
    rows, t0, done = [], time.time(), 0
    for e in keys:
        if time.time() - t0 > BUDGET: break
        done += 1
        for m in ev[e]:
            if float(m.get("volume_fp") or m.get("volume") or 0) <= 0: continue
            close = pd.Timestamp(m["close_time"]); K = float(m["floor_strike"])
            win = c[(c.index > close - pd.Timedelta(minutes=61)) & (c.index <= close)]
            if len(win) < 30: continue
            tau = (close - win.index).total_seconds() / 60
            z = np.log(win / K) / (vol.reindex(win.index) * np.sqrt(np.maximum(tau, 0.5)))
            if np.nanmax(np.abs(z)) < 6: continue
            for t in trades(m["ticker"], close - pd.Timedelta(minutes=60), close):
                ts_side = t.get("taker_side")
                if ts_side not in ("yes", "no"): continue
                try: px = float(t.get(f"{ts_side}_price_dollars"))
                except (TypeError, ValueError): continue
                if not (0.01 - 1e-9 <= px <= 0.02 + 1e-9): continue
                side = "no" if ts_side == "yes" else "yes"     # the 99c bid this sell would fill
                ts = pd.Timestamp(t["created_time"]); mm = ts.floor("min")  # last completed minute ends at mm
                if mm not in c.index or mm - pd.Timedelta(minutes=1) not in c.index: continue
                sg = 1 if side == "yes" else -1
                tl = max((close - mm).total_seconds() / 60, 0.5)
                zz = sg * np.log(c[mm] / K) / (vol[mm] * np.sqrt(tl))
                m1 = mm - pd.Timedelta(minutes=1)
                zl = sg * np.log(c[m1] / K) / (vol[m1] * np.sqrt(tl + 1))
                rows.append(dict(series=series, event=e, ticker=m["ticker"], ts=ts, side=side, n=float(t.get("count_fp") or t.get("count") or 0),
                                 won=m["result"] == side, z=zz, zlag=zl, tau=(close - ts).total_seconds() / 60,
                                 d1=sg * d1[mm], d5=sg * d5[mm]))
        if done % 200 == 0:
            print(f"  {series} events {done}/{len(keys)} flow rows {len(rows)} {time.time() - t0:.0f}s", flush=True)
    print(f"{series}: processed {done}/{len(keys)} events", flush=True)
    return pd.DataFrame(rows), done, len(keys)


RULES = {
    "base z>=6": lambda f: f.z >= 6, "base, 1-min lag": lambda f: f.zlag >= 6,
    **{f"z>={k}": (lambda f, k=k: f.z >= k) for k in (8, 10, 15, 20)},
    **{f"z>=6 & d1>-{k}": (lambda f, k=k: (f.z >= 6) & (f.d1 > -k)) for k in (1, 2, 3)},
    **{f"z>=6 & d5>-{k}*sqrt5": (lambda f, k=k: (f.z >= 6) & (f.d5 > -k * np.sqrt(5))) for k in (1, 2)},
    "z>=6 & <=15 min left": lambda f: (f.z >= 6) & (f.tau <= 15),
    "z>=6 & >=30 min left": lambda f: (f.z >= 6) & (f.tau >= 30),
}


def score(f):
    if f.empty or f.n.sum() == 0:
        return dict(flow=0, L=np.nan, cents=np.nan, losing_hours=0)
    L = f.n[~f.won].sum() / f.n.sum()
    return dict(flow=round(f.n.sum()), L=L, cents=round(1 - 100 * L - FEE_C, 3), losing_hours=f[~f.won].event.nunique())


def main():
    p = f"{OUT}/flow.pkl"
    if os.path.exists(p):
        F = pd.read_pickle(p); info = "cached"
    else:
        parts, info = [], []
        for s, prod in COINS.items():
            f, done, tot = run_coin(s, prod); parts.append(f); info.append(f"{s} {done}/{tot} hours")
            pd.concat(parts).to_pickle(p)
        F = pd.concat(parts); info = ", ".join(info)
    out = ["# Round 41: does the 99c bid's losing flow come after a visible move?", "",
           f"Kalshi KXBTCD + KXETHD hourly, 2026-05-01 → 2026-11-09 ({info}). Flow = 1–2c long-shot buys that would fill "
           "a 99c bid. L = lost share of that flow; breakeven ≈ 0.98%.", ""]
    base = F[RULES["base z>=6"](F)].n.sum()
    rows = []
    for name, fn in RULES.items():
        g = F[fn(F)]
        for per, x in [("dev", g[g.ts < HOLD]), ("holdout", g[g.ts >= HOLD]), ("Oct 29+", g[g.ts >= pd.Timestamp("2026-10-29", tz="UTC")])]:
            rows.append(dict(rule=name, period=per, **score(x)))
    t = pd.DataFrame(rows); t["L"] = t.L.map(lambda v: f"{v:.3%}" if pd.notna(v) else "")
    out += [t.to_markdown(index=False), ""]
    passed = []
    for name, fn in RULES.items():
        g = F[fn(F)]
        dv, ho = score(g[g.ts < HOLD]), score(g[g.ts >= HOLD])
        if all(pd.notna(x["L"]) and x["L"] < 0.005 and x["cents"] > 0 for x in (dv, ho)) and g.n.sum() >= 0.25 * base:
            passed.append(name)
    out.append(f"**Pass (L < 0.5% dev and holdout, > 0 cents, ≥ 25% of base flow):** {', '.join(passed) or 'none'}.")
    # where the lost flow sat
    lost = F[(F.z >= 6) & ~F.won]
    if len(lost):
        out += ["", "## Lost flow at z ≥ 6 (what the bot could see at the time)", "",
                lost.groupby("event").agg(contracts=("n", "sum"), z_med=("z", "median"), d1_med=("d1", "median"),
                                          d5_med=("d5", "median"), tau_med=("tau", "median")).sort_values("contracts", ascending=False)
                .head(15).round(2).to_markdown()]
        won = F[(F.z >= 6) & F.won]
        out += ["", f"Median d1 / d5 of winning flow: {won.d1.median():.2f} / {won.d5.median():.2f}; "
                f"of lost flow: {lost.d1.median():.2f} / {lost.d5.median():.2f} (σ units, negative = toward the strike)."]
    open("reports/ROUND41.md", "w").write("\n".join(out) + "\n"); print("\n".join(out))


if __name__ == "__main__":
    main()

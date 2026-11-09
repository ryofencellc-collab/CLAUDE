"""Round 40 (PROTOCOL_ROUND40.md): empirical loss rate of z >= Z hourly crypto bets on Binance 1m history."""
import io, os, sys, zipfile, concurrent.futures as cf
import numpy as np, pandas as pd, requests

VISION = "https://data.binance.vision/data/spot/monthly/klines"
COINS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"]
ZS = [6, 8, 10, 15, 20]
TAUS = [(1, 5), (6, 15), (16, 30), (31, 59)]
FEE_C = 100 * 0.0175 * 0.99 * 0.01  # maker fee, cents per contract at 99c (rounded up per order in reality)
OUT = "data/r40"


def month(sym, m):
    r = requests.get(f"{VISION}/{sym}/1m/{sym}-1m-{m}.zip", timeout=120)
    if r.status_code != 200:
        return None
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        d = pd.read_csv(z.open(z.namelist()[0]), header=None, usecols=[0, 4])
    t = d[0].astype("int64")
    t = np.where(t > 1e14, t // 1000, t)  # 2025+ files are in microseconds
    return pd.Series(d[4].values, index=pd.to_datetime(t + 60_000, unit="ms"))  # indexed by candle END


def load(sym):
    p = f"{OUT}/{sym}.pkl"
    if os.path.exists(p):
        return pd.read_pickle(p)
    ms = [f"{y}-{m:02d}" for y in range(2020, 2027) for m in range(1, 13) if f"{y}-{m:02d}" <= "2026-10"]
    with cf.ThreadPoolExecutor(8) as ex:
        parts = [x for x in ex.map(lambda m: month(sym, m), ms) if x is not None]
    s = pd.concat(parts).sort_index()
    s = s[~s.index.duplicated()].asfreq("1min").ffill(limit=3)
    os.makedirs(OUT, exist_ok=True); s.to_pickle(p); return s


def samples(s):
    lc = np.log(s)
    vol = lc.diff().rolling(60, min_periods=55).std()
    idx = s.index
    hour_end = idx.ceil("h")
    hour_end = hour_end.where(hour_end != idx, idx + pd.Timedelta(hours=1))  # at :00 the next hour is H+1
    tau = ((hour_end - idx).total_seconds() // 60).astype(int)
    settle = (s.reindex(hour_end - pd.Timedelta(minutes=1)).values + s.reindex(hour_end).values) / 2
    r = np.log(settle / s.values) / (vol.values * np.sqrt(tau))
    d = pd.DataFrame({"r": r, "tau": tau, "hour": hour_end}, index=idx)
    d = d[(d.tau >= 1) & (d.tau <= 59)].dropna()
    return d[np.isfinite(d.r)]


def rate(r, z):
    return (np.abs(r) > z).mean() / 2


def main():
    rows, tail = [], []
    for sym in COINS:
        s = load(sym); d = samples(s); print(sym, s.index.min(), s.index.max(), len(d), flush=True)
        for per, x in [("dev", d[d.index < "2024-01-01"]), ("holdout", d[d.index >= "2024-01-01"])]:
            for z in ZS:
                row = dict(coin=sym[:-4], period=per, z=z, minutes=len(x), p_all=rate(x.r, z),
                           losing_hours=int(x[np.abs(x.r) > z].hour.nunique()), hours=int(x.hour.nunique()))
                for a, b in TAUS:
                    y = x[(x.tau >= a) & (x.tau <= b)]
                    row[f"p_{a}-{b}m"] = rate(y.r, z)
                row["cents/contract"] = 1 * (1 - row["p_all"]) - 99 * row["p_all"] - FEE_C
                rows.append(row)
            big = x[np.abs(x.r) > 10].groupby("hour").r.agg(["count", lambda v: np.abs(v).max()])
            tail.append((sym, per, big.sort_values("count", ascending=False).head(5)))
    t = pd.DataFrame(rows)
    fmt = t.copy()
    for c in [c for c in t if c.startswith("p_")]:
        fmt[c] = (t[c] * 100).map(lambda v: f"{v:.3f}%")
    fmt["cents/contract"] = t["cents/contract"].round(3)
    out = ["# Round 40: how often does a z ≥ Z hourly crypto bet lose? (Binance 1m, 2020 → 2026-10)", "",
           "Per-side loss rate P(|r| > z)/2 over every minute with 1–59 minutes left. Breakeven for a 99c bid ≈ 0.98%.",
           "", fmt.to_markdown(index=False), ""]
    # paper forward: contract-weighted loss rate
    try:
        import re
        cols = eval(re.search(r"COLS = (\[.*?\])\n", open("edge/paper21.py").read(), re.S).group(1))
        f = pd.read_csv("paper/r21_fills.csv", header=None, names=cols)
        h = f[f.series.isin(["KXBTCD", "KXETHD", "KXSOLD", "KXXRPD"])]
        lost = h[h.pnl < -0.05].filled.sum(); tot = h.filled.sum()
        out += [f"**Paper forward (hourly series, Oct 29 → now):** {tot:,.0f} contracts filled, {lost:,.0f} lost → "
                f"contract-weighted loss rate **{lost / tot:.2%}** (breakeven ≈ 0.98%).", ""]
        paper_rate = lost / tot
    except Exception as e:
        out.append(f"paper read failed: {e!r}"); paper_rate = 1.0
    ho = t[(t.period == "holdout") & (t.z == 6)]
    ok = bool((ho.p_all < 0.005).all()) and paper_rate < 0.01
    zstar = None
    for z in ZS:
        dv = t[(t.period == "dev") & (t.z == z)]
        if (dv.p_all < 0.005).all():
            zstar = z; break
    out.append(f"**Pass (z = 6 holdout < 0.5% every coin, paper < 1%): {'PASS' if ok else 'FAIL'}.** "
               f"Smallest z passing on dev: {zstar}; its holdout: "
               + (", ".join(f"{r.coin} {r.p_all:.3%}" for r in t[(t.period == 'holdout') & (t.z == zstar)].itertuples()) if zstar else "none"))
    out += ["", "## Worst hours (most minutes with |r| > 10)", ""]
    for sym, per, b in tail:
        out += [f"{sym} {per}: " + "; ".join(f"{i:%Y-%m-%d %H:%M} ({int(c)} min, max |r| {m:.0f})" for i, (c, m) in b.iterrows())]
    open("reports/ROUND40.md", "w").write("\n".join(out) + "\n"); print("\n".join(out))


if __name__ == "__main__":
    main()

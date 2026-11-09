"""Round 39a (PROTOCOL_ROUND39.md): is 0DTE implied move (VIX1D) richer than the realized move?"""
import io, math, sys
import numpy as np, pandas as pd, requests

H = {"User-Agent": "Mozilla/5.0 (research)"}
CBOE = "https://cdn.cboe.com/api/global/us_indices/daily_prices/{}_History.csv"
COST = 0.6
K = math.sqrt(1 / 252)


def cboe(sym):
    r = requests.get(CBOE.format(sym), headers=H, timeout=60); r.raise_for_status()
    d = pd.read_csv(io.StringIO(r.text)); d.columns = [c.strip().upper() for c in d.columns]
    d["DATE"] = pd.to_datetime(d["DATE"]); return d.set_index("DATE").sort_index()


def spx():
    try:
        d = cboe("SPX")
        if {"OPEN", "CLOSE"} <= set(d.columns) and (d.OPEN != d.CLOSE).mean() > 0.9:
            return d[["OPEN", "HIGH", "LOW", "CLOSE"]]
    except Exception as e:
        print("cboe SPX failed", e)
    import yfinance as yf
    d = yf.download("^GSPC", start="2010-01-01", auto_adjust=False, progress=False)
    d.columns = [c[0].upper() if isinstance(c, tuple) else c.upper() for c in d.columns]
    d.index = pd.to_datetime(d.index).tz_localize(None); return d[["OPEN", "HIGH", "LOW", "CLOSE"]]


def norm_put(S, K_, s):  # Bachelier price, sd = s points
    z = (K_ - S) / s
    return (K_ - S) * 0.5 * math.erfc(-z / math.sqrt(2)) + s * math.exp(-z * z / 2) / math.sqrt(2 * math.pi)


def stats(x):
    x = pd.Series(x).dropna(); n = len(x)
    if n < 2: return dict(n=n)
    return dict(n=n, mean=round(x.mean(), 3), t=round(x.mean() / x.std() * math.sqrt(n), 2),
                win=round((x > 0).mean(), 3), worst=round(x.min(), 2), total=round(x.sum(), 1))


def main():
    v = cboe("VIX1D"); s = spx()
    d = s.join(v[["OPEN", "CLOSE"]].rename(columns={"OPEN": "V1O", "CLOSE": "V1C"}), how="inner").dropna()
    d = d[(d.V1O > 1) & (d.V1C > 1)]
    print("VIX1D/SPX joined:", d.index.min().date(), "->", d.index.max().date(), len(d))
    sd_o = d.OPEN * d.V1O / 100 * K
    A = sd_o * math.sqrt(2 / math.pi) - (d.CLOSE - d.OPEN).abs() - COST
    sd_c = d.CLOSE.shift(1) * d.V1C.shift(1) / 100 * K
    B = sd_c * math.sqrt(2 / math.pi) - (d.CLOSE - d.CLOSE.shift(1)).abs() - COST
    prem = sd_o * math.sqrt(2 / math.pi)
    C = []
    for S, sd, c in zip(d.OPEN, sd_o, d.CLOSE):
        lo, hi = S - sd, S + sd
        cr = norm_put(S, lo, sd) * 2  # symmetric normal: call at hi = put at lo
        C.append(cr - max(lo - c, 0) - max(c - hi, 0) - COST)
    C = pd.Series(C, index=d.index)
    half = d.index[len(d) // 2]
    out = ["# Round 39a: 0DTE implied move (VIX1D) vs realized move — model screen", "",
           f"SPX + VIX1D {d.index.min().date()} → {d.index.max().date()}, {len(d)} days; dev < {half.date()} ≤ holdout.",
           f"Units: SPX index points per 1-lot (×$100). Cost {COST} pt. Median premium (A) {prem.median():.1f} pt.", ""]
    rows = []
    for name, x in [("A straddle open→close", A), ("B straddle close→close", B), ("C strangle ±1σ open→close (optimistic)", C)]:
        for part, y in [("dev", x[x.index < half]), ("holdout", x[x.index >= half]), ("all", x)]:
            rows.append(dict(test=name, part=part, **stats(y)))
    t = pd.DataFrame(rows); out.append(t.to_markdown(index=False)); out.append("")
    yr = pd.DataFrame({"A": A, "B": B}).groupby(A.index.year).agg(["mean", "count"]).round(2)
    out += ["## By year (mean pts, days)", "", yr.to_markdown(), ""]
    ok = lambda x: x[x.index < half].mean() > 0 and x[x.index >= half].mean() > 0 and stats(x[x.index >= half])["t"] >= 3
    out.append(f"**Pass:** A {'PASS' if ok(A) else 'fail'}, B {'PASS' if ok(B.dropna()) else 'fail'} (model screen only).")
    open("reports/ROUND39A.md", "w").write("\n".join(out) + "\n"); print("\n".join(out))


if __name__ == "__main__":
    main()

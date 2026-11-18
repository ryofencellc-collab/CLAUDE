"""Round 55 (PROTOCOL_ROUND55.md): Reddit 0DTE SPX iron fly, 2-year model backtest calibrated on real Cboe quotes."""
import glob, math, os, sys
from datetime import time as dtime
import numpy as np, pandas as pd
from scipy.stats import norm
from scipy.optimize import brentq
from edge import odte_score as O
from edge.intraday import load_nq

W, TP, FEE, SLIP = 15.0, 0.15, 1.50, 0.20
FOMC = {"2023-05-03", "2023-06-14", "2023-07-26", "2023-09-20", "2023-11-01", "2023-12-13", "2024-01-31", "2024-03-20", "2024-05-01",
        "2024-06-12", "2024-07-31", "2024-09-18", "2024-11-07", "2024-12-18", "2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18",
        "2025-07-30", "2025-09-17", "2025-10-29", "2025-12-10", "2026-01-28", "2026-03-18", "2026-04-29", "2026-06-17", "2026-07-29",
        "2026-09-16", "2026-10-28", "2026-12-09"} | O.FOMC_DAYS
YEAR_MIN = 390 * 252                      # trading-minute year; the calibration constant absorbs the convention


def bs(S, K, T, sig, cp):
    if T <= 0 or sig <= 0:
        return max(S - K, 0.0) if cp == "C" else max(K - S, 0.0)
    d1 = (math.log(S / K) + 0.5 * sig * sig * T) / (sig * math.sqrt(T)); d2 = d1 - sig * math.sqrt(T)
    return S * norm.cdf(d1) - K * norm.cdf(d2) if cp == "C" else K * norm.cdf(-d2) - S * norm.cdf(-d1)


def fly(S, K, T, sig):
    return bs(S, K, T, sig, "C") + bs(S, K, T, sig, "P") - bs(S, K - W, T, sig, "P") - bs(S, K + W, T, sig, "C")


def vix1d():
    import yfinance as yf
    v = yf.download("^VIX1D", start="2023-04-01", progress=False, auto_adjust=False)["Close"].squeeze()
    v.index = pd.to_datetime(v.index).tz_localize(None).normalize(); return v / 100


def calibrate(v):
    rows = []
    for day in sorted(os.path.basename(p) for p in glob.glob("data/odte/2*")):
        d = O.load_day(day, "SPXW")
        if d.empty: continue
        ss = O.snaps(d); spot = d.groupby("t")["spot"].first()
        t0, g = O.first_at(ss, dtime(14, 50))
        if g is None: continue
        S = float(spot[t0]); legs = O.iron_fly(g, S, W)
        if not legs: continue
        mid = lambda cp, K: (O.q(g, cp, K, "bid") + O.q(g, cp, K, "ask")) / 2
        cr = sum(-s * mid(cp, K) for cp, K, s in legs); K = legs[0][1]
        T = (16 * 60 - (t0.hour * 60 + t0.minute)) / YEAR_MIN
        try:
            sig = brentq(lambda x: fly(S, K, T, x) - cr, 0.01, 3.0)
        except ValueError:
            continue
        prev = v[v.index < pd.Timestamp(day)]
        rows.append(dict(day=day, S=S, K=K, credit_real=cr, sigma_real=sig, vix1d_prev=float(prev.iloc[-1]) if len(prev) else np.nan,
                         real_f1=(O.fly_trade("F1", "SPXW", day, ss, spot, float(spot.iloc[-1]), W) or {}).get("pnl")))
    C = pd.DataFrame(rows); C["ratio"] = C.sigma_real / C.vix1d_prev
    return C


def simulate(M, v, c, entry=dtime(14, 50), tp=TP, slip=SLIP, days_only=None):
    out = []
    e_bar = (entry.hour * 60 + entry.minute) - 570
    for i, day in enumerate(M["days"]):
        ds = str(day.date())
        if days_only is not None and ds not in days_only: continue
        if ds in FOMC: continue
        prev = v[v.index < day]
        if not len(prev) or (day - prev.index[-1]).days > 5: continue
        sig = c * float(prev.iloc[-1]); C = M["c"][i]
        S0 = C[e_bar - 1]; K = round(S0 / 5) * 5
        T0 = (390 - e_bar) / YEAR_MIN
        cr = fly(S0, K, T0, sig) - slip / 2
        pnl, how = None, "expiry"
        if tp is not None:
            for j in range(e_bar, 389):
                val = fly(C[j], K, (389 - j) / YEAR_MIN, sig)
                if val <= (1 - tp) * (cr + slip / 2):
                    pnl = (cr - val - slip / 2) * 100 - 8 * FEE; how = "tp"; break
        if pnl is None:
            ST = C[389]; val = max(K - ST, 0) + max(ST - K, 0) - max(K - W - ST, 0) - max(ST - K - W, 0)
            pnl = (cr - val) * 100 - 4 * FEE
        out.append(dict(day=day, credit=cr, pnl=pnl, how=how))
    return pd.DataFrame(out).set_index("day")


def summ(R, label):
    if R.empty: return dict(variant=label, trades=0)
    p = R.pnl; half = R.index[len(R) // 2]
    return dict(variant=label, trades=len(p), win=f"{(p > 0).mean():.0%}", mean_lot=round(p.mean(), 1), t=round(p.mean() / p.std() * math.sqrt(len(p)), 2),
                worst=round(p.min(), 0), total_4lots=round(4 * p.sum(), 0), h1=round(p[p.index < half].sum(), 0), h2=round(p[p.index >= half].sum(), 0),
                avg_credit=round(R.credit.mean(), 2))


def main():
    v = vix1d(); print("VIX1D", len(v), v.index[0].date(), "->", v.index[-1].date(), flush=True)
    C = calibrate(v); print(C.round(4).to_string(), flush=True)
    c = float(C.ratio.median())
    M = __import__("edge.nygrid", fromlist=["day_matrix"]).day_matrix(load_nq(pair="SPXUSD"))
    print("SPX days", len(M["days"]), M["days"][0].date(), "->", M["days"][-1].date(), flush=True)
    # calibration check: model vs real on the collected days (model credit uses that day's prior VIX1D x c)
    cal = simulate(M, v, c, days_only=set(C.day)).reset_index()
    cal["day"] = cal.day.dt.strftime("%Y-%m-%d"); cal = C.merge(cal, on="day", how="left")
    cal["credit_err"] = (cal.credit - cal.credit_real) / cal.credit_real
    start = pd.Timestamp("2024-08-01")
    base = simulate(M, v, c); base = base[base.index >= start]
    rows = [summ(base, f"F1 as posted (c = {c:.3f})"), summ(simulate(M, v, 0.9 * c).loc[lambda x: x.index >= start], "c × 0.9 (cheaper premium)"),
            summ(simulate(M, v, 1.1 * c).loc[lambda x: x.index >= start], "c × 1.1"),
            summ(simulate(M, v, c, slip=0.0).loc[lambda x: x.index >= start], "mid fills (no slippage)"),
            summ(simulate(M, v, c, tp=None).loc[lambda x: x.index >= start], "no take-profit"),
            summ(simulate(M, v, c, entry=dtime(14, 0)).loc[lambda x: x.index >= start], "entry 14:00"),
            summ(simulate(M, v, c, entry=dtime(15, 15)).loc[lambda x: x.index >= start], "entry 15:15"),
            summ(simulate(M, v, c).loc[lambda x: (x.index >= "2023-05-01") & (x.index < start)], "before the post's window (2023-05 → 2024-07)")]
    Rt = pd.DataFrame(rows); b = rows[0]
    med_err = float(cal.credit_err.abs().median()) if cal.credit_err.notna().any() else np.nan
    ok = b["t"] >= 3 and b["h1"] > 0 and b["h2"] > 0 and med_err <= 0.10 and rows[1]["mean_lot"] > 0
    out = ["# Round 55: Reddit 0DTE SPX iron fly (14:50, ±$15, 15% take-profit), 2-year model backtest", "",
           "Rules: [PROTOCOL_ROUND55.md](../PROTOCOL_ROUND55.md). P&L per 1 lot after $0.20 slippage per side and $1.50/leg; total shown for 4 lots like the post.", "",
           f"**Verdict: {'PASS' if ok else 'FAIL'}.** Calibration: c = {c:.3f} from {len(C)} real days, median credit error {med_err:.1%}.", "",
           "## Results", "", Rt.to_markdown(index=False), "",
           "## Calibration days (real Cboe quotes vs model)", "",
           cal[["day", "S", "credit_real", "credit", "credit_err", "sigma_real", "vix1d_prev", "ratio", "real_f1", "pnl"]].rename(columns={"credit": "credit_model", "pnl": "model_pnl", "real_f1": "real_pnl"}).round(3).to_markdown(index=False), "",
           "## Worst 10 days (as posted)", "", base.sort_values("pnl").head(10).round(1).to_markdown(), "",
           "## By month (as posted, per lot)", "", base.pnl.groupby(base.index.to_period("M")).agg(["count", "sum", "mean"]).round(0).to_markdown()]
    open("reports/ROUND55.md", "w").write("\n".join(out) + "\n"); print("\n".join(out[:12]))


if __name__ == "__main__":
    main()

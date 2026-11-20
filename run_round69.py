"""Round 69 (PROTOCOL_ROUND69.md): blind test of the frozen 0DTE strategy (sell ATM straddle at open; skip Thursdays and mega-cap earnings mornings)."""
import glob, math, os
import numpy as np, pandas as pd, yfinance as yf
from edge import odte_score as O

K_, C2P = math.sqrt(1 / 252), math.sqrt(2 / math.pi)
FEE = 3.0
X = pd.read_csv("data/r68_days.csv", index_col=0, parse_dates=True)
spx = yf.Ticker("^GSPC").history(start="2022-01-01")[["Open", "Close"]]; spx.index = spx.index.tz_localize(None).normalize()


def skip(day):
    day = pd.Timestamp(day)
    if day.weekday() == 3: return "Thursday"
    if day in X.index and X.loc[day, "mega_er"] == 1: return "earnings morning (" + str(X.loc[day, "er_names"]) + ")"
    return ""


def real_day(day, x, src):
    x = x[(x.exp == day) & (x.bid > 0)]
    if x.empty: return None
    t0 = x.t[x.t.dt.hour * 60 + x.t.dt.minute >= 571].min(); g = x[x.t == t0]
    S = float(g.spot.iloc[0])
    both = g.groupby("K").cp.nunique(); both = both[both == 2].index.to_numpy(float)     # strikes with both legs quoted
    if not len(both): return None
    Kc = float(both[np.abs(both - S).argmin()])
    c = g[(g.K == Kc) & (g.cp == "C")]; p = g[(g.K == Kc) & (g.cp == "P")]
    if c.empty or p.empty: return None
    close = float(spx.loc[pd.Timestamp(day), "Close"]); credit = float(c.bid.iloc[0] + p.bid.iloc[0])
    pnl = (credit - abs(close - Kc)) * 100 - FEE
    return dict(day=day, weekday=pd.Timestamp(day).day_name()[:3], source=src, entry=str(t0.time())[:5], spot=round(S, 1), strike=Kc, credit=round(credit, 2),
                close=round(close, 2), move=round(close - Kc, 1), pnl=round(pnl, 0), skip=skip(day))


rows = []
for p in sorted(glob.glob("data/odte/2*")):
    d = os.path.basename(p); r = real_day(d, O.load_day(d, "SPXW"), "Cboe 1-min")
    if r: rows.append(r)
for p in sorted(glob.glob("data/odte_y/2*")):
    d = os.path.basename(p)
    if any(r["day"] == d for r in rows): continue
    y = pd.concat(pd.read_csv(f) for f in glob.glob(f"{p}/SPX_*.csv.gz"))
    y["t"] = pd.to_datetime(y.ts_fetch, utc=True).dt.tz_convert("America/New_York")
    r = real_day(d, y[y.root == "SPXW"] if (y.root == "SPXW").any() else y, "Yahoo 5-min (starts 10:32)")
    if r: rows.append(r)
R = pd.DataFrame(rows)
st, al = R[R.skip == ""], R
bh = (spx.loc[pd.Timestamp(R.day.min()):pd.Timestamp(R.day.max()), "Close"])
bh_pct = (spx.loc[pd.Timestamp(R.day.max()), "Close"] / spx.loc[pd.Timestamp(R.day.min()), "Open"] - 1) * 100

# Test 2: blind holdout, model-priced, with real-quote haircut
H = X[X.index >= "2024-08-12"].join(spx.Open.rename("OPEN"))
sd = H.OPEN * H.vix1d / 100 * K_; prem = sd * C2P
H["A_model"] = H.A; H["A_real"] = H.A - 0.105 * prem
H["strat"] = (H.weekday != 3) & (H.mega_er != 1)
def s(x, base_days):
    x = x.dropna(); eq = x.reindex(base_days).fillna(0).cumsum(); dd = (eq.cummax() - eq).max()
    return dict(days=len(x), mean_pt=round(x.mean(), 2), t=round(x.mean() / x.std() * math.sqrt(len(x)), 2), win=round((x > 0).mean(), 3), total_pt=round(x.sum(), 0),
                total_usd=round(x.sum() * 100, 0), maxdd_usd=round(dd * 100, 0), worst_usd=round(x.min() * 100, 0))
T2 = pd.DataFrame([dict(pricing=lab, trade=nm, **s(H.loc[m, col], H.index)) for lab, col in (("model", "A_model"), ("model × 0.895 (real-quote haircut)", "A_real"))
                   for nm, m in (("STRATEGY (skip Thu + earnings mornings)", H.strat), ("every day (the curve)", H.strat | True))])
spx_h = (spx.loc["2024-08-12":"2026-11-19", "Close"]); bh2 = (spx_h.iloc[-1] / spx_h.iloc[0] - 1) * 100
row = T2[(T2.pricing.str.contains("haircut")) & T2.trade.str.startswith("STRATEGY")].iloc[0]; base = T2[(T2.pricing.str.contains("haircut")) & T2.trade.str.startswith("every")].iloc[0]
passed = row.mean_pt > 0 and row.t >= 2 and row.mean_pt > base.mean_pt and row.maxdd_usd < base.maxdd_usd and st.pnl.mean() >= 0
out = ["# Round 69: blind test of the frozen 0DTE strategy", "", "Rules: [PROTOCOL_ROUND69.md](../PROTOCOL_ROUND69.md). Strategy: sell the SPX 0DTE ATM straddle at the open; skip Thursdays and mega-cap earnings mornings.", "",
       f"**Verdict: {'PASS' if passed else 'FAIL'}.**", "",
       "## Test 1: real recorded quotes (sold at the real bid, settled at the official close, $3 fees)", "", R.to_markdown(index=False), "",
       f"Strategy (traded days only): {len(st)} trades, total ${st.pnl.sum():,.0f}, mean ${st.pnl.mean():,.0f}, wins {int((st.pnl > 0).sum())}/{len(st)}.  ",
       f"Every day (the curve): {len(al)} trades, total ${al.pnl.sum():,.0f}, mean ${al.pnl.mean():,.0f}.  ",
       f"Without the 11-20 late-start day: strategy ${st[st.day != '2026-11-20'].pnl.sum():,.0f}, every day ${al[al.day != '2026-11-20'].pnl.sum():,.0f}.  ",
       f"S&P buy-and-hold over the same days: {bh_pct:+.2f}%.", "",
       "## Test 2: blind holdout 2024-08-12 → 2026-11-19 (rules fixed on 2022-06 → 2024-08 data; model-priced, P&L per SPX straddle)", "", T2.to_markdown(index=False), "",
       f"S&P buy-and-hold over the holdout: {bh2:+.1f}%.", ""]
open("reports/ROUND69.md", "w").write("\n".join(out) + "\n"); print("\n".join(out))

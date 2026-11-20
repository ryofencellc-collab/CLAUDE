"""Does adding the day's realized vol so far (known at decision time) fix the day-level IV error? LODO on 9 days, ATM-ish quotes."""
import math, glob, os, json
import numpy as np, pandas as pd, yfinance as yf
from edge import odte_score as O
from edge.odte import _iv, _bs
days = sorted(os.path.basename(p) for p in glob.glob("data/odte/2*"))
vix = yf.Ticker("^VIX").history(start="2026-10-01", end="2026-12-31")["Close"]; vix.index = vix.index.tz_localize(None).normalize()
rows = []
for d in days:
    x = O.load_day(d, "SPXW"); x = x[x.exp == d]
    V = float(vix[vix.index < pd.Timestamp(d)].iloc[-1]) / 100
    sp = x.groupby("t").spot.first().sort_index()
    lr = np.log(sp).diff()
    for t, g in x.groupby("t"):
        tt = g.t.iloc[0]
        if tt.time() < pd.Timestamp("10:00").time() or tt.time() > pd.Timestamp("15:50").time(): continue
        past = lr[(lr.index <= t) & (lr.index >= t.normalize() + pd.Timedelta(hours=9, minutes=31))]
        rv = float(np.sqrt((past ** 2).sum() / max(len(past), 1) * 252 * 390)) if len(past) > 10 else np.nan
        mins = (tt.normalize() + pd.Timedelta(hours=16) - tt).total_seconds() / 60; T = mins / (365 * 1440); S = float(g.spot.iloc[0])
        g = g[(g.bid > 0) & (g.ask >= g.bid) & ((g.K / S - 1).abs() < 0.004)]
        g = g[((g.cp == "C") & (g.K >= S)) | ((g.cp == "P") & (g.K <= S))]
        for r in g.itertuples():
            mid = (r.bid + r.ask) / 2; iv = _iv(S, r.K, T, mid, r.cp)
            if iv == iv: rows.append(dict(day=d, mins=mins, V=V, rv=rv, S=S, K=r.K, cp=r.cp, mid=mid, iv=iv, T=T))
D = pd.DataFrame(rows).dropna(); print(len(D), D.day.nunique())
D["lr"] = np.log(D.iv / D.V); D["lrv"] = np.log(D.rv / D.V)
mb = np.array([0, 15, 30, 60, 90, 120, 180, 240, 300, 360, 420]); D["mb"] = pd.cut(D.mins, mb)
out = []
for beta in (0.0, 0.2, 0.35, 0.5, 0.7):
    e = []
    for d in D.day.unique():
        tr, te = D[D.day != d], D[D.day == d]
        a = (tr.lr - beta * tr.lrv).groupby(tr.mb, observed=False).median()
        pred = np.exp(te.mb.map(a).astype(float).fillna(float((tr.lr - beta * tr.lrv).median())) + beta * te.lrv) * te.V
        model = np.array([_bs(S, K, T, v, cp)[2] for S, K, T, v, cp in zip(te.S, te.K, te.T, pred, te.cp)])
        e += list((model - te.mid.values) / te.mid.values)
    e = np.array(e); e = e[np.isfinite(e)]; out.append(dict(beta=beta, median_abs_pct=float(np.median(np.abs(e))), mean_pct=float(np.mean(e)), p90_abs_pct=float(np.percentile(np.abs(e), 90))))
print(pd.DataFrame(out).round(3).to_string())
json.dump(out, open("data/r66_cal_rv.json", "w"))

# ---- anchor 2: trailing realized intraday vol (RVk, prior k sessions of 1-min SPY returns), available historically from HistData
import glob as _g
rvd = {}
for f in sorted(_g.glob("data/ctx/2*.csv.gz")):
    c = pd.read_csv(f); c["Datetime"] = pd.to_datetime(c.Datetime, utc=True).dt.tz_convert("America/New_York")
    c = c[(c.Datetime.dt.time >= pd.Timestamp("09:31").time()) & (c.Datetime.dt.time <= pd.Timestamp("16:00").time())].dropna(subset=["SPY_close"])
    r = np.log(c.SPY_close).diff().dropna(); rvd[os.path.basename(f)[:10]] = float(np.sqrt((r ** 2).sum() * 252))
rv = pd.Series(rvd).sort_index(); print("daily RV", rv.round(3).to_dict())
for k in (5, 10, 20):
    D[f"rv{k}"] = D.day.map({d: rv[rv.index < d].tail(k).mean() if (rv.index < d).sum() >= min(k, 5) else np.nan for d in D.day.unique()})
res = []
for anchor in ["V", "rv5", "rv10", "rv20"]:
    X = D.dropna(subset=[anchor]); e = []
    for d in X.day.unique():
        tr, te = X[X.day != d], X[X.day == d]
        a = np.log(tr.iv / tr[anchor]).groupby(tr.mb, observed=False).median()
        pred = np.exp(te.mb.map(a).astype(float).fillna(float(np.log(tr.iv / tr[anchor]).median()))) * te[anchor]
        e += list(np.log(pred / te.iv))
    e = np.array(e); res.append(dict(anchor=anchor, days=X.day.nunique(), median_abs_log_iv_err=float(np.median(np.abs(e))), mean_log_err=float(np.mean(e))))
print(pd.DataFrame(res).round(3).to_string())

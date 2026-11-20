"""Round 66 amendment 2, M1: does real 0DTE ATM IV rise with intraday realized vol (rv30)? Writes data/r66_m1.json."""
import glob, json, math, os
import numpy as np, pandas as pd, yfinance as yf
from edge import odte_score as O
from edge.odte import _iv
from run_round66 import iv_model

vix = yf.Ticker("^VIX").history(start="2026-10-01", end="2026-12-31")["Close"]; vix.index = vix.index.tz_localize(None).normalize()
rows = []
for d in sorted(os.path.basename(p) for p in glob.glob("data/odte/2*")):
    x = O.load_day(d, "SPXW"); x = x[x.exp == d]
    V = float(vix[vix.index < pd.Timestamp(d)].iloc[-1]) / 100
    sp = x.groupby("t").spot.first().sort_index()
    lr = np.log(sp).diff()
    rv = np.sqrt((lr ** 2).rolling(30).sum() * 252 * 13)
    for t, g in x.groupby("t"):
        hm = t.hour * 60 + t.minute
        if hm < 600 or hm > 930 or not rv.get(t, np.nan) > 0: continue
        mins = 960 - hm - t.second / 60; T = mins / (365 * 1440); S = float(g.spot.iloc[0])
        g = g[(g.bid > 0) & (g.ask >= g.bid)]
        z = np.log(g.K / S) / (V * math.sqrt(T)); g = g[np.abs(z) < 0.25]
        ivs = [_iv(S, r.K, T, (r.bid + r.ask) / 2, r.cp) for r in g.itertuples()]
        ivs = [v for v in ivs if v == v and 0.02 < v < 3]
        if ivs: rows.append(dict(day=d, t=t, mins=mins, V=V, rv30=float(rv[t]), iv=float(np.median(ivs)), model=float(iv_model(V, mins, 0.0))))
D = pd.DataFrame(rows)
D["y"] = np.log(D.iv / D.model); D["x"] = np.log(D.rv30 / D.V)
b, a = np.polyfit(D.x, D.y, 1)
# day-demeaned slope too (within-day reaction, removes day-level IV error)
Dm = D.assign(y=D.y - D.groupby("day").y.transform("mean"), x=D.x - D.groupby("day").x.transform("mean"))
bw = np.polyfit(Dm.x, Dm.y, 1)[0]
q = D.rv30.quantile([.1, .5, .8, .9, .99]).round(4).to_dict()
hi = D[D.rv30 >= 0.1596]
out = dict(n=len(D), days=D.day.nunique(), beta=float(b), alpha=float(a), beta_within_day=float(bw), corr=float(np.corrcoef(D.x, D.y)[0, 1]),
           rv30_quantiles=q, n_rv_ge_016=len(hi), mean_ratio_rv_ge_016=float(np.exp(hi.y).mean()) if len(hi) else None,
           mean_ratio_all=float(np.exp(D.y).mean()), by_rv_bin=D.groupby(pd.qcut(D.rv30, 5)).apply(lambda g: float(np.exp(g.y).median())).to_dict())
out["by_rv_bin"] = {str(k): v for k, v in out["by_rv_bin"].items()}
json.dump(out, open("data/r66_m1.json", "w"), indent=1); print(json.dumps(out, indent=1))

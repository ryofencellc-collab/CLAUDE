"""Round 66 step 1: calibrate a 0DTE SPX option-pricing model to our real recorded Cboe quotes (9 days).
iv(K, t) = VIXprev/100 * A(minutes_to_close) * S(z),  z = ln(K/S) / (VIXprev/100 * sqrt(T));  spread(mid) by mid bins. Output data/r66_cal.json."""
import json, math, sys
import numpy as np, pandas as pd, yfinance as yf
from edge import odte_score as O
from edge.odte import _iv, _bs

days = O.days() if hasattr(O, "days") else None
import glob, os
days = sorted(os.path.basename(p) for p in glob.glob("data/odte/2*"))
vix = yf.Ticker("^VIX").history(start="2026-10-01", end="2026-12-31")["Close"]; vix.index = vix.index.tz_localize(None).normalize()
rows = []
for d in days:
    try: x = O.load_day(d, "SPXW")
    except Exception as e: print(d, e); continue
    if x.empty: continue
    x = x[x.exp == d]
    prev = vix[vix.index < pd.Timestamp(d)]
    if prev.empty: continue
    V = float(prev.iloc[-1]) / 100
    for t, g in x.groupby("t"):
        if g.t.iloc[0].time() < pd.Timestamp("09:45").time() or g.t.iloc[0].time() > pd.Timestamp("15:55").time(): continue
        close = g.t.iloc[0].normalize() + pd.Timedelta(hours=16)
        mins = (close - g.t.iloc[0]).total_seconds() / 60; T = mins / (365 * 1440)
        S = float(g.spot.iloc[0])
        g = g[(g.bid > 0) & (g.ask >= g.bid)]
        g = g[((g.cp == "C") & (g.K >= S)) | ((g.cp == "P") & (g.K <= S))]        # OTM only
        g = g[(g.K / S - 1).abs() < 0.03]
        for r in g.itertuples():
            mid = (r.bid + r.ask) / 2
            iv = _iv(S, r.K, T, mid, r.cp)
            if iv == iv and 0.02 < iv < 3:
                rows.append(dict(day=d, mins=mins, V=V, S=S, K=r.K, cp=r.cp, mid=mid, spread=r.ask - r.bid, iv=iv, z=math.log(r.K / S) / (V * math.sqrt(T))))
D = pd.DataFrame(rows); print("quotes", len(D), "days", D.day.nunique())
D["ratio"] = D.iv / D.V
atm = D[D.z.abs() < 0.25]
mb = [0, 15, 30, 60, 90, 120, 180, 240, 300, 360, 420]
A = atm.groupby(pd.cut(atm.mins, mb)).ratio.median()
D["A"] = np.interp(D.mins, [(a.left + a.right) / 2 for a in A.index], A.values)
D["s"] = D.iv / (D.V * D.A)
zb = np.arange(-6, 6.5, 0.5)
Sm = D.groupby(pd.cut(D.z, zb)).s.median().dropna()
pb = [0, 0.1, 0.25, 0.5, 1, 2, 4, 8, 16, 32, 64]
Sp = D.groupby(pd.cut(D.mid, pb)).spread.median().dropna()
cal = dict(A_mins=[(a.left + a.right) / 2 for a in A.index], A=A.values.tolist(),
           smile_z=[(a.left + a.right) / 2 for a in Sm.index], smile=Sm.values.tolist(),
           spread_mid=[(a.left + a.right) / 2 for a in Sp.index], spread=Sp.values.tolist(), n_quotes=len(D), days=sorted(D.day.unique().tolist()))
# out-of-sample check: leave-one-day-out mean abs pricing error of the model vs real mid, ATM-ish
err = []
for d in D.day.unique():
    tr, te = D[D.day != d], D[D.day == d]
    a_ = tr[tr.z.abs() < 0.25].groupby(pd.cut(tr[tr.z.abs() < 0.25].mins, mb)).ratio.median()
    Ai = np.interp(te.mins, cal["A_mins"], a_.values)
    trs = tr.iv / (tr.V * np.interp(tr.mins, cal["A_mins"], a_.values)); s_ = trs.groupby(pd.cut(tr.z, zb)).median()
    si = np.interp(te.z, [(a.left + a.right) / 2 for a in s_.index], s_.fillna(1).values)
    T = te.mins / (365 * 1440)
    model = [_bs(S, K, t_, v, cp)[2] for S, K, t_, v, cp in zip(te.S, te.K, T, te.V * Ai * si, te.cp)]
    e = (np.array(model) - te.mid.values)
    err.append(dict(day=d, n=len(te), mean_err=float(np.mean(e)), mae=float(np.mean(np.abs(e))), mae_pct_of_mid=float(np.median(np.abs(e) / te.mid.values))))
cal["lodo_error"] = err
json.dump(cal, open("data/r66_cal.json", "w"), indent=1)
print(pd.DataFrame({"A": A}).round(3).to_string()); print(Sm.round(3).to_string()); print(Sp.round(3).to_string()); print(pd.DataFrame(err).round(3).to_string())

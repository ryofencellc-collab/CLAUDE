"""Round 66 amendment 2: descriptive real-quote replay of the PASS rules on the recorded 1-minute SPXW quotes (Cboe days)."""
import glob, os
import numpy as np, pandas as pd
from edge import odte_score as O
from run_round66 import day_features, FEATS, SLOTS

FI = {f: i for i, f in enumerate(FEATS)}
RULES = [  # (name, [(feat, op, thr)], type, pt)  -- the 15 PASS configurations from reports/ROUND66.md
    ("rv30>=.1596 & ret30<=-8.979", [("rv30", ">=", .1596), ("ret30", "<=", -8.979)], "C30", .25),
    ("rv30>=.1596 & vs_low<=15.94", [("rv30", ">=", .1596), ("vs_low", "<=", 15.94)], "C30", .25),
    ("rv30>=.1596 & ema9_21<=-1.723", [("rv30", ">=", .1596), ("ema9_21", "<=", -1.723)], "C30", .25),
    ("macd_slope<=-.5211 & rv30>=.1596", [("macd_slope", "<=", -.5211), ("rv30", ">=", .1596)], "C50", .5),
    ("rv30>=.1353 & ema9_21<=-1.723", [("rv30", ">=", .1353), ("ema9_21", "<=", -1.723)], "C30", .25),
    ("macd_slope<=-.5211 & rv30>=.1596", [("macd_slope", "<=", -.5211), ("rv30", ">=", .1596)], "C30", .25),
    ("macd_slope<=-.5211 & rv30>=.1596", [("macd_slope", "<=", -.5211), ("rv30", ">=", .1596)], "C50", .25),
    ("rv30>=.1596", [("rv30", ">=", .1596)], "C30", .25),
    ("rv30>=.1596 & vs_low<=15.94", [("rv30", ">=", .1596), ("vs_low", "<=", 15.94)], "C30", .5),
    ("rv30>=.1596 & rsi<=43.63", [("rv30", ">=", .1596), ("rsi", "<=", 43.63)], "C30", .25),
    ("rv30>=.1997", [("rv30", ">=", .1997)], "C50", .5),
    ("rv30>=.1353 & ret30<=-8.979", [("rv30", ">=", .1353), ("ret30", "<=", -8.979)], "C30", .25),
    ("macd_slope<=-.5211 & rv30>=.1596", [("macd_slope", "<=", -.5211), ("rv30", ">=", .1596)], "C30", .5),
    ("rv30>=.1596", [("rv30", ">=", .1596)], "C30", .5),
    ("rv30>=.1596 & vs_open<=-26.61", [("rv30", ">=", .1596), ("vs_open", "<=", -26.61)], "C30", .5),
]
missing = {f for _, cs, _, _ in RULES for f, _, _ in cs} - set(FI); assert not missing, missing


def trade(x, d, s_time, typ, pt):
    """Real trade: buy at ask at s_time, exit at bid on first PT hit else 15:55 bid. $ per contract, $1/side fee."""
    g = x[x.t == s_time]; g = g[(g.cp == "C") & (g.bid > 0) & (g.ask > 0.05)]
    if g.empty: return np.nan
    S = float(g.spot.iloc[0])
    r = g.iloc[(g.K - S).abs().argmin()] if typ == "C50" else g.iloc[(g.delta - 0.30).abs().argmin()]
    ask0 = float(r.ask); path = x[(x.cp == "C") & (x.K == r.K) & (x.t > s_time) & (x.t <= s_time.normalize() + pd.Timedelta(hours=15, minutes=55))].sort_values("t")
    if path.empty: return np.nan
    hit = path[path.bid / ask0 - 1 >= pt]
    bid = float(hit.bid.iloc[0]) if len(hit) else float(path.bid.iloc[-1])
    return (bid - ask0) * 100 - 2.0


rows = []
for d in sorted(os.path.basename(p) for p in glob.glob("data/odte/2*")):
    x = O.load_day(d, "SPXW"); x = x[x.exp == d].copy(); x["t"] = x.t.dt.floor("min")
    sp = x.groupby("t").spot.first()
    idx = pd.date_range(pd.Timestamp(d + " 09:31", tz=sp.index.tz), periods=390, freq="1min")
    c = sp.reindex(idx).ffill().bfill().to_numpy(float)
    F = day_features(c, c[0], 0, 0, 0, 0, 0, pd.Timestamp(d).weekday())
    for si, s in enumerate(SLOTS):
        st = idx[s]
        for typ, pt in {("C30", .25), ("C30", .5), ("C50", .25), ("C50", .5)}:
            rows.append(dict(day=d, slot=si, typ=typ, pt=pt, pnl=trade(x, d, st, typ, pt), **{f: F[si, FI[f]] for f in FI}))
T = pd.DataFrame(rows)
base = T.groupby(["slot", "typ", "pt"]).pnl.mean().rename("base")
T = T.join(base, on=["slot", "typ", "pt"]); T["excess"] = T.pnl - T.base
out = []
for name, conds, typ, pt in RULES:
    m = (T.typ == typ) & (T.pt == pt)
    for f, op, thr in conds: m &= (T[f] >= thr) if op == ">=" else (T[f] <= thr)
    first = T[m & T.pnl.notna()].sort_values("slot").groupby("day").head(1)
    out.append(dict(rule=name, type=typ, pt=pt, days_triggered=len(first), mean_pnl=round(first.pnl.mean(), 2), mean_excess=round(first.excess.mean(), 2),
                    wins=int((first.excess > 0).sum())))
R = pd.DataFrame(out)
uncond = T.groupby(["typ", "pt"]).pnl.mean().round(2)
txt = ["# Round 66: real-quote replay of the PASS rules (descriptive, ≤ 9 days — can veto, cannot confirm)", "",
       f"Recorded SPXW days: {T.day.nunique()} ({T.day.min()} → {T.day.max()}). Real ask in, real bid out, $1/side.", "",
       R.to_markdown(index=False), "", "Unconditional mean P&L of the same trades, every slot every day:", "", uncond.to_frame().to_markdown(), "",
       f"rv30 at entry slots on these days: median {T.rv30.median():.3f}, share ≥ 0.1596: {(T.rv30 >= .1596).mean():.0%}."]
open("reports/ROUND66_REPLAY.md", "w").write("\n".join(txt) + "\n"); print("\n".join(txt))

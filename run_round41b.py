"""Round 41b (diagnostic, PROTOCOL_ROUND41.md amendment): Round 41 flow with a queue ahead of us at 99c."""
import numpy as np, pandas as pd
F = pd.read_pickle("data/r41/flow.pkl")
HOLD = pd.Timestamp("2026-09-01", tz="UTC")
FEE_C = 100 * 0.0175 * 0.99 * 0.01
RULES = {"base z>=6": lambda f: f.zlag >= 6, "z>=10": lambda f: f.zlag >= 10, "z>=15": lambda f: f.zlag >= 15,
         "z>=20": lambda f: f.zlag >= 20, "z>=6 & d5>-1*sqrt5": lambda f: (f.zlag >= 6) & (f.d5 > -np.sqrt(5)),
         "z>=15 & d5>-1*sqrt5": lambda f: (f.zlag >= 15) & (f.d5 > -np.sqrt(5))}
out = ["# Round 41b: the same flow, but our 99c bid waits behind a queue", "",
       "Diagnostic for the failed Round 41 sanity check (no-queue loss share 0.77% Oct 29+ vs paper 3.21%). Per market and side, "
       "flow fills the queue ahead first; we get what passes it (≤ 1,000 contracts). Queue sizes from the paper bot "
       "(median KXBTCD ≈ 18.5k, KXETHD ≈ 20k at placement).", ""]
rows = []
for name, fn in RULES.items():
    g = F[fn(F)].sort_values("ts")
    for Q in (0, 2000, 5000, 20000):
        fills = []
        for (tk, side), x in g.groupby(["ticker", "side"]):
            cum = x.n.cumsum().values
            got = np.clip(cum - Q, 0, 1000); got = np.diff(np.concatenate([[0], got]))
            fills.append(pd.DataFrame({"ts": x.ts.values, "n": got, "won": x.won.values, "event": x.event.values}))
        f = pd.concat(fills) if fills else pd.DataFrame(columns=["ts", "n", "won", "event"])
        f = f[f.n > 0]
        for per, y in [("dev", f[f.ts < HOLD]), ("holdout", f[f.ts >= HOLD]), ("Oct 29+", f[f.ts >= pd.Timestamp("2026-10-29", tz="UTC")])]:
            tot = y.n.sum(); L = y.n[~y.won.astype(bool)].sum() / tot if tot else np.nan
            rows.append(dict(rule=name, queue=Q, period=per, our_fills=round(tot), L=f"{L:.2%}" if tot else "",
                             cents=round(1 - 100 * L - FEE_C, 3) if tot else np.nan, pnl_usd=round(tot * (1 - 100 * L - FEE_C) / 100, 2) if tot else 0))
out += [pd.DataFrame(rows).to_markdown(index=False), ""]
open("reports/ROUND41B.md", "w").write("\n".join(out) + "\n"); print("\n".join(out))

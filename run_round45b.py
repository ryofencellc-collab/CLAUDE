"""Round 45b: list Round 45's passing cells (the report only showed the top 40 by dev t)."""
import numpy as np, pandas as pd
import run_round45 as r
d = r.prep(pd.read_pickle("data/r45/trades.pkl"))
rows = []
for (c, pb, tb), x in d.groupby(["category", "pb", "tb"], observed=True):
    dv, ho = r.clustered(x[x.dev]), r.clustered(x[~x.dev])
    rows.append(dict(category=c, maker_price=pb, time_left=tb, dev_events=dv["events"], dev_ret=dv["ret"], dev_t=dv["t"],
                     hold_events=ho["events"], hold_ret=ho["ret"], hold_t=ho["t"], hold_contracts=ho.get("contracts", 0)))
T = pd.DataFrame(rows)
cand = (T.dev_events >= 100) & (T.dev_ret >= 0.03) & (T.dev_t >= 3)
T["pass"] = cand & (T.hold_events >= 30) & (T.hold_ret > 0) & (T.hold_t >= 2)
f = lambda v: f"{v:.1%}" if pd.notna(v) else ""
P = T[cand].sort_values("hold_t", ascending=False).copy()
for c in ("dev_ret", "hold_ret"): P[c] = P[c].map(f)
out = ["# Round 45b: Round 45 candidate and passing cells", "",
       f"Candidates (dev: ≥ 100 events, ≥ +3%/$, t ≥ 3): {int(cand.sum())}; pass on holdout (≥ 30 events, > 0, t ≥ 2): {int(T['pass'].sum())}.", "",
       P.round(2).to_markdown(index=False), "",
       "Holdout maker return when the maker holds the favourite (.70–.99), by category:", ""]
fav = d[(~d.dev) & (d.x >= 0.70)]
out += [pd.DataFrame([dict(category=c, **{k: (f(v) if k == "ret" else v) for k, v in r.clustered(x).items()}) for c, x in fav.groupby("category")]).to_markdown(index=False)]
open("reports/ROUND45B.md", "w").write("\n".join(out) + "\n"); print("\n".join(out))

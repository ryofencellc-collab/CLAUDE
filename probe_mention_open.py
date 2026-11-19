"""Probe for Round 58f: what open Mentions markets look like (open_time, status) right now. Writes probe/mention/open_now.csv."""
import os
import pandas as pd
from edge import mention_live as L
rows = []
for s in L.series_list()[:80]:
    for st in ("open", None):
        p = {"series_ticker": s, "limit": 200}
        if st: p["status"] = st
        j = L.get("markets", p) or {}
        for m in j.get("markets", []):
            rows.append(dict(q=st or "any", series=s, ticker=m["ticker"], status=m.get("status"), open_time=m.get("open_time"),
                             close_time=m.get("close_time"), created=m.get("created_time"), yes_ask=m.get("yes_ask_dollars"), result=m.get("result")))
D = pd.DataFrame(rows); os.makedirs("probe/mention", exist_ok=True); D.to_csv("probe/mention/open_now.csv", index=False)
print(len(D)); print(D.groupby(["q", "status"]).size())
o = D[D.q == "open"]; print("open markets:", len(o)); print(o.sort_values("open_time").tail(15).to_string())
a = D[(D.q == "any") & (D.status.isin(["active", "open", "initialized", "unopened"]))]; print(a.sort_values("open_time").tail(15).to_string())

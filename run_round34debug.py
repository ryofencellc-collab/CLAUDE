import json, run_round34 as R, run_round34b as B
out = {}
for name, w in [("Lucerys", "0x1387d145aaf01f6e33b66525dda6e1f51f6955f8"), ("k9Q2", "0xd0d6053c3c37e727402d84c14069780d360993aa"),
                ("0x50f7", "0xee65685de42f8de9a03b4c53ee77d56a20d2cfc9")]:
    j = R.get("trades", {"user": w, "limit": 500})
    tr = (j or {}).get("data", [])
    pag = (j or {}).get("pagination")
    slugs = list(dict.fromkeys(t["slug"] for t in tr))[:3]
    g = {}
    for s in slugs:
        r = R.S.get(f"{B.G}/markets", params={"slug": s}, timeout=30)
        g[s] = {"status": r.status_code, "n": len(r.json()) if r.status_code == 200 else None,
                "first": {k: (r.json()[0].get(k) if r.status_code == 200 and r.json() else None)
                          for k in ("closed", "outcomePrices", "endDate", "closedTime", "umaResolutionStatus", "active")}}
        r2 = R.S.get(f"{B.G}/markets", params={"slug": s, "closed": "true"}, timeout=30)
        g[s]["closed_query_n"] = len(r2.json()) if r2.status_code == 200 else r2.status_code
    acts = (R.get("activity", {"user": w, "limit": 50}) or {}).get("data", [])
    out[name] = {"n_trades_page": len(tr), "pagination": pag, "first_trade": tr[0] if tr else None,
                 "last_ts": tr[-1]["timestamp"] if tr else None, "slugs": slugs, "gamma": g,
                 "activity_types": sorted({a.get("type") for a in acts}), "activity_sample": acts[:2]}
json.dump(out, open("probe/r34b_debug.json", "w"), indent=1, default=str)
print(json.dumps(out, indent=1, default=str)[:6000])

"""Timing/coverage probe for DoltHub post-no-preference/options (run in Actions)."""
import json, time, urllib.parse
import requests
API = "https://www.dolthub.com/api/v1alpha1/post-no-preference/options/master"
S = requests.Session()


def q(sql):
    t = time.time()
    r = S.get(API, params={"q": sql}, timeout=120)
    j = r.json()
    return j.get("query_execution_status"), j.get("query_execution_message", "")[:120], len(j.get("rows", [])), round(time.time() - t, 2), j.get("rows", [])


out = {}
for d in ["2019-02-15", "2019-06-14", "2020-03-16", "2021-06-18", "2022-06-17", "2023-06-16", "2024-06-14", "2025-06-13", "2025-12-12", "2026-06-12", "2026-11-06"]:
    out[d] = q(f"SELECT COUNT(*) AS n, MIN(expiration), MAX(expiration) FROM option_chain WHERE date='{d}' AND act_symbol='SPY'")[:5]
for sym in ["QQQ", "IWM", "AAPL", "NVDA", "TSLA", "MSFT", "AMZN", "META"]:
    out[sym] = q(f"SELECT COUNT(*) AS n FROM option_chain WHERE date='2024-06-14' AND act_symbol='{sym}'")[:5]
st, msg, n, secs, rows = q("SELECT * FROM option_chain WHERE date='2024-06-14' AND act_symbol='SPY' AND expiration<='2024-08-20' LIMIT 1000 OFFSET 0")
out["page_1000"] = (st, msg, n, secs)
st, msg, n, secs, rows = q("SELECT DISTINCT date FROM option_chain WHERE date BETWEEN '2024-06-01' AND '2024-06-30' AND act_symbol='SPY'")
out["june2024_dates"] = (st, msg, n, secs, [r.get("date") for r in rows])
out["vol_hist"] = q("SELECT * FROM volatility_history WHERE act_symbol='SPY' AND date='2024-06-14'")
json.dump(out, open("probe/opt/dolt_timing.json", "w"), indent=1, default=str)
print(json.dumps(out, indent=1, default=str)[:5000])

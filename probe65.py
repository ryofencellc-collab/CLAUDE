"""Round 65 data probe: how to get hourly history for RESOLVED Polymarket markets."""
import json, time, requests
G = "https://gamma-api.polymarket.com"; C = "https://clob.polymarket.com"
def get(u, p=None):
    r = requests.get(u, params=p, timeout=40, headers={"User-Agent": "research-probe"}); return (r.status_code, r.json() if r.ok else r.text[:200])
ev = get(f"{G}/events", {"tag_slug": "fed-rates", "closed": "true", "limit": 100})[1]
e = next(x for x in ev if "fed decision in" in x["title"].lower() and "2026" in (x.get("endDate") or ""))
m = max(e["markets"], key=lambda m: float(m.get("volume") or 0))
tok = json.loads(m["clobTokenIds"])[0]; end = int(pd_end) if (pd_end := __import__("pandas").Timestamp(e["endDate"]).timestamp()) else 0
print(e["title"], e["endDate"], m["question"], "closedTime", m.get("closedTime"))
for p in [dict(interval="all", fidelity=60), dict(interval="max", fidelity=60), dict(interval="1m", fidelity=60), dict(interval="all"),
          dict(startTs=end - 7 * 86400, endTs=end, fidelity=60), dict(startTs=end - 30 * 86400, endTs=end, fidelity=60),
          dict(startTs=end - 7 * 86400, endTs=end, fidelity=1), dict(startTs=end - 2 * 86400, endTs=end), dict(startTs=end - 90 * 86400, endTs=end, fidelity=1440)]:
    s, j = get(f"{C}/prices-history", {"market": tok, **p})
    h = j.get("history", []) if isinstance(j, dict) else []
    print(p, s, len(h), h[:1], h[-1:] if h else "", (j if not h else "")[:150] if isinstance(j, str) else "")
    time.sleep(0.5)

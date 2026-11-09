"""One-off: Kalshi liquidity incentive programs and Polymarket liquidity rewards (public endpoints)."""
import json, os, requests
os.makedirs("probe/rewards", exist_ok=True)
H = {"User-Agent": "Mozilla/5.0 (research probe)"}
K = "https://api.elections.kalshi.com/trade-api/v2"
out = {}
progs, cursor = [], None
for status in ("active", None):
    cursor = None
    for _ in range(50):
        p = {"limit": 1000}
        if status: p["status"] = status
        if cursor: p["cursor"] = cursor
        r = requests.get(f"{K}/incentive_programs", params=p, headers=H, timeout=30)
        out.setdefault("kalshi_status", []).append([status, r.status_code, r.text[:300]])
        if r.status_code != 200: break
        j = r.json(); progs += j.get("incentive_programs", [])
        cursor = j.get("next_cursor") or j.get("cursor")
        if not cursor or not j.get("incentive_programs"): break
    if progs: break
json.dump(progs, open("probe/rewards/kalshi_programs.json", "w"), indent=1)
out["kalshi_n"] = len(progs)
# Polymarket: markets with rewards
pm = []
for off in range(0, 10000, 500):
    r = requests.get("https://gamma-api.polymarket.com/markets", params={"closed": "false", "active": "true", "limit": 500, "offset": off}, headers=H, timeout=40)
    if r.status_code != 200 or not r.json(): break
    for m in r.json():
        if m.get("rewardsMinSize") or m.get("clobRewards"):
            pm.append({k: m.get(k) for k in ("slug", "question", "rewardsMinSize", "rewardsMaxSpread", "clobRewards", "volume24hr", "liquidity", "bestBid", "bestAsk", "endDate", "spread")})
json.dump(pm, open("probe/rewards/poly_reward_markets.json", "w"), indent=1)
out["poly_n"] = len(pm)
for u in ("https://clob.polymarket.com/rewards/markets/current", "https://clob.polymarket.com/sampling-markets"):
    try:
        r = requests.get(u, headers=H, timeout=30); out[u] = [r.status_code, r.text[:1500]]
    except Exception as e:
        out[u] = repr(e)
json.dump(out, open("probe/rewards/report.json", "w"), indent=1)
print(json.dumps(out)[:3000])

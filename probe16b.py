"""One-off snapshot: same upcoming game on Kalshi and Polymarket; how big are the price gaps?"""
import json
import re
import urllib.request

def get(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=30) as r:
            return json.load(r)
    except Exception as e:
        return {"error": str(e)}

K = "https://api.elections.kalshi.com/trade-api/v2"
G = "https://gamma-api.polymarket.com"
kal = {}
for s in ["KXNFLGAME", "KXNBAGAME", "KXNHLGAME", "KXNCAAFGAME"]:
    cursor = ""
    while True:
        j = get(f"{K}/markets?series_ticker={s}&status=open&limit=200&cursor={cursor}")
        for m in j.get("markets", []):
            kal.setdefault(m["event_ticker"], []).append(m)
        cursor = j.get("cursor") or ""
        if not cursor or not j.get("markets"):
            break
print("kalshi game events:", len(kal))
poly = []
for tag in ["nfl", "nba", "nhl", "college-football", "ncaaf"]:
    for off in range(0, 1000, 100):
        evs = get(f"{G}/events?tag_slug={tag}&active=true&closed=false&limit=100&offset={off}")
        if not isinstance(evs, list) or not evs:
            break
        poly += [e for e in evs if re.search(r" vs\.? ", e.get("title", ""))]
print("polymarket game events:", len(poly), [e["title"] for e in poly[:8]])
norm = lambda x: re.sub(r"[^a-z]", "", x.lower())
gaps = []
for e in poly:
    teams = [t.strip() for t in re.split(r" vs\.? ", e["title"])]
    if len(teams) != 2:
        continue
    for ev, ms in kal.items():
        names = {norm(m.get("yes_sub_title", "")): m for m in ms}
        hit = {t: next((m for n, m in names.items() if n and (n in norm(t) or norm(t).endswith(n) or norm(t) in n)), None) for t in teams}
        if all(hit.values()):
            mk = next((m for m in e.get("markets", []) if m.get("outcomes") and set(json.loads(m["outcomes"])) >= set(teams)), None)
            if mk is None:
                break
            outs, prices = json.loads(mk["outcomes"]), [float(x) for x in json.loads(mk["outcomePrices"])]
            for i, t in enumerate(teams):
                other = teams[1 - i]
                k_ask = float(hit[t]["yes_ask_dollars"] or 1)
                p_other = prices[outs.index(other)]  # mid price on Polymarket (gamma), not the ask
                gaps.append((round(k_ask + p_other, 3), e["title"], t, k_ask, other, p_other, mk.get("bestAsk"), mk.get("spread")))
            break
gaps.sort()
print("matched games x sides:", len(gaps))
for g in gaps[:15]:
    print(g)
print("pairs with Kalshi ask + Poly price < 0.965:", sum(g[0] < 0.965 for g in gaps), "of", len(gaps))

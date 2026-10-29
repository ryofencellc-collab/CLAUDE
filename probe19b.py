"""Hindsight size of the 'lottery flow' by Kalshi category: contracts where a taker bought the
eventual loser at <= 2c, in recently settled markets. An upper bound on what resting 98-99c bids
could earn, before asking whether the outcome was knowable in time."""
import collections, json, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

K = "https://api.elections.kalshi.com/trade-api/v2"


def get(path, **p):
    u = f"{K}/{path}?" + urllib.parse.urlencode(p)
    for _ in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60) as r:
                return json.load(r)
        except Exception:
            pass
    return {}


cat = {s["ticker"]: s.get("category") for s in get("series").get("series", [])}
ms, cur = [], None
for _ in range(15):
    j = get("markets", status="settled", limit=1000, **({"cursor": cur} if cur else {}))
    ms += j.get("markets", [])
    cur = j.get("cursor")
    if not cur:
        break
print("settled markets fetched", len(ms))
for m in ms:
    m["_series"] = m["event_ticker"].split("-")[0]
    m["_cat"] = cat.get(m["_series"], "?")
    m["_vol"] = float(m.get("volume_fp") or m.get("volume") or 0)
ms = [m for m in ms if m.get("result") in ("yes", "no")]
top = sorted(ms, key=lambda m: -m["_vol"])[:1500]


def flow(m):
    loser = "no" if m["result"] == "yes" else "yes"
    j = get("markets/trades", ticker=m["ticker"], limit=1000)
    n = 0.0
    for t in j.get("trades", []):
        px = float(t.get(f"{loser}_price_dollars") or 0)
        if t.get("taker_side") == loser and 0 < px <= 0.02:
            n += float(t.get("count_fp") or t.get("count") or 0) * px  # what the winning-side maker earns
    return m, n


with ThreadPoolExecutor(8) as ex:
    res = list(ex.map(flow, top))
by_cat, by_ser = collections.defaultdict(float), collections.defaultdict(float)
span = [m["close_time"] for m in top if m.get("close_time")]
for m, usd in res:
    by_cat[m["_cat"]] += usd
    by_ser[(m["_cat"], m["_series"])] += usd
print("close_time span", min(span), max(span))
print("maker profit pool at 98-99c ($, gross) by category:")
for k, v in sorted(by_cat.items(), key=lambda x: -x[1]):
    print(f"  {k:<25} ${v:,.0f}")
print("top series:")
for k, v in sorted(by_ser.items(), key=lambda x: -x[1])[:40]:
    print(f"  {k[0]:<22} {k[1]:<28} ${v:,.0f}")

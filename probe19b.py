"""Hindsight size of the 'lottery flow' by Kalshi series: contracts where a taker bought the
eventual loser at <= 2c, in markets settled over the last 30 days. An upper bound on what resting
98-99c bids could earn, before asking whether the outcome was knowable in time."""
import json, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

K = "https://api.elections.kalshi.com/trade-api/v2"
SERIES = ["KXHIGHNY", "KXHIGHCHI", "KXLOWTNYC",                       # weather (reference)
          "KXNFLGAME", "KXNBAGAME", "KXMLBGAME", "KXNHLGAME", "KXNCAAFGAME", "KXEPLGAME", "KXUCLGAME",
          "KXUFCFIGHT", "KXATPMATCH", "KXWTAMATCH", "KXMLSGAME", "KXNFLSPREAD", "KXNFLTOTAL", "KXMLBTOTAL",
          "KXBTCD", "KXETHD", "KXBTC", "KXETH", "KXSOLD", "KXBTC15M", "KXETH15M",
          "KXINXD", "KXINX", "KXNASDAQ100D", "KXNASDAQ100", "KXINXU",
          "KXCPI", "KXFED", "KXPAYROLLS", "KXJOBLESSCLAIMS", "KXGASD", "KXAAAGASD",
          "KXTRUMPMENTION", "KXMENTION", "KXNETFLIXRANK", "KXSPOTIFY", "KXTOPSONG", "KXBILLBOARD",
          "KXTSAW", "KXRT", "KXNYTHEAD", "KXEARNINGSMENTION"]
since = int(time.time()) - 30 * 86400


def get(path, **p):
    u = f"{K}/{path}?" + urllib.parse.urlencode(p)
    for i in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60) as r:
                return json.load(r)
        except Exception:
            time.sleep(2 ** i)
    return {}


def markets(s):
    out, cur = [], None
    for _ in range(20):
        j = get("markets", series_ticker=s, status="settled", min_close_ts=since, limit=1000, **({"cursor": cur} if cur else {}))
        out += j.get("markets", [])
        cur = j.get("cursor")
        if not cur or not j.get("markets"):
            break
    return [m for m in out if m.get("result") in ("yes", "no")]


def flow(m):
    loser = "no" if m["result"] == "yes" else "yes"
    usd, n, cur = 0.0, 0, None
    for _ in range(10):
        j = get("markets/trades", ticker=m["ticker"], limit=1000, **({"cursor": cur} if cur else {}))
        for t in j.get("trades", []):
            px = float(t.get(f"{loser}_price_dollars") or 0)
            if t.get("taker_side") == loser and 0 < px <= 0.02:
                usd += float(t.get("count_fp") or t.get("count") or 0) * px  # what the winning-side maker earns
                n += 1
        cur = j.get("cursor")
        if not cur or not j.get("trades"):
            break
    return usd, n


print(f"{'series':<20}{'markets':>8}{'pool $/30d':>12}{'trades':>9}  (pool = loser bought at <=2c; maker earns that)")
rows = []
for s in SERIES:
    ms = markets(s)
    if not ms:
        print(f"{s:<20}{0:>8}")
        continue
    ms = sorted(ms, key=lambda m: -float(m.get("volume_fp") or m.get("volume") or 0))
    sample = ms[:400]
    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(flow, sample))
    usd = sum(r[0] for r in res) * len(ms) / len(sample)
    rows.append((s, len(ms), usd))
    print(f"{s:<20}{len(ms):>8}{usd:>12,.0f}{sum(r[1] for r in res):>9}{'  (scaled from top 400)' if len(ms) > 400 else ''}", flush=True)
print("\nRANKED")
for s, n, usd in sorted(rows, key=lambda r: -r[2]):
    print(f"  {s:<20} ${usd:,.0f} per 30 days over {n} markets")

"""Everything-scan: does a resting 98-99c bid make money anywhere on Kalshi, with no outcome knowledge?

Sample N random hours from the last 30 days and fetch every public trade in each hour, across all
series. Each trade where a taker bought a side at <= 2c was filled by a maker bidding >= 98c on the
other side. Once the market settles, that maker earned px per contract (long shot lost) or lost
1 - px (long shot won). Aggregate the net by category and series. No series is skipped, and the
pnl is hindsight-free per fill: it is what blindly resting the bid would have made."""
import collections, json, random, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

K = "https://api.elections.kalshi.com/trade-api/v2"
HOURS = int(sys.argv[1]) if len(sys.argv) > 1 else 48
MAX_PAGES = 60  # per hour (60k trades); reported if hit


def get(path, **p):
    u = f"{K}/{path}?" + urllib.parse.urlencode(p)
    for i in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60) as r:
                return json.load(r)
        except Exception:
            time.sleep(2 ** i)
    return {}


now = int(time.time()) // 3600 * 3600
random.seed(19)
hours = sorted(random.sample(range(now - 30 * 86400, now - 2 * 86400, 3600), HOURS))  # settled by now (mostly)


def hour_trades(h):
    out, cur, pages = [], None, 0
    while pages < MAX_PAGES:
        j = get("markets/trades", min_ts=h, max_ts=h + 3600, limit=1000, **({"cursor": cur} if cur else {}))
        ts = j.get("trades", [])
        out += ts
        pages += 1
        cur = j.get("cursor")
        if not cur or not ts:
            break
    return h, out, pages >= MAX_PAGES


with ThreadPoolExecutor(6) as ex:
    res = list(ex.map(hour_trades, hours))
total = sum(len(t) for _, t, _ in res)
capped = sum(c for *_, c in res)
cheap = []
for _, ts, _ in res:
    for t in ts:
        side = t.get("taker_side")
        px = float(t.get(f"{side}_price_dollars") or 0)
        if 0 < px <= 0.02:
            cheap.append((t["ticker"], side, px, float(t.get("count_fp") or t.get("count") or 0)))
print(f"hours sampled {HOURS}; trades {total:,}; hours capped at {MAX_PAGES} pages: {capped}; long-shot fills {len(cheap):,}")

tickers = sorted({c[0] for c in cheap})
result = {}


def mk(t):
    j = get(f"markets/{t}")
    m = j.get("market") or {}
    if not m:
        j = get(f"historical/markets/{t}")
        m = j.get("market") or {}
    return t, m.get("result"), m.get("event_ticker", "")


with ThreadPoolExecutor(10) as ex:
    for t, r, ev in ex.map(mk, tickers):
        result[t] = (r, ev)
cat = {s["ticker"]: s.get("category", "?") for s in get("series").get("series", [])}

agg = collections.defaultdict(lambda: [0, 0.0, 0.0, 0, 0.0])  # fills, contracts, net, longshot wins, gross
unsettled = 0
for t, side, px, n in cheap:
    r, ev = result.get(t, (None, ""))
    if r not in ("yes", "no"):
        unsettled += 1
        continue
    ser = ev.split("-")[0] if ev else t.split("-")[0]
    won = r == side
    pnl = -(1 - px) * n if won else px * n
    for key in (("CAT", cat.get(ser, "?")), ("SER", f"{cat.get(ser, '?')}|{ser}")):
        a = agg[key]
        a[0] += 1; a[1] += n; a[2] += pnl; a[3] += won; a[4] += px * n
scale = 720 / HOURS
print(f"unsettled fills skipped {unsettled:,}; scale to 30 days x{scale:.1f}\n")
print(f"{'category':<26}{'fills':>8}{'contracts':>12}{'longshot wins':>14}{'net $/30d':>12}{'gross $/30d':>12}")
for (k, name), a in sorted(agg.items(), key=lambda x: -x[1][2]):
    if k == "CAT":
        print(f"{name:<26}{a[0]:>8,}{a[1]:>12,.0f}{a[3]:>14,}{a[2] * scale:>12,.0f}{a[4] * scale:>12,.0f}")
print("\nTOP 40 SERIES by net (min 20 fills)")
sers = [(n, a) for (k, n), a in agg.items() if k == "SER" and a[0] >= 20]
for name, a in sorted(sers, key=lambda x: -x[1][2])[:40]:
    print(f"  {name:<45}{a[0]:>7,} fills {a[3]:>5} longshot wins  net ${a[2] * scale:>10,.0f}/30d  gross ${a[4] * scale:>9,.0f}")
print("\nBOTTOM 15 SERIES by net")
for name, a in sorted(sers, key=lambda x: x[1][2])[:15]:
    print(f"  {name:<45}{a[0]:>7,} fills {a[3]:>5} longshot wins  net ${a[2] * scale:>10,.0f}/30d")

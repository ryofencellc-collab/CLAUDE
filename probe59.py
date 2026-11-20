"""Backlog 59 step-1 probe: matched Kalshi/Polymarket events with minute price history (Fed decision, CPI, recession etc.)."""
import json, os, re, time, requests
OUT = "probe/leadlag"; os.makedirs(OUT, exist_ok=True)
K = "https://api.elections.kalshi.com/trade-api/v2"; G = "https://gamma-api.polymarket.com"; C = "https://clob.polymarket.com"
def get(u, p=None):
    try:
        r = requests.get(u, params=p, timeout=30, headers={"User-Agent": "research-probe"}); return r.json() if r.ok else {"status": r.status_code}
    except Exception as e: return {"error": repr(e)}
log = {}
# Kalshi series about the Fed / macro
S = get(f"{K}/series", {"limit": 1000}).get("series", [])
ks = [s for s in S if re.search(r"fed|fomc|rate|cpi|inflation|recession|unemploy|payroll|gdp", (s.get("title") or "").lower())]
log["kalshi_macro_series"] = [(s["ticker"], s.get("title")) for s in ks][:80]
# Polymarket events on the same topics (closed ones too, for history)
pe = []
for q in ["fed", "fed-rates", "economy", "inflation", "cpi"]:
    for closed in ("true", "false"):
        for off in range(0, 500, 100):
            e = get(f"{G}/events", {"tag_slug": q, "closed": closed, "limit": 100, "offset": off})
            if not isinstance(e, list) or not e: break
            pe += e
seen = {}
for e in pe: seen[e.get("id")] = e
pe = list(seen.values())
log["poly_events"] = len(pe)
log["poly_titles"] = sorted({e.get("title") for e in pe})[:200]
# one price-history sample
tok = None
for e in pe:
    for m in e.get("markets", []):
        t = m.get("clobTokenIds")
        if t: tok = json.loads(t)[0] if isinstance(t, str) else t[0]; break
    if tok: break
h = get(f"{C}/prices-history", {"market": tok, "interval": "max", "fidelity": 1}) if tok else {}
log["poly_history_sample_points"] = len(h.get("history", [])) if isinstance(h, dict) else None
log["poly_history_sample_head"] = (h.get("history", [])[:3] if isinstance(h, dict) else None)
# Kalshi candlesticks sample on a settled Fed market
if ks:
    s0 = next((s["ticker"] for s in ks if "FED" in s["ticker"]), ks[0]["ticker"])
    m = get(f"{K}/markets", {"series_ticker": s0, "status": "settled", "limit": 5}).get("markets", [])
    if m:
        mm = m[0]; end = int(time.time()); st = end - 400 * 86400
        c = get(f"{K}/series/{s0}/markets/{mm['ticker']}/candlesticks", {"start_ts": st, "end_ts": end, "period_interval": 1})
        log["kalshi_candle_sample"] = dict(ticker=mm["ticker"], n=len(c.get("candlesticks", [])) if isinstance(c, dict) else None, keys=list(c)[:5] if isinstance(c, dict) else None)
json.dump(log, open(f"{OUT}/probe.json", "w"), indent=1, default=str)
print(json.dumps({k: (v if not isinstance(v, list) else v[:30]) for k, v in log.items()}, indent=1, default=str)[:6000])

"""Backlog 59 probe 2: Fed decision + US CPI events on both venues, with price history from each."""
import json, os, re, time, requests
OUT = "probe/leadlag"; os.makedirs(OUT, exist_ok=True)
K = "https://api.elections.kalshi.com/trade-api/v2"; G = "https://gamma-api.polymarket.com"; C = "https://clob.polymarket.com"
def get(u, p=None):
    try:
        r = requests.get(u, params=p, timeout=30, headers={"User-Agent": "research-probe"}); return r.json() if r.ok else {"status": r.status_code, "text": r.text[:200]}
    except Exception as e: return {"error": repr(e)}
log = {}
pe = {}
for q in ["fed-rates", "fed", "inflation", "cpi", "economy", "economic-policy"]:
    for closed in ("true", "false"):
        for off in range(0, 2000, 100):
            e = get(f"{G}/events", {"tag_slug": q, "closed": closed, "limit": 100, "offset": off})
            if not isinstance(e, list) or not e: break
            for x in e: pe[x["id"]] = x
fed = [e for e in pe.values() if re.match(r"fed decision in", (e.get("title") or "").lower())]
cpi = [e for e in pe.values() if re.search(r"inflation us - (monthly|annual)", (e.get("title") or "").lower())]
log["poly_fed_events"] = sorted((e["title"], e.get("endDate"), round(float(e.get("volume") or 0))) for e in fed)
log["poly_cpi_events"] = sorted((e["title"], e.get("endDate"), round(float(e.get("volume") or 0))) for e in cpi)
def hist(e):
    m = max(e.get("markets", []), key=lambda m: float(m.get("volume") or 0))
    tok = json.loads(m["clobTokenIds"])[0]
    end = int(time.time()); out = {}
    for fid in (1, 60):
        h = get(f"{C}/prices-history", {"market": tok, "startTs": end - 120 * 86400, "endTs": end, "fidelity": fid})
        out[fid] = len(h.get("history", [])) if isinstance(h, dict) else h
    h = get(f"{C}/prices-history", {"market": tok, "interval": "all", "fidelity": 60})
    out["all_60"] = len(h.get("history", [])) if isinstance(h, dict) else h
    return dict(title=e["title"], market=m.get("question"), **{str(k): v for k, v in out.items()})
log["poly_hist"] = [hist(e) for e in sorted(fed, key=lambda e: e.get("endDate") or "")[-4:]]
for s in ("KXFED", "KXFEDDECISION", "KXCPI"):
    ms = get(f"{K}/markets", {"series_ticker": s, "status": "settled", "limit": 200}).get("markets", [])
    ev = sorted({m["event_ticker"] for m in ms})
    log[f"kalshi_{s}"] = dict(settled=len(ms), events=ev[-12:])
    if ms:
        m = max(ms, key=lambda m: float(m.get("volume_fp") or 0)); end = int(pd_ts) if (pd_ts := time.time()) else 0
        cl = int(time.mktime(time.strptime(m["close_time"][:19], "%Y-%m-%dT%H:%M:%S")))
        c1 = get(f"{K}/series/{s}/markets/{m['ticker']}/candlesticks", {"start_ts": cl - 3 * 86400, "end_ts": cl, "period_interval": 1})
        c60 = get(f"{K}/series/{s}/markets/{m['ticker']}/candlesticks", {"start_ts": cl - 60 * 86400, "end_ts": cl, "period_interval": 60})
        hc = get(f"{K}/historical/markets/{m['ticker']}/candlesticks", {"start_ts": cl - 3 * 86400, "end_ts": cl, "period_interval": 1})
        log[f"kalshi_{s}_candles"] = dict(ticker=m["ticker"], min1=len(c1.get("candlesticks", [])) if "candlesticks" in c1 else c1,
                                          h1=len(c60.get("candlesticks", [])) if "candlesticks" in c60 else c60,
                                          hist_min1=len(hc.get("candlesticks", [])) if "candlesticks" in hc else hc)
json.dump(log, open(f"{OUT}/probe_b.json", "w"), indent=1, default=str)
print(json.dumps(log, indent=1, default=str)[:8000])

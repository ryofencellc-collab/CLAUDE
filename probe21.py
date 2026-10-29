"""How are Kalshi's fixed-close crypto markets defined? Fields and rules for a few of each."""
import json, urllib.parse, urllib.request
K = "https://api.elections.kalshi.com/trade-api/v2"
def get(path, **p):
    with urllib.request.urlopen(urllib.request.Request(f"{K}/{path}?" + urllib.parse.urlencode(p), headers={"User-Agent": "Mozilla/5.0"}), timeout=60) as r:
        return json.load(r)
for s in ["KXBTC15M", "KXETH15M", "KXBTCD", "KXBTC", "KXGOLD15M", "KXINXU"]:
    ms = get("markets", series_ticker=s, status="settled", limit=3).get("markets", [])
    for m in ms[:2]:
        keep = {k: m.get(k) for k in ["ticker", "event_ticker", "strike_type", "floor_strike", "cap_strike", "open_time", "close_time",
                                      "expected_expiration_time", "expiration_time", "result", "expiration_value", "settlement_value"]}
        print(s, json.dumps(keep))
        print("   RULES:", (m.get("rules_primary") or "")[:400].replace("\n", " "))
        print("   SECONDARY:", (m.get("rules_secondary") or "")[:300].replace("\n", " "))

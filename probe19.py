"""Probe for Round 19: which other Kalshi markets could carry the Round 18 edge?"""
import json, urllib.request, urllib.parse, collections

K = "https://api.elections.kalshi.com/trade-api/v2"


def get(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60) as r:
            return r.read()
    except Exception as e:
        return str(e).encode()


ser = json.loads(get(f"{K}/series?category=" + urllib.parse.quote("Climate and Weather")))["series"]
print("WEATHER SERIES", len(ser))
for s in sorted(ser, key=lambda s: s["ticker"]):
    print(f"  {s['ticker']:<22} {s['title'][:70]:<70} {s.get('frequency','')}")
allser = json.loads(get(f"{K}/series"))["series"]
print("ALL SERIES", len(allser), collections.Counter(s.get("category") for s in allser).most_common(30))
for code in ["EWR", "EGLL", "RJTT", "LFPG", "CYYZ", "EBBR", "LSGG", "EHAM", "ZSPD", "LTFM", "EDDF"]:
    u = ("https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?station=" + code +
         "&data=tmpf&year1=2026&month1=10&day1=27&year2=2026&month2=10&day2=28&tz=Etc/UTC&format=onlycomma")
    t = get(u).decode(errors="replace").splitlines()
    print("IEM", code, len(t) - 1, "rows", t[1:3])
for st in ["KXLOWTNYC", "KXLOWNY", "KXRAINNYC"]:
    j = json.loads(get(f"{K}/markets?series_ticker={st}&limit=3") or b"{}")
    print(st, [(m["ticker"], m.get("strike_type"), m.get("floor_strike"), m.get("cap_strike"), m.get("rules_primary", "")[:200]) for m in j.get("markets", [])])

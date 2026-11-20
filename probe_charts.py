"""Round 63 step 1 probe (AUTONOMOUS backlog 58): do Kalshi chart/streaming/box-office markets exist with enough settled history, and is kworb reachable?"""
import json, os, time, requests
from edge import round20 as r20
import pandas as pd

K = "https://api.elections.kalshi.com/trade-api/v2"
OUT = "probe/charts"; os.makedirs(OUT, exist_ok=True)
KEYS = ("spotify", "billboard", "hot 100", "box office", "opening weekend", "song", "album", "streams", "netflix", "top 10", "chart", "rotten tomatoes", "imdb", "app store")

series, cur = [], None
for _ in range(50):
    p = {"limit": 1000}
    if cur: p["cursor"] = cur
    j = requests.get(f"{K}/series", params=p, timeout=30).json()
    series += j.get("series", []); cur = j.get("cursor")
    if not cur: break
hits = [s for s in series if any(k in ((s.get("title") or "") + " " + (s.get("category") or "")).lower() for k in KEYS)]
rows = []
for s in hits:
    ms = r20.markets(s["ticker"], pd.Timestamp("2025-01-01", tz="UTC"), pd.Timestamp.now(tz="UTC") + pd.Timedelta(days=1))
    ev = {m.get("event_ticker") for m in ms}
    vol = sum(float(m.get("volume_fp") or m.get("volume") or 0) for m in ms)
    rows.append(dict(ticker=s["ticker"], title=s.get("title"), category=s.get("category"), settled_markets=len(ms), events=len(ev), volume=vol))
    time.sleep(0.2)
pd.DataFrame(rows).sort_values("volume", ascending=False).to_csv(f"{OUT}/series.csv", index=False)
print(pd.DataFrame(rows).sort_values("volume", ascending=False).head(40).to_string())

for name, url in {"kworb_us_daily": "https://kworb.net/spotify/country/us_daily.html", "kworb_global_daily": "https://kworb.net/spotify/country/global_daily.html",
                  "boxofficemojo_weekend": "https://www.boxofficemojo.com/weekend/", "the_numbers": "https://www.the-numbers.com/weekend-box-office-chart"}.items():
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "research-probe"}); print(name, r.status_code, len(r.text))
        open(f"{OUT}/{name}.status", "w").write(f"{r.status_code} {len(r.text)}\n")
    except Exception as e:
        print(name, "ERR", e); open(f"{OUT}/{name}.status", "w").write(f"ERR {e}\n")

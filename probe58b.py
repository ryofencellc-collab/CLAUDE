"""Probe: which Kalshi series cover Spotify/music charts now, and what's open in them?"""
import requests
B = "https://api.elections.kalshi.com/trade-api/v2"
ser = []
cur = None
for _ in range(30):
    p = {"limit": 1000}
    if cur: p["cursor"] = cur
    j = requests.get(B + "/series", params=p, timeout=60).json(); ser += j.get("series", []); cur = j.get("cursor")
    if not cur: break
print("series total", len(ser))
hits = [s for s in ser if any(k in (s.get("title", "") + " " + s["ticker"]).lower() for k in ("spotify", "song", "billboard", "album", "stream"))]
for s in hits:
    m = requests.get(B + "/markets", params={"series_ticker": s["ticker"], "status": "open", "limit": 200}, timeout=60).json().get("markets", [])
    print(s["ticker"], "|", s.get("title"), "|", s.get("frequency"), "| open:", len(m), [x["ticker"] for x in m[:3]])
for t in ["KXSPOTIFYD", "KXSPOTIFYW"]:
    m = requests.get(B + "/markets", params={"series_ticker": t, "limit": 3}, timeout=60).json().get("markets", [])
    print("latest any-status", t, [(x["ticker"], x["status"], x.get("close_time")) for x in m])

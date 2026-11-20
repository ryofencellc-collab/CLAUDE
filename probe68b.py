"""Probe: Kalshi economic-release series as a release calendar (close/expiration times = release times)."""
import pandas as pd, requests
from edge import round20 as r20
B = "https://api.elections.kalshi.com/trade-api/v2"
ser = []; cur = None
for _ in range(30):
    p = {"limit": 1000}
    if cur: p["cursor"] = cur
    j = requests.get(B + "/series", params=p, timeout=60).json(); ser += j.get("series", []); cur = j.get("cursor")
    if not cur: break
kw = ("cpi", "inflation", "payroll", "jobs", "unemployment", "gdp", "pce", "ppi", "jobless", "retail sales", "ism", "jolts", "consumer sentiment", "fed ")
hits = [s for s in ser if any(k in (s.get("title", "") + " " + s["ticker"]).lower() for k in kw) and s.get("frequency") in ("monthly", "weekly", "quarterly", "custom", "daily")]
print("candidate series", len(hits))
for s in hits: print(s["ticker"], "|", s.get("title"), "|", s.get("frequency"), "|", s.get("category"))
a, b = pd.Timestamp("2021-06-01", tz="UTC"), pd.Timestamp("2026-12-31", tz="UTC")
for t in ["KXCPI", "CPI", "KXCPIYOY", "KXPAYROLLS", "PAYROLLS", "KXU3", "KXGDP", "GDP", "KXPCE", "KXPPI", "KXJOBLESS", "KXJOBLESSCLAIMS", "KXRETAIL", "KXFEDDECISION", "FED", "KXFED"]:
    try:
        ms = r20.markets(t, a, b)
    except Exception as e:
        print(t, "err", e); continue
    if not ms: print(t, "0 markets"); continue
    ev = pd.DataFrame([dict(ev=m["event_ticker"], close=m["close_time"], exp=m.get("expected_expiration_time") or m.get("expiration_time")) for m in ms]).drop_duplicates("ev")
    ev["close"] = pd.to_datetime(ev.close, utc=True, format="ISO8601")
    print(t, "events", len(ev), ev.close.min(), ev.close.max()); print(ev.sort_values("close").tail(4).to_string())

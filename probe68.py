"""Probe for Round 68 catalyst data: FRED release calendars (HTML), GDELT news volume, yfinance earnings dates, Fed calendar."""
import json, re, time
import requests
H = {"User-Agent": "Mozilla/5.0 (research script)"}
def show(name, r, n=600):
    print("=====", name, r.status_code, len(r.text)); print(r.text[:n].replace("\n", " ")); print()
for rid in (10, 50):
    for url in (f"https://fred.stlouisfed.org/releases/calendar?rid={rid}&y=2024", f"https://fred.stlouisfed.org/release/dates?rid={rid}"):
        try:
            r = requests.get(url, headers=H, timeout=60); show(url, r, 300)
            print("date-like:", re.findall(r"(20\d\d-\d\d-\d\d)", r.text)[:12], re.findall(r"((?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, 20\d\d)", r.text)[:12])
        except Exception as e: print(url, e)
for url in ("https://api.stlouisfed.org/fred/release/dates?release_id=10&file_type=json",
            "https://www.bls.gov/schedule/2024/home.htm", "https://www.bea.gov/news/schedule/full", "https://www.census.gov/economic-indicators/calendar-listview.html"):
    try: r = requests.get(url, headers=H, timeout=60); show(url, r, 300)
    except Exception as e: print(url, e)
g = "https://api.gdeltproject.org/api/v2/doc/doc"
for q, extra in (('tariff', dict(startdatetime="20250401000000", enddatetime="20250412000000")), ('"stock market"', dict(startdatetime="20251101000000", enddatetime="20251110000000"))):
    try:
        r = requests.get(g, params=dict(query=q + " sourcelang:english", mode="timelinevolraw", format="json", **extra), headers=H, timeout=90)
        show("gdelt " + q, r, 900)
    except Exception as e: print("gdelt", e)
    time.sleep(6)
try:
    r = requests.get(g, params=dict(query='"stock market" sourcelang:english', mode="artlist", format="json", maxrecords=10, startdatetime="20261105000000", enddatetime="20261105235959", sort="hybridrel"), headers=H, timeout=90)
    show("gdelt artlist 2026-11-05", r, 2500)
except Exception as e: print(e)
import yfinance as yf
for t in ("NVDA", "AAPL"):
    try: e = yf.Ticker(t).get_earnings_dates(limit=24); print(t, len(e)); print(e.head(3)); print(e.tail(2))
    except Exception as ex: print(t, "earn fail", ex)
m = yf.Ticker("^GSPC").history(period="30d", interval="1m"); print("gspc 1m", len(m), m.index.min(), m.index.max())

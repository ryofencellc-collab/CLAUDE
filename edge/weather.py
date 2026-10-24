"""Round 5: Kalshi daily-high temperature markets vs archived GFS forecasts.

See PROTOCOL_ROUND5.md. Everything a trade uses is known at 09:00 local on
the target day: the quote at that hour and a forecast from model runs
published before ~04:00 local.
"""
import math
import re
import time
from concurrent.futures import ThreadPoolExecutor
from statistics import NormalDist

import numpy as np
import pandas as pd
import requests

from edge.data import CACHE

KALSHI = "https://api.elections.kalshi.com/trade-api/v2"
STAKE, DECISION_HOUR, HOLDOUT_DAYS = 10.0, 9, 120
PHI = NormalDist().cdf
_s = requests.Session()

# keyword in series title -> (NOAA GHCN station, lat, lon, tz) of the NWS climate-report site
CITIES = {
    "new york": ("USW00094728", 40.779, -73.969, "America/New_York"),
    "nyc": ("USW00094728", 40.779, -73.969, "America/New_York"),
    "chicago": ("USW00014819", 41.786, -87.752, "America/Chicago"),
    "miami": ("USW00012839", 25.788, -80.317, "America/New_York"),
    "austin": ("USW00013904", 30.183, -97.680, "America/Chicago"),
    "los angeles": ("USW00023174", 33.938, -118.389, "America/Los_Angeles"),
    "denver": ("USW00003017", 39.847, -104.656, "America/Denver"),
    "philadelphia": ("USW00013739", 39.873, -75.227, "America/New_York"),
    "houston": ("USW00012918", 29.638, -95.282, "America/Chicago"),
    "new orleans": ("USW00012916", 29.993, -90.251, "America/Chicago"),
    "boston": ("USW00014739", 42.361, -71.010, "America/New_York"),
    "seattle": ("USW00024233", 47.444, -122.314, "America/Los_Angeles"),
    "atlanta": ("USW00013874", 33.630, -84.442, "America/New_York"),
    "dallas": ("USW00003927", 32.898, -97.019, "America/Chicago"),
    "phoenix": ("USW00023183", 33.428, -112.004, "America/Phoenix"),
    "san francisco": ("USW00023234", 37.620, -122.365, "America/Los_Angeles"),
    "las vegas": ("USW00023169", 36.072, -115.163, "America/Los_Angeles"),
    "washington": ("USW00013743", 38.848, -77.034, "America/New_York"),
    "minneapolis": ("USW00014922", 44.883, -93.229, "America/Chicago"),
    "san antonio": ("USW00012921", 29.544, -98.484, "America/Chicago"),
}
MONTHS = {m: i for i, m in enumerate(["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG",
                                      "SEP", "OCT", "NOV", "DEC"], 1)}


def _get(url, params=None, tries=6):
    for i in range(tries):
        try:
            r = _s.get(url, params=params, timeout=60)
        except requests.RequestException:
            time.sleep(2 ** i)
            continue
        if r.status_code == 429:
            time.sleep(2 ** i)
            continue
        return r
    return None


def daily_high_series():
    r = _get(f"{KALSHI}/series", {"category": "Climate and Weather"})
    out = []
    for s in r.json().get("series", []):
        title = s["title"].lower()
        if not any(w in title for w in ("highest temperature", "high temp", "max temp")):
            continue
        if any(w in title for w in ("week", "average", "month", "year")):
            continue
        city = next((c for c in CITIES if c in title), None)
        if city:
            out.append((s["ticker"], city))
        else:
            print(f"  skip series without station mapping: {s['ticker']} | {s['title']}")
    return out


def _target_date(event_ticker):
    m = re.search(r"-(\d{2})([A-Z]{3})(\d{2})$", event_ticker)
    if not m:
        return None
    return pd.Timestamp(2000 + int(m.group(1)), MONTHS[m.group(2)], int(m.group(3)))


def markets(series):
    out, cursor = [], None
    while True:
        p = {"series_ticker": series, "status": "settled", "limit": 1000}
        if cursor:
            p["cursor"] = cursor
        r = _get(f"{KALSHI}/markets", p)
        if r is None or r.status_code != 200:
            break
        j = r.json()
        out += j.get("markets", [])
        cursor = j.get("cursor")
        if not cursor or not j.get("markets"):
            break
    return out


def _quote(series, m, tz):
    """yes_bid / yes_ask at 09:00 local on the target day (latest hourly close within 3h)."""
    day = _target_date(m["event_ticker"])
    decide = pd.Timestamp(day.year, day.month, day.day, DECISION_HOUR).tz_localize(tz).tz_convert("UTC")
    t1 = int(decide.timestamp())
    r = _get(f"{KALSHI}/series/{series}/markets/{m['ticker']}/candlesticks",
             {"start_ts": t1 - 3 * 3600, "end_ts": t1, "period_interval": 60})
    if r is None or r.status_code != 200:
        return None
    best = None
    for c in r.json().get("candlesticks", []):
        if c["end_period_ts"] <= t1:
            ask, bid = c.get("yes_ask", {}).get("close_dollars"), c.get("yes_bid", {}).get("close_dollars")
            if ask is not None and bid is not None:
                best = (float(bid), float(ask))
    return best


def forecasts(lat, lon, tz, start, end):
    r = _get("https://previous-runs-api.open-meteo.com/v1/forecast", dict(
        latitude=lat, longitude=lon, start_date=start, end_date=end, timezone=tz,
        hourly="temperature_2m_previous_day1", models="gfs_seamless", temperature_unit="fahrenheit"))
    h = r.json()["hourly"]
    s = pd.Series(h["temperature_2m_previous_day1"], index=pd.to_datetime(h["time"]), dtype=float)
    return s.groupby(s.index.normalize()).max(min_count=18)  # need most of the day's hours


def observed(station, start, end):
    r = _get("https://www.ncei.noaa.gov/access/services/data/v1", dict(
        dataset="daily-summaries", stations=station, startDate=start, endDate=end,
        dataTypes="TMAX", units="standard", format="json"))
    rows = r.json() if r is not None and r.status_code == 200 else []
    return pd.Series({pd.Timestamp(x["DATE"]): float(x["TMAX"]) for x in rows if x.get("TMAX")}, dtype=float)


def dataset(refresh=False) -> pd.DataFrame:
    path = CACHE / "weather.pkl"
    if path.exists() and not refresh:
        return pd.read_pickle(path)
    rows = []
    for series, city in daily_high_series():
        station, lat, lon, tz = CITIES[city]
        ms = [m for m in markets(series) if _target_date(m["event_ticker"]) is not None
              and m.get("result") in ("yes", "no")]
        if not ms:
            continue
        days = sorted({_target_date(m["event_ticker"]) for m in ms})
        start, end = days[0].date().isoformat(), days[-1].date().isoformat()
        fc, ob = forecasts(lat, lon, tz, start, end), observed(station, start, end)
        with ThreadPoolExecutor(6) as ex:
            quotes = list(ex.map(lambda m: _quote(series, m, tz), ms))
        for m, q in zip(ms, quotes):
            d = _target_date(m["event_ticker"])
            rows.append(dict(series=series, city=city, date=d, ticker=m["ticker"],
                             event=m["event_ticker"], strike_type=m.get("strike_type"),
                             floor=m.get("floor_strike"), cap=m.get("cap_strike"),
                             yes_won=m["result"] == "yes",
                             bid=q[0] if q else np.nan, ask=q[1] if q else np.nan,
                             forecast=fc.get(d, np.nan), observed=ob.get(d, np.nan)))
        print(f"  {series} ({city}): {len(ms)} markets, {len(days)} days {start}..{end}, "
              f"quoted {sum(q is not None for q in quotes)}", flush=True)
    df = pd.DataFrame(rows)
    df.to_pickle(path)
    return df


def prob_yes(row, mu, sd):
    f, c, t = row["floor"], row["cap"], row["strike_type"]
    above = lambda k: 1 - PHI((k + 0.5 - mu) / sd)   # P(high > k), integer highs
    below = lambda k: PHI((k - 0.5 - mu) / sd)       # P(high < k)
    if t == "greater":
        return above(f)
    if t == "less":
        return below(c)
    if t == "between" and f is not None and c is not None:
        return PHI((c + 0.5 - mu) / sd) - PHI((f - 0.5 - mu) / sd)
    return np.nan


def fee(contracts, price):
    return math.ceil(0.07 * contracts * price * (1 - price) * 100 - 1e-9) / 100


def bets(df, calib, edge, per_event):
    out = []
    for _, r in df.dropna(subset=["forecast", "bid", "ask"]).iterrows():
        bias, sd = calib.get(r["city"], (0.0, 3.0))
        p = prob_yes(r, r["forecast"] + bias, sd)
        if not np.isfinite(p):
            continue
        for side, prob, price in (("yes", p, r["ask"]), ("no", 1 - p, 1 - r["bid"])):
            if 0.01 <= price <= 0.99 and prob - price >= edge:
                n = STAKE / price
                won = r["yes_won"] if side == "yes" else not r["yes_won"]
                pnl = n * won - STAKE - fee(n, price)
                out.append(dict(date=r["date"], city=r["city"], event=r["event"], side=side,
                                price=price, prob=prob, edge=prob - price, won=won, pnl=pnl))
    b = pd.DataFrame(out)
    if per_event == "best" and len(b):
        b = b.loc[b.groupby("event")["edge"].idxmax()]
    return b.sort_values("date") if len(b) else b


def calibrate(df):
    """Per-city bias and sd of (observed - forecast), one row per city-day."""
    d = df.drop_duplicates(["city", "date"]).dropna(subset=["forecast", "observed"])
    err = d["observed"] - d["forecast"]
    return {c: (float(e.mean()), max(float(e.std()), 1.5)) for c, e in err.groupby(d["city"]) if len(e) >= 20}


GRID = [dict(edge=e, per_event=p) for e in (0.05, 0.10, 0.15) for p in ("best", "all")]

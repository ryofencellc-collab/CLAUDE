"""Probe: Kalshi S&P daily/hourly series structure and 1-minute candle availability for 2026-11-09..19."""
import json, pandas as pd, requests
from edge import round20 as r20
B = "https://api.elections.kalshi.com/trade-api/v2"
for s in ["KXINX", "KXINXU", "KXINXD", "INX", "INXD", "KXINXY"]:
    j = requests.get(f"{B}/series/{s}", timeout=30); print(s, j.status_code, j.text[:300].replace("\n", " "))
a, b = pd.Timestamp("2026-11-09", tz="UTC"), pd.Timestamp("2026-11-21", tz="UTC")
for s in ["KXINX", "KXINXU"]:
    ms = r20.markets(s, a, b); print(s, "settled markets", len(ms))
    if not ms: continue
    df = pd.DataFrame(ms); print(df.event_ticker.value_counts().head(12))
    keys = ["ticker", "event_ticker", "yes_sub_title", "subtitle", "floor_strike", "cap_strike", "strike_type", "open_time", "close_time", "result", "volume_fp", "volume"]
    print(df[[k for k in keys if k in df]].head(8).to_string())
    m = ms[len(ms) // 2]; tk, ev = m["ticker"], m["event_ticker"]
    c0 = int(pd.Timestamp(m["close_time"]).timestamp())
    for path in (f"{B}/series/{s}/markets/{tk}/candlesticks", f"{B}/historical/markets/{tk}/candlesticks"):
        r = requests.get(path, params={"start_ts": c0 - 6 * 3600, "end_ts": c0, "period_interval": 1}, timeout=30)
        print(path[-60:], r.status_code, r.text[:700].replace("\n", " "))
    r = requests.get(f"{B}/markets/trades", params={"ticker": tk, "limit": 5}, timeout=30); print("trades live", r.status_code, r.text[:400])
    r = requests.get(f"{B}/historical/trades", params={"ticker": tk, "limit": 5}, timeout=30); print("trades hist", r.status_code, r.text[:400])

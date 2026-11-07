"""Round 31 data (PROTOCOL_ROUND31.md): Kalshi 15-minute crypto markets with 1-minute real quotes + spot."""
import numpy as np
import pandas as pd

from edge import round20, round27
from edge import weather as wx

SERIES = {"KXBTC15M": "BTCUSDT", "KXETH15M": "ETHUSDT", "KXSOL15M": "SOLUSDT", "KXXRP15M": "XRPUSDT",
          "KXDOGE15M": "DOGEUSDT"}


def num(x, *keys):
    for k in keys:
        v = (x or {}).get(k)
        if v not in (None, ""):
            try:
                return float(v)
            except (TypeError, ValueError):
                pass
    return np.nan


def parse_candles(ticker: str, cs: list[dict]) -> pd.DataFrame:
    rows = []
    for c in cs or []:
        yb, ya, pr = c.get("yes_bid") or {}, c.get("yes_ask") or {}, c.get("price") or {}
        rows.append({"ticker": ticker, "t": pd.Timestamp(int(c["end_period_ts"]), unit="s", tz="UTC"),
                     "bid": num(yb, "close_dollars", "close"), "ask": num(ya, "close_dollars", "close"),
                     "bid_high": num(yb, "high_dollars", "high"), "ask_low": num(ya, "low_dollars", "low"),
                     "px_low": num(pr, "low_dollars", "low"), "px_high": num(pr, "high_dollars", "high"),
                     "vol": num(c, "volume_fp", "volume")})
    return pd.DataFrame(rows)


def candles_live(series: str, ms: list[dict]) -> pd.DataFrame:
    out = []
    for i in range(0, len(ms), 100):
        chunk = ms[i:i + 100]
        opens = pd.to_datetime([m["open_time"] for m in chunk], utc=True)
        closes = pd.to_datetime([m["close_time"] for m in chunk], utc=True)
        r = wx._get(f"{wx.KALSHI}/markets/candlesticks", {"market_tickers": ",".join(m["ticker"] for m in chunk),
                                                           "start_ts": int(opens.min().timestamp()) - 60,
                                                           "end_ts": int(closes.max().timestamp()), "period_interval": 1})
        if r is None or r.status_code != 200:
            continue
        for mk in r.json().get("markets", []):
            out.append(parse_candles(mk.get("market_ticker"), mk.get("candlesticks")))
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()


def candles_hist(m: dict) -> pd.DataFrame:
    o, c = pd.Timestamp(m["open_time"]), pd.Timestamp(m["close_time"])
    r = wx._get(f"{wx.KALSHI}/historical/markets/{m['ticker']}/candlesticks",
                {"start_ts": int(o.timestamp()) - 60, "end_ts": int(c.timestamp()), "period_interval": 1})
    if r is None or r.status_code != 200:
        return pd.DataFrame()
    return parse_candles(m["ticker"], r.json().get("candlesticks"))


def fetch(series: str, a: pd.Timestamp, b: pd.Timestamp, split: pd.Timestamp, cap: int = 2500) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(markets, minute quotes) for one series."""
    ms = [m for m in round20.markets(series, a, b) if m.get("open_time") and m.get("floor_strike") is not None]
    cut = round27.cutoff()
    close = lambda m: pd.Timestamp(m["close_time"])
    live = [m for m in ms if close(m) > cut]
    hist = [m for m in ms if close(m) <= cut]
    pick = []
    for lo, hi in ((a, split), (split, b)):
        part = sorted([m for m in hist if lo <= close(m) < hi], key=close)
        w = max(1, -(-len(part) // cap))
        pick += part[::w]
    print(f"{series}: {len(ms)} markets; live {len(live)}, archived {len(hist)} -> sampled {len(pick)}", flush=True)
    q = [candles_live(series, sorted(live, key=close))]
    for i, m in enumerate(pick):
        q.append(candles_hist(m))
        if i % 500 == 0:
            print(f"  {series} archived {i}/{len(pick)}", flush=True)
    quotes = pd.concat([x for x in q if len(x)], ignore_index=True) if any(len(x) for x in q) else pd.DataFrame()
    keep = {m["ticker"] for m in live + pick}
    meta = pd.DataFrame([{"ticker": m["ticker"], "series": series, "open": pd.Timestamp(m["open_time"]),
                          "close": pd.Timestamp(m["close_time"]), "strike": float(m["floor_strike"]),
                          "up": 1.0 if m["result"] == "yes" else 0.0} for m in ms if m["ticker"] in keep])
    return meta, quotes

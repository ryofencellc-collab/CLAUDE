"""Real end-of-day option chains (bid/ask/IV/greeks) from DoltHub post-no-preference/options, plus earnings dates
and underlying prices. Coverage (probe, Nov 8 2026): SPY and large single stocks daily from ~2020-03; ~6
expirations 2 weeks to 2 months out; strikes a few % apart. QQQ/IWM absent."""
import time
from pathlib import Path

import pandas as pd
import requests

API = "https://www.dolthub.com/api/v1alpha1/post-no-preference/{repo}/master"
S = requests.Session()
S.headers["User-Agent"] = "research"
CACHE = Path("data/opt")


def sql(query: str, repo: str = "options", tries: int = 5) -> list[dict] | None:
    for i in range(tries):
        try:
            r = S.get(API.format(repo=repo), params={"q": query}, timeout=120)
            if r.status_code == 200:
                j = r.json()
                if j.get("query_execution_status") == "Success":
                    return j.get("rows", [])
                if "deadline" not in str(j.get("query_execution_message", "")):
                    return None
            elif r.status_code not in (429, 500, 502, 503, 504):
                return None
        except (requests.RequestException, ValueError):
            pass
        time.sleep(3 * (i + 1))
    return None


def chain(symbol: str, day: str) -> list[dict] | None:
    rows, off = [], 0
    while True:
        page = sql(f"SELECT * FROM option_chain WHERE date='{day}' AND act_symbol='{symbol}' LIMIT 1000 OFFSET {off}")
        if page is None:
            return None if not rows else rows
        rows += page
        if len(page) < 1000:
            return rows
        off += 1000


def fetch_symbol(symbol: str, start: str = "2020-01-01", end: str | None = None) -> pd.DataFrame:
    CACHE.mkdir(parents=True, exist_ok=True)
    out = CACHE / f"{symbol}.pkl"
    have = pd.read_pickle(out) if out.exists() else pd.DataFrame()
    done = set(have["date"].astype(str)) if len(have) else set()
    days = pd.bdate_range(start, end or pd.Timestamp.now().normalize()).strftime("%Y-%m-%d")
    parts, failed = [have] if len(have) else [], []
    for i, d in enumerate(days):
        if d in done:
            continue
        rows = chain(symbol, d)
        if rows is None:
            failed.append(d)
        elif rows:
            parts.append(pd.DataFrame(rows))
        if i % 100 == 0:
            print(f"{symbol} {d}: {sum(len(p) for p in parts):,} rows, {len(failed)} failed days", flush=True)
            if parts:
                pd.concat(parts, ignore_index=True).to_pickle(out)
    df = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
    if len(df):
        for c in ("strike", "bid", "ask", "vol", "delta", "gamma", "theta", "vega", "rho"):
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df["date"], df["expiration"] = pd.to_datetime(df["date"]), pd.to_datetime(df["expiration"])
        df.to_pickle(out)
    print(f"{symbol}: {len(df):,} rows, {df['date'].nunique() if len(df) else 0} days; failed {len(failed)}: {failed[:10]}", flush=True)
    return df


def earnings(symbol: str) -> list[str]:
    for table in ("earnings_calendar", "earnings"):
        rows = sql(f"SELECT * FROM {table} WHERE act_symbol='{symbol}'", repo="earnings")
        if rows:
            return sorted({r.get("date") for r in rows if r.get("date")})
    return []


def underlying(symbol: str, start="2019-06-01") -> pd.DataFrame:
    import yfinance as yf
    d = yf.download(symbol, start=start, auto_adjust=False, progress=False)
    if isinstance(d.columns, pd.MultiIndex):
        d.columns = d.columns.get_level_values(0)
    return d[["Open", "High", "Low", "Close"]]

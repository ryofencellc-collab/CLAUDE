"""Round 6: sell a weekly cash-secured BTC put every Friday (PROTOCOL_ROUND6.md)."""
import re
import time

import numpy as np
import pandas as pd
import requests

from edge import data

HISTORY = "https://history.deribit.com/api/v2/public/get_last_trades_by_currency_and_time"
HAIRCUT, TRADE_FEE, SETTLE_FEE, FEE_CAP = 0.05, 0.0003, 0.00015, 0.125
HOLDOUT_FROM = "2024-01-01"
_s = requests.Session()
NAME = re.compile(r"BTC-(\d{1,2}[A-Z]{3}\d{2})-(\d+)-([PC])$")


def _trades(t0: int, t1: int) -> list[dict]:
    out, start = [], t0
    while True:
        for i in range(5):
            try:
                r = _s.get(HISTORY, params=dict(currency="BTC", kind="option", start_timestamp=start,
                                                end_timestamp=t1, count=1000, sorting="asc",
                                                include_old="true"), timeout=60)
                if r.status_code == 200:
                    break
            except requests.RequestException:
                pass
            time.sleep(2 ** i)
        else:
            return out
        res = r.json()["result"]
        out += res["trades"]
        if not res.get("has_more") or not res["trades"]:
            return out
        start = res["trades"][-1]["timestamp"] + 1


def _spot_8utc() -> pd.Series:
    """BTCUSDT open of the 08:00 UTC hourly bar, by date."""
    base = f"{data.VISION}/spot/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-"
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(16) as ex:
        parts = [p for p in ex.map(data._fetch_zip_csv, [f"{base}{m}.zip" for m in data._months("2019-01")])
                 if p is not None]
    df = pd.concat(parts)
    ts = data._to_ts(df[0]).dt.tz_localize(None)
    s = pd.Series(pd.to_numeric(df[1]).values, index=ts.values)
    s = s[s.index.hour == 8]
    return pd.Series(s.values, index=s.index.normalize()).groupby(level=0).first()


def weekly_puts(refresh=False) -> pd.DataFrame:
    """For each Friday: spot, and for each strike of next Friday's expiry, median traded put price."""
    path = data.CACHE / "btc_puts.pkl"
    if path.exists() and not refresh:
        return pd.read_pickle(path)
    rows = []
    for fri in pd.date_range("2019-04-05", pd.Timestamp.utcnow().tz_localize(None) - pd.Timedelta(days=8),
                             freq="W-FRI"):
        t0 = int((fri + pd.Timedelta(hours=8)).tz_localize("UTC").timestamp() * 1000)
        trades = _trades(t0, t0 + 3600 * 1000)
        expiry = fri + pd.Timedelta(days=7)
        tag = f"{expiry.day}{expiry.strftime('%b').upper()}{expiry.strftime('%y')}"
        puts = {}
        for t in trades:
            m = NAME.match(t["instrument_name"])
            if m and m.group(1) == tag and m.group(3) == "P":
                puts.setdefault(int(m.group(2)), []).append((t["price"], t["index_price"]))
        for k, v in puts.items():
            rows.append(dict(friday=fri, expiry=expiry, strike=k, price_btc=float(np.median([p for p, _ in v])),
                             spot=float(np.median([s for _, s in v])), n_trades=len(v)))
        if fri.month == 1 and fri.day <= 7:
            print(f"  {fri.date()}: {len(trades)} option trades, {len(puts)} next-week put strikes", flush=True)
    df = pd.DataFrame(rows)
    df.to_pickle(path)
    return df


def sell_puts(df: pd.DataFrame, spot_at: pd.Series, m: float) -> pd.DataFrame:
    out = []
    for fri, g in df.groupby("friday"):
        spot = g["spot"].median()
        row = g.iloc[(g["strike"] - m * spot).abs().argmin()]
        if abs(row["strike"] / spot - m) > 0.03:  # nothing traded near the target strike
            continue
        st = spot_at.get(row["expiry"])
        if st is None or np.isnan(st):
            continue
        p = row["price_btc"] * (1 - HAIRCUT)
        fees = min(TRADE_FEE, FEE_CAP * p) + min(SETTLE_FEE, FEE_CAP * p)
        k = row["strike"]
        pnl = (p - fees) * row["spot"] - max(k - st, 0.0)
        out.append(dict(friday=fri, strike=k, spot=row["spot"], settle=st, premium_usd=p * row["spot"],
                        ret=pnl / k, won=st >= k))
    return pd.DataFrame(out).set_index("friday")


GRID = [dict(m=m) for m in (0.95, 0.90, 0.85)]

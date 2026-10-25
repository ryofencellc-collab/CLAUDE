"""Round 7 families (PROTOCOL_ROUND7.md)."""
import io
import json
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
import requests

from edge import data
from edge import weather as wx

# ---------------------------------------------------------------- 7A bracket arbitrage

ARB_SIZE = 100  # contracts per bracket


def bracket_arb(wdf: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    rows, checked, bad = [], 0, 0
    for ev, g in wdf.groupby("event"):
        if len(g) < 2 or g[["bid", "ask"]].isna().any().any():
            continue
        if int(g["yes_won"].sum()) != 1:
            bad += 1
            continue
        checked += 1
        asks, bids = g["ask"].to_numpy(), g["bid"].to_numpy()
        buy_fee = sum(wx.fee(ARB_SIZE, p) for p in asks if 0 < p < 1) / ARB_SIZE
        buy = 1 - asks.sum() - buy_fee
        no_prices = 1 - bids
        sell_fee = sum(wx.fee(ARB_SIZE, p) for p in no_prices if 0 < p < 1) / ARB_SIZE
        sell = bids.sum() - 1 - sell_fee
        rows.append(dict(event=ev, city=g["city"].iloc[0], date=g["date"].iloc[0], brackets=len(g),
                         sum_ask=asks.sum(), sum_bid=bids.sum(), buy_all=buy, sell_all=sell))
    return pd.DataFrame(rows), dict(events_checked=checked, events_bad_settlement=bad)


# ---------------------------------------------------------------- 7B tennis value

def tennis(refresh=False) -> pd.DataFrame:
    path = data.CACHE / "tennis.pkl"
    if path.exists() and not refresh:
        return pd.read_pickle(path)

    def one(args):
        year, tour = args
        url = f"http://www.tennis-data.co.uk/{year}{'w' if tour == 'wta' else ''}/{year}.xlsx"
        try:
            r = requests.get(url, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code != 200:
                return None
            df = pd.read_excel(io.BytesIO(r.content))
        except Exception as e:  # missing year / format change
            print(f"  tennis {tour} {year}: {e!r}")
            return None
        df["year"], df["tour"] = year, tour
        return df

    jobs = [(y, t) for y in range(2013, pd.Timestamp.utcnow().year + 1) for t in ("atp", "wta")]
    with ThreadPoolExecutor(8) as ex:
        parts = [p for p in ex.map(one, jobs) if p is not None]
    df = pd.concat(parts, ignore_index=True)
    keep = ["year", "tour", "Date", "Winner", "Loser", "PSW", "PSL", "MaxW", "MaxL"]
    df = df[[c for c in keep if c in df.columns]]
    for c in ("PSW", "PSL", "MaxW", "MaxL"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["PSW", "PSL", "MaxW", "MaxL"])
    df.to_pickle(path)
    return df


def tennis_value(df, edge, max_odds):
    book = 1 / df["PSW"] + 1 / df["PSL"]
    out = []
    for side, won in (("W", 1.0), ("L", 0.0)):
        fair = df[f"PS{side}"] * book
        best = df[f"Max{side}"]
        pick = (best >= fair * (1 + edge)) & (best <= (max_odds or np.inf))
        b = df[pick]
        out.append(pd.DataFrame({"year": b["year"], "ret": won * best[pick] - 1}))
    return pd.concat(out)


TENNIS_GRID = [dict(edge=e, max_odds=m) for e in (0.02, 0.05) for m in (None, 3.0)]

# ---------------------------------------------------------------- 7C cross-exchange funding

COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE"]
FUND_COST = 0.001  # 2 taker legs x 0.05% per unit of position change


def _hl_funding(coin: str) -> pd.Series:
    out, start = [], int(pd.Timestamp("2023-01-01", tz="UTC").timestamp() * 1000)
    end = int(pd.Timestamp.utcnow().timestamp() * 1000)
    while start < end:
        for i in range(5):
            try:
                r = requests.post("https://api.hyperliquid.xyz/info", timeout=60,
                                  json={"type": "fundingHistory", "coin": coin, "startTime": start})
                if r.status_code == 200:
                    break
            except requests.RequestException:
                pass
            time.sleep(2 ** i)
        else:
            break
        page = r.json()
        if not page:
            break
        out += page
        start = page[-1]["time"] + 1
        if len(page) < 100:
            break
    if not out:
        return pd.Series(dtype=float)
    s = pd.Series([float(x["fundingRate"]) for x in out], index=pd.to_datetime([x["time"] for x in out], unit="ms"))
    return s.groupby(s.index.normalize()).sum()


def funding_panel(refresh=False):
    path = data.CACHE / "funding_xvenue.pkl"
    if path.exists() and not refresh:
        return pd.read_pickle(path)
    hl = pd.DataFrame({c: _hl_funding(c) for c in COINS})
    bn = pd.DataFrame({c: data._funding(f"{c}USDT") for c in COINS})
    p = {"hl": hl, "bn": bn}
    pd.to_pickle(p, path)
    return p


def funding_arb(p, w, thr):
    diff = (p["hl"] - p["bn"]).dropna(how="all")
    sig = diff.rolling(w, min_periods=w).mean()
    pos = np.sign(sig).where(sig.abs() > thr, 0.0)       # +1: short Hyperliquid, long Binance
    held = pos.shift(1).fillna(0.0)
    pnl = held * diff - held.diff().abs().fillna(held.abs()) * FUND_COST
    daily = pnl.mean(axis=1, skipna=True).dropna()
    turnover = held.diff().abs().sum(axis=1)
    return daily, turnover.reindex(daily.index).fillna(0)


FUNDING_GRID = [dict(w=w, thr=t) for w in (3, 7) for t in (0.0003, 0.001)]

# ---------------------------------------------------------------- 7D pairs


def pairs(panel, n):
    px = panel["spot_close"][COINS]
    lp = np.log(px)
    r = px.pct_change(fill_method=None)
    rets, turns = [], []
    for i, a in enumerate(COINS):
        for b in COINS[i + 1:]:
            la, lb = lp[a], lp[b]
            beta = la.rolling(n).cov(lb) / lb.rolling(n).var()
            spread = la - beta * lb
            z = (spread - spread.rolling(n).mean()) / spread.rolling(n).std()
            pos = pd.Series(np.nan, index=z.index)
            pos[z > 2] = -1.0
            pos[z < -2] = 1.0
            pos[(z.shift(1) * z) < 0] = 0.0  # spread crossed its mean: exit
            pos = pos.ffill().fillna(0.0)
            wa, wb = pos / (1 + beta.abs()), -pos * beta / (1 + beta.abs())
            ha, hb = wa.shift(1).fillna(0), wb.shift(1).fillna(0)
            turn = ha.diff().abs().fillna(0) + hb.diff().abs().fillna(0)
            rets.append((ha * r[a] + hb * r[b] - turn * 0.001).rename(f"{a}/{b}"))
            turns.append(turn)
    daily = pd.concat(rets, axis=1).dropna(how="all").fillna(0).mean(axis=1)
    return daily, pd.concat(turns, axis=1).sum(axis=1).reindex(daily.index).fillna(0)


PAIRS_GRID = [dict(n=n) for n in (30, 60)]

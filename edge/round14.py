"""Round 14: SPY options (PROTOCOL_ROUND14.md).

Part A: Cboe's published option-strategy indexes. Part B: TikTok-style short-dated trades priced
with Black-Scholes from the market's own implied vol (VIX9D for weeklies, VIX1D for 0DTE).
"""
import io
from math import erf, exp, log, sqrt

import numpy as np
import pandas as pd
import requests

CBOE = ["PUT", "WPUT", "BXM", "CNDR", "BFLY", "PPUT", "CLL"]
SPREAD = 0.05             # half bid-ask, as a share of the option price, each way
STAKE = 0.02              # buyers spend 2% of the account per trade
MINUTES_0DTE = 390        # open to close
START = pd.Timestamp("2012-01-01")


def _N(x):
    return 0.5 * (1 + erf(x / sqrt(2)))


def bs(S, K, T, sigma, r, kind):
    """Black-Scholes price; T in years, sigma and r annual decimals."""
    if T <= 0 or sigma <= 0:
        return max(S - K, 0.0) if kind == "call" else max(K - S, 0.0)
    d1 = (log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)
    if kind == "call":
        return S * _N(d1) - K * exp(-r * T) * _N(d2)
    return K * exp(-r * T) * _N(-d2) - S * _N(-d1)


def cboe_index(name: str) -> pd.Series:
    url = f"https://cdn.cboe.com/api/global/us_indices/daily_prices/{name}_History.csv"
    try:
        r = requests.get(url, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
    except requests.RequestException:
        return pd.Series(dtype=float)
    if r.status_code != 200 or b"," not in r.content[:200]:
        return pd.Series(dtype=float)
    df = pd.read_csv(io.BytesIO(r.content))
    date_col = df.columns[0]
    val_col = [c for c in df.columns[1:] if pd.to_numeric(df[c], errors="coerce").notna().mean() > 0.9][-1]
    s = pd.Series(pd.to_numeric(df[val_col], errors="coerce").to_numpy(),
                  index=pd.to_datetime(df[date_col], errors="coerce")).dropna()
    return s[~s.index.duplicated()].sort_index()


def weekly_ends(idx: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """Last trading day of each calendar week."""
    s = pd.Series(idx, index=idx)
    return pd.DatetimeIndex(s.groupby(idx.to_period("W-FRI")).max().to_numpy())


def b1_weekly_calls(close: pd.Series, vix9d: pd.Series, rate: pd.Series) -> pd.DataFrame:
    ends = weekly_ends(close.index)
    rows = []
    for a, b in zip(ends[:-1], ends[1:]):
        S, ST, v = close[a], close[b], vix9d.get(a, np.nan)
        if not np.isfinite(v):
            continue
        T = (b - a).days / 365
        K = S * 1.02
        cost = bs(S, K, T, v / 100, rate.get(a, 0.0), "call") * (1 + SPREAD)
        pay = max(ST - K, 0.0)
        rows.append(dict(entry=a, exit=b, cost=cost, payoff=pay, ret=pay / cost - 1 if cost > 0 else -1.0,
                         cash_rate=rate.get(a, 0.0), dt=T))
    return pd.DataFrame(rows)


def b2_0dte_calls(opn: pd.Series, close: pd.Series, vix1d_open: pd.Series, rate: pd.Series) -> pd.DataFrame:
    rows = []
    T = MINUTES_0DTE / 525600
    for d in vix1d_open.dropna().index.intersection(opn.index):
        S, ST = opn[d], close[d]
        K = S * 1.005
        cost = bs(S, K, T, vix1d_open[d] / 100, rate.get(d, 0.0), "call") * (1 + SPREAD)
        pay = max(ST - K, 0.0)
        rows.append(dict(entry=d, exit=d, cost=cost, payoff=pay, ret=pay / cost - 1 if cost > 0 else -1.0,
                         cash_rate=rate.get(d, 0.0), dt=1 / 252))
    return pd.DataFrame(rows)


def b3_0dte_condor(opn: pd.Series, close: pd.Series, vix1d_open: pd.Series, rate: pd.Series) -> pd.DataFrame:
    rows = []
    T = MINUTES_0DTE / 525600
    for d in vix1d_open.dropna().index.intersection(opn.index):
        S, ST, v, r = opn[d], close[d], vix1d_open[d] / 100, rate.get(d, 0.0)
        c1, c2 = bs(S, S * 1.01, T, v, r, "call"), bs(S, S * 1.02, T, v, r, "call")
        p1, p2 = bs(S, S * 0.99, T, v, r, "put"), bs(S, S * 0.98, T, v, r, "put")
        credit = (1 - SPREAD) * (c1 + p1) - (1 + SPREAD) * (c2 + p2)
        width = 0.01 * S
        max_loss = width - credit
        if max_loss <= 0:
            continue
        loss = min(max(ST - S * 1.01, 0.0), width) + min(max(S * 0.99 - ST, 0.0), width)
        pnl = credit - loss
        rows.append(dict(entry=d, exit=d, credit=credit, max_loss=max_loss, pnl=pnl, ret=pnl / max_loss,
                         cash_rate=r, dt=1 / 252))
    return pd.DataFrame(rows)


def b4_weekly_puts(close: pd.Series, vix9d: pd.Series, rate: pd.Series) -> pd.DataFrame:
    ends = weekly_ends(close.index)
    rows = []
    for a, b in zip(ends[:-1], ends[1:]):
        S, ST, v = close[a], close[b], vix9d.get(a, np.nan)
        if not np.isfinite(v):
            continue
        T = (b - a).days / 365
        K = S * 0.98
        r = rate.get(a, 0.0)
        prem = bs(S, K, T, v / 100, r, "put") * (1 - SPREAD)
        pnl = prem - max(K - ST, 0.0)
        rows.append(dict(entry=a, exit=b, premium=prem, pnl=pnl, ret=pnl / K + r * T, cash_rate=r, dt=T))
    return pd.DataFrame(rows)


def equity_buyer(trades: pd.DataFrame) -> pd.Series:
    """Spend STAKE of the account per trade; the rest earns T-bills."""
    g = 1 + STAKE * trades["ret"] + (1 - STAKE) * trades["cash_rate"] * trades["dt"]
    return pd.Series(g.cumprod().to_numpy(), index=pd.DatetimeIndex(trades["exit"]))


def equity_seller(trades: pd.DataFrame) -> pd.Series:
    """The whole account is collateral each trade (B3: one condor per $ of max loss; B4: cash-secured)."""
    g = 1 + trades["ret"]
    return pd.Series(g.cumprod().to_numpy(), index=pd.DatetimeIndex(trades["exit"]))

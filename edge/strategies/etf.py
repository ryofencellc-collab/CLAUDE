"""US ETF / volatility strategy families. Inputs: data.etf_panel()."""
import numpy as np
import pandas as pd

from edge.backtest import Result, from_returns, run

COST = 0.0002  # per side: commission-free broker, spread + slippage
PERIODS = 252


def _rsi(px: pd.Series, n: int) -> pd.Series:
    d = px.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn)


def overnight(p, ticker):
    """Buy at the close, sell at the next open, every day."""
    c, o = p["close"][ticker].dropna(), p["open"][ticker].dropna()
    r = (o / c.shift(1) - 1).dropna()
    turnover = pd.Series(2.0, index=r.index)
    return from_returns(r - turnover * COST, turnover)


def rsi2(p, entry, exit_, trend):
    c = p["close"]["SPY"].dropna()
    rsi = _rsi(c, 2)
    pos = pd.Series(np.nan, index=c.index)
    pos[rsi < entry] = 1.0
    pos[rsi > exit_] = 0.0
    pos = pos.ffill().fillna(0.0)
    if trend:
        pos = pos * (c > c.rolling(200).mean())
    return run(pos.to_frame("SPY"), c.pct_change().to_frame("SPY"), COST)


def vix_carry(p, threshold, smooth):
    """Hold inverse-VIX ETP while the VIX futures curve is in contango."""
    c = p["close"]
    ratio = (c["^VIX"] / c["^VIX3M"]).rolling(smooth).mean()
    svxy = c["SVXY"].dropna()
    w = (ratio.reindex(svxy.index) < threshold).astype(float).to_frame("SVXY")
    return run(w, svxy.pct_change().to_frame("SVXY"), COST)


def turn_of_month(p, before, after):
    c = p["close"]["SPY"].dropna()
    idx = c.index
    month = pd.Series(idx.to_period("M"), index=idx)
    day_in = month.groupby(month).cumcount()           # 0 = first trading day
    left = month.groupby(month).transform("size") - day_in  # 1 = last trading day
    # weights at close t earn day t+1, so shift the target window back by one
    hold_next = ((day_in < after) | (left <= before)).shift(-1).fillna(False)
    w = hold_next.astype(float).to_frame("SPY")
    return run(w, c.pct_change().to_frame("SPY"), COST)


def rotation(p, lookback):
    """Monthly: hold the best of SPY/TLT/GLD by trailing return, cash if all < 0."""
    c = p["close"][["SPY", "TLT", "GLD"]].dropna()
    mom = c.pct_change(lookback)
    best = mom.dropna().idxmax(axis=1).reindex(c.index)
    w = pd.get_dummies(best).reindex(columns=c.columns, fill_value=0).astype(float)
    w = w.mul((mom.max(axis=1) > 0).astype(float), axis=0)
    month_end = c.index.to_series().dt.month != c.index.to_series().shift(-1).dt.month
    w = w.where(month_end, np.nan).ffill().fillna(0.0)
    return run(w, c.pct_change(), COST)


FAMILIES = {
    "overnight": (overnight, [dict(ticker=t) for t in ("SPY", "QQQ", "IWM")]),
    "rsi2": (rsi2, [dict(entry=e, exit_=x, trend=t)
                    for e in (5, 10, 20) for x in (50, 70) for t in (False, True)]),
    "vix_carry": (vix_carry, [dict(threshold=t, smooth=s)
                              for t in (0.9, 0.95, 1.0) for s in (1, 5)]),
    "turn_of_month": (turn_of_month, [dict(before=b, after=a) for b in (1, 3) for a in (3, 5)]),
    "rotation": (rotation, [dict(lookback=l) for l in (63, 126, 252)]),
}


def benchmark(p):
    c = p["close"][["SPY"]].dropna()
    return run(pd.DataFrame(1.0, index=c.index, columns=["SPY"]), c.pct_change(), COST)

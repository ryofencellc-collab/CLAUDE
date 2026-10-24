"""Crypto strategy families. Inputs: the panel from data.crypto_panel()."""
import numpy as np
import pandas as pd

from edge.backtest import Result, run

COST = 0.001  # per side: taker fee + slippage
PERIODS = 365


def _rets(px: pd.DataFrame) -> pd.DataFrame:
    return px.pct_change(fill_method=None)


def _liquid(p, min_usd=5e6):
    return p["spot_qv"].rolling(30, min_periods=20).median() > min_usd


def btc_trend(p, sma):
    px = p["spot_close"][["BTC"]].dropna()
    w = (px > px.rolling(sma).mean()).astype(float)
    return run(w, _rets(px), COST)


def xs_momentum(p, lookback, top, regime):
    px = p["spot_close"]
    mom = px.pct_change(lookback, fill_method=None).where(_liquid(p))
    rank = mom.rank(axis=1, ascending=False)
    w = (rank <= top).astype(float)
    w = w.div(w.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    if regime:
        btc = px["BTC"]
        w = w.mul((btc > btc.rolling(100).mean()).astype(float), axis=0)
    # rebalance weekly: keep the weights chosen on every 7th day
    on_rebalance = pd.Series(np.arange(len(w)) % 7 == 0, index=w.index)
    w = w[on_rebalance].reindex(w.index).ffill().fillna(0.0)
    return run(w, _rets(px), COST)


def xs_reversal(p, lookback, top):
    px = p["spot_close"]
    r = px.pct_change(lookback, fill_method=None).where(_liquid(p))
    rank = r.rank(axis=1, ascending=True)  # biggest losers first
    w = (rank <= top).astype(float)
    w = w.div(w.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    return run(w, _rets(px), COST)


def funding_carry(p, window, threshold, top):
    """Delta-neutral cash-and-carry: long spot + short perp, collect funding.

    Daily P&L per unit pair notional = spot_ret - perp_ret + funding paid that
    day. Half the capital sits in spot, half as perp margin, so pair notional
    is 0.5 of capital in total. Each pair weight change trades two legs.
    """
    spot, perp, fund = p["spot_close"], p["perp_close"], p["funding"]
    cols = spot.columns.intersection(perp.columns).intersection(fund.columns)
    idx = fund.index
    spot, perp, fund = spot[cols].reindex(idx), perp[cols].reindex(idx), fund[cols]
    pair_ret = _rets(spot) - _rets(perp) + fund
    sig = fund.rolling(window, min_periods=window).mean()
    sig = sig.where(_liquid(p).reindex(idx)[cols].fillna(False) & pair_ret.notna())
    rank = sig.rank(axis=1, ascending=False)
    pick = (rank <= top) & (sig > threshold)
    w = pick.astype(float)
    w = 0.5 * w.div(w.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    return run(w, pair_ret, 2 * COST)


FAMILIES = {
    "btc_trend": (btc_trend, [dict(sma=n) for n in (20, 50, 100, 150, 200)]),
    "xs_momentum": (xs_momentum, [dict(lookback=l, top=k, regime=g)
                                  for l in (7, 30, 90) for k in (3, 5) for g in (False, True)]),
    "xs_reversal": (xs_reversal, [dict(lookback=l, top=k) for l in (1, 3) for k in (3, 5)]),
    "funding_carry": (funding_carry, [dict(window=w, threshold=t, top=k)
                                      for w in (3, 7, 14) for t in (0.0, 0.0003) for k in (3, 10)]),
}


def benchmark(p):
    px = p["spot_close"][["BTC"]].dropna()
    return run(pd.DataFrame(1.0, index=px.index, columns=["BTC"]), _rets(px), COST)

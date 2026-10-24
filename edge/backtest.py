"""Minimal, honest daily backtester.

Convention: weights are decided with information available at the close of
day t and earn the asset return of day t+1. The shift happens here, in one
place, so strategies cannot accidentally look ahead.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class Result:
    returns: pd.Series   # net daily strategy returns
    turnover: pd.Series  # sum of |weight change| per day
    exposure: pd.Series  # gross exposure per day


def run(weights: pd.DataFrame, asset_returns: pd.DataFrame, cost: float) -> Result:
    """weights[t] = target allocation at close of t; earns asset_returns[t+1].

    cost is the fractional cost per unit of turnover (one side).
    """
    weights = weights.reindex(asset_returns.index).fillna(0.0)
    held = weights.shift(1).fillna(0.0)
    rets = asset_returns.fillna(0.0)
    gross = (held * rets).sum(axis=1)
    # drift-free approximation: rebalance to target daily
    turnover = held.diff().abs().sum(axis=1)
    turnover.iloc[0] = held.iloc[0].abs().sum()
    net = gross - turnover * cost
    return Result(net, turnover, held.abs().sum(axis=1))


def from_returns(net_returns: pd.Series, turnover: pd.Series) -> Result:
    """For strategies that compute their own return stream (e.g. overnight)."""
    return Result(net_returns, turnover, (turnover > 0).astype(float))


def metrics(r: pd.Series, periods: int, turnover: pd.Series | None = None) -> dict:
    r = r.dropna()
    if len(r) < 2 or r.std() == 0:
        return dict(sharpe=0.0, cagr=0.0, vol=0.0, max_dd=0.0, total=0.0,
                    years=len(r) / periods, n=len(r), trades=0)
    eq = (1 + r).cumprod()
    years = len(r) / periods
    dd = (eq / eq.cummax() - 1).min()
    trades = int((turnover.loc[r.index] > 1e-9).sum()) if turnover is not None else 0
    return dict(
        sharpe=float(r.mean() / r.std() * np.sqrt(periods)),
        cagr=float(eq.iloc[-1] ** (1 / years) - 1) if eq.iloc[-1] > 0 else -1.0,
        vol=float(r.std() * np.sqrt(periods)),
        max_dd=float(dd),
        total=float(eq.iloc[-1] - 1),
        years=float(years),
        n=int(len(r)),
        trades=trades,
    )

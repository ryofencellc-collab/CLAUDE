import numpy as np
import pandas as pd

from edge import round14 as r


def test_bs_put_call_parity_and_limits():
    S, K, T, v, rate = 100.0, 102.0, 7 / 365, 0.2, 0.04
    c, p = r.bs(S, K, T, v, rate, "call"), r.bs(S, K, T, v, rate, "put")
    assert abs((c - p) - (S - K * np.exp(-rate * T))) < 1e-9
    assert r.bs(S, K, 0, v, rate, "call") == 0.0 and r.bs(S, 90, 0, v, rate, "call") == 10.0


def _market(n=400, seed=0, drift=0.0):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2023-05-01", periods=n)
    close = pd.Series(400 * np.exp(np.cumsum(rng.normal(drift, 0.01, n))), index=idx)
    opn = close * np.exp(-rng.normal(drift, 0.01, n))  # open-to-close moves of 1% a day
    vix = pd.Series(16.0, index=idx)
    rate = pd.Series(0.04, index=idx)
    return opn, close, vix, rate


def test_fairly_priced_options_lose_the_spread_on_average():
    # with prices drawn from the same vol the model uses, buyers should lose about the spread, not win
    opn, close, vix, rate = _market(n=3000, seed=1)
    vix1d = pd.Series(0.01 * np.sqrt(252) * 100, index=close.index)  # 1% a day on a trading-time basis
    t = r.b2_0dte_calls(opn, close, vix1d, rate)
    assert len(t) > 2000 and t["ret"].mean() < 0.05


def test_condor_pnl_bounded_by_credit_and_max_loss():
    opn, close, vix, rate = _market()
    t = r.b3_0dte_condor(opn, close, vix * 1.5, rate)
    assert (t["pnl"] <= t["credit"] + 1e-9).all() and (t["pnl"] >= -t["max_loss"] - 1e-9).all()


def test_weekly_puts_and_calls_run():
    opn, close, vix, rate = _market(n=600)
    assert len(r.b4_weekly_puts(close, vix, rate)) > 100
    t = r.b1_weekly_calls(close, vix, rate)
    assert len(t) > 100 and (t["cost"] > 0).all()
    assert r.equity_buyer(t).iloc[-1] > 0


def test_0dte_price_is_sane():
    # an ATM 0DTE SPY call at VIX1D 15 should cost about 0.4 x S x 15%/sqrt(252), not a few cents
    c = r.bs(500, 500, r.T_0DTE, 0.15, 0.04, "call")
    assert 1.5 < c < 2.2

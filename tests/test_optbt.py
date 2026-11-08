"""Round 35 backtester sanity: on synthetic Black-Scholes chains, selling premium must earn money when implied
vol is above realized vol and lose (about the costs) when it is not; natural fills and commissions must bite."""
import numpy as np
import pandas as pd
from scipy.stats import norm

from edge import optbt as B


def synth(iv_over_rv: float, seed=0, days=600, rv=0.18, spread=0.02):
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2021-01-04", periods=days)
    px = 400 * np.exp(np.cumsum(rng.normal(0, rv / np.sqrt(252), days)))
    s = pd.Series(px, index=dates)
    iv = rv * iv_over_rv
    rows = []
    fridays = pd.bdate_range("2021-01-01", periods=days + 120, freq="W-FRI")
    for d, S in s.items():
        exps = [e for e in fridays if 10 <= (e - d).days <= 75][::2]
        for e in exps:
            T = (e - d).days / 365
            for k in np.arange(round(S * 0.8 / 5) * 5, S * 1.2, 5.0):
                d1 = (np.log(S / k) + 0.5 * iv ** 2 * T) / (iv * np.sqrt(T))
                d2 = d1 - iv * np.sqrt(T)
                c = S * norm.cdf(d1) - k * norm.cdf(d2)
                p = c - S + k
                for cp, val, de in (("Call", c, norm.cdf(d1)), ("Put", p, norm.cdf(d1) - 1)):
                    half = max(0.01, spread * val / 2 + 0.01)
                    rows.append({"date": d, "expiration": e, "strike": float(k), "call_put": cp, "bid": max(0.0, round(val - half, 2)),
                                 "ask": round(val + half, 2), "vol": iv, "delta": de})
    chain = pd.DataFrame(rows)
    return chain, pd.DataFrame({"Close": s})


def run_put_spreads(iv_over_rv, seed=0, manage=False):
    chain, px = synth(iv_over_rv, seed)
    book = B.Book(chain, px["Close"])
    ctx = B.context(book)
    st = B.Strat("ps", "put_spread", delta=0.30, manage=manage)
    curve, trades = B.run([st], {"SPY": book}, {"SPY": ctx}, {}, chain["date"].min(), chain["date"].max() + pd.Timedelta(days=1))
    return B.stats(curve, trades, 25_000), trades


def test_premium_selling_pays_only_when_options_are_overpriced():
    # hold-to-expiry: per-trade P&L must be positive when options are rich and negative at fair prices (costs)
    rich = [run_put_spreads(1.6, seed)[1] for seed in range(2)]
    fair = [run_put_spreads(1.0, seed)[1] for seed in range(2)]
    per = lambda ts: np.mean([(t["pnl"] / t["qty"]).mean() for t in ts])
    assert per(rich) > 0 > per(fair)


def test_engine_matches_a_hand_count_of_hold_to_expiry():
    chain, px = synth(1.6, 0)
    book = B.Book(chain, px["Close"])
    st, tr = run_put_spreads(1.6, 0)
    t = tr.iloc[0]
    e = B.pick_exp(book.by_day[t["entry"]], t["entry"], 25, 50, 35)
    legs = B.vertical(book, t["entry"], e, "P", 0.30)[0]
    hand = (B.open_cash(book, t["entry"], legs) + sum(B.intrinsic(l, book.spot(e)) for l in legs)) * 100 - 2 * 0.65
    assert abs(t["pnl"] / t["qty"] - hand) < 1e-6


def test_trades_have_sane_bookkeeping():
    st, tr = run_put_spreads(1.3, manage=True)
    assert len(tr) > 20 and set(tr["why"]) <= {"50% profit", "stop 2x", "21 days left", "expiry"}
    assert (tr["pnl"] >= -tr["max_loss"] - 50).all()                   # never loses more than its defined risk (+ fees)
    assert (tr["max_loss"] <= 0.05 * 60_000).all()

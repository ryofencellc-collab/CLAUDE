import pandas as pd

from edge import options as op


def test_put_payoff_and_fees():
    fri = pd.Timestamp("2024-01-05")
    df = pd.DataFrame([dict(friday=fri, expiry=fri + pd.Timedelta(days=7), strike=40000,
                            price_btc=0.01, spot=44000.0, n_trades=3)])
    spot = pd.Series({fri + pd.Timedelta(days=7): 38000.0})
    r = op.sell_puts(df, spot, m=0.90)
    p = 0.01 * 0.95
    fees = 0.0003 + 0.00015
    assert abs(r["ret"].iloc[0] - ((p - fees) * 44000 - 2000) / 40000) < 1e-12
    assert not r["won"].iloc[0]

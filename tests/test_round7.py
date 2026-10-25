import pandas as pd

from edge import round7 as r7


def test_bracket_arb_detects_cheap_set():
    rows = [dict(event="E", city="x", date=pd.Timestamp("2026-01-01"), bid=b, ask=a, yes_won=w)
            for b, a, w in ((0.20, 0.22, False), (0.30, 0.31, True), (0.40, 0.42, False))]
    arb, info = r7.bracket_arb(pd.DataFrame(rows))
    assert info["events_checked"] == 1
    assert arb["buy_all"].iloc[0] < 1 - 0.95 + 1e-9          # 1 - 0.95 - fees
    assert arb["buy_all"].iloc[0] > 0                         # cheap enough to beat fees
    assert arb["sell_all"].iloc[0] < 0                        # bids sum to 0.90


def test_tennis_symmetric():
    df = pd.DataFrame([dict(year=2023, PSW=1.5, PSL=2.6, MaxW=1.6, MaxL=2.9)])
    b = r7.tennis_value(df, edge=0.02, max_odds=None)
    assert len(b) == 2 and abs(b["ret"].sum() - (0.6 - 1)) < 1e-9

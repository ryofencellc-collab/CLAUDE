import numpy as np
import pandas as pd

from edge import weather as wx


def test_probabilities_and_fee():
    row = dict(strike_type="greater", floor=64, cap=None)
    assert abs(wx.prob_yes(row, 64.5, 2.0) - 0.5) < 1e-9          # P(high >= 65) when mean 64.5
    br = dict(strike_type="between", floor=63, cap=64)
    lo = dict(strike_type="less", floor=None, cap=63)
    hi = dict(strike_type="greater", floor=64, cap=None)
    total = sum(wx.prob_yes(r, 63.7, 2.5) for r in (lo, br, hi))
    assert abs(total - 1) < 1e-9                                   # brackets partition the outcomes
    assert wx.fee(20, 0.5) == 0.35                                 # 0.07*20*0.25 = 0.35
    assert wx._target_date("KXHIGHNY-26OCT23") == pd.Timestamp("2026-10-23")


def test_bets_pays_correctly():
    df = pd.DataFrame([dict(city="nyc", date=pd.Timestamp("2026-01-01"), event="E", strike_type="greater",
                            floor=70, cap=None, yes_won=True, bid=0.18, ask=0.20, gfs=75.0)])
    b = wx.bets(df, {"nyc": (0.0, 2.0)}, edge=0.10, per_event="best", fc="gfs")
    assert list(b["side"]) == ["yes"]
    assert abs(b["pnl"].iloc[0] - (50 - 10 - wx.fee(50, 0.2))) < 1e-9


def test_locate_tiers():
    assert wx.locate("KXHIGHNY", "Highest temperature in NYC")[:2] == ("new york", "major")
    assert wx.locate("KXHIGHTRJTT", "Daily high temp Tokyo")[:2] == ("RJTT", "minor")
    assert wx.locate("KXHIGHTOKC", "Oklahoma City Maximum High Temperature")[:2] == ("OKC", "minor")
    assert wx.locate("KXHIGHMIA", "Highest temperature in Miami")[1] == "major"

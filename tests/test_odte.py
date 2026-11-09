from datetime import datetime, timezone
from edge import odte


def test_parse_keeps_near_dated_near_money():
    js = {"timestamp": "2026-11-09 15:00:00", "data": {"current_price": 7000.0, "options": [
        {"option": "SPXW261109C07000000", "bid": 10.0, "ask": 10.5},   # 0DTE ATM: keep
        {"option": "SPXW261109P06000000", "bid": 0.0, "ask": 0.05},    # far OTM: drop
        {"option": "SPX261218C07000000", "bid": 90.0, "ask": 91.0},    # 39 DTE: drop
        {"option": "SPXW261111P06950000", "bid": 20.0, "ask": 20.6},   # 2DTE: keep
        {"option": "junk"}]}}
    df = odte.parse(js, datetime(2026, 11, 9, 15, 15, tzinfo=timezone.utc))
    assert list(zip(df.root, df.exp, df.cp, df.K)) == [
        ("SPXW", "2026-11-09", "C", 7000.0), ("SPXW", "2026-11-11", "P", 6950.0)]
    assert (df.spot == 7000.0).all() and df.ts_feed.iloc[0] == "2026-11-09 15:00:00"


def test_parse_no_spot_is_empty():
    assert odte.parse({"data": {"options": []}}, datetime.now(timezone.utc)).empty

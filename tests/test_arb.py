from edge import arb


def m(t, K=None, yb=0.0, ya=1.0, ybs=0, yas=0, stype="greater"):
    return {"ticker": t, "floor_strike": K, "strike_type": stype, "yes_bid_dollars": yb, "yes_ask_dollars": ya,
            "yes_bid_size_fp": ybs, "yes_ask_size_fp": yas, "close_time": "2030-01-01T00:00:00Z", "status": "active"}


def test_ladder_violation_is_found_and_priced():
    ms = [m("A-T100", 100, yb=0.40, ya=0.42, ybs=50, yas=30), m("A-T110", 110, yb=0.45, ya=0.47, ybs=20, yas=10)]
    h = arb.mono("A", ms)
    assert len(h) == 1 and h[0]["n"] == 20
    assert abs(h[0]["cost"] - 20 * (0.42 + 0.55)) < 1e-9 and h[0]["payout"] == 20 and h[0]["riskless"]
    assert h[0]["profit"] < 20 * 0.03  # fees bite


def test_consistent_ladder_has_no_hit():
    ms = [m("A-T100", 100, yb=0.60, ya=0.62, ybs=50, yas=30), m("A-T110", 110, yb=0.40, ya=0.42, ybs=20, yas=10)]
    assert arb.mono("A", ms) == []


def test_no_all_on_exclusive_event():
    ms = [m(f"E-{i}", yb=0.40, ya=0.45, ybs=100, yas=100, stype=None) for i in range(3)]  # bids sum 1.20
    h = [x for x in arb.allsides("K", "E", ms, arb.taker_fee) if x["kind"] == "K-NOALL"][0]
    assert h["payout"] == 200 and abs(h["cost"] - 3 * 100 * 0.60) < 1e-9 and h["profit"] > 0


def test_yes_all_is_never_marked_riskless():
    ms = [m(f"E-{i}", yb=0.20, ya=0.30, ybs=10, yas=10, stype=None) for i in range(3)]  # asks sum 0.90
    h = arb.allsides("K", "E", ms, arb.taker_fee)
    assert [x["kind"] for x in h] == ["K-YESALL"] and not h[0]["riskless"]


def test_taker_fee_rounds_up_per_order():
    assert arb.taker_fee(1, 0.5) == 0.02 and arb.taker_fee(100, 0.5) == 1.75 and arb.taker_fee(0, 0.5) == 0.0

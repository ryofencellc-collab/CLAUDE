from edge import lip


def test_reference_is_first_level_reaching_a_fifth_of_target():
    lv = [(0.50, 50), (0.49, 200), (0.48, 1000)]
    assert lip.reference(lv, 1000) == 0.49            # 50 < 200 <= 250


def test_share_with_discount_and_queue_position():
    lv = [(0.50, 100), (0.49, 400), (0.47, 1000)]
    sh, ok = lip.side_share(lv, 1000, 0.5, 300, 0.49)
    # book: .50x100, .49x400, .49x300(us); ref .49; first 1000: 100+400+300 at full credit (.50 >= ref), then 200 @ .47 x .25
    assert ok and abs(sh - 300 / (100 + 400 + 300 + 200 * 0.25)) < 1e-9


def test_side_below_target_is_invalid():
    sh, ok = lip.side_share([(0.5, 100)], 1000, 0.5, 300, 0.5)
    assert not ok and sh == 0.0


def pos(q=100):
    p = lip.new_pos({"market_ticker": "M", "id": "x", "target_size_fp": "1000", "discount_factor_bps": 5000,
                     "period_reward": 1_000_000, "start_date": "2026-11-09T00:00:00Z", "end_date": "2026-11-16T00:00:00Z"})
    p.update(q=q, yes_px=0.40, no_px=0.55, yes_ahead=50.0, no_ahead=0.0)
    return p


def test_queue_ahead_fills_first_then_us_and_pairs_net_to_a_dollar():
    p = pos()
    f = lip.apply_trades(p, [{"created_time": "1", "taker_side": "no", "yes_price_dollars": "0.40", "count_fp": "80"},
                             {"created_time": "2", "taker_side": "yes", "no_price_dollars": "0.55", "count_fp": "30"}])
    assert [x["n"] for x in f] == [30, 30]
    assert p["inv_yes"] == 0 and p["inv_no"] == 0 and abs(p["realized"] - 30 * (1 - 0.40 - 0.55)) < 1e-9


def test_trade_through_our_price_fills_the_rest_but_never_beyond_q():
    p = pos(q=100)
    lip.apply_trades(p, [{"created_time": "1", "taker_side": "no", "yes_price_dollars": "0.38", "count_fp": "5000"}])
    assert p["inv_yes"] == 100
    lip.apply_trades(p, [{"created_time": "2", "taker_side": "no", "yes_price_dollars": "0.30", "count_fp": "5000"}])
    assert p["inv_yes"] == 100                         # inventory cap


def test_pool_day_units():
    assert abs(lip.pool_day({"period_reward": 1_000_000, "start_date": "2026-11-09T00:00:00Z", "end_date": "2026-11-16T00:00:00Z"}) - 100 / 7) < 1e-9

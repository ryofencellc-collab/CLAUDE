"""Hand-checked fills for the intraday simulator."""
import numpy as np
import pandas as pd

from edge import intraday as it


def bars(rows, start="2024-03-05 09:30"):
    idx = pd.date_range(start, periods=len(rows), freq="min")
    return pd.DataFrame(rows, columns=["open", "high", "low", "close"], index=idx, dtype=float)


def run(b, sig, sdist=10.0, rr=1.5, cost=0.0, max_per_win=3):
    n = len(b)
    win = np.zeros(n, np.int64)
    last = np.zeros(n, bool)
    last[-1] = True
    return it.simulate(b, win, last, np.array(sig), np.full(n, sdist), np.full(n, np.nan),
                       np.full(n, rr), max_per_win, cost)


def test_long_target_hit_next_bar_open_entry():
    b = bars([[100, 101, 99, 100], [100, 103, 99, 102], [102, 116, 101, 115], [115, 116, 114, 115]])
    t = run(b, [1, 0, 0, 0])
    assert len(t) == 1
    assert t["time"].iloc[0] == b.index[1]            # filled next bar
    assert np.isclose(t["R"].iloc[0], 1.5)            # target = 100 + 15


def test_stop_wins_when_both_inside_one_bar():
    b = bars([[100, 100, 100, 100], [100, 120, 85, 100], [100, 100, 100, 100]])
    t = run(b, [1, 0, 0])
    assert np.isclose(t["R"].iloc[0], -1.0)


def test_gap_through_stop_fills_at_open():
    b = bars([[100, 100, 100, 100], [100, 101, 99, 100], [80, 81, 79, 80], [80, 80, 80, 80]])
    t = run(b, [1, 0, 0, 0])
    assert np.isclose(t["R"].iloc[0], -2.0)           # (80-100)/10


def test_flat_at_window_end_and_costs():
    b = bars([[100, 100, 100, 100], [100, 102, 99, 101], [101, 104, 100, 104]])
    t = run(b, [-1, 0, 0], cost=1.0)
    assert np.isclose(t["pts"].iloc[0], -(104 - 100) - 1.0)


def test_no_lookahead_signal_on_last_bar_ignored():
    b = bars([[100, 100, 100, 100], [100, 100, 100, 100]])
    assert run(b, [0, 1]).empty


def test_orb_long_uses_range_low_as_stop():
    rows = [[100, 105, 98, 104]] + [[104, 104.5, 103.5, 104]] * 4 + [[104, 104, 104, 104]] + \
           [[104, 125, 103, 124]] + [[124, 124, 124, 124]] * 400
    b = bars(rows)
    t = it.orb(b, n=5, k=1.5)
    assert len(t) == 1
    # direction up (104 > 100), entry 104 at 09:35, stop at OR low 98 -> risk 6, target 113
    assert np.isclose(t["R"].iloc[0], (113 - 104 - it.COST_PTS) / 6)


def test_liquidity_sweep_fades_prior_high():
    day1 = [[100, 110, 95, 105]] + [[105, 106, 104, 105]] * 389          # prior high 110
    day2 = [[105, 106, 104, 105]] * 5 + [[109, 112, 108, 109]] + [[109, 109, 100, 101]] + \
           [[101, 101, 101, 101]] * 383
    b1 = bars(day1, "2024-03-04 09:30")
    b2 = bars(day2, "2024-03-05 09:30")
    t = it.liquidity_sweep(pd.concat([b1, b2]), window="rth", r=1.5)
    assert len(t) == 1
    # swept 112, closed 109 < 110 -> short at next open 109, stop 113 (risk 4), target 103
    assert t["time"].iloc[0] == b2.index[6]
    assert np.isclose(t["R"].iloc[0], (109 - 103 - it.COST_PTS) / 4)

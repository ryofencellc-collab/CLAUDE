import pandas as pd
from edge import odte_score as o


def test_condor_expiry_value_and_credit():
    legs = [("P", 100.0, -1), ("P", 95.0, 1), ("C", 110.0, -1), ("C", 115.0, 1)]
    assert o.spread_value(105, legs) == 0
    assert o.spread_value(112, legs) == -2          # short call 2 in the money
    assert o.spread_value(120, legs) == -5          # capped by the wing
    g = pd.DataFrame({"cp": ["P", "P", "C", "C"], "K": [100.0, 95.0, 110.0, 115.0], "bid": [1.0, 0.4, 1.2, 0.5],
                      "ask": [1.1, 0.5, 1.3, 0.6], "delta": [-0.1, -0.05, 0.1, 0.05]}).set_index(["cp", "K"])
    assert abs(o.credit_of(g, legs) - (1.0 - 0.5 + 1.2 - 0.6)) < 1e-9     # sell at bid, buy at ask
    assert abs(o.close_cost(g, legs) - (1.1 - 0.4 + 1.3 - 0.5)) < 1e-9    # buy back at ask, sell longs at bid
    assert o.by_delta(g, "P", 0.10) == 100.0 and o.wing(g, "P", 100.0, 5) == 95.0

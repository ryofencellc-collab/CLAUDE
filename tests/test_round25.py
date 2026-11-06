import numpy as np
import pandas as pd

from edge import round25 as r


def series(n=60 * 24 * 10, seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2026-01-01", periods=n, freq="1min", tz="UTC")
    return pd.Series(100 * np.exp(np.cumsum(rng.normal(0, 0.0008, n))), index=idx)


def test_frame_labels_and_no_lookahead():
    s = series()
    d = r.frame(s, 0)
    row = d[d["tau"] == 5].iloc[100]
    K, final = s[row["close"] - pd.Timedelta(minutes=15)], s[row["close"]]
    assert row["flip"] == ((np.log(final / K) > 0) != (row["z"] > 0))
    s2 = s.copy()
    s2[s2.index > row["time"]] *= 1.5                                       # change only the future
    d2 = r.frame(s2, 0).set_index("time")
    assert np.isclose(d2.loc[row["time"], "z"], row["z"])                    # features unchanged


def test_kelly_fraction_shrinks_with_risk_and_respects_cap():
    p = np.array([0.0, 0.001, 0.005, 0.02])
    f = r.kelly_fraction(p, 1.0, 0.95)
    assert f[0] == 0.95 and 0 < f[2] < f[1] <= 0.95 and f[3] == 0


def test_simulator_one_market_at_a_time_pyramids_and_books_losses():
    t = pd.date_range("2026-01-01 00:10", periods=4, freq="1min", tz="UTC")
    fills = pd.DataFrame({"time": [t[0], t[1], t[2], t[3]], "ticker": ["A", "A", "B", "A"],
                          "count": [4000.0, 4000.0, 4000.0, 4000.0], "ours_won": [False, False, True, False]})
    fills["close"] = pd.Timestamp("2026-01-01 00:15", tz="UTC")
    out = r.simulate(fills, np.array([0.1, 0.5, 0.5, 0.5]))
    # A: first fill capped at 10% (101 contracts), grows to 50% (505), B ignored (busy), loss books 505 * 0.99
    assert out["markets"] == 1 and out["losses"] == 1
    assert abs(out["final"] - (1000 - 505 * 0.99 - r.fee(101) - r.fee(404))) < 1e-6


def test_models_fit_and_predict_probabilities():
    d = r.frame(series(), 0)
    d = d[d["az"] >= 2]
    for M in (r.ZBins, r.Logit, r.GBM):
        p = M().fit(d).predict(d)
        assert np.all((p >= 0) & (p <= 1)) and abs(np.nanmean(p) - d["flip"].mean()) < 0.02


def test_features_at_fill_times_use_the_last_completed_minute():
    s = series()
    times = pd.Series(pd.to_datetime(["2026-01-03 10:07:30", "2026-01-03 10:13:59"], utc=True))
    f = r.features_at(s, 0, times)
    d = r.frame(s, 0).set_index("time")
    m = d.loc[pd.Timestamp("2026-01-03 10:07", tz="UTC")]                    # last completed minute
    assert np.isclose(f.loc[0, "tau"], 7.5) and np.isclose(f.loc[1, "tau"], 61 / 60)
    assert np.isclose(f.loc[0, "z"], m["z"] * np.sqrt(m["tau"] / 7.5))     # time left from the fill itself


def test_models_survive_edge_values_and_never_enter_on_unscorable_rows():
    d = r.frame(series(), 0)
    tr = d[d["az"] >= 2]
    bad = tr.head(6).copy()
    bad.loc[bad.index[0], "az"] = 0.0                                       # fill exactly at the strike
    bad.loc[bad.index[1], "jump"] = np.inf                                   # zero-volatility minute
    bad.loc[bad.index[2], "volratio"] = np.nan                               # missing feature
    bad.loc[bad.index[3], "mom5"] = -np.inf
    for M in (r.ZBins, r.Logit, r.GBM):
        p = M().fit(tr).predict(bad)
        assert np.all(np.isfinite(p)) and np.all((p >= 0) & (p <= 1))
        if M is not r.GBM:                                                   # GBM handles NaN natively
            assert p[2] == 1.0                                               # unscorable: maximum risk, never entered

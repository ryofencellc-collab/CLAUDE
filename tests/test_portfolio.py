import pandas as pd

from edge import portfolio as pf


def fills(rows):
    return pd.DataFrame([dict(ticker=t, close=pd.Timestamp(c), status=s, excess=e) for t, c, s, e in rows])


def test_losing_fill_pauses_then_halves(monkeypatch):
    monkeypatch.setattr(pf, "sleeve_a_fills", lambda: fills([
        ("W1", "2026-11-02 10:00", "won", 5000.0),
        ("L1", "2026-11-02 11:00", "lost", 5000.0),
        ("W2", "2026-11-02 12:00", "won", 5000.0),     # inside the 24 h pause: skipped
        ("W3", "2026-11-04 12:00", "won", 5000.0)]))   # half size afterwards
    monkeypatch.setattr(pf, "sleeve_b", lambda: pd.Series(dtype=float))
    monkeypatch.setattr(pf, "sleeve_c", lambda: pd.Series(dtype=float))
    t, notes = pf.book()
    fee = pf.paper21.r15._maker_fee
    a = t.set_index("day")["A"]
    want_day1 = (2500 * 0.01 - fee(2500, 0.99)) + (-2500 * 0.99 - fee(2500, 0.99))
    assert abs(a.iloc[0] - want_day1) < 1e-9
    # half size after the loss (1,250), halved again by the -15% drawdown rule (equity fell ~24.5%)
    assert abs(a.iloc[1] - (625 * 0.01 - fee(625, 0.99))) < 1e-9
    assert any("paused" in n for n in notes) and any("daily stop" in n for n in notes)


def test_sleeves_combine_and_compound_b(monkeypatch):
    monkeypatch.setattr(pf, "sleeve_a_fills", lambda: pd.DataFrame())
    monkeypatch.setattr(pf, "sleeve_b", lambda: pd.Series([0.01, 0.01], index=pd.to_datetime(["2026-11-02", "2026-11-03"])))
    monkeypatch.setattr(pf, "sleeve_c", lambda: pd.Series([18.8], index=pd.to_datetime(["2026-11-03"])))
    t, _ = pf.book()
    assert abs(t["B"].iloc[0] - 40.0) < 1e-9 and abs(t["B"].iloc[1] - 40.4) < 1e-9
    assert abs(t["total"].sum() - (40 + 40.4 + 18.8)) < 1e-9
    assert "Portfolio profit" in pf.summary()

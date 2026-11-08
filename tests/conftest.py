import pytest


@pytest.fixture(autouse=True)
def _live21_tests_use_no_reversal_table(monkeypatch, tmp_path):
    """live21 tests must not depend on whichever control/r25_zbins.json is committed; tests that need a
    table install their own."""
    from edge import live21
    monkeypatch.setattr(live21, "ZBINS", tmp_path / "no_table.json")
    # no test may touch the real paper/ files (log, state, report, stop file)
    monkeypatch.setattr(live21, "STATE", tmp_path / "state.json")
    monkeypatch.setattr(live21, "LOG", tmp_path / "log.csv")
    monkeypatch.setattr(live21, "STOP", tmp_path / "STOP")
    root = tmp_path / "paper"
    root.mkdir()
    monkeypatch.setattr(live21, "ROOT", root)
    live21._table.clear()
    # no test may reach a real exchange: every price source answers "no data" unless a test installs one
    import pandas as pd
    from edge import prices
    monkeypatch.setattr(prices, "fetch", lambda source, product: pd.Series(dtype=float))
    prices._cache.clear()
    # tests describe one candidate through L.decide; the trader asks decide_many (late-bound, so later patches apply)
    monkeypatch.setattr(live21, "decide_many", lambda now, exclude=frozenset(), look=12: [
        p for p in [live21.decide(now)] if p and p[0]["ticker"] not in exclude])
    yield
    live21._table.clear()

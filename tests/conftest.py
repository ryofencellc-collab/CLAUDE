import pytest


@pytest.fixture(autouse=True)
def _live21_tests_use_no_reversal_table(monkeypatch, tmp_path):
    """live21 tests must not depend on whichever control/r25_zbins.json is committed; tests that need a
    table install their own."""
    from edge import live21
    monkeypatch.setattr(live21, "ZBINS", tmp_path / "no_table.json")
    live21._table.clear()
    yield
    live21._table.clear()

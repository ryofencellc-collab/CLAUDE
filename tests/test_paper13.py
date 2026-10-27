import pandas as pd

from edge import paper13
from tests.test_round13 import fake


def test_paper13_books_days_append_only(tmp_path, monkeypatch):
    monkeypatch.setattr(paper13, "LEDGER", tmp_path / "led.csv")
    px = fake()
    monkeypatch.setattr(paper13, "FORWARD_START", px.index[-6])
    led1 = paper13.step(px.iloc[:-3])
    assert len(led1) == 3 and led1["day_return"].iloc[0] == 0.0
    led2 = paper13.step(px)
    assert len(led2) == 6
    assert led2.iloc[:3]["equity"].tolist() == led1["equity"].tolist()  # history never rewritten
    w = led2[[c for c in led2 if c.startswith("w_")]].sum(axis=1)
    assert (w <= 1 + 1e-6).all()
    assert "Paper equity" in paper13.summary(led2)

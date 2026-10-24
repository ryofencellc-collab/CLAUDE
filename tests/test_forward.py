"""Paper trader: only pre-kickoff value bets are logged, and settlement pays correctly."""
import pandas as pd

from edge import forward as fw


def fixture_row(date, time, home, away, ps, mx):
    return dict(Div="E0", Date=date, Time=time, HomeTeam=home, AwayTeam=away,
                PSH=ps[0], PSD=ps[1], PSA=ps[2], MaxH=mx[0], MaxD=mx[1], MaxA=mx[2],
                B365H=mx[0], B365D=mx[1], B365A=mx[2])


def test_log_then_settle(tmp_path, monkeypatch):
    monkeypatch.setattr(fw, "LEDGER", tmp_path / "bets.csv")
    monkeypatch.setattr(fw, "ROOT", tmp_path)
    fx = pd.DataFrame([
        # home: Pinnacle 2.0 / 3.5 / 4.0 -> fair home ~2.08; best 2.30 is +10%: bet
        fixture_row("01/11/2026", "15:00", "A", "B", (2.0, 3.5, 4.0), (2.30, 3.5, 4.0)),
        # no edge anywhere
        fixture_row("01/11/2026", "15:00", "C", "D", (2.0, 3.5, 4.0), (2.0, 3.5, 4.0)),
        # already kicked off: never bet
        fixture_row("24/10/2026", "12:00", "E", "F", (2.0, 3.5, 4.0), (2.6, 3.5, 4.0)),
    ])
    results = pd.DataFrame([dict(Div="E0", Date="01/11/2026", HomeTeam="A", AwayTeam="B", FTR="H")])
    monkeypatch.setattr(fw, "_csv", lambda url: fx if "fixtures" in url else results)

    fw.run(pd.Timestamp("2026-10-24 13:00", tz="UTC"))
    led = fw.ledger()
    assert list(led["home"]) == ["A"] and list(led["status"]) == ["open"]

    fw.run(pd.Timestamp("2026-10-24 19:00", tz="UTC"))   # rerun: no duplicate
    assert len(fw.ledger()) == 1

    fw.run(pd.Timestamp("2026-11-02 08:00", tz="UTC"))   # after the match
    led = fw.ledger()
    assert led.loc[0, "status"] == "won"
    assert abs(led.loc[0, "pnl"] - 13.0) < 1e-9          # $10 at 2.30
    assert "+13.00" in (tmp_path / "SUMMARY.md").read_text()

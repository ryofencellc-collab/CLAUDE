import numpy as np
import pandas as pd

from edge import round8 as r8
from edge.copytrade import parse_ptr_text

DATES = pd.bdate_range("2020-01-01", periods=40)


def _px():
    px = pd.DataFrame({"SPY": 100.0, "AAA": 100.0, "BBB": 100.0}, index=DATES)
    px.loc[DATES[10]:, "AAA"] = 110.0   # AAA jumps 10% on session 10
    return px


def test_13f_buys_after_filing_not_before():
    h = pd.DataFrame(dict(filed=[DATES[10]], accession=["a1"], ticker=["AAA"], value=[1.0], shares=[1.0],
                          cik=["1"]))
    r = r8.run_portfolios(r8.portfolios_13f(h, 10, "value", "all"), _px())
    # filed on the jump day: entry is the next close, so the jump is missed
    assert r.loc[:DATES[11]].fillna(0).sum() == -r8.COST
    assert r.loc[DATES[12]:].abs().sum() == 0


def test_13f_captures_moves_after_entry():
    h = pd.DataFrame(dict(filed=[DATES[5]], accession=["a1"], ticker=["AAA"], value=[1.0], shares=[1.0],
                          cik=["1"]))
    r = r8.run_portfolios(r8.portfolios_13f(h, 10, "value", "all"), _px())
    assert np.isclose(r[DATES[10]], 0.10)


def test_congress_entry_after_disclosure_and_hold():
    c = pd.DataFrame(dict(type=["P"], asset_type=["ST"], ticker=["AAA"], amount_low=[1001.0],
                          tx_date=[DATES[0]], filed=[DATES[8]], last=["X"], member=["X"]))
    px = _px()
    e = r8.congress_events(c, px)
    assert e["entry"].iloc[0] == DATES[9]
    r = r8.run_events(e, px, hold=5)
    assert np.isclose(r[DATES[10]], 0.10 - r8.COST * 0)  # entry cost booked on the entry day
    assert r.loc[DATES[15]:].abs().sum() == 0             # after exit: SPY, flat


def test_ptr_split_amount():
    txt = ("          SP          Bloom Energy Corporation Class A         P                07/24/2026 07/24/2026"
           "            $1,000,001 -\n"
           "                      Common Stock (BE) [ST]                                              $5,000,000\n")
    (row,) = parse_ptr_text(txt)
    assert (row["ticker"], row["owner"], row["amount_low"], row["amount_high"]) == ("BE", "SP", 1000001.0, 5000000.0)


def test_ptr_amount_on_line_below_dates():
    txt = ("          SP          Foo Inc (FOO) [ST]         P                07/24/2019 07/24/2019\n"
           "                                                   $1,001 - $15,000\n")
    (row,) = parse_ptr_text(txt)
    assert (row["ticker"], row["amount_low"], row["amount_high"]) == ("FOO", 1001.0, 15000.0)

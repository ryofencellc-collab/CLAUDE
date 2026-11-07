"""edge/prices.py: three-exchange spot, checked on real responses saved by the probe workflow (2026-11-07)."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from edge import paper21 as P
from edge import prices as px

FX = Path(__file__).parent / "fixtures"
NOW = pd.Timestamp(1794066900, unit="s", tz="UTC")  # 15:55 UTC: the probe's last complete minute ends here


def real(source):
    name = {"coinbase": "coinbase_BTC-USD", "kraken": "kraken_XBTUSD", "bitstamp": "bitstamp_btcusd"}[source]
    j = json.loads((FX / f"{name}.json").read_text())
    return {"coinbase": px.parse_coinbase, "kraken": px.parse_kraken, "bitstamp": px.parse_bitstamp}[source](j)


def test_parsers_read_the_real_responses_with_end_time_index():
    for src in px.SOURCES:
        c = real(src).sort_index()
        assert len(c) >= 60 and c.between(70000, 80000).all(), src
        assert (c.index.second == 0).all()
    k = real("kraken")
    assert k.index.max() == pd.Timestamp(1794066960, unit="s", tz="UTC")       # the minute still forming...
    spots, vol, used = px.quote("BTC-USD", NOW, fetcher=lambda s, p: real(s))
    assert used == "coinbase,kraken,bitstamp" and len(spots) == 3              # ...is dropped by quote()
    assert max(spots) / min(spots) - 1 < 0.001 and 0 < vol < 0.01
    assert len(px.parse_kraken(json.loads((FX / "kraken_XDGUSD.json").read_text()))) > 60   # DOGE's odd key


def fake(closes: dict, end=NOW, n=60, vol=0.0005):
    """Synthetic 1-minute closes per source: a random walk that ends exactly at the given close."""
    def f(src, product):
        if src not in closes:
            return pd.Series(dtype=float)
        steps = np.random.default_rng(len(src)).normal(0, vol, n)
        path = closes[src] * np.exp(np.cumsum(steps) - np.cumsum(steps)[-1])
        return pd.Series(path, index=pd.date_range(end=end, periods=n, freq="1min", tz="UTC"))
    return f


def test_needs_two_fresh_sources_and_agreement():
    assert px.quote("BTC-USD", NOW, fake({"coinbase": 75000}))[0] == []                          # one source
    s, v, _ = px.quote("BTC-USD", NOW, fake({"coinbase": 75000, "kraken": 75010}))
    assert len(s) == 2 and np.isfinite(v)
    s, _, why = px.quote("BTC-USD", NOW, fake({"coinbase": 75000, "kraken": 75010, "bitstamp": 76000}))
    assert s == [] and "disagree" in why                                                        # 1.3% off: no price
    stale = fake({"coinbase": 75000, "kraken": 75010}, end=NOW - pd.Timedelta(minutes=4))
    assert px.quote("BTC-USD", NOW, stale)[0] == []
    short = fake({"coinbase": 75000, "kraken": 75010}, n=20)
    assert px.quote("BTC-USD", NOW, short)[0] == []


def test_a_broken_source_is_skipped_not_trusted():
    def f(src, product):
        if src == "bitstamp":
            return pd.Series([0.0, -1.0], index=pd.date_range(end=NOW, periods=2, freq="1min", tz="UTC"))
        return fake({"coinbase": 75000, "kraken": 75005})(src, product)
    s, _, used = px.quote("BTC-USD", NOW, f)
    assert used == "coinbase,kraken"


def test_worst_z_takes_the_smallest_lead_of_every_exchange():
    close = NOW + pd.Timedelta(minutes=5)
    args = ("greater_or_equal", 75000.0, None, close, NOW)
    zy, zn = px.worst_z(P.z_sides, [75400.0, 75200.0, 75300.0], 0.0005, *args)
    assert zy == P.z_sides("greater_or_equal", 75000.0, None, 75200.0, 0.0005, close, NOW)[0]
    assert zn == P.z_sides("greater_or_equal", 75000.0, None, 75400.0, 0.0005, close, NOW)[1]
    assert np.isnan(px.worst_z(P.z_sides, [], 0.0005, *args)[0])


def test_live_fetch_is_cached_briefly_and_never_raises(monkeypatch):
    calls = []

    def get(url, params=None):
        calls.append(url)
        return [[1794066840, 1, 2, 1, 75000.0, 1]]
    monkeypatch.setattr(px, "_get_json", get)
    px._cache.clear()
    a = px.fetch_live("coinbase", "BTC-USD")
    b = px.fetch_live("coinbase", "BTC-USD")
    assert len(calls) == 1 and a.iloc[-1] == b.iloc[-1] == 75000.0
    monkeypatch.setattr(px, "_get_json", lambda url, params=None: {"result": {"XXBTZUSD": [["bad"]]}})
    px._cache.clear()
    assert px.fetch_live("kraken", "BTC-USD").empty                           # garbage -> empty, no exception
    assert px.fetch_live("nowhere", "BTC-USD").empty
    monkeypatch.setattr(px, "_get_json", lambda url, params=None: None)       # exchange down
    px._cache.clear()
    assert px.fetch_live("bitstamp", "BTC-USD").empty


def test_live_trader_bids_only_when_every_exchange_says_decided(monkeypatch):
    from edge import live21 as L
    close = NOW + pd.Timedelta(minutes=5)
    m = {"ticker": "KXBTC15M-T", "strike_type": "greater_or_equal", "floor_strike": 75000.0, "cap_strike": None,
         "_close": close}
    monkeypatch.setattr(L, "SERIES", ["KXBTC15M"])
    monkeypatch.setattr(L.sig, "open_markets", lambda series, now: [m])
    monkeypatch.setattr(L, "flip_risk", lambda z, tau: 0.0 if z >= 6 else 1.0)
    monkeypatch.setattr(px, "fetch", fake({"coinbase": 76000, "kraken": 76010, "bitstamp": 75990}, vol=0.0003))
    px._cache.clear()
    c = L.candidates(NOW)
    assert [(x[0]["ticker"], x[2]) for x in c] == [("KXBTC15M-T", "yes")]
    o = dict(series="KXBTC15M", side="yes", strike_type="greater_or_equal", floor=75000.0, cap=None, close=close.isoformat())
    assert L.still_decided(o, NOW)
    monkeypatch.setattr(px, "fetch", fake({"coinbase": 76000, "kraken": 75100, "bitstamp": 75990}, vol=0.0003))
    assert L.candidates(NOW) == [] and not L.still_decided(o, NOW)          # Kraken 1.2% off: pull, don't bid
    monkeypatch.setattr(px, "fetch", fake({"coinbase": 76000}, vol=0.0003))
    assert L.candidates(NOW) == [] and not L.still_decided(o, NOW)          # only one exchange answering


def test_hourly_markets_use_the_z6_rule_on_every_exchange(monkeypatch):
    from edge import live21 as L
    assert L.SERIES == ["KXBTCD", "KXETHD", "KXSOLD", "KXXRPD"]
    close = NOW + pd.Timedelta(minutes=55)
    m = {"ticker": "KXBTCD-T", "strike_type": "greater", "floor_strike": 75000.0, "cap_strike": None, "_close": close}
    monkeypatch.setattr(L, "SERIES", ["KXBTCD"])
    monkeypatch.setattr(L.sig, "open_markets", lambda series, now: [m])
    vol = 0.0005
    lead = lambda z: 75000.0 * np.exp(z * vol * np.sqrt(55))                    # spot that gives exactly z
    o = dict(series="KXBTCD", side="yes", strike_type="greater", floor=75000.0, cap=None, close=close.isoformat())
    for z, want in ((6.3, True), (5.8, False)):
        monkeypatch.setattr(px, "quote", lambda prod, now, z=z: ([lead(z), lead(z + 1)], vol, "coinbase,kraken"))
        assert bool(L.candidates(NOW)) is want and L.still_decided(o, NOW) is want
    assert L.decided("KXBTCD", 6.0, 55) and not L.decided("KXBTCD", float("nan"), 55)
    assert not L.decided("KXBTCD", -7.0, 55)

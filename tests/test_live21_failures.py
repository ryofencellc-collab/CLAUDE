"""Every failure that is not the market itself: outages, bad data, bad responses, lost control, bad state."""
import subprocess

import numpy as np
import pandas as pd
import pytest

from edge import live21 as L
from edge import paper21 as P
from tests.test_live21_scenarios import CLOSE, Exchange, Market, at, fresh


@pytest.fixture
def world(monkeypatch, tmp_path):
    ex = Exchange()
    mk = Market(ex)
    mk.install(monkeypatch, tmp_path)
    return ex, mk, fresh(), tmp_path


def run_loop_once(ex, st, monkeypatch, mode="LIVE"):
    """One pass of the real loop, so its error handling is what gets tested."""
    t = [1000.0]
    monkeypatch.setattr(L.time, "time", lambda: t.__setitem__(0, t[0] + 3) or t[0])
    monkeypatch.setattr(L.time, "sleep", lambda s: None)
    monkeypatch.setattr(L, "read_control", lambda: {"live": True, "stop": False, "stake_fraction": 0.95, "max_contracts": 1000})
    L.loop(ex, st, mode, t0=1000.0, seconds=8, last_sweep=1e12, last_commit=1e12)


# ---------------------------------------------------------------- Kalshi outages and bad responses

def test_kalshi_down_mid_trade_pulls_the_order(world, monkeypatch):
    ex, mk, st, _ = world
    L.step(ex, st, "LIVE", at(0))
    oid = next(iter(ex.orders))
    monkeypatch.setattr(ex, "balance_usd", lambda: (_ for _ in ()).throw(RuntimeError("GET /portfolio/balance -> 503")))
    run_loop_once(ex, st, monkeypatch)
    assert ex.orders[oid]["status"] == "canceled"                          # an outage never leaves us exposed


def test_rate_limited_and_bad_key_do_not_crash_or_trade(world, monkeypatch):
    ex, mk, st, tmp = world
    monkeypatch.setattr(ex, "balance_usd", lambda: (_ for _ in ()).throw(RuntimeError("-> 401: invalid signature")))
    run_loop_once(ex, st, monkeypatch)
    log = pd.read_csv(tmp / "log.csv")
    assert (log["event"] == "error").any() and not [c for c in ex.calls if c[0] == "buy"]


def test_cancel_that_keeps_failing_is_retried_every_pass(world, monkeypatch):
    ex, mk, st, _ = world
    L.step(ex, st, "LIVE", at(0))
    tries = []
    monkeypatch.setattr(ex, "cancel", lambda oid: tries.append(oid) or (_ for _ in ()).throw(RuntimeError("-> 500")))
    mk.decided = False
    for k in range(3):
        with pytest.raises(RuntimeError):
            L.step(ex, st, "LIVE", at(1 + k * 0.1))
    assert len(tries) == 3 and not st["open"].get("cancelled")              # not marked done until it really is


def test_order_accepted_without_an_id_is_swept_not_left(world):
    ex, mk, st, _ = world
    orig = ex.buy
    ex.buy = lambda *a, **k: (orig(*a, **k), {})[1]                          # the response lost the order id
    L.step(ex, st, "LIVE", at(0))
    assert st["open"]["order_id"] is None
    L.sweep_strays(ex, st, "LIVE")
    assert all(o["status"] != "resting" for o in ex.orders.values())        # nothing rests that we cannot track


def test_kalshi_kalshi_cancel_404_is_fine():
    k = L.Kalshi(None, None)
    k.call = lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("DELETE /portfolio/orders/x -> 404: not found"))
    k.cancel("x")                                                            # already gone: not an error
    k.call = lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("DELETE /portfolio/orders/x -> 500"))
    with pytest.raises(RuntimeError):
        k.cancel("x")                                                        # a real failure still surfaces


# ---------------------------------------------------------------- price data failures

class Resp:
    def __init__(self, code, body):
        self.status_code, self._b = code, body

    def json(self):
        if isinstance(self._b, Exception):
            raise self._b
        return self._b


def test_coinbase_down_garbage_or_short_history_means_no_price(monkeypatch):
    now = pd.Timestamp("2026-11-10 12:00", tz="UTC")
    for resp in (Resp(503, []), Resp(200, ValueError("not json")), Resp(200, [])):
        monkeypatch.setattr(P._cb, "get", lambda *a, **k: resp)
        s, v = P.spot_and_vol("BTC-USD", now)
        assert np.isnan(s) and np.isnan(v)
    rows = [[int((now - pd.Timedelta(minutes=i + 1)).timestamp()), 0, 0, 0, 80000.0, 1] for i in range(10)]
    monkeypatch.setattr(P._cb, "get", lambda *a, **k: Resp(200, rows))      # only 10 minutes of history
    assert np.isnan(P.spot_and_vol("BTC-USD", now)[0])
    old = [[int((now - pd.Timedelta(minutes=i + 10)).timestamp()), 0, 0, 0, 80000.0 + i, 1] for i in range(60)]
    monkeypatch.setattr(P._cb, "get", lambda *a, **k: Resp(200, old))       # newest candle 9 minutes old
    assert np.isnan(P.spot_and_vol("BTC-USD", now)[0])
    good = [[int((now - pd.Timedelta(minutes=i + 1)).timestamp()), 0, 0, 0, 80000.0 + (i % 3), 1] for i in range(60)]
    monkeypatch.setattr(P._cb, "get", lambda *a, **k: Resp(200, good))
    assert np.isfinite(P.spot_and_vol("BTC-USD", now)[0])


def test_kalshi_market_list_down_means_no_candidates(monkeypatch):
    monkeypatch.setattr(P.wx, "_get", lambda url, params=None: None)
    monkeypatch.setattr(P, "spot_and_vol", lambda prod, now: (80000.0, 0.0005))
    assert L.candidates(pd.Timestamp("2026-11-10 12:00", tz="UTC")) == []


def test_missing_or_broken_strike_never_counts_as_decided():
    now, close = pd.Timestamp("2026-11-10 12:10", tz="UTC"), CLOSE
    for st_, f, c in (("greater_or_equal", None, None), ("between", 1.0, None), ("weird", 1.0, 2.0)):
        try:
            zy, zn = P.z_sides(st_, f, c, 1.0, 0.001, close, now)
        except (TypeError, ValueError):
            continue                                                         # an exception is caught by the loop: no order
        assert not (np.isfinite(zy) and zy >= 6) and not (np.isfinite(zn) and zn >= 6)


# ---------------------------------------------------------------- losing control or the account changing

def test_github_unreachable_for_five_minutes_means_stop(monkeypatch, tmp_path):
    monkeypatch.setattr(L, "CONTROL", tmp_path / "c.json")
    (tmp_path / "c.json").write_text('{"live": true, "stop": false, "stake_fraction": 0.5}')
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 1, "", ""))
    L._control_misses[0] = 0
    results = [L.read_control() for _ in range(5)]
    assert results[0]["live"] is True and results[3]["live"] is True        # brief blips: keep the last known file
    assert results[4]["live"] is False and results[4]["stop"] is True       # 5 in a row: stop
    L._control_misses[0] = 0


def test_corrupt_control_values_fall_back_to_safe(monkeypatch, tmp_path):
    monkeypatch.setattr(L, "CONTROL", tmp_path / "c.json")
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    (tmp_path / "c.json").write_text('{"live": true, "stop": false, "stake_fraction": "lots", "max_contracts": "x"}')
    c = L.read_control()
    assert c["stake_fraction"] == 0.25 and c["max_contracts"] == L.MAX_CONTRACTS
    (tmp_path / "c.json").write_text('[1, 2, 3]')
    assert L.read_control()["live"] is False


def test_owner_withdraws_everything(world):
    ex, mk, st, tmp = world
    ex.balance = 0.0
    L.step(ex, st, "LIVE", at(0))
    assert not [c for c in ex.calls if c[0] == "buy"]
    assert (pd.read_csv(tmp / "log.csv")["event"] == "skip").any()


def test_new_day_resets_daily_loss_but_not_the_pause(world):
    ex, mk, st, _ = world
    st.update(day="2026-11-09", day_loss=500.0, day_start_balance=1000.0, pause_until=at(60).timestamp())
    mk.decided = False
    L.step(ex, st, "LIVE", at(0))
    assert st["day"] == "2026-11-10" and st["day_loss"] == 0.0 and st["pause_until"] == at(60).timestamp()


def test_corrupt_state_file_starts_safe(monkeypatch, tmp_path):
    monkeypatch.setattr(L, "STATE", tmp_path / "s.json")
    (tmp_path / "s.json").write_text("{not json")
    st = L.load_state()
    assert st["open"] is None and st["pause_until"] == 0.0


def test_github_cancels_the_job_mid_trade(world, monkeypatch):
    ex, mk, st, _ = world  # _ is the test's temporary folder
    monkeypatch.setattr(L, "Kalshi", lambda key_id, pem: ex)
    monkeypatch.setattr(L, "load_state", lambda: st)
    root = _ / "root"
    root.mkdir()
    monkeypatch.setattr(L, "ROOT", root)                                    # keep the real paper/ report untouched
    monkeypatch.setattr(L, "read_control", lambda: {"live": True, "stop": False, "stake_fraction": 0.95, "max_contracts": 1000})
    ex.orders["r"] = dict(order_id="r", ticker="KXXRP15M-T", side="yes", count=10, status="resting", client_order_id="r21-r")

    def interrupted(*a, **k):
        raise KeyboardInterrupt  # what the SIGTERM handler raises when GitHub cancels the job
    monkeypatch.setattr(L, "loop", interrupted)
    with pytest.raises(KeyboardInterrupt):
        L.run()
    assert ex.orders["r"]["status"] == "canceled"


def test_filled_position_survives_an_error_and_still_settles(world, monkeypatch):
    ex, mk, st, _ = world  # _ is the test's temporary folder
    L.step(ex, st, "LIVE", at(0))
    oid = next(iter(ex.orders))
    ex.fill(oid, 959)                                                       # fully filled before the outage
    monkeypatch.setattr(ex, "balance_usd", lambda: (_ for _ in ()).throw(RuntimeError("-> 503")))
    run_loop_once(ex, st, monkeypatch)                                      # error path tries to cancel: harmless
    monkeypatch.undo()
    mk.install(monkeypatch, _)
    ex.settle("KXXRP15M-T", "yes", CLOSE)
    L.step(ex, st, "LIVE", at(8))
    assert st["open"] is None and st["results"][-1]["pnl"] > 0               # still booked correctly

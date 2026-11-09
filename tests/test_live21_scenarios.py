"""End-to-end scenarios for the live trader against a simulated Kalshi exchange and a controllable clock.
Every rule that protects the $1,000 is exercised in sequence, the way a real day would hit it."""
import pandas as pd
import pytest

from edge import live21 as L

T0 = pd.Timestamp("2026-11-10 12:10", tz="UTC")
CLOSE = pd.Timestamp("2026-11-10 12:15", tz="UTC")


class Exchange:
    """Simulated Kalshi: resting orders, fills, positions, settlements, market results."""

    def __init__(self, balance=1000.0):
        self.authed = True
        self.balance = balance
        self.orders = {}          # order_id -> dict
        self.fills = {}           # ticker -> contracts bought
        self.settlements = []     # (unix time, pnl)
        self.results = {}         # ticker -> "yes" / "no"
        self.reject_next = False
        self.calls = []
        self.n = 0

    # API surface used by live21.Kalshi
    def balance_usd(self):
        return self.balance

    def resting(self):
        return [o for o in self.orders.values() if o["status"] == "resting"]

    def positions(self):
        return [{"ticker": t, "position": n} for t, n in self.fills.items() if n and t not in self.results]

    def buy(self, ticker, side, count, cents=99, expires=None):
        self.calls.append(("buy", ticker, side, count, expires))
        if self.reject_next:
            self.reject_next = False
            raise RuntimeError("POST /portfolio/orders -> 400: post only order would cross")
        self.n += 1
        oid = f"oid{self.n}"
        self.orders[oid] = dict(order_id=oid, ticker=ticker, side=side, count=count, status="resting",
                                client_order_id=f"r21-{self.n}")
        self.balance -= count * cents / 100
        return {"order_id": oid, "status": "resting"}

    def cancel(self, order_id, ticker=None):
        self.calls.append(("cancel", order_id))
        o = self.orders.get(order_id)
        if o and o["status"] == "resting":
            o["status"] = "canceled"
            self.balance += (o["count"] - self.fills.get(o["ticker"], 0)) * 0.99

    def filled(self, ticker, order_id=None):
        return float(self.fills.get(ticker, 0))

    def recent_settlement_pnls(self, since):
        return [(t, p) for t, p in self.settlements if t >= since]

    # exchange-side events
    def fill(self, oid, n):
        o = self.orders[oid]
        self.fills[o["ticker"]] = self.fills.get(o["ticker"], 0) + n
        if self.fills[o["ticker"]] >= o["count"]:
            o["status"] = "executed"

    def settle(self, ticker, result, t):
        self.results[ticker] = result
        for o in self.orders.values():
            if o["ticker"] == ticker and o["status"] == "resting":
                o["status"] = "canceled"
        n = self.fills.get(ticker, 0)
        side = next(o["side"] for o in self.orders.values() if o["ticker"] == ticker)
        won = result == side
        pnl = n * ((1.0 if won else 0.0) - 0.99)
        self.balance += n * (1.0 if won else 0.0)
        self.settlements.append((t.timestamp(), pnl))


class Market:
    def __init__(self, ex):
        self.ex = ex
        self.decided = True
        self.spot_ok = True

    def install(self, monkeypatch, tmp_path):
        monkeypatch.setattr(L, "LOG", tmp_path / "log.csv")
        monkeypatch.setattr(L, "STATE", tmp_path / "state.json")
        monkeypatch.setattr(L, "STOP", tmp_path / "STOP")
        m = {"ticker": "KXXRP15M-T", "strike_type": "greater_or_equal", "floor_strike": 1.0, "cap_strike": None,
             "_close": CLOSE}
        monkeypatch.setattr(L, "decide", lambda now: (m, "KXXRP15M", "yes", 7.0, 1.05, 100.0) if self.decided else None)
        self.m = m
        monkeypatch.setattr(L, "still_decided", lambda o, now: self.decided and self.spot_ok)

        class R:
            def __init__(s, j):
                s.status_code, s._j = 200, j

            def json(s):
                return s._j
        monkeypatch.setattr(L.sig.wx, "_get", lambda url, params=None: R({"market": {"result": self.ex.results.get(url.rsplit("/", 1)[-1], "")}}))


def fresh():
    return {"pause_until": 0.0, "half_until": 0.0, "day": "", "day_start_balance": 0.0, "day_loss": 0.0, "opens": [], "max_positions": 1,
            "results": [], "stake_fraction": 0.95, "max_contracts": 1000}


@pytest.fixture
def world(monkeypatch, tmp_path):
    ex = Exchange()
    mk = Market(ex)
    mk.install(monkeypatch, tmp_path)
    return ex, mk, fresh(), tmp_path


def at(minutes):
    return T0 + pd.Timedelta(minutes=minutes)


def test_winning_market_end_to_end(world):
    ex, mk, st, _ = world
    L.step(ex, st, "LIVE", at(0))
    (oid, o), = ex.orders.items()
    assert o["count"] == 959 and ex.calls[0][4] == CLOSE.timestamp()       # sized from balance, expires at close
    ex.fill(oid, 959)
    L.step(ex, st, "LIVE", at(1))
    assert len([c for c in ex.calls if c[0] == "buy"]) == 1                  # one position at a time
    ex.settle("KXXRP15M-T", "yes", CLOSE)
    L.step(ex, st, "LIVE", at(8))                                           # after close + 2 min
    assert not L.opens(st) and st["results"][-1]["pnl"] > 0
    assert len([c for c in ex.calls if c[0] == "buy"]) == 1                  # never re-trades the same market
    assert L.blocked(st, at(8).timestamp(), ex.balance) is None


def test_reversal_cancels_and_a_loss_pauses_then_halves(world):
    ex, mk, st, _ = world
    L.step(ex, st, "LIVE", at(0))
    oid = next(iter(ex.orders))
    ex.fill(oid, 300)                                                       # partly filled
    mk.decided = False                                                      # price moves back toward the strike
    L.step(ex, st, "LIVE", at(1))
    assert ("cancel", oid) in ex.calls and ex.orders[oid]["status"] == "canceled"
    ex.settle("KXXRP15M-T", "no", CLOSE)                                    # the long shot wins
    L.step(ex, st, "LIVE", at(8))
    L.rebuild_risk(ex, st, at(8).timestamp())
    assert not L.opens(st) and st["results"][-1]["pnl"] < 0
    mk.decided = True
    L.step(ex, st, "LIVE", at(30))
    assert len([c for c in ex.calls if c[0] == "buy"]) == 1                 # paused: no new order for 24 h
    later = at(60 * 25)
    mk.m.update(ticker="KXXRP15M-NEXT", _close=later + pd.Timedelta(minutes=5))  # a new market a day later
    full = L.size_for(ex.balance, {"half_until": 0}, 0)
    L.step(ex, st, "LIVE", later)
    buys = [c for c in ex.calls if c[0] == "buy"]
    assert len(buys) == 2 and buys[-1][3] == full // 2                       # half size for the next 7 days


def test_stale_spot_pulls_the_order(world):
    ex, mk, st, _ = world
    L.step(ex, st, "LIVE", at(0))
    oid = next(iter(ex.orders))
    mk.spot_ok = False
    L.step(ex, st, "LIVE", at(1))
    assert ex.orders[oid]["status"] == "canceled"


def test_stop_file_pulls_and_blocks(world):
    ex, mk, st, tmp = world
    L.step(ex, st, "LIVE", at(0))
    oid = next(iter(ex.orders))
    (tmp / "STOP").write_text("")
    L.step(ex, st, "LIVE", at(1))
    assert ex.orders[oid]["status"] == "canceled"
    ex.settle("KXXRP15M-T", "yes", CLOSE)
    L.step(ex, st, "LIVE", at(8))
    L.step(ex, st, "LIVE", at(20))
    assert len([c for c in ex.calls if c[0] == "buy"]) == 1                 # nothing new while the stop file exists


def test_restart_with_leftovers_sweeps_blocks_and_learns_the_loss(world):
    ex, mk, st, _ = world
    ex.orders["old"] = dict(order_id="old", ticker="KXBTC15M-OLD", side="yes", count=500, status="resting", client_order_id="r21-old")
    ex.orders["mine"] = dict(order_id="mine", ticker="X", side="yes", count=5, status="resting", client_order_id="manual")
    ex.fills["KXSOL15M-POS"] = 400                                          # a position left by a dead job
    L.sweep_strays(ex, st, "LIVE")
    assert ex.orders["old"]["status"] == "canceled" and ex.orders["mine"]["status"] == "resting"
    L.step(ex, st, "LIVE", at(0))
    assert not [c for c in ex.calls if c[0] == "buy"]                        # blocked by the open position
    ex.orders["pos"] = dict(order_id="pos", ticker="KXSOL15M-POS", side="no", count=400, status="executed", client_order_id="r21-pos")
    ex.settle("KXSOL15M-POS", "yes", at(1))                                 # it settles as a loss
    L.rebuild_risk(ex, st, at(2).timestamp())
    L.step(ex, st, "LIVE", at(3))
    assert not [c for c in ex.calls if c[0] == "buy"] and st["pause_until"] > at(3).timestamp()


def test_daily_stop_from_settlements(world):
    ex, mk, st, _ = world
    st.update(day=at(0).date().isoformat(), day_start_balance=1000.0)
    ex.settlements.append((at(-60).timestamp(), -150.0))
    L.rebuild_risk(ex, st, at(0).timestamp())
    st["pause_until"] = 0                                                   # isolate the daily stop
    assert L.blocked(st, at(0).timestamp(), 850.0) == "daily loss limit"


def test_rejected_order_cools_down_instead_of_hammering(world):
    ex, mk, st, _ = world
    ex.reject_next = True
    L.step(ex, st, "LIVE", at(0))                                           # rejected: logged, not raised
    L.step(ex, st, "LIVE", at(0.2))                                         # within 60 s: no retry
    assert len([c for c in ex.calls if c[0] == "buy"]) == 1
    L.step(ex, st, "LIVE", at(1.5))                                         # after the cool-down it tries again
    assert len([c for c in ex.calls if c[0] == "buy"]) == 2
    assert ex.calls[1][1] == "KXXRP15M-T"                                    # a rejected order does not count as traded


def test_void_market_unblocks_after_three_hours(world):
    ex, mk, st, _ = world
    L.step(ex, st, "LIVE", at(0))
    mk.decided = False
    L.step(ex, st, "LIVE", at(10))                                          # closed, no result yet
    assert L.opens(st)
    L.step(ex, st, "LIVE", at(60 * 3 + 10))
    assert not L.opens(st)


def test_small_balance_sizes_down(world):
    ex, mk, st, _ = world
    ex.balance = 50.0
    L.step(ex, st, "LIVE", at(0))
    assert ex.calls[0][3] == 47


def test_job_end_cancels_anything_resting(world, monkeypatch):
    ex, mk, st, _ = world  # _ is the test's temporary folder
    monkeypatch.setattr(L, "Kalshi", lambda key_id, pem: ex)
    monkeypatch.setenv("LIVE21", "1")
    monkeypatch.setenv("LIVE21_SECONDS", "0")                               # the loop ends at once
    monkeypatch.setattr(L, "load_state", lambda: st)
    monkeypatch.setattr(L, "ROOT", _ / "root")                              # keep the real paper/ report untouched
    (_ / "root").mkdir()
    ex.orders["r"] = dict(order_id="r", ticker="KXXRP15M-T", side="yes", count=10, status="resting", client_order_id="r21-r")
    L.run()
    assert ex.orders["r"]["status"] == "canceled"


def test_dry_run_with_real_keys_never_logs_the_balance(monkeypatch, tmp_path):
    monkeypatch.setattr(L, "LOG", tmp_path / "log.csv")
    monkeypatch.setenv("KALSHI_KEY_ID", "kid")
    L.log("DRY", "place", "T", "yes", 10, balance=1234.56)
    assert pd.read_csv(tmp_path / "log.csv")["balance"].isna().all()



def test_stake_fraction_limits_one_market(world):
    ex, mk, st, _ = world
    st["stake_fraction"], st["max_contracts"] = 0.5, 100000
    L.step(ex, st, "LIVE", at(0))
    assert ex.calls[0][3] == 505                                            # half of $1,000 at 99c


def test_control_file_defaults_and_veto(monkeypatch, tmp_path):
    monkeypatch.setattr(L, "CONTROL", tmp_path / "c.json")
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    c = L.read_control()                                                    # missing file: stopped, not live
    assert c["live"] is False and c["stop"] is True and c["stake_fraction"] == 0.25
    (tmp_path / "c.json").write_text('{"live": true, "stop": false, "stake_fraction": 3}')
    c = L.read_control()
    assert c["live"] is True and c["stake_fraction"] == 0.95                # capped at 0.95
    class A:
        authed = True
    monkeypatch.delenv("LIVE21", raising=False)
    assert L.live_allowed(A(), c) is True
    monkeypatch.setenv("LIVE21", "0")                                       # the owner's veto wins
    assert L.live_allowed(A(), c) is False
    (tmp_path / "c.json").write_text('{"live": true, "stop": true}')
    assert L.read_control()["live"] is False                                 # stop overrides live
    (tmp_path / "c.json").write_text("not json")
    assert L.read_control()["live"] is False


def test_control_stop_pulls_order_and_blocks(world):
    ex, mk, st, _ = world
    L.step(ex, st, "LIVE", at(0))
    oid = next(iter(ex.orders))
    st["control_stop"] = True
    L.step(ex, st, "LIVE", at(1))
    assert ex.orders[oid]["status"] == "canceled"


def test_switching_to_dry_pulls_everything(world):
    ex, mk, st, _ = world
    L.step(ex, st, "LIVE", at(0))
    L.go_dry(ex, st)
    assert all(o["status"] != "resting" for o in ex.orders.values()) and not L.opens(st)


def test_dry_run_counts_only_flow_that_reaches_99c(world, monkeypatch):
    ex, mk, st, _ = world
    L.step(ex, st, "DRY", at(0))
    assert L.opens(st) and L.opens(st)[0]["order_id"] is None
    L.opens(st)[0]["queue_ahead"] = 100.0
    ex.results["KXXRP15M-T"] = "yes"
    monkeypatch.setattr(L.fc, "flow", lambda t, s, a, b: (5000.0, 400.0))   # 5,000 long-shot buys, 400 at >= 1c
    L.step(ex, st, "DRY", CLOSE + pd.Timedelta(minutes=3))
    last = L.LOG.read_text().strip().splitlines()[-1]
    assert ",settled," in last and ",300.0," in last                         # 400 - 100 queue, not 4,900
    monkeypatch.setattr(L.fc, "flow", lambda t, s, a, b: (float("nan"), float("nan")))
    st["opens"] = []
    st["traded"] = []
    L.step(ex, st, "DRY", at(0))
    L.step(ex, st, "DRY", CLOSE + pd.Timedelta(minutes=3))
    assert ",settled," in L.LOG.read_text().strip().splitlines()[-1] and ",0.0," in L.LOG.read_text().strip().splitlines()[-1]


def test_hourly_bet_is_sized_by_the_stake_alone(world, monkeypatch):
    ex, mk, st, _ = world
    mk.m["ticker"] = "KXBTCD-T"
    monkeypatch.setattr(L, "decide", lambda now: (mk.m, "KXBTCD", "yes", 7.0, 75000.0, 0.0))
    st["stake_fraction"] = 0.5
    L.step(ex, st, "LIVE", at(0))
    buy = next(c for c in ex.calls if c[0] == "buy")
    assert buy[3] == int(1000 * 0.5 / 0.99)                                   # 505 contracts at half the balance
    assert "risk=nan frac=0.500" in L.LOG.read_text()


def test_decide_prefers_the_market_most_likely_to_fill(monkeypatch):
    m = lambda t: {"ticker": t}
    cands = [(m("FAR"), "KXETHD", "no", 26.0, 1.0), (m("NEAR"), "KXETHD", "no", 6.2, 1.0),
             (m("NEAR_BUT_CROWDED"), "KXETHD", "no", 6.1, 1.0), (m("MID"), "KXBTCD", "yes", 8.0, 1.0)]
    queues = {"FAR": 0.0, "NEAR": 400.0, "NEAR_BUT_CROWDED": 25000.0, "MID": 0.0}
    monkeypatch.setattr(L, "candidates", lambda now: cands)
    monkeypatch.setattr(L.sig, "queue_ahead", lambda t, side: queues[t])
    assert L.decide(T0)[0]["ticker"] == "NEAR"                                # smallest z with a short queue
    queues["NEAR"] = 5000.0
    assert L.decide(T0)[0]["ticker"] == "MID"
    monkeypatch.setattr(L, "candidates", lambda now: [cands[2]])
    assert L.decide(T0)[0]["ticker"] == "NEAR_BUT_CROWDED"                   # last resort still allowed
    monkeypatch.setattr(L, "candidates", lambda now: [])
    assert L.decide(T0) is None



# ---------------------------------------------------------------- several markets at once (Nov 8 fix)
def multi_world(monkeypatch, n_markets=5, slots=10):
    ex = Exchange()
    mk = Market(ex)
    mk.install(monkeypatch, None) if False else None
    ms = [{"ticker": f"KXBTCD-H{i}-T{i}", "strike_type": "greater", "floor_strike": 1.0, "cap_strike": None, "_close": CLOSE}
          for i in range(n_markets)]
    state = {"decided": {m["ticker"]: True for m in ms}}
    monkeypatch.setattr(L, "decide_many", lambda now, exclude=frozenset(), look=12: [
        (m, "KXBTCD", "yes", 6.5 + i, 1.05, 0.0) for i, m in enumerate(ms)
        if m["ticker"] not in exclude and state["decided"][m["ticker"]]])
    monkeypatch.setattr(L, "still_decided", lambda o, now: state["decided"][o["ticker"]])

    class R:
        def __init__(s, j):
            s.status_code, s._j = 200, j

        def json(s):
            return s._j
    monkeypatch.setattr(L.sig.wx, "_get", lambda url, params=None: R({"market": {"result": ex.results.get(url.rsplit("/", 1)[-1], "")}}))
    st = fresh()
    st["max_positions"] = slots
    return ex, st, ms, state


def test_spreads_the_stake_over_several_markets(monkeypatch):
    ex, st, ms, state = multi_world(monkeypatch, n_markets=5, slots=10)
    st["stake_fraction"] = 0.5
    for k in range(3):                                                          # 3 new bids per step at most
        L.step(ex, st, "LIVE", at(k * 0.1))
    buys = [c for c in ex.calls if c[0] == "buy"]
    assert len(buys) == 5 and len({c[1] for c in buys}) == 5                    # every market once, never twice
    equity = 1000.0
    assert all(c[3] == int(equity * 0.5 / 10 / 0.99) for c in buys[:3])        # each slot: 5% of equity (50)
    assert sum(c[3] for c in buys) * 0.99 <= 1000 * 0.5 + 1                    # total stays within the stake


def test_slots_cap_and_each_bid_is_pulled_on_its_own(monkeypatch):
    ex, st, ms, state = multi_world(monkeypatch, n_markets=6, slots=4)
    for k in range(3):
        L.step(ex, st, "LIVE", at(k * 0.1))
    assert len(L.active(st, at(0.3))) == 4                                      # never more than the slots
    state["decided"]["KXBTCD-H1-T1"] = False
    L.step(ex, st, "LIVE", at(0.5))                                            # that one is pulled, the others stay
    pulled = [o for o in L.opens(st) if o.get("cancelled")]
    assert [o["ticker"] for o in pulled] == ["KXBTCD-H1-T1"]
    resting = [o for o in ex.orders.values() if o["status"] == "resting"]
    assert len(resting) == 4                                                    # 3 kept + the freed slot refilled
    assert "KXBTCD-H1-T1" not in {o["ticker"] for o in resting}


def test_one_wrong_call_costs_one_slot_and_pauses_new_bids(monkeypatch):
    ex, st, ms, state = multi_world(monkeypatch, n_markets=3, slots=10)
    st["stake_fraction"] = 0.5
    L.step(ex, st, "LIVE", at(0))
    for oid in list(ex.orders):
        ex.fill(oid, ex.orders[oid]["count"])
    ex.settle("KXBTCD-H0-T0", "no", CLOSE + pd.Timedelta(seconds=30))             # one of the three goes wrong
    ex.settle("KXBTCD-H1-T1", "yes", CLOSE + pd.Timedelta(seconds=30))
    ex.settle("KXBTCD-H2-T2", "yes", CLOSE + pd.Timedelta(seconds=30))
    L.step(ex, st, "LIVE", CLOSE + pd.Timedelta(minutes=3))
    pnls = sorted(r["pnl"] for r in st["results"])
    assert len(pnls) == 3 and pnls[0] < 0 and pnls[0] > -1000 * 0.5 / 10 - 1  # the loss is one slot, not the stake
    assert st["pause_until"] > (CLOSE + pd.Timedelta(minutes=3)).timestamp()   # and the 24 h pause starts
    assert not L.opens(st)


def test_untracked_position_blocks_new_bids_but_tracked_ones_do_not(monkeypatch):
    ex, st, ms, state = multi_world(monkeypatch, n_markets=4, slots=10)
    L.step(ex, st, "LIVE", at(0))
    oid = next(iter(ex.orders))
    ex.fill(oid, 10)                                                            # our own fill: still free to bid more
    L.step(ex, st, "LIVE", at(0.1))
    assert len([c for c in ex.calls if c[0] == "buy"]) == 4
    ex.fills["SOMEONE-ELSES"] = 5                                               # a position we never placed
    st["traded"] = []
    n = len([c for c in ex.calls if c[0] == "buy"])
    for o in L.opens(st):
        o["cancelled"] = True
    L.step(ex, st, "LIVE", at(0.2))
    assert len([c for c in ex.calls if c[0] == "buy"]) == n                    # blocked until it is explained


def test_old_single_open_state_is_migrated():
    st = {"open": {"ticker": "X", "close": "2026-11-10T12:15:00+00:00"}}
    assert L.opens(st) == [{"ticker": "X", "close": "2026-11-10T12:15:00+00:00"}] and "open" not in st
    assert L.opens({"open": None}) == []


def test_real_decide_many_ranks_and_excludes(monkeypatch):
    m = lambda t: {"ticker": t}
    cands = [(m("FAR"), "KXETHD", "no", 26.0, 1.0), (m("NEAR"), "KXETHD", "no", 6.2, 1.0),
             (m("CROWDED"), "KXETHD", "no", 6.1, 1.0), (m("HELD"), "KXBTCD", "yes", 6.0, 1.0)]
    queues = {"FAR": 0.0, "NEAR": 400.0, "CROWDED": 25000.0, "HELD": 0.0}
    monkeypatch.setattr(L, "candidates", lambda now: cands)
    monkeypatch.setattr(L.sig, "queue_ahead", lambda t, side: queues[t])
    got = [x[0]["ticker"] for x in L._decide_many(T0, exclude={"HELD"})]
    assert got == ["NEAR", "FAR", "CROWDED"]


def test_one_position_per_coin_per_hour(monkeypatch):
    """Nov 8 22:00 UTC: four BTC strikes of one hour lost together. Strikes of one event are one bet."""
    ex, st, ms, state = multi_world(monkeypatch, n_markets=4, slots=10)
    same = [{**m, "ticker": f"KXBTCD-26NOV0817-T{7400 + i}"} for i, m in enumerate(ms[:3])]
    other = {**ms[3], "ticker": "KXETHD-26NOV0817-T2200"}
    state["decided"].update({m["ticker"]: True for m in same + [other]})
    monkeypatch.setattr(L, "decide_many", lambda now, exclude=frozenset(), look=12: [
        (m, m["ticker"].split("-")[0], "yes", 9.0, 1.05, 0.0) for m in same + [other] if m["ticker"] not in exclude])
    for k in range(3):
        L.step(ex, st, "LIVE", at(k * 0.1))
    bought = sorted({c[1] for c in ex.calls if c[0] == "buy"})
    assert bought == ["KXBTCD-26NOV0817-T7400", "KXETHD-26NOV0817-T2200"]
    assert L.event_of("KXBTCD-26NOV0817-T74249.99") == "KXBTCD-26NOV0817"

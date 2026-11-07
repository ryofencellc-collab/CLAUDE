"""The control/RULES.md stop and stake rules, enforced by the bot itself so nobody has to be watching."""
import pandas as pd

from edge import live21 as L
from tests.test_live21_scenarios import Exchange, at, fresh, world  # noqa: F401  (world is a fixture)

DAY = 86400.0
START = at(0).timestamp()


def gov(pnls, days_live, deposit=1000.0):
    return L.governor([(START + d * DAY, p) for d, p in pnls], deposit, START, START + days_live * DAY)


def test_stake_schedule():
    assert gov([], 0) == (0.5, None)                                          # first 14 days
    assert gov([(1, 5.0), (3, 5.0)], 13.9) == (0.5, None)
    assert gov([(1, 5.0), (3, 5.0)], 14) == (0.95, None)                      # 14 clean days
    assert gov([(1, 5.0), (10, -20.0)], 15) == (0.25, None)                   # a loss in the last 14 days
    assert gov([(1, 50.0), (10, -20.0)], 24.1) == (0.95, None)                # 14 days after it, P&L >= 0
    assert gov([(1, 5.0), (10, -20.0)], 24.1) == (0.5, None)                  # ... but P&L < 0: not grown


def test_two_losses_in_seven_days_halt_for_good():
    assert gov([(1, -5.0), (7.5, -5.0)], 8)[1] is not None
    assert gov([(1, -5.0), (7.5, -5.0)], 300)[1] is not None                  # never wears off
    assert gov([(1, -5.0), (9, -5.0)], 10) == (0.25, None)                    # 8 days apart: not a halt


def test_equity_floor_halts_for_good_even_after_recovering():
    stake, halt = gov([(1, -310.0), (20, 400.0)], 40)
    assert stake == 0.0 and "floor" in halt
    assert gov([(1, -290.0)], 2) == (0.25, None)                              # $710: above the floor
    assert gov([(1, -2900.0)], 2, deposit=10000.0) == (0.25, None)            # the floor scales with the deposit


def test_govern_takes_the_smaller_stake_and_keeps_the_last_answer_on_errors(world):
    ex, mk, st, _ = world
    control = {"live": True, "live_since": START, "deposit": 1000.0}
    st["stake_fraction"] = 0.95
    L.govern(ex, st, control, START + DAY)
    assert st["stake_fraction"] == 0.5 and st["gov_halt"] is None             # Claude's cap 0.95, rules 0.5
    st["stake_fraction"] = 0.3
    L.govern(ex, st, control, START + DAY)
    assert st["stake_fraction"] == 0.3                                        # Claude's lower cap wins

    class Down(Exchange):
        def recent_settlement_pnls(self, since):
            raise RuntimeError("GET /portfolio/settlements -> 503")
    st2 = fresh()
    L.govern(Down(), st2, control, START)
    assert st2["stake_fraction"] == 0.25 and not st2.get("gov_halt")          # no answer yet: smallest stake
    st["stake_fraction"], st["gov_halt"] = 0.95, "2 losing markets within 7 days"
    L.govern(Down(), st, control, START)
    assert st["gov_halt"] and st["stake_fraction"] == 0.5                     # a halt is not forgotten


def test_a_halt_blocks_and_pulls_the_resting_order(world):
    ex, mk, st, _ = world
    L.step(ex, st, "LIVE", at(0))
    oid = next(iter(ex.orders))
    ex.settlements += [(at(-3000).timestamp(), -5.0), (at(-1000).timestamp(), -5.0)]
    L.govern(ex, st, {"live": True, "live_since": 0.0, "deposit": 1000.0}, at(1).timestamp())
    assert st["gov_halt"]
    L.step(ex, st, "LIVE", at(1))
    assert ex.orders[oid]["status"] == "canceled"
    L.step(ex, st, "LIVE", at(30))
    assert len([c for c in ex.calls if c[0] == "buy"]) == 1                   # nothing new after the halt
    assert L.blocked(st, at(30).timestamp(), 1000.0).startswith("stopped by the rules")


def test_a_halted_account_starts_in_dry_run(world, monkeypatch):
    ex, mk, st, _ = world
    ex.settlements += [(at(-3000).timestamp(), -5.0), (at(-1000).timestamp(), -5.0)]
    monkeypatch.setattr(L, "Kalshi", lambda k, p: ex)
    monkeypatch.setattr(L, "read_control", lambda: {"live": True, "stop": False, "stake_fraction": 0.95,
                                                    "max_contracts": 1000, "deposit": 1000.0, "live_since": 0.0})
    monkeypatch.setenv("LIVE21_SECONDS", "0")
    monkeypatch.delenv("LIVE21", raising=False)
    L.run()
    log = L.LOG.read_text()
    assert ",DRY,start," in log and ",LIVE," not in log


def test_control_reads_deposit_and_live_since(monkeypatch, tmp_path):
    monkeypatch.setattr(L, "CONTROL", tmp_path / "c.json")
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    (tmp_path / "c.json").write_text('{"live": true, "stop": false, "deposit": 1000, "live_since": "2026-11-13T00:00Z"}')
    c = L.read_control()
    assert c["deposit"] == 1000.0 and c["live_since"] == pd.Timestamp("2026-11-13", tz="UTC").timestamp()
    (tmp_path / "c.json").write_text('{"live": true, "stop": false, "deposit": "x", "live_since": "garbage"}')
    c = L.read_control()
    assert c["deposit"] == 1000.0 and c["live_since"] == 0.0                  # 0 = the whole history counts


def test_a_hung_git_fetch_counts_as_a_miss_instead_of_freezing(monkeypatch, tmp_path):
    import subprocess
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setattr(L, "CONTROL", tmp_path / "missing.json")
    calls = []

    def hang(*a, **kw):
        calls.append(kw.get("timeout"))
        raise subprocess.TimeoutExpired(a[0], kw.get("timeout"))
    monkeypatch.setattr(subprocess, "run", hang)
    L._control_misses[0] = 0
    for _ in range(L.CONTROL_MAX_MISSES):
        c = L.read_control()
    assert calls and all(t for t in calls)                                    # every git call has a time limit
    assert c["stop"] is True and c["live"] is False and L._control_misses[0] == L.CONTROL_MAX_MISSES
    L._control_misses[0] = 0
    L.commit_logs()                                                           # must return, not hang or raise


def test_dry_run_sizes_with_the_same_rules_as_live(world):
    ex, mk, st, _ = world

    def Unauthed():
        e = Exchange()
        e.authed = False
        return e
    st["stake_fraction"] = 0.95
    control = {"live": False, "live_since": 0.0, "deposit": 1000.0}
    L.govern(Unauthed(), st, control, START)
    assert st["stake_fraction"] == 0.5                                        # first 14 days, like live
    st["results"] = [{"t": START - 2 * DAY, "pnl": -5.0}, {"t": START - DAY, "pnl": -5.0}]
    L.govern(Unauthed(), st, control, START)
    assert st["gov_halt"]                                                     # the paper ledger can halt it too


def test_a_missing_live_since_never_skips_the_first_14_days():
    assert L.governor([], 1000.0, 0.0, START) == (0.5, None)
    assert L.governor([(START, 5.0)], 1000.0, 0.0, START + 3 * DAY) == (0.5, None)
    assert L.governor([(START, 5.0)], 1000.0, 0.0, START + 14 * DAY) == (0.95, None)


def test_unexplained_cash_change_halts_after_ten_minutes(world):
    ex, mk, st, _ = world
    control = {"live": True, "live_since": 0.0, "deposit": 1000.0}
    L.govern(ex, st, control, START)                                           # first flat check: snapshot
    ex.settlements.append((START + 60, 5.25))
    ex.balance += 5.30                                                         # a win, a few cents of fee drift
    for i in range(12):
        L.govern(ex, st, control, START + 120 + 60 * i)
    assert not st["gov_halt"]                                                  # explained: no halt
    ex.balance += 500.0                                                        # someone deposited $500
    for i in range(9):
        L.govern(ex, st, control, START + 2000 + 60 * i)
    assert not st["gov_halt"]                                                  # 9 minutes: could still be lag
    L.govern(ex, st, control, START + 3000)
    assert st["gov_halt"] and "$" not in st["gov_halt"]                        # 10th: halt, no amounts logged
    ex.balance -= 500.0
    L.govern(ex, st, control, START + 4000)
    assert st["gov_halt"]                                                      # sticky until a fresh start
    L.govern(ex, st, {**control, "live_since": START + 5000}, START + 5000)
    assert not st["gov_halt"]


def test_a_brief_lag_between_cash_and_records_is_tolerated(world):
    ex, mk, st, _ = world
    control = {"live": True, "live_since": 0.0, "deposit": 1000.0}
    L.govern(ex, st, control, START)
    ex.balance += 10.0                                                         # cash credited first...
    for i in range(5):
        L.govern(ex, st, control, START + 60 * (i + 1))
    ex.settlements.append((START + 30, 10.0))                                  # ...record shows up 5 min later
    for i in range(10):
        L.govern(ex, st, control, START + 600 + 60 * i)
    assert not st["gov_halt"]


def test_audit_waits_while_anything_is_open(world):
    ex, mk, st, _ = world
    control = {"live": True, "live_since": 0.0, "deposit": 1000.0}
    L.govern(ex, st, control, START)
    L.step(ex, st, "LIVE", at(0))                                              # an order rests: cash is reserved
    for i in range(15):
        L.govern(ex, st, control, START + 60 * (i + 1))
    assert not st["gov_halt"]

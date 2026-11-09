"""Round 44 (PROTOCOL_ROUND44.md): paper market making for Kalshi liquidity-incentive rewards.

Scoring follows Kalshi's published rules: per side, the reference price is the first bid level where cumulative
size reaches target/5. Orders inside the first `target` contracts score size × discount^(ticks below the reference),
and each side's scores are normalised to shares. Per valid snapshot (both sides reach target) we earn
pool/snapshots × (share_yes + share_no) / 2.
"""
from __future__ import annotations
import json, math, os, subprocess, time
import pandas as pd

from edge import weather as wx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "paper", "r44_state.json")
MINUTES = os.path.join(ROOT, "paper", "r44_minutes.csv")
FILLS = os.path.join(ROOT, "paper", "r44_fills.csv")
REPORT = os.path.join(ROOT, "paper", "ROUND44_LIP.md")
BUDGET = 10_000.0
Q_FRAC = 0.30
TICK = 0.01
MAKER = 0.0175
RUN_SECONDS = int(os.environ.get("R44_SECONDS", str(5 * 3600 + 40 * 60)))
STEP = 60
RANK_EVERY = 3600
MIN_POOL_DAY = 3.0
BANK: dict = {}               # reward/realized/fees of markets we stopped quoting (state['bank'])
MAX_PER_EVENT = 3          # strikes of one event move together (Round 40/41 lesson)
MAX_EVENT_COLLATERAL = 1500.0


def fnum(x, d=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return d


# ------------------------------------------------------------------ scoring (pure)
def levels_desc(raw) -> list[tuple[float, float]]:
    return sorted(((fnum(p), fnum(s)) for p, s in (raw or []) if fnum(s) > 0), reverse=True)


def reference(levels: list[tuple[float, float]], target: float) -> float | None:
    c = 0.0
    for p, s in levels:
        c += s
        if c >= target / 5 - 1e-9:
            return p
    return None


def side_share(levels, target, disc, q, price) -> tuple[float, bool]:
    """Our share of one side's score with q resting at `price` (behind everyone already at that price),
    and whether the side reaches the target (snapshot valid for this side)."""
    book = [(p, s, False) for p, s in levels]
    if q > 0 and price is not None:
        book.append((price, q, True))
    book.sort(key=lambda x: (-x[0], x[2]))          # price desc, ours last within a level
    total = sum(s for _, s, _ in book)
    if total < target - 1e-9:
        return 0.0, False
    ref = reference([(p, s) for p, s, _ in book], target)
    c = raw_all = raw_us = 0.0
    for p, s, us in book:
        if c >= target - 1e-9:
            break
        take = min(s, target - c)
        c += take
        w = take * disc ** max(0, round((ref - p) / TICK))
        raw_all += w
        raw_us += w if us else 0.0
    return (raw_us / raw_all if raw_all > 0 else 0.0), True


def fee(n, p):
    return math.ceil(MAKER * n * p * (1 - p) * 100 - 1e-9) / 100 if n > 0 else 0.0


# ------------------------------------------------------------------ fills (pure)
def apply_trades(pos: dict, trades: list[dict]) -> list[dict]:
    """Fill our resting bids from the tape (oldest first). A YES bid at p is hit by a taker buying NO at a yes-price <= p;
    a NO bid at p is hit by a taker buying YES at a no-price <= p. At our price, the queue ahead goes first."""
    out = []
    q = pos["q"]
    for t in sorted(trades, key=lambda t: t.get("created_time", "")):
        n = fnum(t.get("count_fp") or t.get("count"))
        side = t.get("taker_side")
        for ours, taker, key in (("yes", "no", "yes_price_dollars"), ("no", "yes", "no_price_dollars")):
            if side != taker or pos.get(f"{ours}_px") is None:
                continue
            px, our_px = fnum(t.get(key), 9), pos[f"{ours}_px"]
            if px > our_px + 1e-9:
                continue
            room = q - (pos[f"inv_{ours}"] - pos[f"inv_{'no' if ours == 'yes' else 'yes'}"])
            room = min(room, q - pos.get(f"filled_{ours}_at_peg", 0.0))
            if room <= 0:
                continue
            if px < our_px - 1e-9:
                got = room                                       # traded through our level: we are gone
            else:
                ahead = pos[f"{ours}_ahead"]
                got = max(0.0, min(room, n - ahead))
                pos[f"{ours}_ahead"] = max(0.0, ahead - n)
            if got <= 0:
                continue
            pos[f"inv_{ours}"] += got
            pos[f"cost_{ours}"] += got * our_px
            pos[f"filled_{ours}_at_peg"] = pos.get(f"filled_{ours}_at_peg", 0.0) + got
            f = fee(got, our_px)
            pos["fees"] += f
            out.append({"ticker": pos["ticker"], "time": t.get("created_time"), "side": ours, "n": got, "px": our_px, "fee": f})
    pair(pos)
    return out


def pair(pos: dict) -> None:
    k = min(pos["inv_yes"], pos["inv_no"])
    if k <= 0:
        return
    ay, an = pos["cost_yes"] / pos["inv_yes"], pos["cost_no"] / pos["inv_no"]
    pos["realized"] += k * (1 - ay - an)
    pos["inv_yes"] -= k; pos["inv_no"] -= k
    pos["cost_yes"] -= k * ay; pos["cost_no"] -= k * an


def new_pos(prog: dict) -> dict:
    target = fnum(prog["target_size_fp"])
    return {"ticker": prog["market_ticker"], "program": prog["id"], "target": target, "disc": prog["discount_factor_bps"] / 10000,
            "pool_day": pool_day(prog), "end": prog["end_date"], "q": math.floor(Q_FRAC * target),
            "yes_px": None, "no_px": None, "yes_ahead": 0.0, "no_ahead": 0.0, "inv_yes": 0.0, "inv_no": 0.0,
            "cost_yes": 0.0, "cost_no": 0.0, "realized": 0.0, "fees": 0.0, "reward": 0.0, "active": True, "last_ts": None}


def pool_day(prog: dict) -> float:
    a, b = pd.Timestamp(prog["start_date"]), pd.Timestamp(prog["end_date"])
    return prog["period_reward"] / 10000 / max((b - a).total_seconds() / 86400, 1 / 24)


def peg_and_score(pos: dict, yes_lv, no_lv) -> tuple[float, float, bool]:
    """Re-peg both bids to the current reference and return (share_yes, share_no, valid)."""
    net = pos["inv_yes"] - pos["inv_no"]
    sides = {}
    for ours, lv in (("yes", yes_lv), ("no", no_lv)):
        ref = reference(lv, pos["target"])
        blocked = (net >= pos["q"]) if ours == "yes" else (-net >= pos["q"])
        if not pos["active"] or blocked or ref is None:
            pos[f"{ours}_px"] = None
            sh, ok = side_share(lv, pos["target"], pos["disc"], 0, None)
        else:
            pos[f"{ours}_px"] = ref
            pos[f"{ours}_ahead"] = sum(s for p, s in lv if p >= ref - 1e-9)
            pos[f"filled_{ours}_at_peg"] = 0.0
            sh, ok = side_share(lv, pos["target"], pos["disc"], pos["q"], ref)
        sides[ours] = (sh, ok)
    return sides["yes"][0], sides["no"][0], sides["yes"][1] and sides["no"][1]


# ------------------------------------------------------------------ I/O
def get(path, params=None):
    r = wx._get(f"{wx.KALSHI}/{path}", params)
    return r.json() if r is not None and r.status_code == 200 else None


def programs() -> list[dict]:
    out, cursor = [], None
    for _ in range(60):
        p = {"status": "active", "limit": 1000}
        if cursor:
            p["cursor"] = cursor
        j = get("incentive_programs", p)
        if not j:
            break
        out += [x for x in j.get("incentive_programs", []) if x.get("incentive_type") == "liquidity"]
        cursor = j.get("next_cursor")
        if not cursor or not j.get("incentive_programs"):
            break
    return out


def book(ticker):
    j = get(f"markets/{ticker}/orderbook") or {}
    b = j.get("orderbook_fp") or {}
    return levels_desc(b.get("yes_dollars")), levels_desc(b.get("no_dollars"))


def markets_info(tickers: list[str]) -> dict:
    info = {}
    for i in range(0, len(tickers), 100):
        j = get("markets", {"tickers": ",".join(tickers[i:i + 100]), "limit": 100}) or {}
        for m in j.get("markets", []):
            info[m["ticker"]] = m
    return info


def tape(ticker, since):
    j = get("markets/trades", {"ticker": ticker, "limit": 1000, "min_ts": int(since)}) or {}
    return j.get("trades", [])


def collateral(pos):
    rest = sum(pos["q"] * pos[f"{s}_px"] for s in ("yes", "no") if pos.get(f"{s}_px"))
    return rest + pos["cost_yes"] + pos["cost_no"]


def rank(now: pd.Timestamp, held: dict) -> dict:
    progs = [p for p in programs() if pool_day(p) >= MIN_POOL_DAY and pd.Timestamp(p["end_date"]) > now]
    info = markets_info(sorted({p["market_ticker"] for p in progs}))
    cands = []
    for p in progs:
        m = info.get(p["market_ticker"]) or {}
        if m.get("status") != "active" or m.get("price_level_structure") != "linear_cent":
            continue
        if pd.Timestamp(m.get("close_time")) < now + pd.Timedelta(hours=24):
            continue
        mid = (fnum(m.get("yes_bid_dollars")) + fnum(m.get("yes_ask_dollars"), 1)) / 2
        if not 0.05 <= mid <= 0.95:
            continue
        pos = new_pos(p)
        yl, nl = book(p["market_ticker"])
        sy, sn, ok = peg_and_score(pos, yl, nl)
        if not ok:
            continue
        cap = collateral(pos)
        rew = pos["pool_day"] * (sy + sn) / 2
        if cap > 0 and rew > 0:
            cands.append((rew / cap, rew, cap, p))
    cands.sort(key=lambda x: -x[0])
    keep = {t: v for t, v in held.items() if v["inv_yes"] > 0 or v["inv_no"] > 0}   # inventory stays until it settles
    for v in keep.values():
        v["active"] = False
    used = sum(collateral(v) for v in keep.values())
    ev_n, ev_cap = {}, {}
    for t, v in keep.items():
        e = t.rsplit("-", 1)[0]; ev_cap[e] = ev_cap.get(e, 0.0) + collateral(v)
    chosen = 0
    for per, rew, cap, p in cands:
        t = p["market_ticker"]
        e = t.rsplit("-", 1)[0]
        if used + cap > BUDGET or ev_n.get(e, 0) >= MAX_PER_EVENT or ev_cap.get(e, 0.0) + cap > MAX_EVENT_COLLATERAL:
            continue
        ev_n[e] = ev_n.get(e, 0) + 1; ev_cap[e] = ev_cap.get(e, 0.0) + cap
        if t in held:                                   # same object: its running reward/fees/P&L carry over
            keep[t] = held[t]
            keep[t]["active"] = True
            keep[t].update({k: new_pos(p)[k] for k in ("program", "pool_day", "end", "q", "target", "disc")})
        else:
            keep[t] = new_pos(p)
        used += cap
        chosen += 1
    for t, v in held.items():                           # dropped markets: bank what they earned so totals never go backwards
        if t not in keep:
            for k in ("reward", "realized", "fees"):
                BANK[k] = BANK.get(k, 0.0) + v.get(k, 0.0)
    print(f"{now:%H:%M} ranked {len(cands)} candidates from {len(progs)} programs; quoting {chosen}, collateral ${used:,.0f}", flush=True)
    return keep


def step(pos_all: dict, now: pd.Timestamp, last: float) -> tuple[dict, list[dict]]:
    fills, row = [], {"time": now.isoformat(), "markets": 0, "reward": 0.0, "mtm": 0.0, "realized": 0.0, "fees": 0.0, "collateral": 0.0}
    info = markets_info(list(pos_all))
    for t, pos in list(pos_all.items()):
        m = info.get(t) or {}
        if m.get("result") in ("yes", "no"):
            pay = pos["inv_yes"] * (m["result"] == "yes") + pos["inv_no"] * (m["result"] == "no")
            pos["realized"] += pay - pos["cost_yes"] - pos["cost_no"]
            pos.update(inv_yes=0.0, inv_no=0.0, cost_yes=0.0, cost_no=0.0, active=False, settled=m["result"])
        if pos.get("settled") or (not pos["active"] and pos["inv_yes"] == 0 and pos["inv_no"] == 0):
            continue
        fills += apply_trades(pos, tape(t, last))
        yl, nl = book(t)
        sy, sn, ok = peg_and_score(pos, yl, nl)
        if pd.Timestamp(pos["end"]) > now and pos["active"] and ok:
            pos["reward"] += pos["pool_day"] / 1440 * (sy + sn) / 2 * (STEP / 60)
        yb = yl[0][0] if yl else 0.0
        ya = 1 - nl[0][0] if nl else 1.0
        mid = (yb + ya) / 2
        pos["mtm"] = pos["inv_yes"] * mid + pos["inv_no"] * (1 - mid) - pos["cost_yes"] - pos["cost_no"]
        row["markets"] += pos["active"]
    for pos in pos_all.values():
        row["reward"] += pos["reward"]; row["realized"] += pos["realized"]; row["fees"] += pos["fees"]
        row["mtm"] += pos.get("mtm", 0.0); row["collateral"] += collateral(pos) if not pos.get("settled") else 0.0
    for k in ("reward", "realized", "fees"):
        row[k] += BANK.get(k, 0.0)
    row["net"] = row["reward"] + row["realized"] + row["mtm"] - row["fees"]
    return pos_all, fills + [{"_row": row}]


def summary(now) -> str:
    d = pd.read_csv(MINUTES) if os.path.exists(MINUTES) else pd.DataFrame()
    lines = ["# Round 44: paper market making for Kalshi liquidity rewards", "",
             f"Updated {now:%Y-%m-%d %H:%M} UTC. Rules: [PROTOCOL_ROUND44.md](../PROTOCOL_ROUND44.md). $10,000 budget.", ""]
    if d.empty:
        return "\n".join(lines + ["No data yet."]) + "\n"
    d["time"] = pd.to_datetime(d["time"])
    last = d.iloc[-1]
    lines += [f"Since start: reward **${last.reward:,.2f}**, realised spread/settled **${last.realized:,.2f}**, open inventory "
              f"marked **${last.mtm:,.2f}**, fees **${last.fees:,.2f}** → **net ${last.net:,.2f}**. Quoting {int(last.markets)} markets, "
              f"collateral ${last.collateral:,.0f}.", ""]
    day = d.set_index("time").resample("1D").last()
    day["net_day"] = day.net.diff().fillna(day.net)
    day["reward_day"] = day.reward.diff().fillna(day.reward)
    lines += ["| Day | Reward | Net | Markets |", "|---|---:|---:|---:|"]
    lines += [f"| {i:%Y-%m-%d} | ${r.reward_day:,.2f} | ${r.net_day:,.2f} | {int(r.markets)} |" for i, r in day.iterrows() if pd.notna(r.net)]
    if os.path.exists(FILLS):
        f = pd.read_csv(FILLS)
        lines += ["", f"Fills: {len(f)} ({f.n.sum():,.0f} contracts) in {f.ticker.nunique()} markets."]
    return "\n".join(lines) + "\n"


def commit(now):
    paths = [p for p in (STATE, MINUTES, FILLS, REPORT) if os.path.exists(p)]
    for c in (["git", "add", *paths], ["git", "commit", "-q", "-m", f"round44: lip ledger {now:%Y-%m-%dT%H:%MZ} [skip ci]"],
              ["git", "pull", "--rebase", "-q"], ["git", "push", "-q"]):
        try:
            if subprocess.run(c, cwd=ROOT, timeout=120).returncode != 0 and c[1] == "commit":
                return
        except subprocess.TimeoutExpired:
            return


def recover_bank() -> dict:
    """One-off repair (Nov 9): before banking existed, each hourly re-rank reset the reward of re-chosen markets to 0,
    so the logged running total dropped. Every drop between consecutive minutes is reward that was lost from the total."""
    if not os.path.exists(MINUTES):
        return {}
    r = pd.read_csv(MINUTES)["reward"].to_numpy()
    lost = sum(a - b for a, b in zip(r[:-1], r[1:]) if b < a - 1e-9)
    return {"reward": float(lost)}


def run():
    st = json.load(open(STATE)) if os.path.exists(STATE) else {"pos": {}, "last": time.time() - STEP, "ranked": 0}
    if "bank" not in st:
        st["bank"] = recover_bank()
    BANK.clear(); BANK.update(st["bank"])
    t0, last_commit = time.time(), time.time()
    while time.time() - t0 < RUN_SECONDS:
        now = pd.Timestamp.now(tz="UTC")
        try:
            if time.time() - st["ranked"] > RANK_EVERY:
                st["pos"] = rank(now, st["pos"]); st["ranked"] = time.time()
            st["pos"], out = step(st["pos"], now, st["last"])
            st["last"] = now.timestamp()
            row = out.pop()["_row"]
            pd.DataFrame([row]).to_csv(MINUTES, mode="a", header=not os.path.exists(MINUTES), index=False)
            if out:
                pd.DataFrame(out).to_csv(FILLS, mode="a", header=not os.path.exists(FILLS), index=False)
            st["bank"] = dict(BANK)
            json.dump(st, open(STATE, "w"))
        except Exception as e:
            print(f"{now:%H:%M:%S} step failed: {e!r}", flush=True)
        if os.environ.get("R44_COMMIT") == "1" and time.time() - last_commit > 1800:
            open(REPORT, "w").write(summary(now)); commit(now); last_commit = time.time()
        time.sleep(max(0.0, STEP - (time.time() - now.timestamp())))
    now = pd.Timestamp.now(tz="UTC")
    open(REPORT, "w").write(summary(now))
    if os.environ.get("R44_COMMIT") == "1":
        commit(now)


if __name__ == "__main__":
    run()

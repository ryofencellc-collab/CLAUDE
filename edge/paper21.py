"""Live paper test of Round 21 (PROTOCOL_ROUND21.md, "Forward test").

Runs a loop for RUN_SECONDS. Each pass (about every 15 s):
  1. For each series, list open markets closing within the hour.
  2. Coinbase spot from the last completed minute, and the trailing 60-minute volatility, give z for each market.
  3. z >= Z for one side and no order yet: paper-bid ORDER contracts at 99c on that side; record the queue
     already resting at >= 99c on that side.
  4. Open orders: if z falls below Z the bid is cancelled (no fills counted after that). Every ~30 s, later public
     trades where a taker bought the other side at <= 2c are counted; we are filled only after the queue ahead.
  5. After close, settle on Kalshi's result.
The ledger paper/r21_orders.csv is committed every COMMIT_EVERY seconds and at the end.
"""
import os
import subprocess
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from edge import round15 as r15
from edge import weather as wx

ROOT = Path(__file__).resolve().parent.parent / "paper"
ROOT.mkdir(exist_ok=True)
OPEN = ROOT / "r21_open.csv"      # orders not yet settled (carried between jobs)
FILLS = ROOT / "r21_fills.csv"    # settled markets that got any fill, or were wrong
DAILY = ROOT / "r21_daily.csv"    # every settled market, aggregated by day and series
CAPITAL = ROOT / "r21_capital.csv"  # collateral a real account would tie up, sampled every pass
PLACED15 = ROOT / "r21_15m_placed.csv"  # every 15-minute bid, for the paper vs live comparison
Z, BID, ORDER = 6.0, 0.99, 1000.0
SERIES = {"KXBTC15M": "BTC-USD", "KXETH15M": "ETH-USD", "KXSOL15M": "SOL-USD", "KXXRP15M": "XRP-USD",
          "KXDOGE15M": "DOGE-USD", "KXBTCD": "BTC-USD", "KXETHD": "ETH-USD", "KXSOLD": "SOL-USD", "KXXRPD": "XRP-USD"}
# KXBNB15M is in the backtest, but BNB has no Coinbase market, so it is left out here.
# Round 24 (PROTOCOL_ROUND24.md, forward test): S&P 500 / Nasdaq-100 binaries, Yahoo 1-minute index bars, Z = 2.
INDEX_SERIES = {"KXINXU": "^GSPC", "KXINX": "^GSPC", "KXNASDAQ100U": "^NDX", "KXNASDAQ100": "^NDX"}
SERIES.update(INDEX_SERIES)
Z_INDEX = 2.0
STALE = pd.Timedelta(minutes=5)
MIN_INDEX_BARS = 30  # minutes of today's session needed before the index volatility is trusted


def zmin(series: str) -> float:
    return Z_INDEX if series in INDEX_SERIES else Z
RUN_SECONDS = int(os.environ.get("P21_SECONDS", 20700))
COMMIT_EVERY = 7200
SETTLE_PER_PASS = 40
COLS = ["ticker", "series", "side", "strike", "close_utc", "placed_utc", "z_at_place", "spot_at_place", "queue_ahead",
        "seen", "filled", "status", "cancelled_utc", "result", "pnl", "settled_utc"]
CB = "https://api.exchange.coinbase.com/products/{}/candles"
_cb = requests.Session()


OCOLS = COLS + ["strike_type", "cap"]  # the open ledger also keeps what the cancel check needs
DCOLS = ["day", "series", "settled", "cancelled", "filled_markets", "contracts", "pnl", "lost_filled", "queue_sum"]


def _read(path, cols):
    if path.exists() and path.stat().st_size:
        first = path.read_text().split(",", 1)[0]
        named = {} if first in ("ticker", "day") else {"header": None, "names": cols}  # day-1 file lacked a header
        d = pd.read_csv(path, dtype={"status": str, "result": str, "settled_utc": str, "cancelled_utc": str}, **named)
        for c in ("result", "settled_utc", "cancelled_utc"):
            if c in d:
                d[c] = d[c].fillna("")
        return d
    return pd.DataFrame(columns=cols)


def ledger() -> pd.DataFrame:
    d = _read(OPEN, OCOLS)
    for c, default in (("strike_type", "greater"), ("cap", np.nan)):
        if c not in d:
            d[c] = default
    d["strike_type"] = d["strike_type"].fillna("greater")
    return d


def settle_out(led: pd.DataFrame) -> pd.DataFrame:
    """Move settled rows out of the open ledger: filled or wrong ones to FILLS, all into DAILY totals."""
    done = led[led["status"].isin(["won", "lost"])]
    if done.empty:
        return led
    fills = done[(done["filled"].astype(float) > 0) | (done["status"] == "lost")]
    if len(fills):
        fills[COLS].to_csv(FILLS, mode="a", header=not (FILLS.exists() and FILLS.stat().st_size), index=False)
    g = done.assign(day=pd.to_datetime(done["close_utc"]).dt.date.astype(str),
                    cancelled=(done["cancelled_utc"] != "").astype(int),
                    filled_m=(done["filled"].astype(float) > 0).astype(int),
                    lost_filled=((done["status"] == "lost") & (done["filled"].astype(float) > 0)).astype(int),
                    q=pd.to_numeric(done["queue_ahead"], errors="coerce").fillna(0))
    agg = g.groupby(["day", "series"]).agg(settled=("ticker", "size"), cancelled=("cancelled", "sum"),
                                           filled_markets=("filled_m", "sum"), contracts=("filled", "sum"),
                                           pnl=("pnl", "sum"), lost_filled=("lost_filled", "sum"),
                                           queue_sum=("q", "sum")).reset_index()
    old = _read(DAILY, DCOLS)
    both = pd.concat([old, agg], ignore_index=True) if len(old) else agg
    num = [c for c in DCOLS if c not in ("day", "series")]
    both[num] = both[num].apply(pd.to_numeric)
    both.groupby(["day", "series"])[num].sum().reset_index()[DCOLS].to_csv(DAILY, index=False)
    return led[~led.index.isin(done.index)]


def index_spot_and_vol(ticker: str, now: pd.Timestamp):
    """Yahoo 1-minute index bars: (last completed minute's close, per-minute vol over 60); nan when stale."""
    try:
        import yfinance as yf
        df = yf.download(ticker, period="1d", interval="1m", progress=False, auto_adjust=False)
    except Exception:
        return np.nan, np.nan
    if df is None or df.empty:
        return np.nan, np.nan
    c = df["Close"]
    c = c.iloc[:, 0] if isinstance(c, pd.DataFrame) else c
    idx = c.index.tz_convert("UTC") if c.index.tz is not None else c.index.tz_localize("UTC")
    c = pd.Series(c.to_numpy(dtype=float), index=idx + pd.Timedelta(minutes=1)).dropna()
    c = c[c.index <= now]
    if c.empty or now - c.index[-1] > STALE:
        return np.nan, np.nan
    if len(c) < MIN_INDEX_BARS:  # right after the 9:30 open a few bars give a near-zero vol and a huge z: no bids
        return np.nan, np.nan
    return float(c.iloc[-1]), float(np.log(c).diff().tail(60).std())


def spot_and_vol(product: str, now: pd.Timestamp):
    """(close of the last completed minute, per-minute vol over the trailing 60) from Coinbase 1-minute candles."""
    if product.startswith("^"):
        return index_spot_and_vol(product, now)
    try:
        r = _cb.get(CB.format(product), params={"granularity": 60}, timeout=20, headers={"User-Agent": "paper21"})
        rows = r.json() if r.status_code == 200 else []
    except (requests.RequestException, ValueError):
        rows = []
    if not rows:
        return np.nan, np.nan
    c = pd.Series({pd.Timestamp(x[0] + 60, unit="s", tz="UTC"): float(x[4]) for x in rows}).sort_index()
    c = c[c.index <= now]
    vol = np.log(c).diff().tail(60).std()
    return (float(c.iloc[-1]) if len(c) else np.nan), float(vol)


def z_for(spot, vol, strike, close, now):
    tau = max((close - now).total_seconds() / 60, 0.5)
    return np.log(spot / strike) / (vol * np.sqrt(tau)) if vol and vol > 0 else np.nan


def z_sides(strike_type, floor, cap, spot, vol, close, now):
    """(z that YES is winning, z that NO is winning). A range's YES ('inside') is never treated as decided."""
    if strike_type in ("greater", "greater_or_equal"):
        z = z_for(spot, vol, float(floor), close, now)
        return z, -z
    if strike_type in ("less", "less_or_equal"):
        z = -z_for(spot, vol, float(cap), close, now)
        return z, -z
    if strike_type == "between":
        inside = min(z_for(spot, vol, float(floor), close, now), -z_for(spot, vol, float(cap), close, now))
        return -np.inf, -inside
    return np.nan, np.nan


def queue_ahead(ticker: str, side: str) -> float:
    r = wx._get(f"{wx.KALSHI}/markets/{ticker}/orderbook")
    if r is None or r.status_code != 200:
        return np.nan
    book = r.json().get("orderbook_fp") or r.json().get("orderbook") or {}
    return float(sum(float(sz) for px, sz in (book.get(f"{side}_dollars") or []) if float(px) >= BID - 1e-9))


def seen_since(ticker: str, side: str, since: pd.Timestamp, until: pd.Timestamp) -> float:
    other = "no" if side == "yes" else "yes"
    n, cursor = 0.0, None
    for _ in range(20):
        p = {"ticker": ticker, "limit": 1000, "min_ts": int(since.timestamp())}
        if cursor:
            p["cursor"] = cursor
        r = wx._get(f"{wx.KALSHI}/markets/trades", p)
        if r is None or r.status_code != 200:
            break
        j = r.json()
        for t in j.get("trades", []):
            ts = pd.Timestamp(t["created_time"])
            px = float(t.get(f"{other}_price_dollars") or 1)
            if t.get("taker_side") == other and px <= 0.02 + 1e-9 and since < ts <= until:
                n += float(t.get("count_fp") or t.get("count") or 0)
        cursor = j.get("cursor")
        if not cursor or not j.get("trades"):
            break
    return n


def open_markets(series: str, now: pd.Timestamp) -> list[dict]:
    r = wx._get(f"{wx.KALSHI}/markets", {"series_ticker": series, "status": "open", "limit": 1000})
    ms = r.json().get("markets", []) if r is not None and r.status_code == 200 else []
    out = []
    for m in ms:
        close = pd.to_datetime(m.get("close_time"), utc=True, errors="coerce")
        kinds = ("greater", "greater_or_equal", "less", "less_or_equal", "between") if series in INDEX_SERIES \
            else ("greater", "greater_or_equal")
        if m.get("strike_type") in kinds and pd.notna(close) and \
                now + pd.Timedelta(seconds=5) < close <= now + pd.Timedelta(hours=1):
            out.append({**m, "_close": close})
    return out


def place(led: pd.DataFrame, now: pd.Timestamp) -> pd.DataFrame:
    have, new = set(led["ticker"]), []
    spots = {p: spot_and_vol(p, now) for p in set(SERIES.values())}
    for series, product in SERIES.items():
        s, v = spots[product]
        if not np.isfinite(s):
            continue
        for m in open_markets(series, now):
            if m["ticker"] in have:
                continue
            zy, zn = z_sides(m.get("strike_type"), m.get("floor_strike"), m.get("cap_strike"), s, v, m["_close"], now)
            if np.isfinite(zy) and zy >= zmin(series):
                side, z = "yes", zy
            elif np.isfinite(zn) and zn >= zmin(series):
                side, z = "no", zn
            else:
                continue
            new.append(dict(ticker=m["ticker"], series=series, side=side, strike=m.get("floor_strike"),
                            strike_type=m.get("strike_type"), cap=m.get("cap_strike"),
                            close_utc=m["_close"].isoformat(), placed_utc=now.isoformat(), z_at_place=round(abs(z), 2),
                            spot_at_place=s, queue_ahead=queue_ahead(m["ticker"], side), seen=0.0, filled=0.0,
                            status="open", cancelled_utc="", result="", pnl=np.nan, settled_utc=""))
    if new:
        print(f"{now:%H:%M:%S} placed {len(new)}: {[x['ticker'] for x in new][:6]}", flush=True)
        q15 = [x for x in new if x["series"].endswith("15M")]
        if q15:  # small per-bid log of 15-minute markets, to check the live trader against 1:1
            pd.DataFrame(q15)[["ticker", "series", "side", "placed_utc", "z_at_place", "queue_ahead"]].to_csv(
                PLACED15, mode="a", header=not (PLACED15.exists() and PLACED15.stat().st_size), index=False)
        led = pd.concat([led, pd.DataFrame(new)[OCOLS]], ignore_index=True) if len(led) else pd.DataFrame(new)[OCOLS]
    return led


def watch(led: pd.DataFrame, now: pd.Timestamp, count_fills: bool) -> pd.DataFrame:
    spots, settling = {}, 0
    for i in led.index[led["status"].isin(["open", "cancelled"])]:
        close = pd.Timestamp(led.at[i, "close_utc"])
        side = led.at[i, "side"]
        if now >= close + pd.Timedelta(minutes=2):
            settling += 1
            if settling > SETTLE_PER_PASS:  # keep each pass short so cancels on open bids stay fast
                continue
        if led.at[i, "status"] == "open" and now < close:
            prod = SERIES[led.at[i, "series"]]
            spots.setdefault(prod, spot_and_vol(prod, now))
            s, v = spots[prod]
            zy, zn = z_sides(led.at[i, "strike_type"], led.at[i, "strike"], led.at[i, "cap"], s, v, close, now)
            z = zy if side == "yes" else zn
            if np.isfinite(z) and z < zmin(led.at[i, "series"]):
                led.at[i, "status"], led.at[i, "cancelled_utc"] = "cancelled", now.isoformat()
        if now >= close + pd.Timedelta(minutes=2) and led.at[i, "seen"] == 0:
            until = pd.Timestamp(led.at[i, "cancelled_utc"]) if led.at[i, "cancelled_utc"] else min(now, close)
            seen = seen_since(led.at[i, "ticker"], side, pd.Timestamp(led.at[i, "placed_utc"]), until)
            q = led.at[i, "queue_ahead"]
            led.at[i, "seen"] = seen
            led.at[i, "filled"] = float(min(ORDER, max(0.0, seen - (float(q) if pd.notna(q) else 0.0))))
        if now >= close + pd.Timedelta(minutes=2):
            r = wx._get(f"{wx.KALSHI}/markets/{led.at[i, 'ticker']}")
            m = r.json().get("market", {}) if r is not None and r.status_code == 200 else {}
            if m.get("result") in ("yes", "no"):
                n = float(led.at[i, "filled"])
                right = m["result"] == side
                fee = r15._maker_fee(n, BID) if n > 0 else 0.0
                led.at[i, "result"], led.at[i, "settled_utc"] = m["result"], now.isoformat()
                led.at[i, "pnl"] = round(n * ((1.0 if right else 0.0) - BID) - fee, 2)
                led.at[i, "status"] = "won" if right else "lost"
    return led


def summary(led: pd.DataFrame, now: pd.Timestamp) -> str:
    d = _read(DAILY, DCOLS)
    f = _read(FILLS, COLS)
    num = ["settled", "cancelled", "filled_markets", "contracts", "pnl", "lost_filled", "queue_sum"]
    d[num] = d[num].apply(pd.to_numeric) if len(d) else d[num]
    tot = d[num].sum() if len(d) else pd.Series(0.0, index=num)
    lines = ["# Round 21 live paper test: 99c bids on crypto markets decided by the spot price", "",
             f"Updated {now:%Y-%m-%d %H:%M} UTC. Rules: [PROTOCOL_ROUND21.md](../PROTOCOL_ROUND21.md), \"Forward test\". "
             f"{ORDER:,.0f} contracts per market at z >= {Z:g}; fills only after the live queue ahead.", "",
             "| | |", "|---|---|",
             f"| Markets bid and settled | {int(tot['settled']):,} (cancelled before close {int(tot['cancelled']):,}); open now {len(led):,} |",
             f"| Markets that got any fill | {int(tot['filled_markets']):,} ({tot['filled_markets'] / max(tot['settled'], 1):.1%}) |",
             f"| Losing filled markets | {int(tot['lost_filled'])} |",
             f"| Contracts filled | {tot['contracts']:,.0f} |",
             f"| **Paper profit** | **${tot['pnl']:+,.2f}** |",
             f"| Average queue ahead at placement | {tot['queue_sum'] / max(tot['settled'], 1):,.0f} contracts |", ""]
    if len(d):
        by_day = d.groupby("day")[num].sum()
        lines += ["| Day | Settled | Filled markets | Contracts | P&L |", "|---|---:|---:|---:|---:|"]
        lines += [f"| {k} | {int(r.settled):,} | {int(r.filled_markets)} | {r.contracts:,.0f} | ${r.pnl:+.2f} |" for k, r in by_day.iterrows()]
        by_s = d.groupby("series")[num].sum()
        lines += ["", "| Series | Settled | Filled markets | Contracts | P&L | Avg queue |", "|---|---:|---:|---:|---:|---:|"]
        lines += [f"| {k} | {int(r.settled):,} | {int(r.filled_markets)} | {r.contracts:,.0f} | ${r.pnl:+.2f} | "
                  f"{r.queue_sum / max(r.settled, 1):,.0f} |" for k, r in by_s.iterrows()]
    lines += capital_lines()
    lines += round24_forward(d)
    if len(f):
        lines += round22(f)
        lines += ["", f"Filled or wrong markets are listed in [r21_fills.csv](r21_fills.csv) ({len(f)} rows)."]
    return "\n".join(lines) + "\n"


R22_START, R22_END = pd.Timestamp("2026-10-31", tz="UTC"), pd.Timestamp("2026-11-14", tz="UTC")


def r22_size(series: str) -> float:
    return 10000.0 if series.endswith("15M") else 1000.0


def round22(f: pd.DataFrame) -> list[str]:
    """PROTOCOL_ROUND22.md: the same ledger at 10k contracts on 15-minute markets (filled = min(size, seen - queue))."""
    f = f.copy()
    close = pd.to_datetime(f["close_utc"], utc=True)
    f = f[(close >= R22_START) & (close < R22_END)]
    lines = ["", f"## Round 22 sizing (10k contracts on 15-minute markets), window {R22_START.date()} to "
                 f"{(R22_END - pd.Timedelta(days=1)).date()}", ""]
    if f.empty:
        return lines + ["No settled fills in the window yet."]
    size = f["series"].map(r22_size)
    excess = (f["seen"].astype(float) - pd.to_numeric(f["queue_ahead"], errors="coerce").fillna(0)).clip(lower=0)
    n = excess.clip(upper=size)
    right = f["status"] == "won"
    fee = [r15._maker_fee(x, BID) if x > 0 else 0.0 for x in n]
    f["pnl22"] = (n * (right.astype(float) - BID)).to_numpy() - fee
    day = pd.to_datetime(f["close_utc"], utc=True).dt.date
    daily = f.groupby(day)["pnl22"].sum()
    lost = f[(~right) & (n > 0)]
    lines += ["| | |", "|---|---|", f"| Paper profit at Round 22 size | **${f['pnl22'].sum():+,.2f}** |",
              f"| Losing filled markets | {len(lost)} |", f"| Days with fills | {len(daily)} (green {(daily > 0).mean():.0%}) |",
              f"| Worst day | ${daily.min():+,.2f} |"]
    return lines


R24_START, R24_END = pd.Timestamp("2026-11-02"), pd.Timestamp("2026-11-16")


def round24_forward(d: pd.DataFrame) -> list[str]:
    """PROTOCOL_ROUND24.md forward test: the index series alone, 1,000 contracts per market."""
    lines = ["", f"## Round 24 forward test (S&P 500 / Nasdaq-100 binaries), {R24_START.date()} to "
                 f"{(R24_END - pd.Timedelta(days=1)).date()}", ""]
    if d.empty:
        return lines + ["No settled index markets yet."]
    x = d[d["series"].isin(INDEX_SERIES) & (pd.to_datetime(d["day"]) >= R24_START) & (pd.to_datetime(d["day"]) < R24_END)]
    if x.empty:
        return lines + ["No settled index markets yet."]
    daily = x.groupby("day")[["settled", "filled_markets", "pnl", "lost_filled"]].sum()
    active = daily[daily["filled_markets"] > 0]
    return lines + ["| | |", "|---|---|", f"| Paper profit | **${daily['pnl'].sum():+,.2f}** |",
                    f"| Markets settled / filled | {int(daily['settled'].sum()):,} / {int(daily['filled_markets'].sum())} |",
                    f"| Losing filled markets | {int(daily['lost_filled'].sum())} |",
                    f"| Days with fills | {len(active)} (green {(active['pnl'] > 0).mean() if len(active) else 0:.0%}) |"]


GROUPS = ("crypto15m", "crypto_hourly", "index")
_cap = {}  # (day, group) -> [samples, sum, peak]


def group(series: str) -> str:
    return "index" if series in INDEX_SERIES else "crypto15m" if series.endswith("15M") else "crypto_hourly"


def sample_capital(led: pd.DataFrame, now: pd.Timestamp) -> None:
    """Collateral of resting bids right now: 15-minute markets at the Round 22 size, everything else at ORDER."""
    live = led[(led["status"] == "open") & (pd.to_datetime(led["close_utc"], utc=True) > now)]
    day = now.date().isoformat()
    for g in GROUPS:
        x = live[live["series"].map(group) == g]
        size = 10000.0 if g == "crypto15m" else ORDER
        usd = float(len(x)) * size * BID
        k = _cap.setdefault((day, g), [0, 0.0, 0.0])
        k[0] += 1
        k[1] += usd
        k[2] = max(k[2], usd)


def save_capital() -> None:
    old = pd.read_csv(CAPITAL) if CAPITAL.exists() and CAPITAL.stat().st_size else pd.DataFrame(
        columns=["day", "group", "samples", "sum", "peak"])
    new = pd.DataFrame([dict(day=d, group=g, samples=v[0], sum=v[1], peak=v[2]) for (d, g), v in _cap.items()])
    both = pd.concat([old, new], ignore_index=True) if len(old) else new
    both = both.groupby(["day", "group"]).agg(samples=("samples", "sum"), sum=("sum", "sum"), peak=("peak", "max")).reset_index()
    both.to_csv(CAPITAL, index=False)
    _cap.clear()


def capital_lines() -> list[str]:
    if not (CAPITAL.exists() and CAPITAL.stat().st_size):
        return []
    c = pd.read_csv(CAPITAL)
    c["avg"] = c["sum"] / c["samples"].clip(lower=1)
    lines = ["", "## Capital a real account would tie up (resting bids x size x 99c)", "",
             "| Day | Group | Average | Peak |", "|---|---|---:|---:|"]
    lines += [f"| {r.day} | {r.group} | ${r.avg:,.0f} | ${r.peak:,.0f} |" for r in c.sort_values(["day", "group"]).itertuples()]
    return lines


def save(led, now):
    led = settle_out(led)
    led[OCOLS].to_csv(OPEN, index=False)
    (ROOT / "ROUND21_PAPER.md").write_text(summary(led, now))
    return led


def commit(now):
    cmds = [["git", "add", "paper/r21_open.csv", "paper/r21_fills.csv", "paper/r21_daily.csv", "paper/r21_capital.csv",
             "paper/r21_15m_placed.csv", "paper/ROUND21_PAPER.md"],
            ["git", "commit", "-q", "-m", f"paper21: ledger {now:%Y-%m-%dT%H:%MZ} [skip ci]"],
            ["git", "pull", "--rebase", "-q"], ["git", "push", "-q"]]
    for c in cmds:
        if subprocess.run(c, cwd=ROOT.parent).returncode != 0 and c[1] in ("commit",):
            return


def run():
    for f in (FILLS, DAILY, CAPITAL, PLACED15):
        f.touch()
    t0 = time.time()
    led, last_commit, passes = ledger(), time.time(), 0
    while time.time() - t0 < RUN_SECONDS:
        now = pd.Timestamp.now(tz="UTC")
        try:
            t1 = time.time()
            led = place(led, now)
            t2 = time.time()
            led = watch(led, now, True)
            t3 = time.time()
            sample_capital(led, now)
            led = save(led, now)
            passes += 1
            if passes % 20 == 1:
                print(f"{now:%H:%M:%S} pass {passes}: place {t2 - t1:.0f}s, watch {t3 - t2:.0f}s, save {time.time() - t3:.0f}s; "
                      f"open {len(led)}", flush=True)
        except Exception as e:  # keep the loop alive; the ledger is saved every pass
            print(f"{now:%H:%M:%S} pass failed: {e!r}", flush=True)
        if os.environ.get("P21_COMMIT") == "1" and time.time() - last_commit > COMMIT_EVERY:
            save_capital()
            commit(now)
            last_commit = time.time()
        time.sleep(max(0.0, 15 - (time.time() - now.timestamp())))
    now = pd.Timestamp.now(tz="UTC")
    save_capital()
    led = save(led, now)
    if os.environ.get("P21_COMMIT") == "1":
        commit(now)
    print(summary(led, now))


if __name__ == "__main__":
    run()

"""Round 58f (PROTOCOL_ROUND58.md): live paper forward test of the mention-market word-record rule.

Each run:
1. refresh the settlement history of traded Mentions series;
2. settle open paper trades;
3. decide ONCE per open market, at the first scan at least 1 h after it opened, mirroring the backtest's "first ask after open + 1 h".
   The prior uses only settlements before now. Buy YES if prior - yes_ask >= 0.30; buy NO if (1 - prior) - no_ask >= 0.30.
"""
from __future__ import annotations
import math, os, re, subprocess, time
import numpy as np, pandas as pd

from edge import round20 as r20, round27 as r27, lip
from edge import weather as wx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HIST = os.path.join(ROOT, "paper", "r58f_history.csv")
DEC = os.path.join(ROOT, "paper", "r58f_decisions.csv")
REPORT = os.path.join(ROOT, "paper", "ROUND58F.md")
EDGE, NMIN, START = 0.30, 3, pd.Timestamp("2026-11-19 02:40", tz="UTC")
TOP_SERIES = int(os.environ.get("R58F_SERIES", "80"))


def wkey(s):
    return re.sub(r"\s+", "", str(s or "").lower())


def fee(x):
    return math.ceil(0.07 * x * (1 - x) * 100 - 1e-9) / 100


def get(path, params=None):
    r = wx._get(f"{wx.KALSHI}/{path}", params)
    return r.json() if r is not None and r.status_code == 200 else None


def series_list():
    S = pd.read_csv(os.path.join(ROOT, "probe", "mention", "series.csv"))
    return list(S[S.volume > 0].sort_values("volume", ascending=False).ticker.head(TOP_SERIES))


def row(s, m):
    return dict(series=s, ticker=m["ticker"], event=m.get("event_ticker"), word=wkey(m.get("yes_sub_title")),
                close=m.get("close_time"), y=1.0 if m.get("result") == "yes" else 0.0)


def refresh_history(ser):
    now = pd.Timestamp.now(tz="UTC")
    if os.path.exists(HIST):
        H = pd.read_csv(HIST)
        a = pd.to_datetime(H.close, utc=True, format="ISO8601").max() - pd.Timedelta(days=3)
        new = [row(s, m) for s in ser for m in r27.settled_markets(s, a, now + pd.Timedelta(days=1), max_pages=5)]
    else:                                  # first run: full history from the live + historical endpoints
        H = pd.DataFrame()
        new = [row(s, m) for s in ser for m in r20.markets(s, pd.Timestamp("2025-01-01", tz="UTC"), now + pd.Timedelta(days=1))]
    H = pd.concat([H, pd.DataFrame(new)], ignore_index=True).drop_duplicates("ticker", keep="last")
    H.to_csv(HIST, index=False)
    return H


def prior(H, series, word, now):
    h = H[(H.series == series) & (H.word == word) & (pd.to_datetime(H.close, utc=True, format="ISO8601") < now)]
    return len(h), (h.y.sum() + 1) / (len(h) + 2)


def settle(D):
    for i, r in D[(D.action != "pass") & D.pnl.isna()].iterrows():
        m = (get(f"markets/{r.ticker}") or {}).get("market", {})
        if m.get("result") in ("yes", "no"):
            won = (m["result"] == r.action)
            D.loc[i, "pnl"] = (1.0 if won else 0.0) - r.px - fee(r.px)
            D.loc[i, "result"] = m["result"]
    return D


def scan(H, D, ser, now):
    decided = set(D.ticker)
    rows = []
    for s in ser:
        cursor = None
        for _ in range(5):
            p = {"series_ticker": s, "status": "open", "limit": 1000}
            if cursor: p["cursor"] = cursor
            j = get("markets", p) or {}
            for m in j.get("markets", []):
                if m["ticker"] in decided: continue
                opened = pd.Timestamp(m.get("open_time"))
                if opened + pd.Timedelta(hours=1) > now or opened < START - pd.Timedelta(hours=1): continue   # new markets only
                n, pr = prior(H, s, wkey(m.get("yes_sub_title")), now)
                ya = lip.fnum(m.get("yes_ask_dollars"), np.nan); yb = lip.fnum(m.get("yes_bid_dollars"), np.nan)
                na = 1 - yb if yb == yb and yb > 0 else np.nan
                act, px = "pass", np.nan
                if n >= NMIN:
                    if ya == ya and 0.01 <= ya <= 0.99 and pr - ya >= EDGE: act, px = "yes", ya
                    elif na == na and 0.01 <= na <= 0.99 and (1 - pr) - na >= EDGE: act, px = "no", na
                rows.append(dict(time=now.isoformat(), series=s, ticker=m["ticker"], event=m.get("event_ticker"), word=wkey(m.get("yes_sub_title")),
                                 n=n, prior=round(pr, 3), yes_ask=ya, no_ask=na, action=act, px=px, pnl=np.nan, result=""))
                decided.add(m["ticker"])
            cursor = j.get("cursor")
            if not cursor or not j.get("markets"): break
    return pd.concat([D, pd.DataFrame(rows)], ignore_index=True) if rows else D


def report(D, now):
    T = D[D.action != "pass"]; S = T.dropna(subset=["pnl"])
    lines = ["# Round 58f: live paper forward test, mention markets vs word record", "",
             f"Updated {now:%Y-%m-%d %H:%M} UTC. Rules: [PROTOCOL_ROUND58.md](../PROTOCOL_ROUND58.md) (58f). 1 contract per trade, taker fee. Started {START:%Y-%m-%d}; verdict after 30 days.", "",
             f"Markets decided: {len(D)}; trades: {len(T)} (YES {int((T.action == 'yes').sum())}, NO {int((T.action == 'no').sum())}); settled: {len(S)}."]
    if len(S):
        g = S.groupby("event").pnl.sum()
        t = g.mean() / g.std() * math.sqrt(len(g)) if len(g) > 2 and g.std() > 0 else float("nan")
        lines += ["", f"**Settled P&L: ${S.pnl.sum():+.2f} on {len(S)} contracts, mean {S.pnl.mean():+.3f} $/contract, event-clustered t {t:.2f}, win rate {(S.pnl > 0).mean():.0%}.**", "",
                  S.groupby("series").pnl.agg(["count", "mean", "sum"]).sort_values("count", ascending=False).head(15).round(3).to_markdown()]
    open(REPORT, "w").write("\n".join(lines) + "\n")


def commit(now):
    for c in (["git", "add", HIST, DEC, REPORT], ["git", "commit", "-q", "-m", f"round58f: mention ledger {now:%Y-%m-%dT%H:%MZ} [skip ci]"],
              ["git", "pull", "--rebase", "-q"], ["git", "push", "-q"]):
        try:
            if subprocess.run(c, cwd=ROOT, timeout=120).returncode != 0 and c[1] == "commit": return
        except subprocess.TimeoutExpired:
            return


def run():
    """Loop for R58F_SECONDS (default 5 h 40 m), one cycle every 30 minutes, so a self-chaining workflow keeps it running."""
    t0 = time.time(); secs = int(os.environ.get("R58F_SECONDS", "0"))
    while True:
        try:
            run_once()
        except Exception as e:
            print("cycle failed:", repr(e), flush=True)
        if time.time() - t0 + 1800 > secs:
            break
        time.sleep(1800)


def run_once():
    now = pd.Timestamp.now(tz="UTC"); ser = series_list()
    H = refresh_history(ser); print("history rows", len(H), flush=True)
    D = pd.read_csv(DEC) if os.path.exists(DEC) else pd.DataFrame(columns=["time", "series", "ticker", "event", "word", "n", "prior", "yes_ask", "no_ask", "action", "px", "pnl", "result"])
    D = settle(D)
    D = scan(H, D, ser, pd.Timestamp.now(tz="UTC"))
    D.to_csv(DEC, index=False)
    report(D, pd.Timestamp.now(tz="UTC")); print(open(REPORT).read(), flush=True)
    if os.environ.get("R58F_COMMIT") == "1": commit(pd.Timestamp.now(tz="UTC"))


if __name__ == "__main__":
    run()

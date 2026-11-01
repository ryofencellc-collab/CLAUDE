"""Round 23 portfolio accounting (PROTOCOL_PORTFOLIO.md): sleeves A (Kalshi crypto), B (Round 13), C (football),
combined from their live ledgers with the pre-registered risk engine. Writes paper/PORTFOLIO.md."""
from pathlib import Path

import pandas as pd

from edge import paper21

ROOT = Path(__file__).resolve().parent.parent / "paper"
START, END = pd.Timestamp("2026-11-01"), pd.Timestamp("2026-12-01")
A_SIZE, A_HALF, B_CAPITAL = 2500.0, 1250.0, 4000.0
DAY_STOP, DD_HALF, DD_STOP = -500.0, -0.15, -0.25
BANKROLL = 10000.0


def sleeve_a_fills() -> pd.DataFrame:
    f = paper21._read(paper21.FILLS, paper21.COLS)
    f = f[f["series"].str.endswith("15M") & f["status"].isin(["won", "lost"])].copy()
    if f.empty:
        return f
    f["close"] = pd.to_datetime(f["close_utc"], utc=True).dt.tz_convert(None)
    f["excess"] = (f["seen"].astype(float) - pd.to_numeric(f["queue_ahead"], errors="coerce").fillna(0)).clip(lower=0)
    f = f[(f["close"] >= START) & (f["close"] < END) & (f["excess"] > 0)]
    return f.sort_values("close")


def sleeve_b() -> pd.Series:
    path = ROOT / "r13_ledger.csv"
    if not path.exists():
        return pd.Series(dtype=float)
    d = pd.read_csv(path)
    d["date"] = pd.to_datetime(d["date"], format="mixed").dt.normalize()
    d = d[(d["date"] >= START) & (d["date"] < END)]
    return d.set_index("date")["day_return"].astype(float)


def sleeve_c() -> pd.Series:
    path = ROOT / "bets.csv"
    if not path.exists():
        return pd.Series(dtype=float)
    b = pd.read_csv(path)
    b = b[b["status"].isin(["won", "lost"])].copy()
    b["day"] = pd.to_datetime(b["settled_at_utc"], utc=True).dt.tz_convert(None).dt.normalize()
    b = b[(b["day"] >= START) & (b["day"] < END)]
    return b.groupby("day")["pnl"].sum().astype(float)


def book() -> tuple[pd.DataFrame, list[str]]:
    """Day-by-day P&L per sleeve after the risk engine. Returns (table, notes on rules that fired)."""
    a, b_ret, c = sleeve_a_fills(), sleeve_b(), sleeve_c()
    days = sorted(set(a["close"].dt.normalize()) if len(a) else set()) + []
    days = sorted(set(days) | set(b_ret.index) | set(c.index))
    notes, rows = [], []
    equity, peak, b_eq = BANKROLL, BANKROLL, B_CAPITAL
    a_pause_until, a_half_until, stopped = pd.Timestamp.min, pd.Timestamp.min, False
    for d in days:
        if stopped:
            break
        scale = 0.5 if (equity / peak - 1) <= DD_HALF else 1.0
        day_a, day_total = 0.0, 0.0
        for _, x in (a[a["close"].dt.normalize() == d].iterrows() if len(a) else []):
            if x["close"] < a_pause_until or day_total <= DAY_STOP:
                continue
            size = (A_HALF if x["close"] < a_half_until else A_SIZE) * scale
            n = min(size, x["excess"])
            right = x["status"] == "won"
            pnl = n * ((1.0 if right else 0.0) - paper21.BID) - paper21.r15._maker_fee(n, paper21.BID)
            day_a += pnl
            day_total += pnl
            if not right:
                a_pause_until = x["close"] + pd.Timedelta(hours=24)
                a_half_until = a_pause_until + pd.Timedelta(days=7)
                notes.append(f"{x['close']:%Y-%m-%d %H:%M} A: losing fill on {x['ticker']} (${pnl:,.2f}); A paused 24 h, then half size 7 days")
        day_b = b_eq * b_ret.get(d, 0.0) * scale
        b_eq += day_b
        day_c = c.get(d, 0.0) * scale
        total = day_a + day_b + day_c
        equity += total
        peak = max(peak, equity)
        if total <= DAY_STOP:
            notes.append(f"{d:%Y-%m-%d}: daily stop hit (${total:,.2f})")
        if equity / peak - 1 <= DD_STOP:
            notes.append(f"{d:%Y-%m-%d}: drawdown {equity / peak - 1:.1%}, everything stopped")
            stopped = True
        rows.append(dict(day=d.date(), A=day_a, B=day_b, C=day_c, total=total, equity=equity,
                         drawdown=equity / peak - 1, half_size=scale < 1))
    return pd.DataFrame(rows), notes


def summary(now: pd.Timestamp | None = None) -> str:
    now = now or pd.Timestamp.now(tz="UTC")
    t, notes = book()
    lines = ["# Round 23 live paper portfolio: three unrelated edges with a risk engine", "",
             f"Updated {now:%Y-%m-%d %H:%M} UTC. Rules: [PROTOCOL_PORTFOLIO.md](../PROTOCOL_PORTFOLIO.md). "
             f"$10,000 paper: A $5,000 Kalshi crypto (2,500 contracts/market), B $4,000 Round 13, C $1,000 football.", ""]
    if t.empty:
        return "\n".join(lines + ["No P&L in the window yet."]) + "\n"
    active = t[(t[["A", "B", "C"]].abs().sum(axis=1)) > 0]
    pos = sum(t[s].sum() > 0 for s in "ABC")
    checks = {"profit >= $1,500": t["total"].sum() >= 1500, "max drawdown <= 15%": t["drawdown"].min() >= -0.15,
              "green on >= 60% of active days": len(active) > 0 and (active["total"] > 0).mean() >= 0.6,
              ">= 2 of 3 sleeves positive": pos >= 2}
    lines += ["| | |", "|---|---|",
              f"| **Portfolio profit** | **${t['total'].sum():+,.2f}** (equity ${t['equity'].iloc[-1]:,.2f}) |",
              f"| By sleeve | A ${t['A'].sum():+,.2f} · B ${t['B'].sum():+,.2f} · C ${t['C'].sum():+,.2f} |",
              f"| Days with P&L | {len(active)} (green {(active['total'] > 0).mean() if len(active) else 0:.0%}) |",
              f"| Max drawdown | {t['drawdown'].min():.1%} |", "",
              "| Check (judged on 2026-11-30) | So far |", "|---|---|"] + \
             [f"| {k} | {'yes' if v else 'not yet'} |" for k, v in checks.items()] + \
             ["", "| Day | A | B | C | Total | Equity |", "|---|---:|---:|---:|---:|---:|"] + \
             [f"| {r.day} | {r.A:+.2f} | {r.B:+.2f} | {r.C:+.2f} | **{r.total:+.2f}** | {r.equity:,.2f} |" for r in t.itertuples()]
    lines += ["", "Risk rules that fired: " + ("none" if not notes else "")] + [f"- {n}" for n in notes]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    (ROOT / "PORTFOLIO.md").write_text(summary())
    print(summary())

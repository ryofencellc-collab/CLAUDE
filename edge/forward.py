"""Round 3 forward paper trader for the football value-betting rule.

Runs on a schedule (see .github/workflows/paper.yml). Each run:
  1. reads the live upcoming-fixtures odds feed (football-data.co.uk/fixtures.csv),
  2. logs any new qualifying bet for a match that has not kicked off yet,
  3. settles open bets once the result appears in the season results files,
  4. rewrites paper/SUMMARY.md.

paper/bets.csv is append-only for new bets; settlement only fills in the
result columns. Git history timestamps every bet before its kickoff.
"""
import io
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from edge.betting import DIVS, SIDES

ROOT = Path(__file__).resolve().parent.parent / "paper"
ROOT.mkdir(exist_ok=True)
LEDGER = ROOT / "bets.csv"
FIXTURES = "https://www.football-data.co.uk/fixtures.csv"
RESULTS = "https://www.football-data.co.uk/mmz4281/{season}/{div}.csv"
EDGE, CAP, STAKE, BANK = 0.02, 5.0, 10.0, 1000.0  # frozen in PROTOCOL_ROUND3.md
MIN_LEAD = pd.Timedelta(minutes=30)                # bet must be logged >= 30 min before kickoff
COLS = ["bet_id", "logged_at_utc", "kickoff_uk", "div", "home", "away", "side", "odds",
        "betfair_odds", "fair_odds", "edge", "b365_odds", "stake", "status", "pnl", "settled_at_utc"]
UA = {"User-Agent": "Mozilla/5.0"}


def _csv(url):
    r = requests.get(url, timeout=60, headers=UA)
    r.raise_for_status()
    return pd.read_csv(io.BytesIO(r.content), encoding="latin-1", on_bad_lines="skip")


def _num(df, col):
    return pd.to_numeric(df[col], errors="coerce") if col in df else pd.Series(np.nan, index=df.index)


def ledger() -> pd.DataFrame:
    if LEDGER.exists():
        led = pd.read_csv(LEDGER, dtype={"bet_id": str, "status": str, "settled_at_utc": str})
        led["settled_at_utc"] = led["settled_at_utc"].fillna("")
        led["pnl"] = led["pnl"].astype(float)
        return led
    return pd.DataFrame(columns=COLS)


def find_bets(fx: pd.DataFrame, now: pd.Timestamp) -> pd.DataFrame:
    fx = fx[fx["Div"].isin(DIVS)].copy()
    kick = pd.to_datetime(fx["Date"] + " " + fx["Time"].fillna("15:00"), dayfirst=True, errors="coerce")
    fx["kickoff"] = kick.dt.tz_localize("Europe/London", ambiguous="NaT", nonexistent="NaT")
    fx = fx[fx["kickoff"] > now + MIN_LEAD]
    ps = {s: _num(fx, f"BFE{s}") for s in SIDES}  # Betfair Exchange = sharp reference
    overround = sum(1 / ps[s] for s in SIDES)
    out = []
    for s in SIDES:
        fair = ps[s] * overround
        best = _num(fx, f"Max{s}")
        pick = (best >= fair * (1 + EDGE)) & (best <= CAP)
        b = fx[pick]
        out.append(pd.DataFrame({
            "kickoff_uk": b["kickoff"].dt.strftime("%Y-%m-%d %H:%M"), "div": b["Div"],
            "home": b["HomeTeam"], "away": b["AwayTeam"], "side": s, "odds": best[pick],
            "betfair_odds": ps[s][pick], "fair_odds": fair[pick].round(3),
            "edge": (best[pick] / fair[pick] - 1).round(4), "b365_odds": _num(fx, f"B365{s}")[pick]}))
    new = pd.concat(out, ignore_index=True)
    new["bet_id"] = new["kickoff_uk"].str[:10] + "|" + new["div"] + "|" + new["home"] + "|" + \
        new["away"] + "|" + new["side"]
    return new


def settle(led: pd.DataFrame, now: pd.Timestamp) -> pd.DataFrame:
    open_ = led["status"] == "open"
    if not open_.any():
        return led
    kick = pd.to_datetime(led["kickoff_uk"])
    season_of = lambda d: f"{d.year % 100:02d}{(d.year + 1) % 100:02d}" if d.month >= 7 else \
        f"{(d.year - 1) % 100:02d}{d.year % 100:02d}"
    need = {(season_of(k), dv) for k, dv in zip(kick[open_], led.loc[open_, "div"])}
    results = {}
    for season, dv in need:
        try:
            r = _csv(RESULTS.format(season=season, div=dv))
        except requests.RequestException:
            continue
        r["d"] = pd.to_datetime(r["Date"], dayfirst=True, errors="coerce").dt.strftime("%Y-%m-%d")
        for _, row in r.dropna(subset=["FTR"]).iterrows():
            results[(row["d"], dv, row["HomeTeam"], row["AwayTeam"])] = row["FTR"]
    for i in led.index[open_]:
        if kick[i] > now.tz_convert("Europe/London").tz_localize(None):
            continue  # not played yet
        key = (led.at[i, "kickoff_uk"][:10], led.at[i, "div"], led.at[i, "home"], led.at[i, "away"])
        ftr = results.get(key)
        if ftr is None:
            if now.tz_localize(None) - kick[i] > pd.Timedelta(days=14):
                led.loc[i, ["status", "pnl", "settled_at_utc"]] = ["void", 0.0, now.isoformat()]
            continue
        won = ftr == led.at[i, "side"]
        led.loc[i, "status"] = "won" if won else "lost"
        led.loc[i, "pnl"] = round(STAKE * (float(led.at[i, "odds"]) - 1), 2) if won else -STAKE
        led.loc[i, "settled_at_utc"] = now.isoformat()
    return led


def summary(led: pd.DataFrame, now: pd.Timestamp) -> str:
    s = led[led["status"].isin(["won", "lost"])].copy()
    pnl = s["pnl"].astype(float)
    staked = len(s) * STAKE
    lines = [
        "# Round 3: live paper trading (football value bets)", "",
        f"Updated {now:%Y-%m-%d %H:%M} UTC. Rule frozen in [PROTOCOL_ROUND3.md](../PROTOCOL_ROUND3.md). "
        f"Paper bankroll ${BANK:,.0f}, flat ${STAKE:.0f} stakes.", "",
        "| | |", "|---|---|",
        f"| Bets logged | {len(led)} |",
        f"| Open (not yet played) | {int((led['status'] == 'open').sum())} |",
        f"| Settled | {len(s)} (won {int((s['status'] == 'won').sum())}, lost {int((s['status'] == 'lost').sum())}) |",
        f"| Win rate | {(s['status'] == 'won').mean():.1%} |" if len(s) else "| Win rate | n/a |",
        f"| Staked | ${staked:,.0f} |",
        f"| **Profit** | **${pnl.sum():+,.2f}** |",
        f"| ROI | {pnl.sum() / staked:+.2%} |" if staked else "| ROI | n/a |",
        f"| Paper bankroll | ${BANK + pnl.sum():,.2f} |", "",
    ]
    if len(s):
        s["day"] = pd.to_datetime(s["kickoff_uk"]).dt.date
        daily = s.groupby("day")["pnl"].sum()
        lines += ["## By match day", "", "| Day | Bets | P&L | Bankroll |", "|---|---:|---:|---:|"]
        eq = BANK
        for d, g in s.groupby("day"):
            eq += g["pnl"].sum()
            lines.append(f"| {d} | {len(g)} | ${g['pnl'].sum():+.2f} | ${eq:,.2f} |")
        lines += ["", f"Green days: {(daily > 0).sum()} of {len(daily)}"]
    return "\n".join(lines) + "\n"


def run(now: pd.Timestamp | None = None):
    now = now or pd.Timestamp.now(tz="UTC")
    led = ledger()
    fx = _csv(FIXTURES)
    new = find_bets(fx, now)
    new = new[~new["bet_id"].isin(led["bet_id"])]
    if len(new):
        new = new.assign(logged_at_utc=now.isoformat(), stake=STAKE, status="open",
                         pnl=np.nan, settled_at_utc="")
        led = pd.concat([led, new[COLS]], ignore_index=True)
    led = settle(led, now)
    led[COLS].to_csv(LEDGER, index=False)
    (ROOT / "SUMMARY.md").write_text(summary(led, now))
    print(f"logged {len(new)} new bets; ledger {len(led)}; open {(led['status'] == 'open').sum()}")


if __name__ == "__main__":
    run()

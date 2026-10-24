"""Dollar P&L of the football lead (value_vs_pinnacle, edge >= 2%, odds <= 5).

Diagnostic, not a new trial: the config is the one already reported in
reports/ROUND2.md. Bankroll $1,000, flat $10 stakes (1%).

Realism checks:
  * same rule, but only betting at ONE named bookmaker (no 40-account shopping)
  * ROI by odds bucket
"""
import io

import numpy as np
import pandas as pd
import requests

from edge import betting as bt

STAKE, BANK, EDGE, CAP = 10.0, 1000.0, 0.02, 5.0
BOOKS = ["B365", "BW", "IW", "WH", "VC"]  # Bet365, Bwin, Interwetten, William Hill, BetVictor


def _one(job):
    s, d = job
    r = requests.get(f"https://www.football-data.co.uk/mmz4281/{s}/{d}.csv", timeout=30,
                     headers={"User-Agent": "Mozilla/5.0"})
    if r.status_code != 200 or len(r.content) < 200:
        return None
    df = pd.read_csv(io.BytesIO(r.content), encoding="latin-1", on_bad_lines="skip")
    return df.assign(season=s, div=d)


def raw_matches():
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(8) as ex:
        rows = [x for x in ex.map(_one, [(s, d) for s in bt.SEASONS for d in bt.DIVS]) if x is not None]
    df = pd.concat(rows, ignore_index=True)
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    return df


def bets(df, price_cols, ref="PS"):
    out = []
    for side in bt.SIDES:
        ps = {x: pd.to_numeric(df[f"{ref}{x}"], errors="coerce") for x in bt.SIDES}
        book = sum(1 / ps[x] for x in bt.SIDES)
        if ref == "BFE":
            book = book.where(book.between(0.97, 1.06))  # amendment 1: drop junk exchange prices
        fair = ps[side] * book
        px = pd.to_numeric(df[price_cols[side]], errors="coerce") if price_cols[side] in df else np.nan
        pick = (px >= fair * (1 + EDGE)) & (px <= CAP)
        b = df[pick]
        out.append(pd.DataFrame({"date": b["Date"], "season": b["season"], "odds": px[pick],
                                 "won": (b["FTR"] == side), "key": b["div"] + b["HomeTeam"].astype(str)
                                 + b["AwayTeam"].astype(str) + b["season"] + side}))
    o = pd.concat(out).dropna(subset=["date"]).sort_values("date")
    o["pnl"] = np.where(o["won"], STAKE * (o["odds"] - 1), -STAKE)
    return o


def summarize(o, label):
    eq = BANK + o["pnl"].cumsum()
    return dict(strategy=label, bets=len(o), staked=len(o) * STAKE, profit=o["pnl"].sum(),
                roi=o["pnl"].sum() / (len(o) * STAKE) if len(o) else 0.0,
                win_rate=o["won"].mean() if len(o) else 0.0,
                max_drawdown=(eq - eq.cummax()).min() if len(o) else 0.0)


def main():
    df = raw_matches()
    for s in bt.SIDES:
        df[f"best{s}"] = pd.to_numeric(df.get(f"Max{s}"), errors="coerce").fillna(
            pd.to_numeric(df.get(f"BbMx{s}"), errors="coerce"))
    best = bets(df, {s: f"best{s}" for s in bt.SIDES})
    hold = best[best["season"] >= bt.HOLDOUT_FROM]

    print("=== Best-price rule, $10 flat stakes, by season ===")
    rows = []
    for season, g in best.groupby("season"):
        rows.append(dict(season=season, bets=len(g), profit=g["pnl"].sum(),
                         roi=g["pnl"].sum() / (len(g) * STAKE), win_rate=g["won"].mean(),
                         avg_odds=g["odds"].mean()))
    print(pd.DataFrame(rows).round(3).to_markdown(index=False))

    print("\n=== Totals ===")
    print(pd.DataFrame([summarize(best, "best price, all seasons"),
                        summarize(hold, "best price, holdout 2022/23+")]).round(3).to_markdown(index=False))

    print("\n=== Holdout by month: share of months profitable ===")
    m = hold.groupby(hold["date"].dt.to_period("M"))["pnl"].sum()
    print(f"months={len(m)} profitable={int((m > 0).sum())} ({(m > 0).mean():.0%}) "
          f"best=${m.max():.0f} worst=${m.min():.0f} median=${m.median():.0f}")

    print("\n=== Realism: one bookmaker only (holdout) ===")
    rows = []
    for b in BOOKS:
        o = bets(df, {s: f"{b}{s}" for s in bt.SIDES})
        rows.append(summarize(o[o["season"] >= bt.HOLDOUT_FROM], b))
    print(pd.DataFrame(rows).round(3).to_markdown(index=False))

    print("\n=== Holdout ROI by odds bucket (best price) ===")
    hold = hold.assign(bucket=pd.cut(hold["odds"], [1, 1.5, 2, 2.5, 3, 4, 5]))
    print(hold.groupby("bucket", observed=True).agg(bets=("pnl", "size"), profit=("pnl", "sum"),
                                                     win_rate=("won", "mean")).round(3).to_markdown())

    # per-bet sd for the paper-trading band
    r = hold["pnl"] / STAKE
    print(f"\nholdout per-bet return: mean={r.mean():.4f} sd={r.std():.4f} n={len(r)} "
          f"bets_per_season={len(r) / hold['season'].nunique():.0f}")


if __name__ == "__main__":
    main()

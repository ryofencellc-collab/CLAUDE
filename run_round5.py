"""Round 5 runner (PROTOCOL_ROUND5.md): Kalshi weather markets."""
import json

import numpy as np
import pandas as pd

from edge import weather as wx
from edge.betting import bootstrap_p
from run_round2 import REPORTS, fmt

CUMULATIVE_TRIALS = 177


def stats(b):
    if b is None or not len(b):
        return dict(bets=0, roi=np.nan, profit=0.0, win_rate=np.nan, green_days=np.nan, max_dd=0.0)
    daily = b.groupby("date")["pnl"].sum()
    eq = daily.cumsum()
    return dict(bets=len(b), roi=b["pnl"].sum() / (len(b) * wx.STAKE), profit=b["pnl"].sum(),
                win_rate=b["won"].mean(), green_days=(daily > 0).mean(), max_dd=(eq - eq.cummax()).min(),
                avg_price=b["price"].mean())


def main():
    df = wx.dataset(refresh=True)
    print(f"rows {len(df)}, cities {df['city'].nunique()}, days {df['date'].nunique()}, "
          f"quoted {df['ask'].notna().sum()}, with forecast {df['forecast'].notna().sum()}")
    cut = df["date"].max() - pd.Timedelta(days=wx.HOLDOUT_DAYS)
    is_df, ho_df = df[df["date"] <= cut], df[df["date"] > cut]
    calib = wx.calibrate(is_df)
    print("calibration (bias, sd) per city:", {k: (round(a, 2), round(s, 2)) for k, (a, s) in calib.items()})

    rows, keep = [], {}
    for params in wx.GRID:
        bi, bo = wx.bets(is_df, calib, **params), wx.bets(ho_df, calib, **params)
        si, so = stats(bi), stats(bo)
        row = dict(params=json.dumps(params), **{f"is_{k}": v for k, v in si.items()},
                   **{f"oos_{k}": v for k, v in so.items()},
                   oos_p=bootstrap_p(bo["pnl"] / wx.STAKE) if len(bo) > 1 else 1.0)
        rows.append(row)
        keep[row["params"]] = bo
        print(row, flush=True)
    t = pd.DataFrame(rows)
    best = t.loc[t["is_roi"].idxmax()]
    p_adj = min(1.0, best["oos_p"] * CUMULATIVE_TRIALS)
    checks = {"oos_roi>0": best["oos_roi"] > 0, "p_adj<0.05": p_adj < 0.05,
              "is_roi>0": best["is_roi"] > 0, "evidence": best["oos_bets"] >= 300}
    verdict = pd.DataFrame([dict(params=best["params"], is_roi=best["is_roi"], is_bets=best["is_bets"],
                                 oos_roi=best["oos_roi"], oos_bets=best["oos_bets"],
                                 oos_profit=best["oos_profit"], oos_win_rate=best["oos_win_rate"],
                                 oos_green_days=best["oos_green_days"], p_adjusted=p_adj,
                                 passed=all(checks.values()),
                                 failed=", ".join(k for k, v in checks.items() if not v))])
    bo = keep[best["params"]]
    by_city = bo.groupby("city").agg(bets=("pnl", "size"), profit=("pnl", "sum"),
                                     win_rate=("won", "mean")).reset_index() if len(bo) else pd.DataFrame()
    md = ["## Round 5: Kalshi daily-high temperature markets", "",
          f"Markets: {len(df):,} settled contracts, {df['city'].nunique()} cities, "
          f"{df['date'].min().date()} → {df['date'].max().date()}. Holdout = after {cut.date()}.", "",
          fmt(verdict), "", "All trials ($10 per bet):", "", fmt(t), "",
          "Selected config, holdout by city:", "", fmt(by_city) if len(by_city) else "(no bets)"]
    t.to_csv(REPORTS / "round5_trials.csv", index=False)
    (REPORTS / "round5.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()

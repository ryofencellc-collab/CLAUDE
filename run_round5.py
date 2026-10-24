"""Round 5 runner (PROTOCOL_ROUND5.md + amendments): Kalshi weather markets.

4 combinations: forecast {gfs, multi} x universe {major, minor}, 6 configs each.
gfs x major is the original pre-registered test.
"""
import json

import numpy as np
import pandas as pd

from edge import weather as wx
from edge.betting import bootstrap_p
from run_round2 import REPORTS, fmt

CUMULATIVE_TRIALS = 195


def stats(b):
    if b is None or not len(b):
        return dict(bets=0, roi=np.nan, profit=0.0, win_rate=np.nan, green_days=np.nan, max_dd=0.0)
    daily = b.groupby("date")["pnl"].sum()
    eq = daily.cumsum()
    return dict(bets=len(b), roi=b["pnl"].sum() / (len(b) * wx.STAKE), profit=b["pnl"].sum(),
                win_rate=b["won"].mean(), green_days=(daily > 0).mean(), max_dd=(eq - eq.cummax()).min())


def main():
    import sys
    df = wx.dataset(refresh='--refresh' in sys.argv)
    print(f"rows {len(df)}, cities {df['city'].nunique()}, days {df['date'].nunique()}, "
          f"quoted {df['ask'].notna().sum()}, gfs {df['gfs'].notna().sum()}, multi {df['multi'].notna().sum()}")
    cut = df["date"].max() - pd.Timedelta(days=wx.HOLDOUT_DAYS)
    rows, verdicts, keep = [], [], {}
    for fc in ("gfs", "multi"):
        for tier in ("major", "minor"):
            d = df[df["tier"] == tier]
            is_df, ho_df = d[d["date"] <= cut], d[d["date"] > cut]
            calib = wx.calibrate(is_df, fc)
            err = {k: (round(a, 2), round(s, 2)) for k, (a, s) in calib.items()}
            print(f"[{fc} x {tier}] calibration (bias, sd): {err}", flush=True)
            combo = []
            for params in wx.GRID:
                bi, bo = wx.bets(is_df, calib, fc=fc, **params), wx.bets(ho_df, calib, fc=fc, **params)
                row = dict(forecast=fc, universe=tier, params=json.dumps(params),
                           **{f"is_{k}": v for k, v in stats(bi).items()},
                           **{f"oos_{k}": v for k, v in stats(bo).items()},
                           oos_p=bootstrap_p(bo["pnl"] / wx.STAKE) if len(bo) > 1 else 1.0)
                combo.append(row)
                keep[(fc, tier, row["params"])] = bo
                print(row, flush=True)
            rows += combo
            t = pd.DataFrame(combo)
            if t["is_roi"].isna().all():
                verdicts.append(dict(forecast=fc, universe=tier, passed=False, failed="no in-sample bets"))
                continue
            b = t.loc[t["is_roi"].idxmax()]
            p_adj = min(1.0, b["oos_p"] * CUMULATIVE_TRIALS)
            checks = {"oos_roi>0": b["oos_roi"] > 0, "p_adj<0.05": p_adj < 0.05,
                      "is_roi>0": b["is_roi"] > 0, "evidence": b["oos_bets"] >= 300}
            verdicts.append(dict(forecast=fc, universe=tier, params=b["params"], is_roi=b["is_roi"],
                                 is_bets=b["is_bets"], oos_roi=b["oos_roi"], oos_bets=b["oos_bets"],
                                 oos_profit=b["oos_profit"], oos_win_rate=b["oos_win_rate"],
                                 oos_green_days=b["oos_green_days"], p_adjusted=p_adj,
                                 passed=all(checks.values()),
                                 failed=", ".join(k for k, v in checks.items() if not v)))
    t = pd.DataFrame(rows)
    v = pd.DataFrame(verdicts)
    md = ["## Round 5: Kalshi daily-high temperature markets", "",
          f"{len(df):,} settled contracts, {df['city'].nunique()} cities "
          f"({df[df.tier == 'major'].city.nunique()} major, {df[df.tier == 'minor'].city.nunique()} minor), "
          f"{df['date'].min().date()} → {df['date'].max().date()}. Holdout = after {cut.date()}. $10 per bet.", "",
          "### Verdicts (each combination picks its config on in-sample ROI)", "", fmt(v), "",
          "### All 24 trials", "", fmt(t)]
    t.to_csv(REPORTS / "round5_trials.csv", index=False)
    (REPORTS / "round5.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()

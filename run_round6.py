"""Round 6 runner (PROTOCOL_ROUND6.md): weekly cash-secured BTC puts."""
import json

import numpy as np
import pandas as pd

from edge import options as op
from edge.stats import deflated_sharpe
from run_round2 import REPORTS, fmt

CUMULATIVE_TRIALS = 199


def stats(r: pd.Series) -> dict:
    if len(r) < 2:
        return dict(weeks=len(r), sharpe=np.nan)
    eq = (1 + r).cumprod()
    return dict(weeks=len(r), sharpe=r.mean() / r.std() * np.sqrt(52), total=eq.iloc[-1] - 1,
                cagr=eq.iloc[-1] ** (52 / len(r)) - 1, max_dd=(eq / eq.cummax() - 1).min(),
                win_weeks=(r > 0).mean(), worst_week=r.min(), best_week=r.max(),
                usd_on_1000=1000 * (eq.iloc[-1] - 1))


def main():
    df = op.weekly_puts(refresh=True)
    spot = op._spot_8utc()
    print(f"put quotes: {len(df)} rows, {df['friday'].nunique()} Fridays "
          f"{df['friday'].min().date()}..{df['friday'].max().date()}")
    rows, keep = [], {}
    for params in op.GRID:
        w = op.sell_puts(df, spot, **params)
        is_r, oos_r = w.loc[w.index < op.HOLDOUT_FROM, "ret"], w.loc[w.index >= op.HOLDOUT_FROM, "ret"]
        row = dict(params=json.dumps(params), **{f"is_{k}": v for k, v in stats(is_r).items()},
                   **{f"oos_{k}": v for k, v in stats(oos_r).items()})
        rows.append(row)
        keep[row["params"]] = (w, oos_r)
        print(row, flush=True)
    t = pd.DataFrame(rows)
    b = t.loc[t["is_sharpe"].idxmax()]
    w, oos_r = keep[b["params"]]
    dsr = deflated_sharpe(oos_r, CUMULATIVE_TRIALS, 1 / len(oos_r))
    checks = {"oos_sharpe>=1": b["oos_sharpe"] >= 1, "dsr>=0.95": dsr >= 0.95, "is_sharpe>0": b["is_sharpe"] > 0,
              "max_dd<=25%": b["oos_max_dd"] >= -0.25, "evidence": b["oos_weeks"] >= 50}
    verdict = pd.DataFrame([dict(params=b["params"], is_sharpe=b["is_sharpe"], oos_sharpe=b["oos_sharpe"],
                                 oos_cagr=b["oos_cagr"], oos_max_dd=b["oos_max_dd"], oos_win_weeks=b["oos_win_weeks"],
                                 oos_worst_week=b["oos_worst_week"], dsr=dsr, passed=all(checks.values()),
                                 failed=", ".join(k for k, v in checks.items() if not v))])
    worst = w.nsmallest(8, "ret")[["strike", "spot", "settle", "premium_usd", "ret"]]
    yearly = w.groupby(w.index.year)["ret"].agg(weeks="size", total=lambda r: (1 + r).prod() - 1,
                                                win_weeks=lambda r: (r > 0).mean())
    md = ["## Round 6: sell a weekly BTC put", "", fmt(verdict), "", "All configs:", "", fmt(t), "",
          "Selected config by year:", "", yearly.round(3).to_markdown(), "",
          "Selected config, 8 worst weeks:", "", worst.round(4).to_markdown()]
    t.to_csv(REPORTS / "round6_trials.csv", index=False)
    (REPORTS / "round6.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()

"""Round 4 runner (PROTOCOL_ROUND4.md).

    python run_round4.py crowd   # crypto retail-positioning families
    python run_round4.py sweep   # NQ liquidity-sweep fade
"""
import json
import sys

import numpy as np
import pandas as pd

from edge.stats import deflated_sharpe
from run_round2 import REPORTS, fmt

CUMULATIVE_TRIALS = 171


def judge(rows, daily, dd_ok):
    out = []
    t = pd.DataFrame(rows)
    for fam, g in t.groupby("family", sort=False):
        b = g.loc[g["is_sharpe"].idxmax()]
        d = daily[(fam, b["params"])]
        dsr = deflated_sharpe(d, CUMULATIVE_TRIALS, 1 / len(d)) if d.std() > 0 else 0.0
        checks = {"oos_sharpe>=1": b["oos_sharpe"] >= 1, "dsr>=0.95": dsr >= 0.95,
                  "is_sharpe>0": b["is_sharpe"] > 0, "max_dd_ok": dd_ok(b),
                  "evidence": b["oos_trades"] >= 100}
        out.append({**{k: b[k] for k in b.index if k != "family"}, "family": fam, "dsr": dsr,
                    "passed": all(checks.values()),
                    "failed": ", ".join(k for k, v in checks.items() if not v)})
    return t, pd.DataFrame(out)


def part_crowd():
    from edge import crowd
    p = crowd.panel(refresh=True)
    rows, daily = [], {}
    for fam, (fn, grid) in crowd.FAMILIES.items():
        for params in grid:
            d, tr = fn(p, **params)
            row = dict(family=fam, params=json.dumps(params))
            for seg, dd, tt in (("is", d[d.index < crowd.HOLDOUT_FROM], tr[tr["time"] < crowd.HOLDOUT_FROM]),
                                ("oos", d[d.index >= crowd.HOLDOUT_FROM], tr[tr["time"] >= crowd.HOLDOUT_FROM])):
                eq = (1 + dd).cumprod()
                active = dd[dd != 0]
                row.update({f"{seg}_sharpe": dd.mean() / dd.std() * np.sqrt(365) if dd.std() > 0 else 0.0,
                            f"{seg}_total": eq.iloc[-1] - 1, f"{seg}_max_dd": (eq / eq.cummax() - 1).min(),
                            f"{seg}_trades": len(tt), f"{seg}_win_rate": (tt["ret"] > 0).mean(),
                            f"{seg}_green_days": (active > 0).mean()})
            daily[(fam, row["params"])] = d[d.index >= crowd.HOLDOUT_FROM]
            rows.append(row)
            print(row, flush=True)
    trials, verdict = judge(rows, daily, lambda b: b["oos_max_dd"] >= -0.25)
    return "\n".join(["## A. Crypto: trade against retail positioning", "",
                      f"Coins {crowd.COINS}; holdout from {crowd.HOLDOUT_FROM}.", "",
                      fmt(verdict), "", "All trials:", "", fmt(trials)]), trials


def part_sweep():
    from edge import intraday as it
    from run_round2 import null_bars
    bars = it.load_nq()
    days = bars.between_time("09:30", "15:59").index.normalize().unique()
    cut = "2022-12-31 23:59"

    def trials_for(b):
        rows, daily = [], {}
        for params in it.SWEEP_GRID:
            t = it.liquidity_sweep(b, **params)
            row = dict(family="liquidity_sweep", params=json.dumps(params))
            for seg, tt, dd in (("is", t[t["time"] <= cut], days[days <= cut]),
                                ("oos", t[t["time"] > cut], days[days > cut])):
                row.update({f"{seg}_{k}": v for k, v in it.trade_stats(tt, dd).items()})
            o = t[t["time"] > cut]
            daily[("liquidity_sweep", row["params"])] = o.groupby(o["time"].dt.normalize())["R"].sum() \
                .reindex(days[days > cut], fill_value=0.0)
            rows.append(row)
        return judge(rows, daily, lambda r: r["oos_max_dd_R"] >= -20)

    trials, verdict = trials_for(bars)
    print(trials.to_string(), flush=True)
    nulls = [int(trials_for(null_bars(bars, s))[1]["passed"].sum()) for s in range(2)]
    return "\n".join(["## B. Nasdaq-100: fade the prior-day liquidity sweep", "",
                      fmt(verdict), "", "All trials:", "", fmt(trials), "",
                      f"Null test passes (2 shuffled seeds): {nulls}"]), trials


if __name__ == "__main__":
    part = sys.argv[1]
    md, trials = {"crowd": part_crowd, "sweep": part_sweep}[part]()
    trials.to_csv(REPORTS / f"round4_{part}_trials.csv", index=False)
    (REPORTS / f"round4_{part}.md").write_text(md + "\n")
    print(md)

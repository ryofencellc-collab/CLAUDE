"""Round 2 runner (PROTOCOL_ROUND2.md). One part per invocation:

    python run_round2.py nq         # intraday Nasdaq: jj_fair_value, orb (+ null test)
    python run_round2.py football   # value_vs_pinnacle, favourite_bias
    python run_round2.py pm         # Polymarket favourite-longshot
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from edge.stats import deflated_sharpe

# Round 1 (61) + Round 2 families as pre-registered (84 + 9 + 6)
CUMULATIVE_TRIALS = 61 + 84 + 9 + 6
REPORTS = Path(__file__).resolve().parent / "reports"
REPORTS.mkdir(exist_ok=True)


def fmt(df):
    d = df.copy()
    for c in d.columns:
        if d[c].dtype == float:
            d[c] = d[c].map(lambda x: f"{x:.3f}")
    return d.to_markdown(index=False)


# ---------------------------------------------------------------- A. NQ intraday

def null_bars(b: pd.DataFrame, seed: int) -> pd.DataFrame:
    """Shuffle 1-minute returns and wicks in time: same volatility, no structure."""
    rng = np.random.default_rng(seed)
    r = np.log(b["close"]).diff().fillna(0).to_numpy()
    body_top, body_bot = np.maximum(b["open"], b["close"]), np.minimum(b["open"], b["close"])
    up, dn = (b["high"] - body_top).to_numpy(), (body_bot - b["low"]).to_numpy()
    perm = rng.permutation(len(b))
    r = r[perm] - r.mean()
    c = b["close"].iloc[0] * np.exp(np.cumsum(r))
    o = np.r_[c[0], c[:-1]]
    return pd.DataFrame({"open": o, "high": np.maximum(o, c) + up[perm],
                         "low": np.minimum(o, c) - dn[perm], "close": c}, index=b.index)


def nq_trials(bars):
    from edge import intraday as it
    days = bars.between_time("09:30", "15:59").index.normalize().unique()
    is_days, oos_days = days[days <= "2022-12-31"], days[days > "2022-12-31"]
    rows, oos_daily = [], {}
    for fam, (fn, grid) in it.FAMILIES.items():
        for params in grid:
            t = fn(bars, **params)
            seg = {"is": (t[t["time"] <= "2022-12-31 23:59"], is_days),
                   "oos": (t[t["time"] > "2022-12-31 23:59"], oos_days)}
            row = dict(family=fam, params=json.dumps(params))
            for k, (tt, dd) in seg.items():
                row.update({f"{k}_{m}": v for m, v in it.trade_stats(tt, dd).items()})
            key = row["params"]
            oos_t = seg["oos"][0]
            oos_daily[(fam, key)] = oos_t.groupby(oos_t["time"].dt.normalize())["R"].sum() \
                .reindex(oos_days, fill_value=0.0)
            rows.append(row)
            print(f"  {fam} {key}: IS sharpe {row['is_sharpe']:.2f} OOS sharpe {row['oos_sharpe']:.2f} "
                  f"OOS win {row['oos_win_rate']:.0%} trades {row['oos_trades']}", flush=True)
    return pd.DataFrame(rows), oos_daily


def nq_verdict(trials, oos_daily):
    out = []
    for fam, g in trials.groupby("family", sort=False):
        b = g.loc[g["is_sharpe"].idxmax()]
        d = oos_daily[(fam, b["params"])]
        dsr = deflated_sharpe(d, CUMULATIVE_TRIALS, 1 / len(d)) if d.std() > 0 else 0.0
        checks = {
            "oos_sharpe>=1": b["oos_sharpe"] >= 1.0,
            "dsr>=0.95": dsr >= 0.95,
            "is_sharpe>0": b["is_sharpe"] > 0,
            "max_dd<=20R": b["oos_max_dd_R"] >= -20,
            "evidence": b["oos_trades"] >= 100,
        }
        out.append(dict(family=fam, params=b["params"], is_sharpe=b["is_sharpe"],
                        oos_sharpe=b["oos_sharpe"], oos_trades=b["oos_trades"],
                        oos_win_rate=b["oos_win_rate"], oos_green_days=b["oos_green_days"],
                        oos_profit_factor=b["oos_profit_factor"], oos_avg_R=b["oos_avg_R"],
                        oos_total_R=b["oos_total_R"], oos_max_dd_R=b["oos_max_dd_R"], dsr=dsr,
                        passed=all(checks.values()),
                        failed=", ".join(k for k, v in checks.items() if not v)))
    return pd.DataFrame(out)


def part_nq():
    from edge import intraday as it
    bars = it.load_nq()
    print(f"NQ bars: {len(bars)} {bars.index.min()} -> {bars.index.max()}", flush=True)
    trials, oos_daily = nq_trials(bars)
    trials.to_csv(REPORTS / "round2_nq_trials.csv", index=False)
    verdict = nq_verdict(trials, oos_daily)

    sens = []
    for _, v in verdict.iterrows():
        fn = it.FAMILIES[v["family"]][0]
        for cost in (0.0, it.COST_PTS, 2.5):
            it_cost, it.COST_PTS = it.COST_PTS, cost
            try:
                t = fn(bars, **json.loads(v["params"]))
            finally:
                it.COST_PTS = it_cost
            t = t[t["time"] > "2022-12-31 23:59"]
            sens.append(dict(family=v["family"], cost_pts=cost, oos_avg_R=t["R"].mean(),
                             oos_win_rate=(t["R"] > 0).mean(), oos_total_R=t["R"].sum()))
    nulls = []
    for seed in range(2):
        nt, nd = nq_trials(null_bars(bars, seed))
        nv = nq_verdict(nt, nd)
        nulls.append(dict(seed=seed, passed=int(nv["passed"].sum()),
                          best_oos_sharpe=float(nv["oos_sharpe"].max())))
    md = ["## A. Intraday Nasdaq-100 (1-minute)", "",
          f"Bars: {len(bars):,} from {bars.index.min().date()} to {bars.index.max().date()}. "
          f"Trials: {len(trials)}. Costs {it.COST_PTS} pts round trip.", "",
          fmt(verdict), "", "Cost sensitivity (selected configs, holdout):", "",
          fmt(pd.DataFrame(sens)), "", "Null test (shuffled 1-min bars):", "",
          fmt(pd.DataFrame(nulls))]
    return "\n".join(md)


# ---------------------------------------------------------------- B. Football

def part_football():
    from edge import betting as bt
    df = bt.matches(refresh=True)
    rows = []
    for fam, (fn, grid) in bt.FAMILIES.items():
        for params in grid:
            b = fn(df, **params)
            is_b, oos_b = b[b["season"] < bt.HOLDOUT_FROM], b[b["season"] >= bt.HOLDOUT_FROM]
            rows.append(dict(family=fam, params=json.dumps(params),
                             is_bets=len(is_b), is_roi=is_b["ret"].mean(),
                             oos_bets=len(oos_b), oos_roi=oos_b["ret"].mean(),
                             oos_win_rate=(oos_b["ret"] > 0).mean(),
                             oos_p=bt.bootstrap_p(oos_b["ret"]), _oos=oos_b))
    trials = pd.DataFrame(rows)
    out = []
    for fam, g in trials.groupby("family", sort=False):
        b = g.loc[g["is_roi"].idxmax()]
        p_adj = min(1.0, b["oos_p"] * CUMULATIVE_TRIALS)
        checks = {"oos_roi>0": b["oos_roi"] > 0, "p_adj<0.05": p_adj < 0.05,
                  "is_roi>0": b["is_roi"] > 0, "evidence": b["oos_bets"] >= 1000}
        out.append(dict(family=fam, params=b["params"], is_roi=b["is_roi"], is_bets=b["is_bets"],
                        oos_roi=b["oos_roi"], oos_bets=b["oos_bets"], oos_win_rate=b["oos_win_rate"],
                        oos_p=b["oos_p"], p_adjusted=p_adj, passed=all(checks.values()),
                        failed=", ".join(k for k, v in checks.items() if not v)))
    trials.drop(columns="_oos").to_csv(REPORTS / "round2_football_trials.csv", index=False)
    md = ["## B. Football betting", "",
          f"Matches: {len(df):,}, seasons {df['season'].min()}–{df['season'].max()}, "
          f"{df['div'].nunique()} leagues. Holdout = seasons {bt.HOLDOUT_FROM}+.", "",
          fmt(pd.DataFrame(out)), "", "All trials:", "", fmt(trials.drop(columns="_oos"))]
    return "\n".join(md)


# ---------------------------------------------------------------- C. Polymarket

def part_pm():
    from edge import betting as bt
    from edge import predmkt as pm
    df = pm.dataset(refresh=True)
    cut = df["end"].max() - pd.Timedelta(days=365)
    rows = []
    for fam, (fn, grid) in pm.FAMILIES.items():
        for params in grid:
            b = fn(df, **params)
            is_b, oos_b = b[b["end"] < cut], b[b["end"] >= cut]
            rows.append(dict(family=fam, params=json.dumps(params), is_bets=len(is_b),
                             is_roi=is_b["ret"].mean(), oos_bets=len(oos_b),
                             oos_roi=oos_b["ret"].mean(), oos_win_rate=(oos_b["ret"] > 0).mean(),
                             oos_worst=oos_b["ret"].min(), oos_p=bt.bootstrap_p(oos_b["ret"])))
    trials = pd.DataFrame(rows)
    b = trials.loc[trials["is_roi"].idxmax()]
    p_adj = min(1.0, b["oos_p"] * CUMULATIVE_TRIALS)
    checks = {"oos_roi>0": b["oos_roi"] > 0, "p_adj<0.05": p_adj < 0.05,
              "is_roi>0": b["is_roi"] > 0, "evidence": b["oos_bets"] >= 500}
    verdict = pd.DataFrame([dict(family=b["family"], params=b["params"], is_roi=b["is_roi"],
                                 oos_roi=b["oos_roi"], oos_bets=b["oos_bets"],
                                 oos_win_rate=b["oos_win_rate"], p_adjusted=p_adj,
                                 passed=all(checks.values()),
                                 failed=", ".join(k for k, v in checks.items() if not v))])
    trials.to_csv(REPORTS / "round2_pm_trials.csv", index=False)
    md = ["## C. Polymarket favourite-longshot", "",
          f"Markets: {len(df):,} resolved binary (volume ≥ ${pm.MIN_VOLUME:,}), "
          f"ending {df['end'].min().date()}–{df['end'].max().date()}. Holdout = ends ≥ {cut.date()}.", "",
          fmt(verdict), "", "All trials:", "", fmt(trials)]
    return "\n".join(md)


if __name__ == "__main__":
    part = sys.argv[1]
    md = {"nq": part_nq, "football": part_football, "pm": part_pm}[part]()
    (REPORTS / f"round2_{part}.md").write_text(md + "\n")
    print(md)

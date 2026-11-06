"""Round 25 runner (PROTOCOL_ROUND25.md). python run_round25.py data | run
data: Binance 1-minute closes for the five coins into data/r25/. run: models, policies, report.
R25_SMALL=1: one coin, 2026 only (pipeline check)."""
import json
import os
import sys
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd

from edge import round21, round25 as r

SMALL = os.environ.get("R25_SMALL") == "1"
TRAIN = (pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-04-01", tz="UTC"))
DEV = (pd.Timestamp("2026-04-01", tz="UTC"), pd.Timestamp("2026-09-30", tz="UTC"))
HOLD = (pd.Timestamp("2026-10-01", tz="UTC"), pd.Timestamp("2026-10-28", tz="UTC"))
if SMALL:
    TRAIN = (pd.Timestamp("2026-01-01", tz="UTC"), TRAIN[1])
DATA, FILLS, REPORTS = Path("data/r25"), Path("data/r21"), Path("reports")
SERIES = ["KXXRP15M"] if SMALL else list(r.COINS)


def data():
    DATA.mkdir(parents=True, exist_ok=True)
    for s in SERIES:
        spot = round21.minutes(r.COINS[s], TRAIN[0] - pd.Timedelta(days=1), HOLD[1])
        print(f"{s}: {len(spot):,} minutes {spot.index.min()} .. {spot.index.max()}", flush=True)
        spot.to_pickle(DATA / f"{s}.pkl")


def load_fills(spots: dict) -> pd.DataFrame:
    parts = []
    for s in SERIES:
        for tag in ("dev", "hold"):
            p = FILLS / f"{s}_{tag}.pkl"
            if not p.exists():
                print(f"  no Round 21 fills for {s} {tag}", flush=True)
                continue
            f = pd.read_pickle(p)
            if f.empty:
                continue
            f = f.copy()
            f["series"] = s
            f["close"] = (f["time"] + pd.to_timedelta(f["min_to_close"], unit="min")).dt.round("1min")
            f["maker"] = np.where(f["taker_side"] == "yes", "no", "yes")
            f["ours_won"] = ~f["won_longshot"].astype(bool)
            feats = r.features_at(spots[s], SERIES.index(s), f["time"])
            for c in r.FEATURES + ["z"]:
                f[c] = feats[c].to_numpy()
            f["coin"] = list(r.COINS).index(s)
            f["side_ok"] = np.where(f["maker"] == "yes", f["z"] > 0, f["z"] < 0)  # we only ever back the winning side
            parts.append(f)
    out = pd.concat(parts, ignore_index=True).sort_values("time").reset_index(drop=True)
    return out[np.isfinite(out[["az", "mom5", "volratio"]]).all(axis=1)]


def run():
    spots = {s: pd.read_pickle(DATA / f"{s}.pkl") for s in SERIES}
    frames = []
    for s in SERIES:
        d = r.frame(spots[s], list(r.COINS).index(s))
        frames.append(d[d["az"] >= 2])
    allf = pd.concat(frames, ignore_index=True)
    tr = allf[(allf["time"] >= TRAIN[0]) & (allf["time"] < TRAIN[1])]
    dv = allf[(allf["time"] >= DEV[0]) & (allf["time"] < DEV[1])]
    ho = allf[(allf["time"] >= HOLD[0]) & (allf["time"] < HOLD[1])]
    print(f"samples |z|>=2: train {len(tr):,} (flips {int(tr.flip.sum()):,}), dev {len(dv):,}, hold {len(ho):,}", flush=True)
    if os.environ.get("R25_EXPORT_ONLY") == "1":
        zb = r.ZBins().fit(tr)
        table = {"z_edges": r.ZBins.ZB, "tau_edges": r.ZBins.TB, "fit": f"{TRAIN[0].date()}..{TRAIN[1].date()}",
                 "rate": [[float(zb.rate.loc[(zi, ti)]) for ti in zb.rate.index.levels[1]] for zi in zb.rate.index.levels[0]],
                 "n": [[int(zb.n.loc[(zi, ti)]) for ti in zb.n.index.levels[1]] for zi in zb.n.index.levels[0]]}
        Path("control").mkdir(exist_ok=True)
        Path("control/r25_zbins.json").write_text(json.dumps(table, indent=1))
        print("wrote control/r25_zbins.json", flush=True)
        return
    models = {M.name: M().fit(tr) for M in (r.ZBins, r.Logit, r.GBM)}
    from sklearn.metrics import log_loss
    ll = {k: log_loss(dv["flip"].astype(int), np.clip(m.predict(dv), 1e-7, 1 - 1e-7)) for k, m in models.items()}
    scorer = min(ll, key=ll.get)
    print("dev log-loss:", {k: round(v, 5) for k, v in ll.items()}, "-> scorer", scorer, flush=True)

    fills = load_fills(spots)
    fd = fills[(fills["time"] >= DEV[0]) & (fills["time"] < DEV[1])].reset_index(drop=True)
    fh = fills[(fills["time"] >= HOLD[0]) & (fills["time"] < HOLD[1])].reset_index(drop=True)
    print(f"Kalshi long-shot fills: dev {len(fd):,}, hold {len(fh):,}", flush=True)
    pred = {k: {"dev": m.predict(fd), "hold": m.predict(fh)} for k, m in models.items()}

    policies = [(f"fixed z>={z} stake {st}", None, ("fixed", z, st)) for z, st in product([4, 5, 6, 8, 10], [0.5, 0.95])]
    policies += [(f"{k} kelly x{mu} cap {c} p<{pm:.3%}", k, ("kelly", mu, c, pm))
                 for k, mu, c, pm in product(models, [0.25, 0.5, 1.0], [0.5, 0.75, 0.95], [0.001, 0.003, 0.01])]

    def frac(f, which, kind, model):
        if kind[0] == "fixed":
            return np.where(f["side_ok"] & (f["az"] >= kind[1]), kind[2], 0.0)
        p = pred[model][which]
        k = r.kelly_fraction(p, kind[1], kind[2])
        return np.where(f["side_ok"] & (p < kind[3]), k, 0.0)

    rows = []
    for name, model, kind in policies:
        out = {"policy": name}
        for which, f in (("dev", fd), ("hold", fh)):
            fr = frac(f, which, kind, model)
            sim = r.simulate(f, fr)
            out.update({f"{which}_final": sim["final"], f"{which}_maxdd": sim["max_dd"], f"{which}_markets": sim["markets"],
                        f"{which}_losses": sim["losses"], f"{which}_days10k": sim["days_to_10k"],
                        f"{which}_score": r.expected_log_growth(f, fr, pred[scorer][which])})
            out[f"{which}_frac"] = fr
        rows.append(out)
    res = pd.DataFrame(rows)
    eligible = res[res["dev_maxdd"] >= -0.30]
    chosen = eligible.sort_values("dev_score", ascending=False).iloc[0]
    base = res[res["policy"] == "fixed z>=6 stake 0.5"].iloc[0]

    cal_h = r.calibration(models[scorer].predict(ho), ho["flip"].to_numpy())
    big = cal_h[cal_h["flips"] >= 20]
    cal_ok = bool(((big["actual"] >= 0.5 * big["predicted"]) & (big["actual"] <= 2 * big["predicted"])).all())
    # entry-region check on holdout Binance samples, using the chosen policy's own model and gate
    pk = chosen["policy"].split()[0] if chosen["policy"].startswith(("gbm", "logit", "zbins")) else scorer
    pm = 0.001
    for part in chosen["policy"].split():
        if part.startswith("p<"):
            pm = float(part[2:].rstrip("%")) / 100
    ph = models[pk].predict(ho)
    region = ph < pm
    exp_f, act_f = float(ph[region].sum()), int(ho["flip"].to_numpy()[region].sum())
    region_ok = act_f <= max(2 * exp_f, exp_f + 3)
    checks = {"holdout final >= live rule (z>=6, 0.5)": chosen["hold_final"] >= base["hold_final"],
              "holdout max drawdown <= 30%": chosen["hold_maxdd"] >= -0.30,
              "scorer calibrated on holdout (bins with >= 20 flips)": cal_ok,
              f"entry-region flips {act_f} <= max(2x{exp_f:.1f}, +3)": region_ok}
    ok = all(checks.values()) and not SMALL

    show = ["policy", "dev_final", "dev_maxdd", "dev_markets", "dev_losses", "dev_score", "hold_final", "hold_maxdd",
            "hold_markets", "hold_losses", "hold_days10k"]
    lines = [f"# Round 25{' SMOKE TEST' if SMALL else ''}: confidence-scaled sizing for the 15-minute crypto trade", "",
             "Rules: [PROTOCOL_ROUND25.md](../PROTOCOL_ROUND25.md).", "",
             f"Reversal samples (|z| >= 2): train {len(tr):,}, dev {len(dv):,}, holdout {len(ho):,}. "
             f"Kalshi long-shot fills: dev {len(fd):,}, holdout {len(fh):,}.", "",
             "## Models (dev log-loss, lower is better)", "",
             "| Model | Dev log-loss |", "|---|---:|"] + [f"| {k} | {v:.5f} |" for k, v in ll.items()] + \
            [f"", f"Scoring model: **{scorer}**", "",
             f"## Chosen on dev: **{chosen['policy']}**", "", f"## Verdict: **{'PASS' if ok else 'FAIL'}**", "",
             "| Holdout, $1,000 start | Chosen | Live rule (z>=6, 0.5) |", "|---|---:|---:|",
             f"| Final balance | ${chosen['hold_final']:,.2f} | ${base['hold_final']:,.2f} |",
             f"| Max drawdown | {chosen['hold_maxdd']:.1%} | {base['hold_maxdd']:.1%} |",
             f"| Markets traded / lost | {chosen['hold_markets']} / {chosen['hold_losses']} | {base['hold_markets']} / {base['hold_losses']} |",
             f"| Days to $10k at this pace | {chosen['hold_days10k']:.0f} | {base['hold_days10k']:.0f} |", "",
             "| Check | Result |", "|---|---|"] + [f"| {k} | {'yes' if v else '**no**'} |" for k, v in checks.items()] + \
            ["", "## Calibration of the scoring model on the holdout (Binance samples)", "", cal_h.round(6).to_markdown(),
             "", "## All policies (sorted by dev score)", "",
             res.sort_values("dev_score", ascending=False)[show].round(4).to_markdown(index=False)]
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / ("ROUND25_SMOKE.md" if SMALL else "ROUND25.md")).write_text("\n".join(lines) + "\n")
    if not SMALL:  # the reversal table the live trader uses (fit on the training years only)
        zb = models["zbins"]
        table = {"z_edges": r.ZBins.ZB, "tau_edges": r.ZBins.TB, "fit": f"{TRAIN[0].date()}..{TRAIN[1].date()}",
                 "rate": [[float(zb.rate.loc[(zi, ti)]) for ti in zb.rate.index.levels[1]] for zi in zb.rate.index.levels[0]],
                 "n": [[int(zb.n.loc[(zi, ti)]) for ti in zb.n.index.levels[1]] for zi in zb.n.index.levels[0]]}
        Path("control").mkdir(exist_ok=True)
        Path("control/r25_zbins.json").write_text(json.dumps(table, indent=1))
    print("\n".join(lines[:40]))


if __name__ == "__main__":
    {"data": data, "run": run}[sys.argv[1]]()

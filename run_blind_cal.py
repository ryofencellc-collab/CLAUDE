"""Blind-test calibration: plant each of the 7 strategy types at several strengths (known to the analyst, unlike the blind
draw) and record whether each detector flags the right source, with no hits on the clean ones."""
import re, sys, contextlib, io
import numpy as np, pandas as pd
import gen_blind as GB, run_blind as RB
from edge import nygrid as G

EXTRA = {"orb_continuation": dict(or_minutes=15), "gap_fill": dict(min_gap_pct=0.2, fill_minutes=90), "power_hour_trend": {},
         "weekday_drift": dict(weekday=2, direction=1), "lunch_reversal": {}, "overnight_momentum": {}, "narrow_range_breakout": dict(or_minutes=30)}
rows = []
seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 2
for kind, extra in EXTRA.items():
    for k in [0.15, 0.25, 0.35, 0.45]:
        for rep in range(seeds):
            rng = np.random.default_rng(hash((kind, k, rep)) % 2**32); tgt = RB.SRC[rep % 3]
            s = dict(source=tgt, strategy=kind, strength_k=k, **extra)
            mats = {n: G.day_matrix(GB.make_source(int(rng.integers(1, 2**31)), s if n == tgt else None)) for n in RB.SRC}
            RB.load = lambda n: mats[n]
            with contextlib.redirect_stdout(io.StringIO()):
                g = RB.grid(); sc = RB.scan()
            T = pd.read_csv("reports/blind_grid_all.csv")
            cand = T[(T.ho_t >= 3) & (T.ho_meanR > 0) & (T.dev_t >= 2) & (T.dev_meanR > 0)]
            c1 = {n: int((cand.source == n).sum()) for n in RB.SRC}
            c2 = dict(zip(RB.SRC, map(int, re.findall(r"[XYZ] \*\*(\d+)\*\*", sc.split("Significant per source:")[1].split("\n")[0]))))
            fam = cand[cand.source == tgt].entry.value_counts().index[0] if c1[tgt] else ""
            rows.append(dict(strategy=kind, k=k, rep=rep, grid_hit=c1[tgt] > 0, grid_false=sum(v for n, v in c1.items() if n != tgt),
                             grid_family=fam, scan_hit=c2[tgt] > 0, scan_false=sum(v for n, v in c2.items() if n != tgt)))
            print(rows[-1], flush=True)
D = pd.DataFrame(rows)
S = D.groupby(["strategy", "k"]).agg(grid_found=("grid_hit", "mean"), scan_found=("scan_hit", "mean"),
                                     false_alarms=("grid_false", "sum"), scan_false=("scan_false", "sum"),
                                     grid_family=("grid_family", lambda x: ",".join(sorted(set(x) - {""})))).reset_index()
open("reports/blind_calibration.md", "w").write("## Calibration: detection rate by strategy type and strength\n\n"
    f"{seeds} runs per cell. k = planted drift in standard deviations of the affected segment (the blind draw used 0.30–0.45).\n\n"
    + S.to_markdown(index=False) + "\n")
print(S.to_markdown(index=False))

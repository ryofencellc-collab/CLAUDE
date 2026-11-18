"""Round 54 (PROTOCOL_ROUND54.md). `python run_round54.py MARKET` -> reports/round54_parts/MARKET.csv + scan;
`python run_round54.py report`. BLIND_TEST=1 uses data/blind/X.parquet as every market (offline smoke)."""
import math, os, sys
import numpy as np, pandas as pd
import run_round53 as R53, run_blind as RB
from edge import nygrid as G, stats as S
from edge.intraday import load_nq

MK = {"SP": ("SPXUSD", 1.0), "NQ": ("NSXUSD", 1.5), "GOLD": ("XAUUSD", 2.0), "OIL": ("WTIUSD", 3.0),
      "EURUSD": ("EURUSD", 1.0), "USDJPY": ("USDJPY", 1.0), "GBPUSD": ("GBPUSD", 1.5)}
SPLIT = pd.Timestamp("2021-01-01"); PARTS = "reports/round54_parts"
BLIND = os.environ.get("BLIND_TEST") == "1"


def matrix(m):
    bars = pd.read_parquet("data/blind/X.parquet") if BLIND else load_nq(pair=MK[m][0])
    return G.day_matrix(bars)


def run_market(m):
    os.makedirs(PARTS, exist_ok=True)
    M = matrix(m); print(m, len(M["days"]), "days", M["days"][0].date(), "->", M["days"][-1].date(), flush=True)
    split = SPLIT if not BLIND else pd.Timestamp("2025-01-01")
    cfg = dict(pt=1.0, slip=MK[m][1] / 1e4 * M["o"][:, 0])     # cost in price units, per day
    rows = []; cache = {}
    for c in R53.grid():
        fname, fam, p, sname, sm, sp, rr, flname, flat, filt = c
        usd, R = R53.config_series(M, cfg, m, fam, p, sm, sp, rr, flat, filt, cache)
        dv = R53.stats_of(R, usd, pd.Timestamp("2000-01-01"), split); ho = R53.stats_of(R, usd, split, pd.Timestamp("2100-01-01"))
        rows.append(dict(market=m, entry=fname, stop=sname, target=("prior close" if fam == 2 else f"{rr:g}R" if rr else "time"),
                         exit=flname, filter=filt, dev_n=dv["n"], dev_meanR=dv["meanR"], dev_t=dv["t"],
                         ho_n=ho["n"], ho_meanR=ho["meanR"], ho_t=ho["t"], ho_sr=ho["sr_daily"]))
    pd.DataFrame(rows).to_csv(f"{PARTS}/{m}_grid.csv", index=False)
    # scanner (one market): keep the raw per-test table; Bonferroni is applied across markets in the report
    RB.SRC = [m]; RB.SPLIT = split; RB.load = lambda s: M
    txt = RB.scan()
    open(f"{PARTS}/{m}_scan.md", "w").write(txt)
    W = scan_table(M, m, split); W.to_csv(f"{PARTS}/{m}_scan.csv", index=False)
    print(m, "done", flush=True)


def scan_table(M, m, split):
    """Same tests as run_blind.scan, returned as a table (both periods)."""
    import itertools
    C = M["c"]; O0 = M["o"][:, 0]; days = M["days"]; SEG = RB.SEG; keys = list(SEG)
    px = lambda k: O0 if k == "open" else C[:, SEG[k]]
    sigs = {"overnight/gap": np.sign(O0 - M["prev_close"])}
    for k in ["09:45", "10:00", "10:30", "12:00", "15:00"]:
        sigs[f"open→{k}"] = np.sign(px(k) / O0 - 1)
    nr = np.where(np.isfinite(M["rng_med"]), np.where(M["prev_rng"] < M["rng_med"], 1.0, np.nan), np.nan)
    for k in ["09:45", "10:00", "10:30"]:
        sigs[f"narrowday×open→{k}"] = nr * np.sign(px(k) / O0 - 1)
    for wd in range(5):
        sigs[f"weekday{wd}"] = np.where(days.weekday == wd, 1.0, np.nan)
    rows = []
    for (name, sg), (a, b) in itertools.product(sigs.items(), itertools.combinations(keys, 2)):
        need = "open" if name == "overnight/gap" else (name.split("→")[-1] if "→" in name else "open")
        if keys.index(a) < keys.index(need):
            continue
        x = sg * (px(b) / px(a) - 1); r = dict(market=m, signal=name, target=f"{a}→{b}")
        for tag, msk in (("dev", days < split), ("ho", days >= split)):
            v = x[msk & np.isfinite(x)]
            r.update({f"n_{tag}": len(v), f"bp_{tag}": v.mean() * 1e4, f"t_{tag}": v.mean() / v.std() * math.sqrt(len(v)) if len(v) > 2 else np.nan})
        rows.append(r)
    return pd.DataFrame(rows)


def report():
    from scipy.stats import norm
    g = [pd.read_csv(f"{PARTS}/{m}_grid.csv") for m in MK if os.path.exists(f"{PARTS}/{m}_grid.csv")]
    s = [pd.read_csv(f"{PARTS}/{m}_scan.csv") for m in MK if os.path.exists(f"{PARTS}/{m}_scan.csv")]
    T = pd.concat(g, ignore_index=True); W = pd.concat(s, ignore_index=True)
    have = sorted(T.market.unique()); N = len(T); var_sr = float(np.nanvar(T.ho_sr))
    cand = T[(T.ho_t >= 3) & (T.ho_meanR > 0) & (T.dev_t >= 2) & (T.dev_meanR > 0)]
    # DSR on the R series is not stored; use the holdout Sharpe in the probabilistic-Sharpe form via edge.stats on synthetic? keep it simple:
    # the deflated-Sharpe hurdle is applied to the per-trade t through the expected maximum of N trials.
    emax = math.sqrt(2 * math.log(N)) if N > 1 else 0
    cand = cand.assign(beats_max_of_N=cand.ho_t > emax)
    W["t_all"] = (W.t_dev * np.sqrt(W.n_dev) + W.t_ho * np.sqrt(W.n_ho)) / np.sqrt(W.n_dev + W.n_ho)
    crit = float(-norm.ppf(0.025 / len(W)))
    cost = W.market.map({k: v[1] for k, v in MK.items()}) + 1
    sig = W[(W.t_all.abs() >= crit) & (np.sign(W.t_dev) == np.sign(W.t_ho))]
    sig = sig.assign(beats_cost=(np.minimum(sig.bp_dev.abs(), sig.bp_ho.abs()) > cost.loc[sig.index].values if len(sig) else []))
    passed = sig[sig.beats_cost] if len(sig) else sig
    out = ["# Round 54: NY-session grid + segment scanner on 7 markets", "", f"Rules: [PROTOCOL_ROUND54.md](../PROTOCOL_ROUND54.md). Markets with data: {', '.join(have)}.", "",
           "## Detector 1: grid", "", f"Configurations: **{N}**. Screen (ho t ≥ 3, dev t ≥ 2): **{len(cand)}**. "
           f"Of those, beating the expected best-of-{N} t ({emax:.2f}): **{int(cand.beats_max_of_N.sum()) if len(cand) else 0}**.", "",
           "Share of configurations with holdout mean R > 0, by market: " + ", ".join(f"{m} {(T[T.market==m].ho_meanR > 0).mean():.0%}" for m in have), ""]
    if len(cand):
        out += [cand.sort_values("ho_t", ascending=False).head(25).round(3).to_markdown(index=False), ""]
    top = T.assign(min_t=np.minimum(T.dev_t, T.ho_t)).sort_values("min_t", ascending=False).head(15)
    out += ["Top 15 by the weaker period's t:", "", top[["market", "entry", "stop", "target", "exit", "filter", "dev_n", "dev_meanR", "dev_t", "ho_n", "ho_meanR", "ho_t"]].round(3).to_markdown(index=False), "",
            "## Detector 2: segment scanner", "", f"Tests: {len(W)}; Bonferroni |t| ≥ {crit:.2f}, same sign both periods, |mean| > cost + 1 bp in both.", "",
            f"Significant: **{len(sig)}**; also beating costs: **{len(passed)}**.", ""]
    show = sig.sort_values("t_all", key=abs, ascending=False) if len(sig) else W.sort_values("t_all", key=abs, ascending=False)
    out += [("Significant tests:" if len(sig) else "Nothing significant. Top 15 by |t|:"), "",
            show.head(25).round(2).to_markdown(index=False), ""]
    open("reports/ROUND54.md", "w").write("\n".join(out) + "\n"); print("\n".join(out[:14]))


if __name__ == "__main__":
    report() if sys.argv[1] == "report" else run_market(sys.argv[1])

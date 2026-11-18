"""Blind test (PROTOCOL_BLIND.md). `python run_blind.py grid|scan|reveal`."""
import hashlib, itertools, json, math, sys
import numpy as np, pandas as pd
import run_round53 as R53
from edge import nygrid as G

SRC = ["X", "Y", "Z"]; SPLIT = pd.Timestamp("2025-01-01")
CFG = dict(pair="", pt=5.0, slip=0.5)


def load(s):
    return G.day_matrix(pd.read_parquet(f"data/blind/{s}.parquet"))


def grid(limit=None):
    data = {s: load(s) for s in SRC}
    rows = []; configs = list(R53.grid())[: limit or None]
    for s in SRC:
        M = data[s]; cache = {}
        for c in configs:
            fname, fam, p, sname, sm, sp, rr, flname, flat, filt = c
            usd, R = R53.config_series(M, CFG, s, fam, p, sm, sp, rr, flat, filt, cache)
            dv = R53.stats_of(R, usd, pd.Timestamp("2000-01-01"), SPLIT); ho = R53.stats_of(R, usd, SPLIT, pd.Timestamp("2100-01-01"))
            rows.append(dict(source=s, entry=fname, stop=sname, target=("prior close" if fam == 2 else f"{rr:g}R" if rr else "time"),
                             exit=flname, filter=filt, **{f"dev_{k}": v for k, v in dv.items()}, **{f"ho_{k}": v for k, v in ho.items()}))
    T = pd.DataFrame(rows)
    cand = T[(T.ho_t >= 3) & (T.ho_meanR > 0) & (T.dev_t >= 2) & (T.dev_meanR > 0)]
    out = ["## Detector 1: Round 53 grid (unchanged system)", "", f"Configurations: {len(T)} ({len(T)//3} per source). Dev 2024, holdout 2025.", "",
           "Screen candidates per source: " + ", ".join(f"{s} **{(cand.source == s).sum()}**" for s in SRC), "",
           "Configs with t ≥ 2 in BOTH years, per source: " + ", ".join(f"{s} {((T.source==s)&(T.ho_t>=2)&(T.dev_t>=2)).sum()}" for s in SRC), ""]
    if len(cand):
        out += ["Candidates by source and entry family:", "", cand.groupby(["source", "entry"]).size().rename("n").reset_index().to_markdown(index=False), "",
                "Top 15 candidates:", "", cand.sort_values("ho_t", ascending=False).head(15)[["source", "entry", "stop", "target", "exit", "filter", "dev_n", "dev_meanR", "dev_t", "ho_n", "ho_meanR", "ho_t"]].round(3).to_markdown(index=False), ""]
    both = T.assign(min_t=np.minimum(T.dev_t, T.ho_t)).sort_values("min_t", ascending=False).head(15)
    out += ["Top 15 by the weaker of the two years' t:", "", both[["source", "entry", "stop", "target", "exit", "filter", "dev_t", "ho_t", "ho_meanR"]].round(2).to_markdown(index=False), ""]
    T.to_csv("reports/blind_grid_all.csv", index=False)
    return "\n".join(out)


SEG = {"open": 0, "09:45": 15, "10:00": 30, "10:30": 60, "12:00": 150, "14:00": 270, "15:00": 330, "close": 389}


def scan():
    rows = []
    for s in SRC:
        M = load(s); C = M["c"]; O0 = M["o"][:, 0]; days = M["days"]
        px = lambda k: O0 if k == "open" else C[:, SEG[k]]
        sigs = {"overnight/gap": np.sign(O0 - M["prev_close"])}
        for k in ["09:45", "10:00", "10:30", "12:00", "15:00"]:
            sigs[f"open→{k}"] = np.sign(px(k) / O0 - 1)
        nr = np.where(np.isfinite(M["rng_med"]), np.where(M["prev_rng"] < M["rng_med"], 1.0, np.nan), np.nan)
        for k in ["09:45", "10:00", "10:30"]:
            sigs[f"narrowday×open→{k}"] = nr * np.sign(px(k) / O0 - 1)
        for wd in range(5):
            sigs[f"weekday{wd}"] = np.where(days.weekday == wd, 1.0, np.nan)
        keys = list(SEG)
        for (name, sg), (a, b) in itertools.product(sigs.items(), itertools.combinations(keys, 2)):
            tgt = px(b) / px(a) - 1
            # signal must be known by segment start
            need = {"overnight/gap": "open"}.get(name, name.split("→")[-1] if "→" in name else "open")
            if keys.index(a) < keys.index(need):
                continue
            x = sg * tgt
            for yr, m in (("2024", days < SPLIT), ("2025", days >= SPLIT)):
                v = x[m & np.isfinite(x)]
                rows.append(dict(source=s, signal=name, target=f"{a}→{b}", year=yr, n=len(v), mean_bp=v.mean() * 1e4, t=v.mean() / v.std() * math.sqrt(len(v))))
    T = pd.DataFrame(rows)
    W = T.pivot_table(index=["source", "signal", "target"], columns="year", values=["t", "mean_bp", "n"]).reset_index()
    W.columns = ["_".join(c).strip("_") for c in W.columns]
    W["t_all"] = (W.t_2024 * np.sqrt(W.n_2024) + W.t_2025 * np.sqrt(W.n_2025)) / np.sqrt(W.n_2024 + W.n_2025)  # Stouffer
    ntests = len(W); crit = float(-__import__("scipy").stats.norm.ppf(0.025 / ntests))
    sig = W[(W.t_all.abs() >= crit) & (np.sign(W.t_2024) == np.sign(W.t_2025))].sort_values("t_all", key=abs, ascending=False)
    out = ["## Detector 2: generic segment scanner", "", f"Tests: {ntests} across 3 sources; Bonferroni |t| ≥ {crit:.2f}, same sign both years.", "",
           "Significant per source: " + ", ".join(f"{s} **{(sig.source == s).sum()}**" for s in SRC), ""]
    show = sig if len(sig) else W.sort_values("t_all", key=abs, ascending=False)
    out += [("Significant tests:" if len(sig) else "Nothing significant. Top 15 by |t|:"), "",
            show.head(15)[["source", "signal", "target", "mean_bp_2024", "t_2024", "mean_bp_2025", "t_2025", "t_all"]].round(2).to_markdown(index=False), ""]
    return "\n".join(out)


def reveal():
    blob = open("data/blind/secret.json", "rb").read()
    return f"## Reveal\n\nsha256 = `{hashlib.sha256(blob).hexdigest()}`\n\n```json\n{blob.decode()}\n```\n"


if __name__ == "__main__":
    cmd = sys.argv[1]
    txt = grid(int(sys.argv[2]) if len(sys.argv) > 2 else None) if cmd == "grid" else scan() if cmd == "scan" else reveal()
    print(txt)
    if cmd != "reveal" or True:
        open(f"reports/blind_{cmd}.md", "w").write(txt)

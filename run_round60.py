"""Round 60 (PROTOCOL_ROUND60.md): quiet traders on Hyperliquid. `smoke` | `collect` | `analyze` | `forward_score`."""
import json, math, os, pickle, sys, time
import numpy as np, pandas as pd, requests
import run_round59 as R59

OUT = "data/r60"; os.makedirs(OUT, exist_ok=True)
SPLITS = {"split1 (seen aggregate)": (pd.Timestamp("2026-06-01", tz="UTC"), pd.Timestamp("2026-09-01", tz="UTC")),
          "split2": (pd.Timestamp("2026-07-15", tz="UTC"), pd.Timestamp("2026-10-01", tz="UTC"))}
FWD_SEL = (pd.Timestamp("2026-08-18", tz="UTC"), pd.Timestamp("2026-11-19", tz="UTC"))
CAP = 50


def series(s):
    return [(pd.Timestamp(int(x[0]), unit="ms", tz="UTC"), float(x[1])) for x in s]


def feats(data, vlm, a0, b0, end):
    rows = []
    for a, d in data.items():
        P, V = series(d["pnl"]), series(d["av"])
        if not P: continue
        at = lambda S, t: next((v for tt, v in reversed(S) if tt <= t), np.nan)
        pA0, pB0, pE, vA0, vB0 = at(P, a0), at(P, b0), at(P, end), at(V, a0), at(V, b0)
        inA = [v for t, v in P if a0 <= t < b0]
        inc = np.diff(inA) if len(inA) > 1 else np.array([])
        cum = np.array(inA) - (inA[0] if inA else 0)
        dd = float(np.max(np.maximum.accumulate(cum) - cum)) if len(cum) else np.nan
        rows.append(dict(addr=a, pnlA=pB0 - pA0, pnlB=pE - pB0, avA0=vA0, avB0=vB0, n_inc=len(inc),
                         pos_frac=(inc > 0).mean() if len(inc) else np.nan, mdd=dd / vA0 if vA0 and vA0 > 0 else np.nan,
                         steady=(inc.mean() / inc.std() if len(inc) >= 6 and inc.std() > 0 else np.nan), turnover=vlm.get(a, np.nan) / vB0 if vB0 else np.nan))
    F = pd.DataFrame(rows)
    F = F[(F.avA0 >= 1e3) & (F.avB0 >= 1e4) & (F.n_inc >= 3)].copy()
    F["roiA"] = F.pnlA / ((F.avA0 + F.avB0) / 2); F["roiB"] = (F.pnlB / F.avB0).clip(-1, 3)
    return F


def groups(F):
    med_turn = F.turnover.median()
    q1 = F[(F.roiA.between(0.05, 0.60)) & (F.pos_frac >= 0.70) & (F.n_inc >= 8) & (F.mdd <= 0.10)]
    q2 = F[(F.roiA > 0.05) & (F.turnover < med_turn) & (F.mdd <= 0.20)]
    q3 = F[(F.avB0.between(1e4, 2.5e5)) & (F.roiA > 0.05) & (F.mdd <= 0.15) & (F.pos_frac >= 0.60)]
    cap = lambda g: g.sort_values("steady", ascending=False).head(CAP)
    return {"Q1 steady earners": cap(q1), "Q2 low-turnover winners": cap(q2), "Q3 small and steady": cap(q3)}


def score(F, G):
    res = []
    for name, g in G.items():
        if len(g) < 5:
            res.append(dict(group=name, n=len(g), PASS=False)); continue
        t, w, pos = R59.tstat(g.roiB), R59.welch(g.roiB, F.roiB), (g.roiB > 0).mean()
        res.append(dict(group=name, n=len(g), mean_roiB=g.roiB.mean(), median_roiB=g.roiB.median(), t=t, welch_vs_all=w, pct_profitable=pos,
                        PASS=bool(t >= 2.4 and w >= 2.4 and pos >= 0.55)))
    return pd.DataFrame(res)


def synthetic(quiet, seed=7):
    rng = np.random.default_rng(seed); data = {}; vlm = {}
    t = pd.date_range("2026-03-01", "2026-11-18", freq="5D", tz="UTC"); ms = [int(x.timestamp() * 1000) for x in t]
    for i in range(6000):
        q = quiet and rng.random() < 0.05
        av0 = float(np.exp(rng.uniform(np.log(2e4), np.log(2e5)))) if q else float(np.exp(rng.uniform(np.log(1.2e4), np.log(2e6))))
        mu, sig = (0.012, 0.008) if q else (-0.003, rng.uniform(0.02, 0.15))
        pnl = np.cumsum(rng.normal(mu, sig, len(t)) * av0); av = np.maximum(av0 + pnl, 0)
        data[f"a{i}"] = dict(pnl=[[m, str(v)] for m, v in zip(ms, pnl)], av=[[m, str(v)] for m, v in zip(ms, av)])
        vlm[f"a{i}"] = av0 * (rng.uniform(1, 5) if q else rng.uniform(2, 60))
    return data, vlm


def smoke():
    end = pd.Timestamp("2026-11-18", tz="UTC")
    for quiet in (True, False):
        data, vlm = synthetic(quiet)
        for nm, (a0, b0) in SPLITS.items():
            F = feats(data, vlm, a0, b0, end); R = score(F, groups(F))
            print("planted" if quiet else "null", nm, R[["group", "n", "mean_roiB", "t", "pct_profitable", "PASS"]].round(2).to_string(index=False))
            assert bool(R.PASS.any()) == quiet, "calibration failed"
    print("smoke OK")


def collect():
    rows = requests.get("https://stats-data.hyperliquid.xyz/Mainnet/leaderboard", timeout=120).json()["leaderboardRows"]
    vlm = {r["ethAddress"]: float(dict(r["windowPerformances"])["month"]["vlm"]) for r in rows}
    addrs, n_all, n_pool = R59.sample(); data = {}
    for i, a in enumerate(addrs):
        for k in range(4):
            try:
                r = requests.post(R59.INFO, json={"type": "portfolio", "user": a}, timeout=30)
                if r.status_code == 200:
                    d = dict(r.json()).get("allTime", {}); data[a] = dict(pnl=d.get("pnlHistory", []), av=d.get("accountValueHistory", [])); break
            except Exception: pass
            time.sleep(2 + 3 * k)
        if i % 500 == 0: print(i, flush=True); pickle.dump(dict(data=data, vlm=vlm), open(f"{OUT}/raw.pkl", "wb"))
    pickle.dump(dict(data=data, vlm=vlm), open(f"{OUT}/raw.pkl", "wb"))


def analyze():
    d = pickle.load(open(f"{OUT}/raw.pkl", "rb")); data, vlm = d["data"], d["vlm"]
    end = max(pd.Timestamp(int(x[0]), unit="ms", tz="UTC") for v in data.values() for x in v["pnl"][-1:])
    out = ["# Round 60: quiet traders on Hyperliquid", "", "Rules: [PROTOCOL_ROUND60.md](../PROTOCOL_ROUND60.md).", f"Accounts with history: {len(data)}. Data end: {end:%Y-%m-%d}.", ""]
    ok2 = False
    for nm, (a0, b0) in SPLITS.items():
        F = feats(data, vlm, a0, b0, end); R = score(F, groups(F))
        if nm == "split2": ok2 = bool(R.PASS.any())
        out += [f"## {nm}: select {a0:%b %d} → {b0:%b %d}, test {b0:%b %d} → {end:%b %d}", "",
                f"Eligible: {len(F)}; universe mean ROI {F.roiB.mean():+.1%}, profitable {(F.roiB > 0).mean():.0%}.", "", R.round(3).to_markdown(index=False), ""]
    # forward-test selection, frozen today
    F = feats(data, vlm, FWD_SEL[0], FWD_SEL[1], FWD_SEL[1]); G = groups(F)
    frozen = {nm: [dict(addr=r.addr, avB0=r.avB0) for r in g.itertuples()] for nm, g in G.items()}
    json.dump(dict(selected_at=str(FWD_SEL[1]), groups=frozen, universe=[dict(addr=r.addr, avB0=r.avB0) for r in F.itertuples()]),
              open("paper/r60_forward_selection.json", "w"))
    out += ["## Forward test (the real one)", "", f"Selected on Aug 18 → Nov 19 and frozen in `paper/r60_forward_selection.json`: " +
            ", ".join(f"{k}: {len(v)}" for k, v in frozen.items()) + f" (universe {len(F)}). Scored on Dec 19.", "",
            f"**Split 2 verdict: {'PASS' if ok2 else 'FAIL'}.** The overall pass needs split 2 AND the forward test."]
    open("reports/ROUND60.md", "w").write("\n".join(out) + "\n"); print("\n".join(out))


if __name__ == "__main__":
    {"smoke": smoke, "collect": collect, "analyze": analyze}[sys.argv[1]]()

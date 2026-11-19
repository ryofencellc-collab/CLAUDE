"""Round 59 (PROTOCOL_ROUND59.md): persistence of Hyperliquid trader performance. `smoke` | `collect SHARD NSHARDS` | `analyze`."""
import json, math, os, pickle, sys, time
import numpy as np, pandas as pd, requests

OUT = "data/r59"; os.makedirs(OUT, exist_ok=True)
A0, B0 = pd.Timestamp("2026-06-01", tz="UTC"), pd.Timestamp("2026-09-01", tz="UTC")
N_SAMPLE, SEED, GROUP = 6000, 59, 50
INFO = "https://api.hyperliquid.xyz/info"


def sample():
    rows = requests.get("https://stats-data.hyperliquid.xyz/Mainnet/leaderboard", timeout=120).json()["leaderboardRows"]
    vlm = lambda r: float(dict(r["windowPerformances"])["allTime"]["vlm"])
    pool = sorted(r["ethAddress"] for r in rows if vlm(r) >= 5e6)
    rng = np.random.default_rng(SEED)
    return list(rng.choice(pool, size=min(N_SAMPLE, len(pool)), replace=False)), len(rows), len(pool)


def collect(shard, nshards):
    addrs, n_all, n_pool = sample()
    mine = addrs[shard::nshards]; out = {}
    for i, a in enumerate(mine):
        for k in range(4):
            try:
                r = requests.post(INFO, json={"type": "portfolio", "user": a}, timeout=30)
                if r.status_code == 200:
                    d = dict(r.json()).get("allTime", {})
                    out[a] = dict(pnl=d.get("pnlHistory", []), av=d.get("accountValueHistory", [])); break
                time.sleep(2 + 3 * k)
            except Exception:
                time.sleep(2 + 3 * k)
        if i % 250 == 0: print(shard, i, len(mine), flush=True)
    pickle.dump(dict(data=out, n_all=n_all, n_pool=n_pool), open(f"{OUT}/shard{shard}.pkl", "wb"))


def step(series, t):
    """Value of a [[ms, value], ...] step series at time t (last point <= t), else NaN."""
    ts = [(pd.Timestamp(int(x[0]), unit="ms", tz="UTC"), float(x[1])) for x in series]
    v = [val for tt, val in ts if tt <= t]
    return v[-1] if v else np.nan


def features(data, end):
    rows = []
    for a, d in data.items():
        pnl, av = d["pnl"], d["av"]
        if not pnl: continue
        pA0, pB0, pE = step(pnl, A0), step(pnl, B0), step(pnl, end)
        vA0, vB0 = step(av, A0), step(av, B0)
        inA = [float(x[1]) for x in pnl if A0 <= pd.Timestamp(int(x[0]), unit="ms", tz="UTC") < B0]
        rows.append(dict(addr=a, pnlA=pB0 - pA0, pnlB=pE - pB0, avA0=vA0, avB0=vB0, nA=len(inA),
                         steady=(np.mean(np.diff(inA)) / np.std(np.diff(inA)) if len(inA) >= 7 and np.std(np.diff(inA)) > 0 else np.nan)))
    F = pd.DataFrame(rows)
    F = F[(F.avA0 >= 1e3) & (F.avB0 >= 1e4) & (F.nA >= 4)].copy()
    F["roiA"] = F.pnlA / ((F.avA0 + F.avB0) / 2)
    F["roiB"] = (F.pnlB / F.avB0).clip(-1, 3)
    return F


def tstat(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    return x.mean() / x.std(ddof=1) * math.sqrt(len(x)) if len(x) > 2 and x.std(ddof=1) > 0 else np.nan


def welch(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    return (x.mean() - y.mean()) / math.sqrt(x.var(ddof=1) / len(x) + y.var(ddof=1) / len(y))


def analyze(F, label="real"):
    groups = {"G1 top PnL_A": F.nlargest(GROUP, "pnlA"),
              "G2 top ROI_A (PnL_A ≥ $10k)": F[F.pnlA >= 1e4].nlargest(GROUP, "roiA"),
              "G3 steadiest (PnL_A > 0)": F[(F.pnlA > 0) & F.steady.notna()].nlargest(GROUP, "steady")}
    res = []
    for name, g in groups.items():
        t, w, pos = tstat(g.roiB), welch(g.roiB, F.roiB), (g.roiB > 0).mean()
        res.append(dict(group=name, n=len(g), mean_roiB=g.roiB.mean(), median_roiB=g.roiB.median(), t=t, welch_vs_all=w,
                        pct_profitable=pos, pnlB_total=g.pnlB.sum(), PASS=bool(t >= 2.4 and w >= 2.4 and pos >= 0.55)))
    R = pd.DataFrame(res)
    # decile persistence: ROI_A decile -> mean ROI_B
    F = F.copy(); F["decA"] = pd.qcut(F.roiA.rank(method="first"), 10, labels=False) + 1
    dec = F.groupby("decA").agg(n=("roiB", "size"), mean_roiA=("roiA", "mean"), mean_roiB=("roiB", "mean"), pct_profitable_B=("roiB", lambda x: (x > 0).mean()))
    return dict(label=label, R=R, dec=dec, n=len(F), all_mean=F.roiB.mean(), all_pos=(F.roiB > 0).mean())


def synthetic(skill, seed=5):
    rng = np.random.default_rng(seed); data = {}
    t = pd.date_range("2026-03-01", "2026-11-18", freq="5D", tz="UTC")
    for i in range(6000):
        mu = (0.03 if (skill and rng.random() < 0.05) else -0.003) / 1.0      # weekly-ish drift as fraction of capital
        sig = rng.uniform(0.02, 0.15); av0 = float(np.exp(rng.uniform(np.log(2e4), np.log(2e6))))
        inc = rng.normal(mu, sig, len(t)) * av0
        pnl = np.cumsum(inc); av = np.maximum(av0 + pnl, 0)
        ms = [int(x.timestamp() * 1000) for x in t]
        data[f"a{i}"] = dict(pnl=[[m, str(v)] for m, v in zip(ms, pnl)], av=[[m, str(v)] for m, v in zip(ms, av)])
    return data


def report(res, n_all=None, n_pool=None, n_got=None):
    out = ["# Round 59: do Hyperliquid's winning traders keep winning?", "", "Rules: [PROTOCOL_ROUND59.md](../PROTOCOL_ROUND59.md).", "",
           f"Leaderboard accounts: {n_all}; volume ≥ $5M: {n_pool}; sampled with history: {n_got}; eligible: {res['n']}. "
           f"Selection window Jun 1 → Sep 1 2026, test window Sep 1 → now.", "",
           f"Eligible universe in the test window: mean ROI {res['all_mean']:+.1%}, profitable {res['all_pos']:.0%}.", "",
           f"**Verdict: {'PASS → Round 59b copy simulation' if res['R'].PASS.any() else 'FAIL'}.**", "",
           "## Groups picked on the selection window, scored on the test window", "", res["R"].round(3).to_markdown(index=False), "",
           "## Persistence by ROI decile (decile 10 = best in the selection window)", "", res["dec"].round(3).to_markdown()]
    open("reports/ROUND59.md", "w").write("\n".join(out) + "\n"); print("\n".join(out))


def smoke():
    end = pd.Timestamp("2026-11-18", tz="UTC")
    for skill in (True, False):
        r = analyze(features(synthetic(skill), end), "planted" if skill else "null")
        print(r["label"], r["R"][["group", "mean_roiB", "t", "welch_vs_all", "pct_profitable", "PASS"]].round(2).to_string(index=False))
        assert bool(r["R"].PASS.any()) == skill, f"calibration failed: {r['label']}"
    print("smoke OK")


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "smoke": smoke()
    elif c == "collect": collect(int(sys.argv[2]), int(sys.argv[3]))
    else:
        data, meta = {}, {}
        for f in sorted(os.listdir(OUT)):
            if f.startswith("shard"):
                d = pickle.load(open(f"{OUT}/{f}", "rb")); data.update(d["data"]); meta = d
        end = max(pd.Timestamp(int(x[0]), unit="ms", tz="UTC") for d in data.values() for x in d["pnl"][-1:])
        report(analyze(features(data, end)), meta.get("n_all"), meta.get("n_pool"), len(data))

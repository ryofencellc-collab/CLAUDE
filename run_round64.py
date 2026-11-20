"""Round 64 (PROTOCOL_ROUND64.md): win-condition mining on 0DTE trades. `smoke` | `report`."""
import math, sys, time
import numpy as np, pandas as pd
import run_round62 as R

QS = [10, 20, 30, 70, 80, 90]
SIDES = {"call": "pnl_call", "put": "pnl_put"}
GAP = 30          # minutes between the 2 trades of a day
TOPK = 40


class Root:
    """Arrays for one root's snapshots, sorted by (day, time)."""
    def __init__(self, D, F):
        D = D.sort_values(["day", "t"]).reset_index(drop=True)
        self.D, self.F = D, F
        self.X = D[F].to_numpy(float)
        self.days = np.array(sorted(D.day.unique()))
        di = D.day.map({d: i for i, d in enumerate(self.days)}).to_numpy()
        mins = (pd.to_datetime(D.t).dt.hour * 60 + pd.to_datetime(D.t).dt.minute).to_numpy()
        self.T = di * 10000 + mins
        self.starts = np.searchsorted(di, np.arange(len(self.days)))
        self.ends = np.searchsorted(di, np.arange(len(self.days)), side="right")
        self.di = di
        self.pnl = {s: D[c].to_numpy(float) for s, c in SIDES.items()}

    def day_pnl(self, mask, side, pnl=None):
        """Per-day P&L of a rule: first trigger of the day, then one more >= GAP minutes later. Returns (pnl per day, trades per day)."""
        p = self.pnl[side] if pnl is None else pnl
        idx = np.flatnonzero(mask & ~np.isnan(p))
        out, n = np.zeros(len(self.days)), np.zeros(len(self.days), int)
        if not len(idx): return out, n
        Ti = self.T[idx]
        k1 = np.searchsorted(idx, self.starts); ok1 = (k1 < len(idx))
        ok1[ok1] = idx[k1[ok1]] < self.ends[ok1]
        i1 = idx[np.minimum(k1, len(idx) - 1)]
        k2 = np.searchsorted(Ti, self.T[i1] + GAP); ok2 = ok1 & (k2 < len(idx))
        ok2[ok2] = idx[k2[ok2]] < self.ends[ok2]
        i2 = idx[np.minimum(k2, len(idx) - 1)]
        out = np.where(ok1, p[i1], 0.0) + np.where(ok2, p[i2], 0.0)
        return out, ok1.astype(int) + ok2.astype(int)


def conditions(X, rows):
    """Single conditions (j, op, threshold) from percentiles of the training rows."""
    Q = np.nanpercentile(X[rows], QS, axis=0)
    return [(j, op, Q[qi, j], q) for j in range(X.shape[1]) for qi, q in enumerate(QS) for op in ((">=",) if q >= 70 else ("<=",))]


def cmask(X, c):
    j, op, th, _ = c
    with np.errstate(invalid="ignore"):
        return X[:, j] >= th if op == ">=" else X[:, j] <= th


def mine(r, train_days, pnl=None):
    """Best rule on train_days (bool per day). Returns (score, side, conds)."""
    rows = train_days[r.di]
    C = conditions(r.X, rows)
    M = [cmask(r.X, c) for c in C]
    need = max(4, int(math.ceil(train_days.sum() / 2)))
    best = (-np.inf, None, None); singles = {s: [] for s in SIDES}
    for s in SIDES:
        pp = None if pnl is None else pnl[s]
        for ci, m in enumerate(M):
            dp, n = r.day_pnl(m, s, pp)
            if (n[train_days] > 0).sum() < need: continue
            sc = dp[train_days].sum(); singles[s].append((sc, ci))
            if sc > best[0]: best = (sc, s, [C[ci]])
        top = [ci for _, ci in sorted(singles[s], reverse=True)[:TOPK]]
        for a in range(len(top)):
            for b in range(a + 1, len(top)):
                if C[top[a]][0] == C[top[b]][0]: continue
                dp, n = r.day_pnl(M[top[a]] & M[top[b]], s, pp)
                if (n[train_days] > 0).sum() < need: continue
                sc = dp[train_days].sum()
                if sc > best[0]: best = (sc, s, [C[top[a]], C[top[b]]])
    return best


def apply(r, rule, pnl=None):
    _, s, conds = rule
    m = np.ones(len(r.X), bool)
    for c in conds: m &= cmask(r.X, c)
    return r.day_pnl(m, s, None if pnl is None else pnl[s])


def lodo(r, pnl=None):
    tot, rows = np.zeros(len(r.days)), []
    for k, d in enumerate(r.days):
        tr = np.ones(len(r.days), bool); tr[k] = False
        rule = mine(r, tr, pnl)
        if rule[1] is None: rows.append(dict(day=d, rule="none", pnl=0.0, trades=0)); continue
        dp, n = apply(r, rule, pnl)
        tot[k] = dp[k]; rows.append(dict(day=d, rule=describe(r, rule), pnl=round(dp[k], 1), trades=int(n[k])))
    return tot, pd.DataFrame(rows)


def describe(r, rule):
    _, s, conds = rule
    return f"BUY {s.upper()} when " + " AND ".join(f"{r.F[j]} {op} {th:.4g} (p{q})" for j, op, th, q in conds)


def shifted(r, rng):
    out = {}
    for s in SIDES:
        p = r.pnl[s].copy()
        for a, b in zip(r.starts, r.ends):
            if b - a > 2: p[a:b] = np.roll(p[a:b], int(rng.integers(60, 240)) % (b - a))
        out[s] = p
    return out


def stats(dp, n=None):
    d = np.asarray(dp, float)
    t = d.mean() / d.std(ddof=1) * math.sqrt(len(d)) if len(d) > 2 and d.std(ddof=1) > 0 else float("nan")
    return dict(total=round(float(d.sum()), 0), green=f"{int((d > 0).sum())}/{len(d)}", t=round(t, 2), trades=int(n.sum()) if n is not None else None)


def cross(ra, rb):
    """Mine on all of ra, apply the same percentile thresholds computed on rb's own data."""
    rule = mine(ra, np.ones(len(ra.days), bool))
    if rule[1] is None: return None, np.zeros(len(rb.days)), np.zeros(len(rb.days), int)
    Qb = np.nanpercentile(rb.X, QS, axis=0)
    ja = {f: i for i, f in enumerate(rb.F)}
    conds = [(ja[ra.F[j]], op, Qb[QS.index(q), ja[ra.F[j]]], q) for j, op, th, q in rule[2]]
    dp, n = apply(rb, (rule[0], rule[1], conds))
    return describe(ra, rule), dp, n


def winners_vs_losers(D, F):
    rows = []
    for s, c in SIDES.items():
        x = D[D[c].notna()]
        w, l = x[x[c] > 0], x[x[c] <= 0]
        for f in F:
            sd = x[f].std()
            if sd and sd == sd: rows.append(dict(side=s, variable=f, winners_mean=w[f].mean(), losers_mean=l[f].mean(), std_diff=(w[f].mean() - l[f].mean()) / sd))
    W = pd.DataFrame(rows)
    return W.assign(abs_d=W.std_diff.abs()).sort_values(["side", "abs_d"], ascending=[True, False]).groupby("side").head(15).drop(columns="abs_d")


def evaluate(D, F, n_null=20, seed=0):
    rng = np.random.default_rng(seed); res = {}
    roots = {k: Root(D[D.root == k], F) for k in sorted(D.root.unique())}
    for k, r in roots.items():
        t0 = time.time(); tot, T = lodo(r)
        base = {s: r.day_pnl(np.ones(len(r.X), bool), s) for s in SIDES}
        nulls = [lodo(r, shifted(r, rng))[0].sum() for _ in range(n_null)]
        final = mine(r, np.ones(len(r.days), bool))
        res[k] = dict(lodo=stats(tot), lodo_trades=int(T.trades.sum()), folds=T, null95=float(np.percentile(nulls, 95)) if nulls else float("nan"),
                      nulls=nulls, base={s: stats(*base[s]) for s in SIDES}, final=describe(r, final) if final[1] else "none",
                      final_in_sample=round(final[0], 0) if final[1] else 0)
        print(k, res[k]["lodo"], "null95", res[k]["null95"], round(time.time() - t0), "s", flush=True)
    ks = sorted(roots)
    if len(ks) == 2:
        for a, b in ((ks[0], ks[1]), (ks[1], ks[0])):
            rule, dp, n = cross(roots[a], roots[b])
            res[f"{a}->{b}"] = dict(rule=rule, **stats(dp, n))
    return res


def verdict(res):
    roots = [k for k in res if "->" not in k]
    ok = all(res[k]["lodo"]["total"] > 0 and res[k]["lodo"]["total"] > res[k]["null95"]
             and res[k]["lodo"]["total"] > max(b["total"] for b in res[k]["base"].values()) and (res[k]["lodo"]["t"] or 0) >= 2.5 for k in roots)
    ok = ok and all(v["total"] > 0 for k, v in res.items() if "->" in k)
    return ok


def report():
    D = R.build(); F = R.feat_cols(D); n_days = D.day.nunique()
    res = evaluate(D, F)
    W = winners_vs_losers(D, F)
    out = ["# Round 64: \"when X happens, we win\" (win-condition mining on 0DTE trades)", "", "Rules: [PROTOCOL_ROUND64.md](../PROTOCOL_ROUND64.md).",
           f"Recorded days: **{n_days}** ({'INTERIM: verdict needs 20 days' if n_days < 20 else 'scored'}); snapshots {len(D):,}; variables {len(F)}; "
           f"rules searched per fold ≈ {len(F) * len(QS) * 2 + 2 * TOPK * (TOPK - 1) // 2:,}. ATM, X2 exits, real bid/ask, ≤ 2 trades/day.", "",
           f"**Verdict: {'PASS' if verdict(res) and n_days >= 20 else ('would pass (interim)' if verdict(res) else 'FAIL') + (' (interim)' if n_days < 20 else '')}.**", ""]
    for k, v in res.items():
        if "->" in k: continue
        out += [f"## {k}", "",
                f"- **Held-out (leave-one-day-out) P&L: ${v['lodo']['total']:,.0f}** on {v['lodo_trades']} trades; green days {v['lodo']['green']}; t {v['lodo']['t']}.",
                f"- Luck test (same search on time-shifted labels, 20 runs): 95th percentile ${v['null95']:,.0f} → real is **{'above' if v['lodo']['total'] > v['null95'] else 'NOT above'}** luck.",
                f"- Baselines on the same ≤ 2/day schedule: always call ${v['base']['call']['total']:,.0f}, always put ${v['base']['put']['total']:,.0f}.",
                f"- Best rule on ALL days (in-sample, for reference only): {v['final']} → ${v['final_in_sample']:,.0f} in-sample.", "",
                "Rule picked for each held-out day (mined on the other days):", "", v["folds"].to_markdown(index=False), ""]
    for k, v in res.items():
        if "->" in k:
            out += [f"## Cross-ticker {k}", "", f"Rule mined on all of {k.split('->')[0]}: {v['rule']}", "",
                    f"Applied to {k.split('->')[1]}: **${v['total']:,.0f}** on {v['trades']} trades, green days {v['green']}, t {v['t']}.", ""]
    out += ["## Why winners win (descriptive, no verdict): variables that differ most at entry between winning and losing trades", "",
            "std_diff = (winners' mean − losers' mean) / std. Within-day level variables are biased here (see Round 62 amendment 1); read with care.", "",
            W.round(4).to_markdown(index=False)]
    open("reports/ROUND64.md", "w").write("\n".join(out) + "\n"); print("\n".join(out[:12]))


def smoke():
    D = R.build(); F = R.feat_cols(D); rng = np.random.default_rng(3)
    P = D.copy(); P["planted"] = np.sign(P.pnl_call.fillna(0) - P.pnl_put.fillna(0)) + rng.normal(0, 0.8, len(P))
    res = evaluate(P[P.root == "SPY"], F + ["planted"], n_null=5)
    v = res["SPY"]; print("planted:", v["lodo"], "null95", v["null95"]); assert v["lodo"]["total"] > max(v["null95"], 0), "planted not found"
    N = D[["day", "root", "t", "pnl_call", "pnl_put"]].copy()
    for i in range(10): N[f"noise{i}"] = rng.normal(size=len(N))
    res = evaluate(N[N.root == "SPY"], [f"noise{i}" for i in range(10)], n_null=10)
    v = res["SPY"]; print("noise:", v["lodo"], "null95", v["null95"]); assert v["lodo"]["total"] <= v["null95"], "noise beat the null"
    print("smoke OK")


if __name__ == "__main__":
    {"smoke": smoke, "report": report}[sys.argv[1]]()

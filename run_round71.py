"""Round 71 (PROTOCOL_ROUND71.md): share-class pairs mean reversion.  Usage: smoke | report"""
import math, sys
import numpy as np, pandas as pd

PAIRS = [("GOOGL", "GOOG"), ("FOXA", "FOX"), ("NWSA", "NWS"), ("LEN", "LEN-B"), ("HEI", "HEI-A"), ("BF-B", "BF-A"), ("Z", "ZG"), ("FWONK", "FWONA"),
         ("LBRDK", "LBRDA"), ("CWEN", "CWEN-A"), ("UHAL-B", "UHAL"), ("MOG-A", "MOG-B"), ("GEF", "GEF-B"), ("LGF-A", "LGF-B"), ("BATRK", "BATRA"),
         ("RUSHA", "RUSHB"), ("MKC", "MKC-V"), ("TAP", "TAP-A"), ("BIO", "BIO-B")]
DEV_END, HO_START = pd.Timestamp("2017-12-31"), pd.Timestamp("2018-01-01")
BORROW = 0.02
PRIMARY = (60, 2.0)
GRID = [(w, e) for w in (20, 60, 120) for e in (1.5, 2.0, 2.5)]
MAX_HOLD = 20


def cs_spread(h, l):
    """Corwin-Schultz (2012) bid-ask spread estimate from daily highs/lows; 20-day median, floor 2 bp (full spread)."""
    lh = np.log(h / l) ** 2
    beta = lh + lh.shift(1)
    gamma = np.log(np.maximum(h, h.shift(1)) / np.minimum(l, l.shift(1))) ** 2
    k = 3 - 2 * math.sqrt(2)
    alpha = (np.sqrt(2 * beta) - np.sqrt(beta)) / k - np.sqrt(gamma / k)
    s = (2 * (np.exp(alpha) - 1) / (1 + np.exp(alpha))).clip(lower=0)
    return s.rolling(20, min_periods=5).median().fillna(0.002).clip(lower=0.0002)


def trades_for(cA, cB, sA, sB, window, entry):
    """Trades for one pair. cA/cB adjusted closes (aligned), sA/sB full-spread estimates."""
    r = np.log(cA) - np.log(cB)
    mu = r.rolling(window).mean().shift(1); sd = r.rolling(window).std().shift(1)
    z = ((r - mu) / sd).to_numpy(); idx = r.index; A = cA.to_numpy(); B = cB.to_numpy(); SA = sA.to_numpy(); SB = sB.to_numpy()
    out = []; i = window + 1; n = len(r)
    while i < n - 2:
        if np.isfinite(z[i]) and abs(z[i]) >= entry:
            side = -1 if z[i] > 0 else 1            # z>0: A rich -> short A, long B
            e = i + 1                                # trade at next close
            x = None
            for j in range(e, min(e + MAX_HOLD, n - 1)):
                if np.isfinite(z[j]) and np.sign(z[j]) != np.sign(z[i]):      # crossed zero
                    x = j + 1; break
            if x is None: x = min(e + MAX_HOLD, n - 1)
            ra, rb = A[x] / A[e] - 1, B[x] / B[e] - 1
            gross = side * (ra - rb)
            cost = (SA[e] + SB[e] + SA[x] + SB[x]) / 2          # half-spread per leg, in and out
            days = x - e
            net = gross - cost - BORROW * days / 252
            out.append(dict(entry=idx[e], exit=idx[x], days=days, side=side, gross=gross, cost=cost, net=net))
            i = x + 1
        else:
            i += 1
    return pd.DataFrame(out)


def stats(T):
    if T.empty: return dict(n=0)
    x = T.net.to_numpy(); w, l = x[x > 0].sum(), -x[x <= 0].sum()
    yrs = max((T.exit.max() - T.entry.min()).days / 365.25, 0.5)
    return dict(n=len(x), per_yr=round(len(x) / yrs, 1), win=round((x > 0).mean(), 3), mean_bp=round(x.mean() * 1e4, 1),
                t=round(x.mean() / x.std(ddof=1) * math.sqrt(len(x)), 2) if len(x) > 2 else np.nan,
                pf=round(w / l, 2) if l > 0 else np.inf, avg_win_bp=round(x[x > 0].mean() * 1e4, 1) if (x > 0).any() else np.nan,
                avg_loss_bp=round(x[x <= 0].mean() * 1e4, 1) if (x <= 0).any() else np.nan, worst_bp=round(x.min() * 1e4, 1), cost_bp=round(T.cost.mean() * 1e4, 1))


def portfolio(T, days, n_slots):
    """Daily return: each trade's net return spread evenly over its holding days, divided by the number of pair slots."""
    ret = pd.Series(0.0, index=days)
    for t in T.itertuples():
        span = days[(days > t.entry) & (days <= t.exit)]
        if len(span): ret.loc[span] += t.net / len(span) / n_slots
    eq = (1 + ret).cumprod(); dd = float((1 - eq / eq.cummax()).max())
    yrs = len(ret) / 252
    sh = float(ret.mean() / ret.std() * math.sqrt(252)) if ret.std() > 0 else float("nan")
    return dict(cagr=round((eq.iloc[-1] ** (1 / yrs) - 1) * 100, 2) if yrs > 0 else np.nan, sharpe=round(sh, 2), maxdd=round(dd * 100, 2))


def evaluate(data, window, entry):
    """data: {pair: (cA, cB, sA, sB)} -> (all trades, per-pair counts)."""
    allT = []
    for name, (cA, cB, sA, sB) in data.items():
        T = trades_for(cA, cB, sA, sB, window, entry)
        if len(T): allT.append(T.assign(pair=name))
    return pd.concat(allT, ignore_index=True) if allT else pd.DataFrame(columns=["entry", "exit", "days", "side", "gross", "cost", "net", "pair"])


def verdict(T, days, n_slots):
    s = stats(T)
    if not s.get("n"): return s, {}, False
    p = portfolio(T, days, n_slots)
    ok = s["win"] >= 0.70 and s["mean_bp"] > 0 and s["t"] >= 2.5 and s["pf"] >= 1.5 and s["per_yr"] >= 20 and p["sharpe"] >= 1.0 and p["maxdd"] <= 15
    return s, p, ok


def run(data, days):
    dev_days, ho_days = days[days <= DEV_END], days[days >= HO_START]
    n = len(data)
    G = []
    for w, e in GRID:
        T = evaluate(data, w, e)
        d = T[T.entry <= DEV_END]; s = stats(d); G.append(dict(window=w, entry=e, **{f"dev_{k}": v for k, v in s.items()}))
    G = pd.DataFrame(G)
    ok = G[G.dev_n >= 50] if "dev_n" in G else G.iloc[:0]
    choice = tuple(ok.sort_values("dev_mean_bp", ascending=False).iloc[0][["window", "entry"]]) if len(ok) else PRIMARY
    res = {}
    for lab, (w, e) in (("primary", PRIMARY), ("dev choice", (int(choice[0]), float(choice[1])))):
        T = evaluate(data, w, e)
        H = T[T.entry >= HO_START]; D = T[T.entry <= DEV_END]
        sh, ph, okh = verdict(H, ho_days, n); sd_, pd_, _ = verdict(D, dev_days, n)
        res[lab] = dict(w=w, e=e, T=T, ho=sh, ho_port=ph, dev=sd_, dev_port=pd_, PASS=okh)
    return G, res


# ---------------------------------------------------------------- calibration
def synthetic(planted, n_pairs=12, seed=5):
    rng = np.random.default_rng(seed); days = pd.bdate_range("2010-01-04", "2026-11-20"); n = len(days); data = {}
    for k in range(n_pairs):
        b = 50 * np.exp(np.cumsum(rng.normal(0.0003, 0.018, n)))
        if planted:
            th = math.log(2) / 10; g = np.zeros(n)
            for i in range(1, n): g[i] = g[i - 1] * (1 - th) + rng.normal(0, 0.015 * math.sqrt(2 * th))
            a = b * np.exp(g)
        else:
            a = 50 * np.exp(np.cumsum(rng.normal(0.0003, 0.018, n)))
        s = pd.Series(0.001, index=days)
        data[f"P{k}"] = (pd.Series(a, index=days), pd.Series(b, index=days), s, s)
    return data, days


def smoke():
    out = {}
    for planted in (True, False):
        for seed in (5, 6):
            data, days = synthetic(planted, seed=seed)
            G, res = run(data, days)
            r = res["primary"]; out[(planted, seed)] = r["PASS"]
            print("planted" if planted else "null", seed, "PASS", r["PASS"], r["ho"], r["ho_port"])
    assert all(out[(True, s)] for s in (5, 6)) and not any(out[(False, s)] for s in (5, 6)), "calibration failed"
    print("smoke OK")


# ---------------------------------------------------------------- real data
def load():
    import yfinance as yf
    tick = sorted({t for p in PAIRS for t in p})
    d = yf.download(tick, start="2009-06-01", auto_adjust=True, progress=False, group_by="column", threads=True)
    C, Hh, L = d["Close"], d["High"], d["Low"]
    data, cov = {}, []
    for a, b in PAIRS:
        if a not in C or b not in C:
            cov.append(dict(pair=f"{a}/{b}", days=0, start=None, note="missing")); continue
        j = pd.concat([C[a], C[b], Hh[a], L[a], Hh[b], L[b]], axis=1, keys=["ca", "cb", "ha", "la", "hb", "lb"]).dropna()
        j = j[(j.ca > 0) & (j.cb > 0)]
        cov.append(dict(pair=f"{a}/{b}", days=len(j), start=j.index.min().date() if len(j) else None, end=j.index.max().date() if len(j) else None,
                        note="kept" if len(j) >= 500 else "dropped (< 500 days)"))
        if len(j) >= 500:
            data[f"{a}/{b}"] = (j.ca, j.cb, cs_spread(j.ha, j.la), cs_spread(j.hb, j.lb))
    days = pd.DatetimeIndex(sorted(set().union(*[v[0].index for v in data.values()])))
    return data, days, pd.DataFrame(cov)


def report():
    data, days, cov = load()
    G, res = run(data, days)
    out = ["# Round 71: share-class pairs (buy the cheap class, sell the rich class, wait for the gap to close)", "", "Rules: [PROTOCOL_ROUND71.md](../PROTOCOL_ROUND71.md).", "",
           f"Pairs kept: {len(data)} of {len(PAIRS)}. Dev 2010–2017, holdout 2018 → {days.max().date()}. Costs: half the Corwin–Schultz spread per leg in and out, 2%/yr borrow.", "",
           f"**Verdict (primary rule, holdout): {'PASS → live paper tracker' if res['primary']['PASS'] else 'FAIL'}.**", ""]
    for lab, r in res.items():
        out += [f"## {lab}: window {r['w']}, entry |z| ≥ {r['e']}", "", pd.DataFrame([dict(part="dev", **r["dev"], **r["dev_port"]), dict(part="holdout", **r["ho"], **r["ho_port"])]).to_markdown(index=False), ""]
        H = r["T"][r["T"].entry >= HO_START]
        if len(H):
            out += ["Holdout by pair:", "", H.groupby("pair").apply(lambda g: pd.Series(stats(g))).to_markdown(), ""]
    out += ["## Dev grid", "", G.to_markdown(index=False), "", "## Data coverage", "", cov.to_markdown(index=False), ""]
    open("reports/ROUND71.md", "w").write("\n".join(out) + "\n"); print("\n".join(out[:40]))


if __name__ == "__main__":
    {"smoke": smoke, "report": report}[sys.argv[1]]()

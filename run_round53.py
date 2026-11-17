"""Round 53 (PROTOCOL_ROUND53.md): exhaustive NY-session grid on S&P and Nasdaq micros."""
import itertools, math, os, sys, time
import numpy as np, pandas as pd
from edge import nygrid as G
from edge import stats as S
from edge.intraday import load_nq

SPLIT = pd.Timestamp("2021-01-01")
MARKETS = {"SP": dict(pair="SPXUSD", pt=5.0, slip=0.5), "NQ": dict(pair="NSXUSD", pt=2.0, slip=1.25)}
COMM, RISK, MAXC = 1.24, 250.0, 15
FAMS = [("ORB5", 0, 5), ("ORB15", 0, 15), ("ORB30", 0, 30), ("ORB60", 0, 60), ("ORfade15", 1, 15), ("ORfade30", 1, 30),
        ("GapFill0.2", 2, 0.002), ("GapFill0.5", 2, 0.005), ("GapGo0.2", 3, 0.002), ("GapGo0.5", 3, 0.005),
        ("FirstHour0.2", 4, 0.002), ("FirstHour0.4", 4, 0.004), ("PrevDayBreak", 5, 0), ("OvernightBreak", 6, 0),
        ("PowerHour0.3", 7, 0.003), ("StretchFade0.5", 8, 0.005)]
STOPS = [("structure", 0, 0.0), ("0.25%", 1, 0.0025), ("0.5%", 1, 0.005)]
RRS = [1.0, 2.0, 3.0, 0.0]
FLATS = [("11:30", 120), ("15:55", 385)]
FILTERS = ["none", "with_gap", "with_trend20", "skip_mon_fri", "high_vol", "low_vol"]


def filter_mask(name, M, side):
    D = len(M["days"]); ok = np.ones(D, bool)
    if name == "with_gap":
        g = np.sign(M["o"][:, 0] - M["prev_close"]); ok = (g == side)
    elif name == "with_trend20":
        ok = (np.sign(M["prev_close"] - M["prev_sma20"]) == side)
    elif name == "skip_mon_fri":
        wd = M["days"].weekday; ok = (wd != 0) & (wd != 4)
    elif name == "high_vol":
        ok = M["prev_rng"] >= M["rng_med"]
    elif name == "low_vol":
        ok = M["prev_rng"] < M["rng_med"]
    return ok & np.isfinite(M["prev_close"])


def config_series(M, cfg, mk, fam, p, stop_mode, stop_pct, rr, flat, filt, cache):
    key = (fam, p, flat)
    if key not in cache:
        cache[key] = G.entries(fam, p, M["o"], M["h"], M["l"], M["c"], M["prev_close"], M["prev_hi"], M["prev_lo"],
                               M["on_hi"], M["on_lo"], flat)
    ent, side, sstop = cache[key]
    tov = M["prev_close"].copy() if fam == 2 else np.full(len(ent), np.nan)
    e, x, risk = G.run_config(M["o"], M["h"], M["l"], M["c"], ent, side, sstop, stop_mode, stop_pct, rr, flat, tov)
    ok = np.isfinite(x) & filter_mask(filt, M, side)
    pts = side * (x - e) - cfg["slip"]
    n = np.clip(np.floor(RISK / np.maximum(risk * cfg["pt"], 1e-9)), 1, MAXC)
    usd = np.where(ok, n * pts * cfg["pt"] - n * COMM, 0.0)
    R = np.where(ok, pts / risk, np.nan)
    return pd.Series(usd, index=M["days"]), pd.Series(R, index=M["days"])


def grid():
    for (fname, fam, p), (sname, sm, sp), rr, (flname, flat), filt in itertools.product(FAMS, STOPS, RRS, FLATS, FILTERS):
        if sm == 0 and fam not in (0, 1, 5, 6):
            continue                                   # structural stop only where a structure exists
        if fam == 2 and rr != 0.0:
            continue                                   # gap fill targets the prior close
        if fam == 7:
            if flname != "15:55": continue
            flat = 390; flname = "15:59"
        yield fname, fam, p, sname, sm, sp, rr, flname, flat, filt


def stats_of(R, usd, a, b):
    m = (R.index >= a) & (R.index < b)
    r = R[m].dropna()
    if len(r) < 20:
        return dict(n=len(r), meanR=np.nan, t=np.nan, win=np.nan, usd_month=np.nan, sr_daily=np.nan)
    u = usd[m]
    return dict(n=len(r), meanR=r.mean(), t=r.mean() / r.std() * math.sqrt(len(r)) if r.std() > 0 else np.nan,
                win=(r > 0).mean(), usd_month=u.sum() / max((u.index[-1] - u.index[0]).days / 30.4, 1),
                sr_daily=u.mean() / u.std() if u.std() > 0 else np.nan)


def main(limit=None):
    t0 = time.time()
    data = {}
    for mk, cfg in MARKETS.items():
        bars = load_nq(pair=cfg["pair"])
        data[mk] = G.day_matrix(bars)
        print(mk, "days", len(data[mk]["days"]), data[mk]["days"][0].date(), "->", data[mk]["days"][-1].date(), flush=True)
    end = pd.Timestamp("2100-01-01"); start = pd.Timestamp("2000-01-01")
    rows = []
    configs = list(grid())[: limit or None]
    print("configs per market", len(configs), flush=True)
    for mk, cfg in MARKETS.items():
        M = data[mk]; cache = {}
        for c in configs:
            fname, fam, p, sname, sm, sp, rr, flname, flat, filt = c
            usd, R = config_series(M, cfg, mk, fam, p, sm, sp, rr, flat, filt, cache)
            dv, ho = stats_of(R, usd, start, SPLIT), stats_of(R, usd, SPLIT, end)
            rows.append(dict(market=mk, entry=fname, stop=sname, target=("prior close" if fam == 2 else f"{rr:g}R" if rr else "time"),
                             exit=flname, filter=filt, **{f"dev_{k}": v for k, v in dv.items()}, **{f"ho_{k}": v for k, v in ho.items()}, _cfg=c))
        print(mk, "done", round(time.time() - t0), "s", flush=True)
    T = pd.DataFrame(rows)
    N = len(T); var_sr = float(np.nanvar(T.ho_sr_daily))
    # candidates: strict statistical screen first, then DSR, cross-market and prop scoring
    cand = T[(T.ho_t >= 3) & (T.ho_meanR > 0) & (T.dev_t >= 2) & (T.dev_meanR > 0)].copy()
    out_c = []
    for _, r in cand.iterrows():
        M = data[r.market]; cfg = MARKETS[r.market]
        fname, fam, p, sname, sm, sp, rr, flname, flat, filt = r._cfg
        usd, R = config_series(M, cfg, r.market, fam, p, sm, sp, rr, flat, filt, {})
        hu = usd[usd.index >= SPLIT]
        dsr = S.deflated_sharpe(hu, N, var_sr)
        other = "NQ" if r.market == "SP" else "SP"
        ou, oR = config_series(data[other], MARKETS[other], other, fam, p, sm, sp, rr, flat, filt, {})
        other_meanR = oR[oR.index >= SPLIT].mean()
        days = hu.index; starts = np.array([i for i, d in enumerate(days) if d.weekday() == 0], dtype=np.int64)
        passed, used, funded = G.prop_sim(hu.to_numpy(), starts)
        pr = passed.mean() if len(passed) else np.nan; ev = funded.mean() - 150 if len(funded) else np.nan
        ok = dsr >= 0.95 and other_meanR > 0 and pr >= 0.5 and ev > 0
        out_c.append(dict(market=r.market, entry=r.entry, stop=r.stop, target=r.target, exit=r.exit, filter=r.filter,
                          ho_n=r.ho_n, ho_meanR=round(r.ho_meanR, 3), ho_t=round(r.ho_t, 2), dev_t=round(r.dev_t, 2),
                          ho_usd_month=round(r.ho_usd_month, 0), dsr=round(dsr, 3), other_mkt_meanR=round(other_meanR, 3),
                          prop_pass=f"{pr:.0%}", ev_per_attempt=round(ev, 0), PASS="YES" if ok else ""))
    C = pd.DataFrame(out_c)
    top = T.sort_values("ho_t", ascending=False).head(40).copy()
    show = top[["market", "entry", "stop", "target", "exit", "filter", "dev_n", "dev_meanR", "dev_t", "ho_n", "ho_meanR", "ho_t", "ho_win", "ho_usd_month"]].round(3)
    out = ["# Round 53: exhaustive New York-session grid (S&P and Nasdaq micros)", "",
           f"Rules: [PROTOCOL_ROUND53.md](../PROTOCOL_ROUND53.md). Configurations run: **{N}** ({N // 2} per market). "
           f"Holdout = 2021 → now. Runtime {round(time.time() - t0)} s.", "",
           f"Screen (holdout t ≥ 3 and dev t ≥ 2, both positive): **{len(cand)}** candidates. "
           f"Full pass (also deflated Sharpe ≥ 0.95, positive on the other market, prop pass ≥ 50%, EV > 0): "
           f"**{int((C.PASS == 'YES').sum()) if len(C) else 0}**.", ""]
    if len(C):
        out += ["## Candidates", "", C.sort_values("ho_t", ascending=False).to_markdown(index=False), ""]
    out += ["## Top 40 by holdout t (all configurations)", "", show.to_markdown(index=False), "",
            "## Share of configurations with holdout mean R > 0, by entry family", "",
            T.groupby(["market", "entry"]).apply(lambda x: f"{(x.ho_meanR > 0).mean():.0%} of {len(x)}", include_groups=False).unstack(0).to_markdown()]
    os.makedirs("reports", exist_ok=True)
    T.drop(columns=["_cfg"]).to_csv("reports/round53_all.csv", index=False)
    open("reports/ROUND53.md", "w").write("\n".join(out) + "\n"); print("\n".join(out[:12]))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else None)

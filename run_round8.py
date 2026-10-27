"""Round 8 runner (PROTOCOL_ROUND8.md).

    python run_round8.py fetch13f <cik> | fetchptr <year> | prices | dev | final

dev cuts every price and filing after 2021-12-31 before computing anything,
and appends each config it scores to reports/round8_dev_log.csv.
final runs only round8_frozen.json (plus the baselines) on 2022-01-01 onward.
"""
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from edge import copytrade as ct
from edge import round8 as r8
from edge.stats import deflated_sharpe

DATA = Path("data/r8")
DATA.mkdir(parents=True, exist_ok=True)
REPORTS = Path("reports")
DEV_LOG = REPORTS / "round8_dev_log.csv"
FROZEN = Path("round8_frozen.json")
FILERS = json.loads(Path("edge/r8_filers.json").read_text())
PRIOR_TRIALS = 211
SMALL = os.environ.get("R8_SMALL") == "1"  # smoke test: tiny slice, fast fail, results not logged as trials


def fetch13f(cik):
    name = next(f["name"] for f in FILERS if f["cik"] == cik)
    ct.fetch_13f(cik, name).to_pickle(DATA / f"13f_{cik}.pkl")


CACHE13F = Path("cache13f")  # committed: survives between the scheduled SEC attempts


def sec13f():
    """One polite pass over the funds not fetched yet. Stops at the first SEC 403."""
    CACHE13F.mkdir(exist_ok=True)
    todo = [f for f in FILERS if not (CACHE13F / f"13f_{f['cik']}.pkl").exists()]
    print(f"{len(FILERS) - len(todo)} of {len(FILERS)} funds cached; fetching {len(todo)}", flush=True)
    for f in todo:
        try:
            df = ct.fetch_13f(f["cik"], f["name"])
        except ct.SecBlocked as e:
            print(f"SEC rate threshold at {e}; stopping until the next scheduled attempt", flush=True)
            break
        df.to_pickle(CACHE13F / f"13f_{f['cik']}.pkl")
    left = sum(not (CACHE13F / f"13f_{f['cik']}.pkl").exists() for f in FILERS)
    print(f"funds still missing: {left}")
    if left == 0 and todo:
        Path("cache13f/COMPLETE").write_text(pd.Timestamp.now(tz="UTC").isoformat())


def fetchptr(year):
    ct.fetch_congress_year(int(year)).to_pickle(DATA / f"ptr_{year}.pkl")


def prices():
    import yfinance as yf
    files = list(DATA.glob("13f_*.pkl")) + list(Path("cache13f").glob("13f_*.pkl"))
    h = pd.concat([pd.read_pickle(p) for p in files], ignore_index=True) if files else pd.DataFrame(
        columns=["cik", "fund", "accession", "filed", "period", "cusip", "issuer", "value", "shares", "weight", "rank"])
    cus = sorted(h["cusip"].unique())
    print(f"13F rows {len(h):,}, unique CUSIPs {len(cus):,}; mapping via OpenFIGI", flush=True)
    m = ct.figi_map(cus) if cus else {}
    h["ticker"] = h["cusip"].map(m)
    if cus:
        print(f"  mapped {len(m):,} of {len(cus):,} CUSIPs ({h['ticker'].notna().mean():.1%} of rows)", flush=True)
    h.to_pickle(DATA / "holdings.pkl")
    c = pd.concat([pd.read_pickle(p) for p in DATA.glob("ptr_*.pkl")], ignore_index=True)
    if SMALL:
        c = c[c["filed"].between("2019-01-01", "2020-12-31")]
    c.to_pickle(DATA / "congress.pkl")
    buys = c[c["asset_type"].isin(["ST", "OP"]) & (c["type"] == "P")]["ticker"].str.replace(".", "-", regex=False)
    tks = set(h["ticker"].dropna()) | set(buys)
    tks = ["SPY"] + sorted(tks - {"SPY"})
    if SMALL:
        tks = ["SPY"] + list(buys.value_counts().index.drop("SPY", errors="ignore")[:60])
    print(f"downloading {len(tks):,} tickers", flush=True)
    got = {}
    waits = (0, 60) if SMALL else (0, 180, 600)
    for rnd, wait in enumerate(waits):  # Yahoo rate-limits bursts: small batches, back off between rounds
        miss = [t for t in tks if t not in got]
        if not miss:
            break
        time.sleep(wait)
        for i in range(0, len(miss), 40):
            chunk = miss[i:i + 40]
            raw = yf.download(chunk, start="2013-06-01", auto_adjust=True, progress=False, threads=False)
            if raw is None or raw.empty:
                continue
            close = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw[["Close"]].rename(
                columns={"Close": chunk[0]})
            for t in close.columns[close.notna().any()]:
                got[t] = close[t]
            print(f"    batch {i // 40 + 1}: {len(got):,} priced so far", flush=True)
            if rnd == 0 and i >= 80 and len(got) == 0:  # fail fast: 3 batches and nothing came back
                raise RuntimeError("Yahoo returned no prices for the first 120 tickers: blocked, stopping now")
            time.sleep(4)
        print(f"  round {rnd + 1}: {len(got):,} of {len(tks):,} tickers priced", flush=True)
    if "SPY" not in got:
        raise RuntimeError("no SPY prices: Yahoo still rate-limiting; rerun later")
    px = pd.concat(got, axis=1)
    px = px.loc[:, px.notna().sum() > 20].dropna(subset=["SPY"]).sort_index()
    px.index = pd.DatetimeIndex(px.index).tz_localize(None)
    print(f"prices: {px.shape[1]:,} tickers with data, {px.index[0].date()} to {px.index[-1].date()}")
    px.to_pickle(DATA / "prices.pkl")


# ------------------------------------------------------------------ configs

def configs():
    """Every config the dev search may score. Declared here, before the dev run."""
    out = [dict(id="13F-base-avg", kind="13f_avg", n=10, weight="value", select="all"),
           dict(id="Congress-base", kind="congress", hold=60, assets=["ST"], min_amount=0, max_delay=None,
                members=None)]
    for f in FILERS:
        out.append(dict(id=f"13F-base-{f['short']}", kind="13f_fund", cik=f["cik"], n=10, weight="value",
                        select="all"))
    for n in (5, 10, 20):
        for w in ("value", "equal"):
            for s in ("all", "added"):
                if (n, w, s) != (10, "value", "all"):
                    out.append(dict(id=f"13F-avg-n{n}-{w}-{s}", kind="13f_avg", n=n, weight=w, select=s))
        out.append(dict(id=f"13F-consensus-n{n}", kind="13f_consensus", n=n))
    for hold in (5, 20, 60, 120):
        for assets in (["ST"], ["ST", "OP"]):
            for mina in (0, 15001, 50001):
                for delay in (None, 15):
                    cid = f"Congress-h{hold}-{'+'.join(assets)}-min{mina}-d{delay or 'any'}"
                    out.append(dict(id=cid, kind="congress", hold=hold, assets=assets, min_amount=mina,
                                    max_delay=delay, members=None))
        out.append(dict(id=f"Pelosi-h{hold}-ST+OP", kind="congress", hold=hold, assets=["ST", "OP"],
                        min_amount=0, max_delay=None, members=["Pelosi"]))
    seen, uniq = set(), []
    for c in out:  # the base config is also generated by the grid; keep one copy
        key = json.dumps({k: v for k, v in c.items() if k != "id"}, sort_keys=True)
        if key not in seen:
            seen.add(key)
            uniq.append(c)
    return uniq


def run_config(c, h, cg, px):
    if c["kind"] == "13f_fund":
        return r8.run_portfolios(r8.portfolios_13f(h[h["cik"] == c["cik"]], c["n"], c["weight"], c["select"]), px)
    if c["kind"] == "13f_avg":
        return r8.average_series([r8.run_portfolios(r8.portfolios_13f(g, c["n"], c["weight"], c["select"]), px)
                                  for _, g in h.groupby("cik")])
    if c["kind"] == "13f_consensus":
        return r8.run_portfolios(r8.consensus_portfolios(h, c["n"]), px)
    e = r8.congress_events(cg, px, tuple(c["assets"]), c["min_amount"], c["max_delay"], c["members"])
    return r8.run_events(e, px, c["hold"])


def load(cut_end=None):
    h = pd.read_pickle(DATA / "holdings.pkl")
    h["filed"] = pd.to_datetime(h["filed"])
    cg = pd.read_pickle(DATA / "congress.pkl")
    cg = cg[cg["filed"].notna()]
    px = pd.read_pickle(DATA / "prices.pkl")
    if cut_end is not None:  # the seal: nothing after the dev period reaches any calculation
        h, cg, px = h[h["filed"] <= cut_end], cg[cg["filed"] <= cut_end], px[px.index <= cut_end]
    return h, cg, px


def table(rows):
    df = pd.DataFrame(rows)
    cols = ["id", "start", "end", "cagr", "spy_cagr", "excess_ann", "ir", "excess_mdd", "beat_spy_months",
            "usd_1000", "usd_1000_spy", "trades"]
    df = df[[c for c in cols if c in df]]
    fmt = {"cagr": "{:+.1%}", "spy_cagr": "{:+.1%}", "excess_ann": "{:+.1%}", "ir": "{:+.2f}",
           "excess_mdd": "{:.1%}", "beat_spy_months": "{:.0%}", "usd_1000": "${:,.0f}", "usd_1000_spy": "${:,.0f}"}
    for k, f in fmt.items():
        if k in df:
            df[k] = df[k].map(lambda v, f=f: f.format(v) if pd.notna(v) else "")
    return df.to_markdown(index=False)


def dev():
    h, cg, px = load(r8.DEV_END)
    spy = px["SPY"].pct_change(fill_method=None)
    stamp = pd.Timestamp.now(tz="UTC").isoformat(timespec="seconds")
    rows = []
    cfgs = [c for c in configs() if len(h) or not c["kind"].startswith("13f")]  # unrun configs are not trials
    for c in cfgs:
        s = r8.score(run_config(c, h, cg, px), spy)
        if c["kind"] == "congress":
            s["trades"] = len(r8.congress_events(cg, px, tuple(c["assets"]), c["min_amount"], c["max_delay"],
                                                 c["members"]))
        rows.append(dict(id=c["id"], **s))
        print(f"  {c['id']}: IR {s.get('ir', float('nan')):+.2f}", flush=True)
    if not SMALL:
        log = pd.DataFrame(rows).assign(run_utc=stamp, config=[json.dumps(c) for c in cfgs])
        log.to_csv(DEV_LOG, mode="a", header=not DEV_LOG.exists(), index=False)
    n_dev = pd.read_csv(DEV_LOG)["id"].nunique() if DEV_LOG.exists() else 0
    data_note = (f"13F: {h['cik'].nunique()} funds, {h['accession'].nunique():,} filings, "
                 f"{h['ticker'].notna().mean():.0%} of holdings mapped to a priced ticker. " if len(h) else
                 "13F: no data yet (SEC blocks GitHub's servers; to be fetched from the owner's computer). ")
    data_note += (
                 f"Congress: {len(cg):,} parsed transactions from {cg['doc_id'].nunique():,} reports, "
                 f"{(cg['type'] == 'P').sum():,} purchases, {cg['member'].nunique()} members.")
    df = pd.DataFrame(rows)
    groups = [("Baselines", df["id"].str.contains("base-avg|Congress-base")),
              ("13F, one fund each (top 10, value-weighted)", df["id"].str.startswith("13F-base-") &
               ~df["id"].str.contains("avg")),
              ("13F tweaks", df["id"].str.startswith("13F-avg-") | df["id"].str.startswith("13F-consensus")),
              ("Congress tweaks", df["id"].str.startswith("Congress-h")),
              ("Pelosi only", df["id"].str.startswith("Pelosi"))]
    lines = ["# Round 8, development period (2014 → 2021-12-31)", "",
             f"Run {stamp}. Sealed data (2022 onward) was cut before any calculation. "
             f"Distinct dev configs logged so far: {n_dev} (each adds to the trial count for the final test).",
             "", data_note, "",
             "Columns: CAGR of the strategy and of SPY over the same days; excess = annual return over SPY; "
             "IR = information ratio (pass needs ≥ 0.5 in the sealed period); excess MDD = worst drop of "
             "the strategy relative to SPY; $1000 = what $1,000 grew to.", ""]
    for title, mask in groups:
        sub = df[mask].sort_values("ir", ascending=False)
        if len(sub):
            lines += [f"## {title}", "", table(sub.to_dict("records")), ""]
    if SMALL:
        lines[0] = "# Round 8 SMOKE TEST (pipeline check: 2019-2020 filings, 60 tickers; not results)"
    (REPORTS / ("ROUND8_SMOKE.md" if SMALL else "ROUND8_DEV.md")).write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def final():
    frozen = json.loads(FROZEN.read_text())
    n_trials = PRIOR_TRIALS + pd.read_csv(DEV_LOG)["id"].nunique()
    h, cg, px = load()
    spy = px["SPY"].pct_change(fill_method=None)
    cfgs = {c["id"]: c for c in configs()}
    ids = ["13F-base-avg", "Congress-base"] + frozen["ids"]
    lines = ["# Round 8, sealed test (2022-01-01 onward)", "",
             f"Frozen: {frozen['ids']}. Trials deflated over: {n_trials}.", "",
             "| Config | Dev IR | Sealed IR | Sealed DSR | Sealed excess MDD | Sealed CAGR | SPY CAGR | Pass |",
             "|---|---:|---:|---:|---:|---:|---:|---|"]
    for cid in ids:
        r = run_config(cfgs[cid], h, cg, px)
        d = r8.score(r[r.index <= r8.DEV_END], spy)
        sealed = r[r.index >= r8.SEALED_START]
        s = r8.score(sealed, spy)
        x = (sealed - spy.reindex(sealed.index)).dropna()
        dsr = deflated_sharpe(x, n_trials, 1 / len(x)) if len(x) > 60 else 0.0
        ok = s.get("ir", -9) >= 0.5 and dsr >= 0.95 and d.get("ir", -9) > 0 and s.get("excess_mdd", -1) >= -0.25
        lines.append(f"| {cid} | {d.get('ir', np.nan):+.2f} | {s.get('ir', np.nan):+.2f} | {dsr:.3f} | "
                     f"{s.get('excess_mdd', np.nan):.1%} | {s.get('cagr', np.nan):+.1%} | "
                     f"{s.get('spy_cagr', np.nan):+.1%} | **{'PASS' if ok else 'FAIL'}** |")
    (REPORTS / "ROUND8.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "list13f":
        print(json.dumps([f["cik"] for f in FILERS]))
    else:
        {"fetch13f": fetch13f, "sec13f": sec13f, "fetchptr": fetchptr, "prices": prices, "dev": dev, "final": final}[mode](*sys.argv[2:])

"""Round 48 (PROTOCOL_ROUND48.md): SEC Form 4 insider open-market purchases."""
import io, math, os, sys, time, zipfile
import numpy as np, pandas as pd, requests

UA = {"User-Agent": "ryofencellc-collab-research 265339802+ryofencellc-collab@users.noreply.github.com", "Accept-Encoding": "gzip, deflate"}
URL = "https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets/{}q{}_form345.zip"
OUT, PX = "data/r48", "data/r38"
DEV0, SPLIT, END = pd.Timestamp("2015-01-01"), pd.Timestamp("2022-01-01"), pd.Timestamp("2026-11-01")


def read_tsv(z, name, cols):
    f = [n for n in z.namelist() if n.upper().endswith(name)]
    d = pd.read_csv(z.open(f[0]), sep="\t", dtype=str, on_bad_lines="skip", low_memory=False)
    d.columns = [c.upper() for c in d.columns]
    miss = [c for c in cols if c not in d.columns]
    if miss:
        raise KeyError(f"{name} missing {miss}; has {list(d.columns)[:40]}")
    return d[cols]


def quarter(y, q, s):
    r = s.get(URL.format(y, q), timeout=120)
    if r.status_code != 200:
        print("skip", y, q, r.status_code, flush=True); return None
    z = zipfile.ZipFile(io.BytesIO(r.content))
    sub = read_tsv(z, "SUBMISSION.TSV", ["ACCESSION_NUMBER", "FILING_DATE", "DOCUMENT_TYPE", "ISSUERTRADINGSYMBOL"])
    own = read_tsv(z, "REPORTINGOWNER.TSV", ["ACCESSION_NUMBER", "RPTOWNERCIK", "RPTOWNER_RELATIONSHIP", "RPTOWNER_TITLE"])
    tr = read_tsv(z, "NONDERIV_TRANS.TSV", ["ACCESSION_NUMBER", "SECURITY_TITLE", "TRANS_CODE", "TRANS_SHARES", "TRANS_PRICEPERSHARE", "TRANS_ACQUIRED_DISP_CD"])
    tr = tr[(tr.TRANS_CODE == "P") & (tr.TRANS_ACQUIRED_DISP_CD == "A")].copy()
    tr["value"] = pd.to_numeric(tr.TRANS_SHARES, errors="coerce") * pd.to_numeric(tr.TRANS_PRICEPERSHARE, errors="coerce")
    tr = tr[tr.SECURITY_TITLE.fillna("").str.contains("common|ordinary|class a|class b", case=False)]
    v = tr.groupby("ACCESSION_NUMBER").value.sum().rename("value").reset_index()
    own = own.groupby("ACCESSION_NUMBER").agg(owner=("RPTOWNERCIK", "first"), rel=("RPTOWNER_RELATIONSHIP", "first"), title=("RPTOWNER_TITLE", "first")).reset_index()
    d = v.merge(sub, on="ACCESSION_NUMBER").merge(own, on="ACCESSION_NUMBER", how="left")
    d = d[d.DOCUMENT_TYPE.isin(["4", "4/A"])]
    d["filed"] = pd.to_datetime(d.FILING_DATE, format="%d-%b-%Y", errors="coerce")
    d["sym"] = d.ISSUERTRADINGSYMBOL.fillna("").str.upper().str.strip()
    return d[["filed", "sym", "owner", "rel", "title", "value"]].dropna(subset=["filed"])


def filings():
    p = f"{OUT}/buys.pkl"
    if os.path.exists(p): return pd.read_pickle(p)
    os.makedirs(OUT, exist_ok=True)
    s = requests.Session(); s.headers.update(UA)
    parts = []
    for y in range(2015, 2027):
        for q in range(1, 5):
            if (y, q) > (2026, 3): break
            d = quarter(y, q, s)
            if d is not None:
                parts.append(d); print(y, q, len(d), flush=True)
            time.sleep(0.5)
    d = pd.concat(parts, ignore_index=True); d.to_pickle(p); return d


def prices():
    O, C, V = (pd.read_pickle(f"{PX}/stocks_{k}.pkl").astype(float) for k in "OCV")
    R = pd.read_pickle(f"{PX}/stocks_R.pkl").astype(float).reindex(index=C.index, columns=C.columns)
    O, V = O.reindex(index=C.index, columns=C.columns), V.reindex(index=C.index, columns=C.columns)
    dv = (R * V).rolling(20, min_periods=15).mean()
    import yfinance as yf
    spy = yf.download("SPY", start="2014-06-01", auto_adjust=True, progress=False)
    so, sc = spy["Open"].squeeze(), spy["Close"].squeeze()
    so.index = sc.index = pd.to_datetime(sc.index).tz_localize(None)
    return O, C, R, dv, so.reindex(C.index), sc.reindex(C.index)


def events(b, rule):
    b = b.sort_values("filed")
    is_off = b.rel.fillna("").str.contains("Officer|Director", case=False) | b.title.fillna("").str.len().gt(0)
    ceo = b.title.fillna("").str.contains(r"\bCEO\b|Chief Executive|\bCFO\b|Chief Financial", case=False, regex=True)
    if rule in ("I1", "I2"):
        e = b[is_off & (b.value >= 50_000)]
    elif rule == "I4":
        e = b[ceo & (b.value >= 100_000)]
    else:   # I3 cluster: the filing that makes >= 3 distinct insiders in 30 days
        rows = []
        for sym, x in b[is_off & (b.value > 0)].groupby("sym"):
            x = x.sort_values("filed")
            for i in range(len(x)):
                w = x[(x.filed > x.filed.iloc[i] - pd.Timedelta(days=30)) & (x.filed <= x.filed.iloc[i])]
                if w.owner.nunique() >= 3:
                    rows.append(x.iloc[i])
        e = pd.DataFrame(rows)
    return e


HOLD = {"I1": 21, "I2": 63, "I3": 63, "I4": 63}


def trades(e, rule, O, C, R, dv, so, sc, tier):
    cost, pmin, dmin = (0.001, 10, 20e6) if tier == "liquid" else (0.003, 5, 1e6)
    idx = C.index; out, last = [], {}
    for _, r in e.iterrows():
        s = r.sym
        if s not in C.columns: continue
        i = idx.searchsorted(r.filed, side="right")     # first trading day after the filing date
        j = i + HOLD[rule]
        if j >= len(idx): continue
        if s in last and (idx[i] - last[s]).days < 30: continue
        px, d = R[s].iloc[i - 1], dv[s].iloc[i - 1]
        if not (np.isfinite(px) and px >= pmin and np.isfinite(d) and d >= dmin): continue
        o, c = O[s].iloc[i], C[s].iloc[j]
        if not (np.isfinite(o) and np.isfinite(c) and o > 0): continue
        ret = c / o - 1 - 2 * cost
        spy = sc.iloc[j] / so.iloc[i] - 1
        last[s] = idx[i]
        out.append(dict(date=idx[i], exit=idx[j], sym=s, ret=ret, ex=ret - spy, value=r.value))
    return pd.DataFrame(out)


def tstat(t):
    if len(t) < 3: return np.nan
    wk = t.date.dt.to_period("W")
    g = t.groupby(wk).ex.sum(); n = t.groupby(wk).size(); m = t.ex.mean()
    se = math.sqrt(((g - m * n) ** 2).sum()) / len(t)
    return m / se if se > 0 else np.nan


def portfolio(t, a, b, w=0.05, cap=20):
    t = t[(t.date >= a) & (t.date < b)].sort_values(["date", "value"], ascending=[True, False])
    days = pd.bdate_range(a, b); pnl = pd.Series(0.0, index=days); open_ = []
    for _, r in t.iterrows():
        open_ = [x for x in open_ if x > r.date]
        if len(open_) >= cap: continue
        open_.append(r.exit)
        if r.exit in pnl.index: pnl[r.exit] += w * r.ret
    eq = (1 + pnl).cumprod(); yrs = (b - a).days / 365.25
    return eq.iloc[-1] ** (1 / yrs) - 1, (pnl.mean() / pnl.std() * math.sqrt(252) if pnl.std() > 0 else 0), (eq / eq.cummax() - 1).min()


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "smoke":
        s = requests.Session(); s.headers.update(UA)
        d = quarter(2024, 1, s); print(d.head(10).to_string()); print(len(d), d.value.describe()); return
    b = filings(); print("purchases", len(b), b.filed.min(), b.filed.max(), flush=True)
    O, C, R, dv, so, sc = prices()
    spy_y = lambda a, z: (sc[(sc.index >= a) & (sc.index < z)].iloc[-1] / sc[(sc.index >= a) & (sc.index < z)].iloc[0]) ** (365.25 / (z - a).days) - 1
    spy_ho = spy_y(SPLIT, END)
    rows, passed = [], []
    for rule in ("I1", "I2", "I3", "I4"):
        e = events(b, rule)
        for tier in ("liquid", "small"):
            t = trades(e, rule, O, C, R, dv, so, sc, tier)
            if t.empty: continue
            dv_, ho = t[(t.date >= DEV0) & (t.date < SPLIT)], t[t.date >= SPLIT]
            pc, ps, pdd = portfolio(t, SPLIT, END)
            ok = len(ho) > 30 and ho.ex.mean() >= 0.01 and tstat(ho) >= 3 and dv_.ex.mean() > 0 and ps >= 1 and pc >= spy_ho + 0.05
            rows.append(dict(rule=rule, tier=tier, dev_trades=len(dv_), dev_excess=f"{dv_.ex.mean():.2%}", hold_trades=len(ho),
                             hold_ret=f"{ho.ret.mean():.2%}", hold_excess=f"{ho.ex.mean():.2%}", hold_t=round(tstat(ho), 2),
                             hold_win=f"{(ho.ex > 0).mean():.0%}", port_CAGR=f"{pc:.1%}", port_Sharpe=round(ps, 2), port_drop=f"{pdd:.1%}",
                             PASS="YES" if ok else ""))
            passed += [f"{rule}/{tier}"] if ok else []
            print(rows[-1], flush=True)
    out = ["# Round 48: insider open-market purchases (SEC Form 4)", "",
           f"Rules: [PROTOCOL_ROUND48.md](../PROTOCOL_ROUND48.md). {len(b):,} purchase filings 2015→2026Q3. SPY holdout CAGR {spy_ho:.1%}.",
           "Excess = trade return minus SPY over the same days. Survivorship bias (current listings only) flatters results.", "",
           pd.DataFrame(rows).to_markdown(index=False), "", f"**Passing: {', '.join(passed) or 'none'}.**"]
    open("reports/ROUND48.md", "w").write("\n".join(out) + "\n"); print("\n".join(out))


if __name__ == "__main__":
    main()

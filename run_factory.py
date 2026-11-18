"""Run every registered strategy not yet in the ledger; rebuild the leaderboard (PROTOCOL_FACTORY.md)."""
import os, sys, io, zipfile
import numpy as np, pandas as pd, requests

from edge import factory as F
from edge.factory_strats import REG

ETFS = ["SPY", "QQQ", "IWM", "EFA", "EEM", "AGG", "IEF", "TLT", "BIL", "GLD", "XLK", "XLF", "XLE", "XLV", "XLY", "XLP", "XLI",
        "XLB", "XLU", "XLRE", "XLC", "DBC", "VWO", "BND", "^VIX", "^VIX3M", "HG=F", "GC=F"]
COINS = ["BTC", "ETH", "SOL", "XRP", "BNB", "DOGE", "ADA", "AVAX", "LINK", "DOT", "LTC", "TRX", "ATOM", "NEAR", "UNI", "ETC",
         "FIL", "APT", "ARB", "OP", "INJ", "SUI", "AAVE", "BCH", "XLM", "HBAR", "ICP", "TON", "MATIC", "SHIB"]


CBOE = ["PUT", "BXM", "CNDR", "WPUT"]   # batch 9: Cboe option-strategy benchmark indexes (free daily history)


def cboe_indexes():
    """Daily closes of Cboe strategy indexes from cdn.cboe.com; columns CBOE_<sym>. Missing ones are skipped."""
    out = {}
    for sym in CBOE:
        try:
            txt = requests.get(f"https://cdn.cboe.com/api/global/us_indices/daily_prices/{sym}_History.csv", timeout=30).text
            rows = [l.split(",") for l in txt.splitlines()]
            rows = [r for r in rows if len(r) >= 2 and r[0][:1].isdigit()]
            ser = pd.Series({pd.to_datetime(r[0]): float(r[-1]) for r in rows if r[-1].strip() not in ("", "-")}).sort_index()
            if len(ser) > 500:
                out[f"CBOE_{sym}"] = ser; print("cboe", sym, len(ser), ser.index[0].date(), flush=True)
        except Exception as e:
            print("cboe", sym, "failed", repr(e), flush=True)
    return pd.DataFrame(out)


def load(markets):
    d = {}
    if "stocks" in markets:
        C = pd.read_pickle("data/r38/stocks_C.pkl").astype(float)
        V = pd.read_pickle("data/r38/stocks_V.pkl").astype(float).reindex_like(C)
        R = pd.read_pickle("data/r38/stocks_R.pkl").astype(float).reindex_like(C)
        dv = (R * V).rolling(20, min_periods=15).mean()
        d["C"], d["V"], d["dv"] = C, V, dv
        d["O"] = pd.read_pickle("data/r38/stocks_O.pkl").astype(float).reindex_like(C)
        d["ok"] = (R >= 10) & (dv >= 20e6)
    if "etfs" in markets:
        import yfinance as yf
        x = yf.download(ETFS, start="2013-01-01", auto_adjust=True, progress=False)["Close"]
        x.index = pd.to_datetime(x.index).tz_localize(None)
        d["E"] = x.join(cboe_indexes(), how="left")
    if "crypto" in markets:
        from run_round38 import binance
        got = {c: binance(f"{c}USDT") for c in COINS}
        d["X"] = pd.DataFrame({c: f["C"] for c, f in got.items() if f is not None}).sort_index()
    return d


def main():
    led = pd.read_csv(F.LEDGER) if os.path.exists(F.LEDGER) else pd.DataFrame()
    done = set(led["name"]) if len(led) else set()
    todo = {n: v for n, v in REG.items() if n not in done}
    print(f"{len(todo)} new strategies, {len(done)} already in the ledger", flush=True)
    d = load({m for m, _, _ in todo.values()} | {"etfs"})
    end = pd.Timestamp.now().normalize()
    bench = {"etfs": d["E"]["SPY"].pct_change(fill_method=None).fillna(0)}
    if "C" in d:
        bench["stocks"] = d["C"].pct_change(fill_method=None).where(d["ok"].shift(1, fill_value=False)).mean(axis=1).fillna(0)
    if "X" in d:
        bench["crypto"] = d["X"]["BTC"].pct_change(fill_method=None).fillna(0)
    close = {"stocks": d.get("C"), "etfs": d["E"], "crypto": d.get("X")}
    rets, rows = {}, []
    for name, (mkt, batch, fn) in todo.items():
        try:
            w = fn(d)
            r = F.returns(w, close[mkt], mkt)
            rets[name] = r
            row = F.evaluate(name, mkt, r, bench[mkt], end); row["batch"] = batch
            rows.append(row)
            print(f"{name}: hold CAGR {row['hold_cagr']:.1%} Sharpe {row['hold_sharpe']:.2f} dd {row['hold_dd']:.1%}", flush=True)
        except Exception as e:
            print(f"{name} FAILED: {e!r}", flush=True)
    led = pd.concat([led, pd.DataFrame(rows)], ignore_index=True) if rows else led
    led = F.judge(led, rets)
    os.makedirs(os.path.dirname(F.LEDGER), exist_ok=True)
    led.to_csv(F.LEDGER, index=False)
    open(F.REPORT, "w").write(F.report(led)); print(F.report(led)[:3000])


if __name__ == "__main__":
    main()

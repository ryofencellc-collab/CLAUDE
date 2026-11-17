"""Round 51 (PROTOCOL_ROUND51.md): model-priced replay of the 0DTE opening-range breakout on 5-minute SPY bars."""
import math
from zoneinfo import ZoneInfo
import numpy as np, pandas as pd

ET = ZoneInfo("America/New_York")
N = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
SLIP, FEE, R = 0.03, 0.65, 0.04


def bs(S, K, T, sig, cp):
    if T <= 1e-6:
        return max(S - K, 0.0) if cp == "C" else max(K - S, 0.0)
    d1 = (math.log(S / K) + (R + 0.5 * sig * sig) * T) / (sig * math.sqrt(T)); d2 = d1 - sig * math.sqrt(T)
    return S * N(d1) - K * math.exp(-R * T) * N(d2) if cp == "C" else K * math.exp(-R * T) * N(-d2) - S * N(-d1)


def day_trade(bars: pd.DataFrame, sig: float, breakout=True):
    close16 = bars.index[0].normalize() + pd.Timedelta(hours=16)
    orng = bars[bars.index.time < pd.Timestamp("10:00").time()]
    after = bars[(bars.index.time >= pd.Timestamp("10:00").time())]
    if len(orng) < 5 or after.empty:
        return None
    hi, lo = orng.High.max(), orng.Low.min()
    entry = None
    for t, b in after.iterrows():
        if t.time() >= pd.Timestamp("15:45").time():
            break
        if not breakout:
            entry = (t, b.Close, "C"); break
        if b.Close > hi: entry = (t, b.Close, "C"); break
        if b.Close < lo: entry = (t, b.Close, "P"); break
    if entry is None:
        return None
    t0, s0, cp = entry; K = round(s0)
    T = lambda t: max((close16 - t).total_seconds() / (365 * 24 * 3600), 0)
    paid = bs(s0, K, T(t0), sig, cp) * (1 + SLIP)
    exit_v, how = None, "15:45"
    for t, b in bars[bars.index > t0].iterrows():
        v = bs(b.Close, K, T(t), sig, cp)
        if v >= 2 * paid: exit_v, how = v, "target"; break
        if v <= 0.5 * paid: exit_v, how = v, "floor"; break
        if t.time() >= pd.Timestamp("15:45").time(): exit_v, how = v, "15:45"; break
    if exit_v is None:
        exit_v = bs(bars.Close.iloc[-1], K, T(bars.index[-1]), sig, cp)
    got = exit_v * (1 - SLIP)
    pnl = (got - paid) * 100 - 2 * FEE
    return dict(day=str(t0.date()), entry=t0.strftime("%H:%M"), side=cp, paid=round(paid, 3), exit=how, pnl=round(pnl, 2), roi=pnl / (paid * 100))


def main():
    import yfinance as yf
    b = yf.download("SPY", interval="5m", period="60d", auto_adjust=False, progress=False, prepost=False)
    b.columns = [c[0] if isinstance(c, tuple) else c for c in b.columns]
    b.index = pd.to_datetime(b.index).tz_convert(ET)
    v = yf.download("^VIX1D", period="6mo", auto_adjust=False, progress=False)
    v.columns = [c[0] if isinstance(c, tuple) else c for c in v.columns]
    vopen = v["Open"]; vopen.index = pd.to_datetime(vopen.index).date
    rows, base = [], []
    for day, g in b.groupby(b.index.date):
        g = g.between_time("09:30", "15:55")
        if day not in vopen.index or len(g) < 60:
            continue
        sig = float(vopen[day]) / 100
        r = day_trade(g, sig); r0 = day_trade(g, sig, breakout=False)
        if r: rows.append(r)
        if r0: base.append(r0)
    T, B0 = pd.DataFrame(rows), pd.DataFrame(base)
    def summ(x):
        if x.empty: return {}
        t = x.roi.mean() / x.roi.std() * math.sqrt(len(x)) if x.roi.std() > 0 else np.nan
        return dict(trades=len(x), win=f"{(x.pnl > 0).mean():.0%}", mean_roi=f"{x.roi.mean():.1%}", t=round(t, 2), total=round(x.pnl.sum(), 0), worst=round(x.pnl.min(), 0))
    out = ["# Round 51: model-priced 0DTE opening-range breakout (SPY, last ~60 days)", "",
           "Rules: [PROTOCOL_ROUND51.md](../PROTOCOL_ROUND51.md). Black-Scholes with VIX1D; 3% slippage each way + $0.65/side. Per 1 SPY contract.", "",
           "| version | " + " | ".join(summ(T).keys()) + " |", "|---|" + "---:|" * len(summ(T)),
           "| B1 breakout | " + " | ".join(str(v) for v in summ(T).values()) + " |",
           "| baseline: ATM call at 10:00 every day | " + " | ".join(str(v) for v in summ(B0).values()) + " |", ""]
    # calibration vs the real-quote forward test
    try:
        real = pd.read_csv("paper/r39b_trades.csv")
        real = real[(real.strategy.str.startswith("B1")) & (real.root == "SPY")].copy()
        real["side"] = real.legs.str.extract(r"'([CP])'")
        m = real.merge(T, on="day", suffixes=("_real", "_model"))
        if len(m):
            dir_ok = (m.side_real == m.side_model).mean()
            ex_r = m.exit_real.str.split().str[0]; ex_m = m.exit_model
            ex_ok = (ex_r == ex_m).mean()
            out += [f"## Calibration vs real quotes (overlap {len(m)} days)", "",
                    f"Direction agrees {dir_ok:.0%}, exit type agrees {ex_ok:.0%} (usable if ≥ 90% / ≥ 75%).", "",
                    m[["day", "side_real", "side_model", "exit_real", "exit_model", "pnl_real", "pnl_model"]].to_markdown(index=False), ""]
    except Exception as e:
        out.append(f"calibration failed: {e!r}")
    out += ["## All model trades", "", T.to_markdown(index=False) if len(T) else "none"]
    open("reports/ROUND51.md", "w").write("\n".join(out) + "\n"); print("\n".join(out[:12]))


if __name__ == "__main__":
    main()

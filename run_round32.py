"""Round 32 runner: python run_round32.py   (needs network for Binance 1-minute data)"""
import math
from pathlib import Path

import numpy as np
import pandas as pd

from edge import round32 as g

OUT = Path("reports/ROUND32.md")
FEE_PCT, FEE_CT, MARGIN, CAP = 0.0008, 0.12, 0.2001, 2000.0


def load(sym):
    from edge import round21
    s = round21.minutes(sym, pd.Timestamp("2023-01-01", tz="UTC"), pd.Timestamp("2026-11-08", tz="UTC"))
    return s[~s.index.duplicated()].asfreq("1min").ffill()


def units_for(coin, price):
    """Dashboard: 500 XRP per contract. SOL: same dollar size per contract as XRP at the start (~$800)."""
    return 500.0 if coin == "XRP" else round(800.0 / price, 2)


CONFIGS = {  # name: (spacing, levels, margin, stop_below_levels, contract_scale)
    "dashboard (1% x 50, 20% margin)": (0.01, 50, MARGIN, 0, 1.0),
    "tighter 0.5% x 50": (0.005, 50, MARGIN, 0, 1.0),
    "wider 2% x 50": (0.02, 50, MARGIN, 0, 1.0),
    "stop-loss 5 steps under the grid": (0.01, 50, MARGIN, 5, 1.0),
    "no leverage (grid sized to $2,000)": (0.01, 50, 1.0, 0, None),
}


def run_one(px, start, horizon, coin, cfg):
    sp, lev, mg, stop, scale = cfg
    p0 = px[start]
    u = units_for(coin, p0) if scale else CAP / (lev * p0)        # no leverage: whole grid costs ~ $2,000
    return g.grid(px, start, horizon, sp, lev, u, FEE_PCT, FEE_CT, mg, CAP, stop, True)


def main():
    lines = ["# Round 32: the AP3X-style grid bot, tested independently", "",
             "Rules: [PROTOCOL_ROUND32.md](../PROTOCOL_ROUND32.md). Binance 1-minute prices; fees 0.08%/side + "
             "$0.12/contract/side; broker liquidates when equity < margin × open notional.", ""]
    data = {"XRP": load("XRPUSDT"), "SOL": load("SOLUSDT")}
    # 1. replication
    s = data["XRP"]
    t0 = pd.Timestamp("2026-11-07 22:51", tz="UTC") - pd.Timedelta(days=50.3)
    i0 = s.index.get_indexer([t0], method="nearest")[0]
    px = s.to_numpy(dtype=np.float64)
    r = g.grid(px, i0, int(50.3 * 1440), 0.0164 / px[i0], 50, 500.0, FEE_PCT, FEE_CT, MARGIN, CAP, 0, True)
    r_nomargin = g.grid(px, i0, int(50.3 * 1440), 0.0164 / px[i0], 50, 500.0, FEE_PCT, FEE_CT, 0.0, CAP, 0, True)
    lines += ["## 1. Replicating the dashboard (XRP, from " + f"{s.index[i0]:%Y-%m-%d %H:%M}, start price {px[i0]:.4f})", "",
              "| | dashboard | this replication (no margin calls) | with broker margin calls |", "|---|---:|---:|---:|",
              f"| realized P&L (what the dashboard shows) | $1,898.79 | ${r_nomargin[0]:,.2f} | ${r[0]:,.2f} |",
              f"| open positions now | 29 | {r_nomargin[6]} | {r[6]} |",
              f"| unrealized P&L on them | not shown | ${r_nomargin[1]:,.2f} | ${r[1]:,.2f} |",
              f"| **true equity (of $2,000)** | $3,898.79 shown | **${r_nomargin[2]:,.2f}** | **${r[2]:,.2f}** |",
              f"| lowest equity along the way | — | ${r_nomargin[3]:,.2f} | ${r[3]:,.2f} |",
              f"| liquidated by the broker | — | n/a | {'YES' if r[4] else 'no'} |", ""]
    # 2. every start date
    for horizon_days in (50, 180):
        rows = []
        for coin, s in data.items():
            px = s.to_numpy(dtype=np.float64)
            starts = range(0, len(px) - horizon_days * 1440, 3 * 1440)
            for name, cfg in CONFIGS.items():
                res = np.array([run_one(px, st, horizon_days * 1440, coin, cfg) for st in starts])
                real, eq, liq = res[:, 0], res[:, 2], res[:, 4]
                rows.append({"coin": coin, "settings": name, "runs": len(res),
                             "realized > 0": f"{(real > 0).mean():.0%}", "TRUE equity up": f"{(eq > CAP).mean():.0%}",
                             "median true $": round(float(np.median(eq - CAP)), 0),
                             "worst true $": round(float((eq - CAP).min()), 0),
                             "liquidated": f"{liq.mean():.0%}",
                             "median $/day (true)": round(float(np.median(eq - CAP)) / horizon_days, 2)})
        lines += [f"## 2. Every start date since 2023, held {horizon_days} days ($2,000 each)", "",
                  pd.DataFrame(rows).to_markdown(index=False), ""]
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

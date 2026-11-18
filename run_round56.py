"""Round 56 (PROTOCOL_ROUND56.md). `python run_round56.py MARKET` | `report` | `smoke`."""
import os, sys
import numpy as np, pandas as pd
from edge import mega as MG, nygrid as G

MK = {"SP": ("SPXUSD", 1.0), "NQ": ("NSXUSD", 1.5), "GOLD": ("XAUUSD", 2.0), "SILVER": ("XAGUSD", 3.0), "OIL": ("WTIUSD", 3.0),
      "BRENT": ("BCOUSD", 3.0), "EURUSD": ("EURUSD", 1.0), "USDJPY": ("USDJPY", 1.0), "GBPUSD": ("GBPUSD", 1.5),
      "AUDUSD": ("AUDUSD", 1.5), "USDCAD": ("USDCAD", 1.5), "DAX": ("GRXEUR", 1.5), "FTSE": ("UKXGBP", 1.5), "NIKKEI": ("JPXJPY", 2.0)}
CUTS = (pd.Timestamp("2020-01-01"), pd.Timestamp("2023-01-01"))
PARTS = "reports/round56_parts"


def smoke():
    import gen_blind as GB
    M = G.day_matrix(GB.make_source(11, dict(source="X", strategy="lunch_reversal", strength_k=0.4)))
    T = MG.run_market(M, 1.0, "SYN", (pd.Timestamp("2024-09-01"), pd.Timestamp("2025-05-01")))
    V = MG.verdict(MG.shortlist(T)[0])
    hit = V[V.PASS & (V.signal == "since_open") & (V["mode"] == "rev")]
    print(V.head(5).to_string()); assert len(hit), "calibration failed: planted lunch reversal not recovered"
    print("smoke OK: planted edge recovered")


def market(m):
    from edge.intraday import load_nq
    M = G.day_matrix(load_nq(pair=MK[m][0]))
    print(m, len(M["days"]), "days", M["days"][0].date(), "->", M["days"][-1].date(), flush=True)
    T = MG.run_market(M, MK[m][1], m, CUTS)
    os.makedirs(PARTS, exist_ok=True); T.to_parquet(f"{PARTS}/{m}.parquet", index=False)
    print(m, len(T), "configs written", flush=True)


def report():
    fs = [f"{PARTS}/{m}.parquet" for m in MK if os.path.exists(f"{PARTS}/{m}.parquet")]
    T = pd.concat([pd.read_parquet(f) for f in fs], ignore_index=True)
    S, ns = MG.shortlist(T); V = MG.verdict(S); V["entry"] = V.entry_bar.map(MG.bar_time)
    have = [os.path.basename(f)[:-8] for f in fs]
    per = T.groupby("market").agg(configs=("signal", "size"), search_days=("search_n", "max"), select_days=("select_n", "max"),
                                  final_days=("final_n", "max"), search_t2=("search_t", lambda x: int((x >= 2).sum())))
    cols = ["market", "entry", "signal", "mode", "filter", "hold", "stop", "search_n", "search_bp", "search_t", "select_n", "select_bp", "select_t",
            "final_n", "final_bp", "final_t", "PASS"]
    out = ["# Round 56: mega-search of intraday combinations", "", f"Rules: [PROTOCOL_ROUND56.md](../PROTOCOL_ROUND56.md). Markets: {', '.join(have)}.", "",
           f"Configurations tested: **{len(T):,}**. Survived search (t ≥ 2) and selection (t ≥ 2): **{ns:,}**. Shortlisted: {len(V)}. "
           f"**Passed the final exam (2023 → now, t ≥ 2.81, n ≥ 100): {int(V.PASS.sum())}**.", "",
           "Expected survivors from luck alone if nothing were real: about N × 0.023 × 0.023 × ½ ≈ "
           f"{len(T) * 0.023 * 0.023 / 2:,.0f} (rough; configurations are correlated).", "",
           "## Shortlist and final exam", "", V[cols].round(2).to_markdown(index=False), "",
           "## Per market", "", per.to_markdown(), ""]
    open("reports/ROUND56.md", "w").write("\n".join(out) + "\n"); print("\n".join(out[:10]))


if __name__ == "__main__":
    {"smoke": smoke, "report": report}.get(sys.argv[1], lambda: market(sys.argv[1]))()

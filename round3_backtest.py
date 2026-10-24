"""Round 3 step 1 (PROTOCOL_ROUND3.md): does the Betfair Exchange line work like Pinnacle?"""
import pandas as pd

import profit_report as pr
from edge import betting as bt


def main():
    df = pr.raw_matches()
    if "BFEH" not in df:
        raise SystemExit("no Betfair Exchange columns in history")
    has = df[["BFEH", "BFED", "BFEA", "MaxH", "MaxD", "MaxA"]].apply(pd.to_numeric, errors="coerce").notna().all(axis=1)
    df = df[has]
    print(f"matches with both Betfair and Max odds: {len(df)}; seasons {sorted(df['season'].unique())}")
    bfe = pr.bets(df, {s: f"Max{s}" for s in bt.SIDES}, ref="BFE")
    rows = []
    for season, g in bfe.groupby("season"):
        rows.append(dict(season=season, bets=len(g), profit=g["pnl"].sum(),
                         roi=g["pnl"].sum() / (len(g) * pr.STAKE), win_rate=g["won"].mean()))
    print(pd.DataFrame(rows).round(3).to_markdown(index=False))
    is_ = bfe[bfe["season"] < bt.HOLDOUT_FROM]
    ho = bfe[bfe["season"] >= bt.HOLDOUT_FROM]
    print(pd.DataFrame([pr.summarize(is_, "Betfair ref, in-sample"),
                        pr.summarize(ho, "Betfair ref, holdout")]).round(3).to_markdown(index=False))
    ps_ok = df[["PSH", "PSD", "PSA"]].apply(pd.to_numeric, errors="coerce").notna().all(axis=1) \
        if "PSH" in df else pd.Series(False, index=df.index)
    ps = pr.bets(df[ps_ok], {s: f"Max{s}" for s in bt.SIDES}, ref="PS")
    both = set(ps["key"]) & set(bfe["key"])
    print(f"overlap with Pinnacle-referenced bets (same matches): {len(both)} of {len(ps)} Pinnacle bets, "
          f"{len(bfe)} Betfair bets")
    verdict = "GO" if len(ho) and ho["pnl"].sum() > 0 else "NO GO"
    print(f"FEASIBILITY: {verdict} (holdout ROI {ho['pnl'].sum() / max(len(ho) * pr.STAKE, 1):+.2%} "
          f"on {len(ho)} bets)")


if __name__ == "__main__":
    main()

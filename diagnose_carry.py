"""Diagnostic only (not a trial): why did funding_carry fail out of sample?

Splits the selected config's P&L into funding income, basis P&L and costs,
and prints raw annualised funding by coin and year.
"""
import pandas as pd

from edge import data
from edge.strategies.crypto import COST, _liquid

p = data.crypto_panel()
spot, perp, fund = p["spot_close"], p["perp_close"], p["funding"]
cols = spot.columns.intersection(perp.columns).intersection(fund.columns)
idx = fund.index
spot, perp, fund = spot[cols].reindex(idx), perp[cols].reindex(idx), fund[cols]
basis = spot.pct_change(fill_method=None) - perp.pct_change(fill_method=None)

sig = fund.rolling(14, min_periods=14).mean()
sig = sig.where(_liquid(p).reindex(idx)[cols].fillna(False) & (basis + fund).notna())
pick = (sig.rank(axis=1, ascending=False) <= 10) & (sig > 0)
w = pick.astype(float)
w = 0.5 * w.div(w.sum(axis=1).replace(0, float("nan")), axis=0).fillna(0.0)
held = w.shift(1).fillna(0.0)
parts = pd.DataFrame({
    "funding": (held * fund.fillna(0)).sum(axis=1),
    "basis": (held * basis.fillna(0)).sum(axis=1),
    "cost": -held.diff().abs().sum(axis=1) * 2 * COST,
    "n_held": (held > 0).sum(axis=1),
})
by_year = parts.groupby(parts.index.year).agg(
    funding=("funding", "sum"), basis=("basis", "sum"), cost=("cost", "sum"), avg_held=("n_held", "mean"))
by_year["net"] = by_year[["funding", "basis", "cost"]].sum(axis=1)
print("=== funding_carry(window=14, top=10, threshold=0) P&L by year, fraction of capital ===")
print(by_year.round(4).to_string())
print("\n=== biggest single-day basis hits ===")
print(parts["basis"].nsmallest(8).round(4).to_string())
print("\n=== raw annualised funding rate (sum per year), majors ===")
print(fund[["BTC", "ETH", "SOL", "XRP", "DOGE"]].groupby(fund.index.year).sum().round(3).to_string())

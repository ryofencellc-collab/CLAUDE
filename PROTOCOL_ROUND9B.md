# Round 9b pre-registration: data-chosen trade gates on US stock ETFs

Written 2026-10-27, before any Round 9b code ran on real data. This is the
same procedure as [PROTOCOL_ROUND9.md](PROTOCOL_ROUND9.md) (crypto), moved
to stocks. Only the market, the gate inputs, the dates and the benchmark
change. This round counts as one more trial (265 in total).

## Market and data

Daily Yahoo Finance adjusted closes for 13 ETFs: SPY, QQQ, IWM, DIA and the
nine sector SPDRs (XLK, XLF, XLE, XLV, XLY, XLP, XLI, XLB, XLU). All are
liquid every day. Costs: 0.02% per side. Weights are set at the close of day t
and earn day t+1. The macro inputs are ^VIX, ^VIX3M, ^IRX, HYG, IEF and TLT.
The data starts 2007-06-01, because ^VIX3M and HYG begin in 2007.

## Gate library (fixed now, in `edge/gates.py`, `stock_base_gates`)

Each gate is offered in both directions:

| Family | Gates |
|---|---|
| Trend (per ETF) | close above SMA 50 / 100 / 200; 20-day and 60-day return positive |
| Market regime | SPY above its SMA 200 |
| Volatility (per ETF) | 20-day vol below its 1-year median; 20-day vol below 60-day vol |
| Fear | VIX below its 1-year median; VIX below VIX3M (calm term structure) |
| Credit | HYG/IEF above its 100-day average (credit markets calm) |
| Rates | 13-week T-bill yield lower than 60 days ago |
| Bonds | TLT above its SMA 100 (money moving to safety) |
| Short-term move | 3-day return below 0 |
| Calendar | turn of month (last trading day and first 3 of each month) |

That is 15 base gates and 30 with both directions.

## Procedure and test

The procedure is identical to Round 9: a greedy gate path of up to 6 gates,
the number of gates chosen on the last 25% of training, and at least 60
position changes in training. It is refit every 6 months on an expanding window from
2007-07-01. The first refit trains through 2011-12-31. Out-of-sample runs from
2012-01-01 to latest, 252 trading days a year.

## Pass rule (OOS series, all must hold)

1. Annualised Sharpe after costs ≥ 1.0
2. Deflated Sharpe ≥ 0.95, deflated by 265 trials
3. CAGR beats T-bills (4%/yr)
4. Max drawdown ≤ 25%
5. At least 30 position changes
6. Sharpe higher than buy-and-hold SPY over the same OOS days

The noise and planted-edge self-checks apply unchanged.

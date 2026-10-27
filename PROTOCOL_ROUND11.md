# Round 11 pre-registration: multi-asset trend with risk balancing

Written 2026-10-27, before any Round 11 code ran on real data.

## Why this round

Single trend signals are real but weak. Crypto trend had an out-of-sample
Sharpe of 0.85 in Round 10. A weak edge can't clear a bar of 1.0, but several
weak edges with low correlation to each other can: two independent 0.85
streams combine to about 1.2. This is the classic managed-futures design: follow
the trend in stocks, bonds, gold, commodities, property and Bitcoin, each sized
by its own risk. A longer out-of-sample period (2012 onward) also makes the
deflated Sharpe test fairer, since it needs about 0.75 over 15 years.

## Assets (daily Yahoo adjusted closes)

SPY (US stocks), EFA (developed ex-US), EEM (emerging), TLT (long Treasuries),
IEF (7–10y Treasuries), GLD (gold), DBC (commodities), VNQ (US property), and
BTC-USD (Bitcoin, from 2014-09 when Yahoo's data starts). Prices are aligned
on US trading days, so Bitcoin's weekend moves land on Monday. Costs: 0.02% per
side for ETFs and 0.10% for Bitcoin.

## Strategy family (fixed now, `edge/round11.py`)

For each asset each day, using only data up to that close:

1. **Trend signal:** long if the trend rule says up, otherwise flat (no shorts).
2. **Risk balancing:** each long asset's weight is proportional to
   1 / (its 60-day volatility), so each contributes similar risk.
3. **Portfolio risk limit:** the whole book is scaled so its estimated
   volatility (60-day, using the asset covariance) equals the target, with
   gross exposure capped at 1.0 (no leverage).

The grid is 4 × 3 × 2 = 24 configs:

| Parameter | Values |
|---|---|
| Trend rule | close above SMA 50; above SMA 100; above SMA 200; 12-month return > 0 |
| Target vol | 8%, 10%, 12% a year |
| Bitcoin included | yes, no |

## Test: walk-forward selection

Every 6 months from 2012-01-01, the config with the best net Sharpe on all
data from 2007-07-01 up to that date is chosen. It trades the next 6 months.
Out-of-sample runs from 2012-01-01 to latest, 252 days a year. The procedure
is one trial, making 267 in total.

## Pass rule (OOS series, all must hold)

1. Annualised Sharpe after costs ≥ 1.0
2. Deflated Sharpe ≥ 0.95, deflated by 267 trials
3. CAGR beats T-bills (4%/yr)
4. Max drawdown ≤ 25%
5. At least 30 position changes
6. Sharpe higher than buy-and-hold SPY over the same OOS days

## Prediction written now

Uncertain, leaning FAIL. Max drawdown and the deflated Sharpe should pass. A
Sharpe of 1.0 is the hurdle: published multi-asset trend results since 2012
run at about 0.5–0.9 without Bitcoin, and Bitcoin may lift that.

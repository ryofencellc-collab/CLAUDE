# Round 10 pre-registration: crypto trend gate with a volatility risk limit

Written 2026-10-27, before any Round 10 code ran on real data.

## Why this round

In Round 9 (crypto), "BTC above its SMA 100" was the gate the data chose
most often (8 of 12 refits). The strategy beat holding BTC
($13,052 vs $2,891 out of sample, Sharpe 0.89 vs 0.61), but its −59% worst
drop and a Sharpe under 1 failed the rules. This round keeps that trend idea
and adds a hard risk limit: position size shrinks when volatility rises.

## Strategy family (fixed now, `edge/round10.py`)

On each day, for each coin in the universe:

- **Regime gate:** BTC close above its SMA *R*, so a BTC uptrend is required.
- **Coin gate (optional):** the coin's close is above its own SMA 50.
- Each coin that passes the gates gets an equal share of the book. The whole
  book is then scaled to a target volatility *V*. The scale factor is *V*
  divided by the book's realised volatility over the last 20 days, capped at 1
  (no leverage). The rest of the book is cash.

The grid is 4 × 3 × 2 × 3 = 72 configs:

| Parameter | Values |
|---|---|
| Universe | BTC; BTC+ETH; the 5 most-traded coins; all tradable coins (30-day median volume ≥ $5M, ranked by 30-day volume as of that day) |
| Regime SMA *R* | 50, 100, 200 |
| Coin gate | off, on |
| Target vol *V* | 20%, 30%, 40% a year |

Costs are 0.10% per side, and weights set at the close of day t earn day t+1.

## Test: walk-forward selection

Every 6 months (1 January, 1 July) from 2021-01-01, the config with the best
net Sharpe on all data from 2019-10-01 up to that date is chosen. It trades the
next 6 months. Out-of-sample runs from 2021-01-01 to latest. This selection
procedure is the trial, so the count is 266 (264 + Round 9b + this).

## Pass rule (OOS series, all must hold)

1. Annualised Sharpe after costs ≥ 1.0
2. Deflated Sharpe ≥ 0.95, deflated by 266 trials. Over ~2,100 OOS days this
   needs an annualised Sharpe of about 1.2.
3. CAGR beats T-bills (4%/yr)
4. Max drawdown ≤ 25%
5. At least 30 position changes
6. Sharpe higher than buy-and-hold BTC over the same OOS days

## Prediction written now

Likely FAIL on the deflated Sharpe. Volatility targeting should fix the
drawdown, but crypto trend-following has historically run at a Sharpe of
about 0.8–1.1, short of the ~1.2 needed after 266 trials.

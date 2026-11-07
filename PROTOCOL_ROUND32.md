# Round 32: independent test of the "AP3X 2.0" grid bots (XRP / SOL futures grid)

Written 2026-11-07, prompted by a screenshot of a paper-trading dashboard: S4 XRP grid, $2,000 capital, 50.3 days,
shown +$1,898.79 ($37.76/day), 202 fills, 29 open buys, grid center 1.6365, last price 1.1581, spacing $0.0164,
50 levels downward from entry, 500 XRP per contract, 20.01% intraday margin, fees 0.08%/side + $0.12/contract/side.

## Question

Does the grid make money once open positions are valued at the market price (mark-to-market) and margin is
enforced the way a broker would?

## Model (edge/round32.py, Binance 1-minute closes as the futures price)

- Grid: at start, buy orders every `spacing` below the start price, `levels` deep; a filled buy gets a sell one
  step up; a filled sell re-arms its buy. If price rises a full step above the grid with nothing open, the grid
  re-centres at the price (a "breakout").
- Accounting: realized P&L (what the dashboard shows) and equity = capital + realized + unrealized.
- Margin: if equity < margin rate × open notional, the broker liquidates everything at market (one liquidation
  ends the run).
- Fees as above. Futures basis/funding ignored.

## Runs

1. **Replication:** XRP, the dashboard's settings, from 2026-09-18 (50.3 days before 2026-11-07 22:51 UTC).
2. **Every start date:** a new start every 3 days from 2023-01-01, held 50 days and 180 days; XRP and SOL;
   settings: the dashboard's (1% spacing, 50 levels, 500/contract), plus 0.5% and 2% spacing, a version with
   no leverage (capital must cover the full grid), and one with a stop-loss below the bottom level.

Reported: share of runs that end up, median and worst outcome, liquidations, and realized-vs-true gap.
Prediction written now: realized P&L is positive in almost every run; true equity is negative in a large
share; leveraged runs get liquidated in sustained drops.

## Result (2026-11-07, reports/ROUND32.md)

- **Dashboard settings (20% margin):** true equity up in only 8–24% of XRP runs and 15% of SOL runs; median
  −$265 to −$380 per $2,000; the broker liquidates 69–100% of runs. Replaying the dashboard's own 50 days: a broker
  would have liquidated it; without margin calls the account ends at −$49 (wiped out), not +$1,899.
- **No leverage (you own the coins):** realized profit is positive in **100%** of runs (the dashboard would always
  look green), yet true equity is up in only 27–48% and the median run loses money. That is the whole trick: the
  dashboard counts the small wins and leaves out the coins bought on the way down.
- Tighter/wider spacing and a stop-loss under the grid do not fix it.

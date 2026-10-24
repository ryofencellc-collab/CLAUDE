# Round 6 pre-registration: selling weekly Bitcoin puts

Written 2026-10-24, before any option data was downloaded.

## Hypothesis

Option buyers (largely retail, paying for lottery tickets and crash
insurance) overpay. Selling short-dated out-of-the-money puts collects that
premium. It is expected to win most weeks and to lose heavily in crashes.
The question is whether the premium beats the crashes after costs.

## Rule

- Every Friday 08:00–09:00 UTC (right after Deribit's weekly expiry), sell
  1 put on 1 BTC notional, expiring the next Friday 08:00 UTC, strike nearest
  to m × spot. Cash-secured: collateral = strike in USD. No leverage.
- Entry price = median traded price of that instrument in the hour (Deribit
  history API), less a 5% haircut for selling at the bid. Fees: 0.0003 BTC
  trade + 0.00015 BTC settlement, each capped at 12.5% of the option price.
- Settlement: BTC spot at expiry (Binance BTCUSDT 08:00 UTC hourly open).
  Weekly return = (premium − fees − max(K − S_T, 0)) / K.
- Grid m ∈ {0.95, 0.90, 0.85} = **3 trials**. Cumulative 196 + 3 = **199**.
- In-sample: before 2024-01-01; holdout: 2024-01-01 on. Config chosen on IS
  Sharpe.

## Pass

Holdout Sharpe (weekly, annualised ×√52) ≥ 1.0; Deflated Sharpe ≥ 0.95 with
199 trials; IS Sharpe > 0; holdout max drawdown ≤ 25%; ≥ 50 holdout weeks.
Reported for all configs, as the owner asked: % winning weeks, worst week,
and $ P&L on $1,000 of collateral.

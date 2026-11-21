# Round 72 pre-registration: high-win-rate SPY put credit spreads, traded daily or 3× a week

Written 2026-11-21, before any Round 72 result.

## Why
Round 35's best configuration was a 16-delta SPY put spread, opened only above the 200-day average and held to expiry, once a week:
- 93% wins;
- Sharpe 1.51 on the holdout;
- worst drop −6%;
- but only 6.9%/yr, because each trade risked little and the total risk was capped at 30%.

The user wants options, a high win rate, and 1 trade a day or 3 a week. This round asks whether more frequent entries plus larger total risk turn that into real money while keeping the high win rate and a better risk profile than holding SPY.

## Data and engine
- **Data:** real DoltHub end-of-day SPY chains (bid/ask/delta), 2020-03 → 2026-11 (the Round 35 download; the nearest expiries are ~2 weeks out).
- **Engine:** Round 35's `edge/optbt.py`:
  - fills at natural prices (sell at bid, buy at ask), $0.65/contract/leg;
  - cash-settled at intrinsic value at expiry;
  - managed exits at a 50% profit target, a 2× loss stop, or 21 days left.

## Fixed for every configuration
- Short put at the target delta, long put one strike lower.
- Open only when SPY > its 200-day average.
- Account: $25,000.

## Grid (72 configurations)
- **Frequency:** daily, or Mon/Wed/Fri.
- **Short delta:** 0.10, 0.16, 0.25.
- **Expiry:**
  - short: 7–21 days, target 14;
  - standard: 25–50 days, target 35.
- **Exit:** hold to expiry, or managed.
- **Total open-risk cap:** 30%, 50% or 70% of equity.
- **Risk per entry:** cap ÷ the number of overlapping entries, i.e. holding trading days ÷ entry spacing.

## Selection and split
- Dev 2020-03 → 2023-12; holdout 2024-01 → 2026-11.
- **Dev choice:** among configurations with dev win rate ≥ 85% and dev CAGR ≥ 8%, the highest dev Sharpe.

## Pass (dev choice, on the holdout; SPY buy-and-hold over the same days as the benchmark)
- win rate ≥ 85%;
- CAGR ≥ 12%;
- Sharpe ≥ SPY's Sharpe;
- max drawdown smaller than SPY's.

All 72 configurations are reported on the holdout for transparency, but only the dev choice can pass. A pass goes to a live paper tracker (real quotes), not money.

## Check first
A 1-configuration, 6-month run must complete before the full grid.

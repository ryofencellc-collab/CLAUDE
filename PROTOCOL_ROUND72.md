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

## Amendment 1 (2026-11-21, after the 6-month sample run, before any full or holdout result)
The sample made 0 trades. Two fixes:
- **Sizing:** one SPY spread's max loss (~$740) exceeds the per-entry budget (e.g. 30% × $25k / 15 = $500), so the quantity rounded to 0. Rule: take **1 contract** whenever the per-entry budget rounds to 0 but the total open-risk cap still has room. The cap still binds.
- **Data:** the DoltHub chains exist only on Mondays, Wednesdays and Fridays (sample: 24/24/26 days, no Tue/Thu). The "daily" arm cannot be tested and is dropped, leaving **36 configurations**, all 3× a week (Mon/Wed/Fri). Selection and pass rules are unchanged.

## Verdict (2026-11-21): PASS → live paper tracker
- **Dev choice:** Mon/Wed/Fri, 10-delta short put, 25–50 days to expiry, managed, 70% open-risk cap.
- **Holdout 2024-01 → 2026-11:**

| | Strategy | SPY buy-and-hold |
|---|---|---|
| CAGR | +14.9% | +16.8% |
| Sharpe | 2.35 | 1.07 |
| Max drop | −9.1% | −19.0% |

  - win rate 95.1%, 2.4 trades/week;
  - average win $51, average loss −$331, worst trade −$1,407;
  - it earns slightly less than SPY with half the drawdown.
- **Neighbours agree:** every 10-delta, 25–50-day configuration has a holdout Sharpe of 1.5–2.5, a max drop of 5–12% and a 94–98% win rate.
  - 16- and 25-delta versions earn more in good years but drop 24–48%.
  - The 7–21-day 10-delta versions earn 21–36%/yr but drop 16–26%.
- **Caveats:**
  - End-of-day prices on Mon/Wed/Fri only, so daily marks are smoothed and Sharpe is overstated.
  - Live intraday fills will differ.
  - The 200-day filter kept it mostly out of 2022.
  - The holdout includes the Aug 2024 and Apr 2025 shocks.
  - 36 configurations were tried; the choice was made on dev only.
- **Next:** a live paper tracker on real SPY quotes, then a verdict before any money.

## Live paper tracker (registered 2026-11-21, before its first run)
- **Engine:** `edge/paper72.py`, run every weekday at 20:40 UTC (15:40 ET in winter; 16:40 ET in summer is after the close, so the cron moves to 19:40 UTC when DST starts).
- **Quotes:** real Yahoo SPY quotes; deltas from mid-implied vol; SPY from the chain's own price.
- **Rules:** exactly the dev choice (Mon/Wed/Fri, 10-delta, 25–50 days, managed, 70% cap, above the 200-day). Fills at natural prices; each entry also logs the mid credit. $25,000 paper account.
- **Starting state:** SPY is currently below its 200-day average (689.81 vs 730.29 on 2026-11-20), so by rule the tracker stays in cash until it recovers. It may not trade for weeks.
- **Verdict:** at 40 closed trades, or 2027-05-21, whichever comes first.
  - **Pass:** net P&L > 0, win rate ≥ 85%, max drawdown ≤ 12%, and the average natural credit ≥ 50% of the average mid credit (fills are realistic).
  - A pass makes it a real-money candidate at a budget the user sets.

# Round 61: common indicator setups as 0DTE scalps on real recorded quotes (written 2026-11-20, before any results)

**Why:** the user asked to test "every variable": Greeks and indicators. We could not decode the Reddit trader's timing (too fuzzy), so
this round tests the indicator setups 0DTE scalpers commonly use, on our own real Cboe SPY/SPXW quotes (corrected clock, about 1-minute snapshots).

**Triggers** are computed on the underlying from 09:45 to 15:30 ET, one position at a time, re-entry allowed.

| Code | Trigger | Buys |
|---|---|---|
| R1 | RSI(14) < 30 | call |
| R1 | RSI(14) > 70 | put |
| R2 | RSI crosses below 40 | put |
| R2 | RSI crosses above 60 | call |
| V1 | price crosses the session mean (VWAP proxy, no volume data) | call when it crosses up, put when it crosses down |
| E1 | EMA9 crosses EMA21 | call on an up-cross, put on a down-cross |
| M1 | MACD(12,26,9) histogram changes sign | call when it turns positive, put when it turns negative |
| B1 | price touches the lower Bollinger band (20, 2) | call (mean reversion) |
| B1 | price touches the upper band | put |
| B2 | price closes outside a band | put below the lower band, call above the upper band (breakout) |

**Option and fills.** Each trade buys 1 contract of the nearest-ATM option of that day's expiry: at the ask on entry, at the bid on exit, with fees as in Round 39b.

**Exits:**
- X1: +25% / −15% / 10 minutes.
- X2: +50% / −25% / 30 minutes.
- X3: held to 15:45.

Every trade is closed by 15:45 at the latest.

**Grid:** 7 triggers × 3 exits × 2 roots = **42 configurations**.

**Scoring** happens at ≥ 20 recorded days, then again at 40. Dev is the first half of the days and holdout the second half.
**Pass:** all of
1. holdout mean > 0;
2. holdout day-clustered t ≥ 3.0 (the Bonferroni-style bar for 42 configurations);
3. dev mean > 0;
4. both halves positive in total.

Before 20 days, results are reported as interim only.

**Calibration:** synthetic days with Black-Scholes-priced option quotes and a 2-cent spread.
- Null: a random walk. Every configuration must lose about the costs.
- Planted: after RSI < 30 the price drifts up, and after RSI > 70 it drifts down. The R1 configurations must make money.

## Interim (2026-11-20, 9 recorded days: INTERIM, cannot pass before 20)
- **Trades:** 3,188 across 42 configurations; 21 were profitable.
- **MACD flip with X2 exits was best on both roots:** SPY +$1,850 on 115 trades (+$16 a trade), SPXW +$20,892 on 126 trades. Holdout-half t was about 2.2 on both,
  below the 3.0 bar.
- **Mean-reversion setups lost badly:** RSI extremes and Bollinger touches (R1/B1), with SPXW B1-X2 at −$17k, t −5.5.
- **Reading:** the 9 days were a steady down-trend (SPX 7,550 → 7,340). Trend-following triggers win in trends and fade-the-move triggers lose.
  Whether that holds outside a trending stretch is exactly what days 10–40 decide. The report refreshes nightly with the 0DTE scorer.

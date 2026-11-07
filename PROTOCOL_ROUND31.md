# Round 31 pre-registration: a theory factory on Kalshi's 15-minute crypto markets, against REAL quotes

Written 2026-11-07, before the data is fetched.

## Data

Kalshi KXBTC15M, KXETH15M, KXSOL15M, KXXRP15M, KXDOGE15M settled markets closing 2025-07-01 → 2026-11-01:
1-minute candlesticks (YES bid/ask open/low/high/close, trade price, volume) from Kalshi's own endpoints
(batch for recent markets, historical endpoint for archived ones; archived markets sampled evenly up to 2,500
per coin per period). Binance 1-minute spot for the same coins. Strike = the market's own floor_strike.

**Dev:** markets closing before 2026-05-01. **Holdout:** 2026-05-01 → 2026-11-01. The fair-value model
(logistic on z, z³, minute) is fitted on dev only.

## Execution (identical for every theory)

At most one position per market, $10 per bet. Decisions at a minute's close use that minute's closing quotes
and spot (nothing later).
- **Taker:** buy YES at the ask or NO at 1 − bid; fee ceil(7% × C × P × (1−P)) per order.
- **Maker:** rest a bid at price b; filled only if a later minute (before close) TRADES below b (price low ≤ b − 1c,
  so the level was traded through); fee 1.75% × C × P × (1−P). Queue ignored beyond that: optimistic, so maker
  passes must be confirmed live.

## Theories (37 configs)

T1 fair-value gap, taker, margin {3, 5, 8, 12}c · T2 fair-value gap, maker, margin {2, 4, 6}c ·
T3 indicator model (Round 30's B) vs real quotes: taker {3, 5}c, maker {2, 4}c ·
T4 buy the favourite at ask in {80–90, 90–95, 95–99}c from minute {5, 10, 13} ·
T5 buy the long shot at ask ≤ {3, 5, 10}c from minute {5, 10} · T6 fade an early move (minute 2, |z| < 0.3,
price ≥ {5, 10}c from 50) · T7 chase / fade a 2-minute price jump of ≥ {10, 20}c · T8 time-of-day drift
(hours with dev up-rate > 53%) · T9 RSI(2) extremes on spot, reversal and trend · T10 cross-coin lead (BTC's z
moved ≥ {0.5, 1.0} in a minute; the alt's price did not follow).

## Pass (each config)

Dev P&L > 0 **and** holdout P&L > 0 with ≥ 200 holdout bets **and** holdout per-bet t-stat ≥ 3.0 (strict,
because 37 configs are tried). Maker passes are provisional until a live paper test confirms fills.

Prediction written now: taker theories fail on fees; if anything passes it is a maker version of the
fair-value or indicator gap, and it must then survive a live test with real queues.

## Result (2026-11-07, reports/ROUND31.md): 0 of 37 pass

23,100 markets, 322,518 quote-minutes of real Kalshi prices. Nothing passes; almost everything loses on both
periods. What the data say:
- **Kalshi's 15-minute prices are honest.** Holdout calibration: a 50c market went YES 51.6%, 80c → 80.6%,
  90c → 91.2%, 95c → 96.8%. There is no mispricing big enough to beat the fee.
- **Our own fair-value model loses to Kalshi's price** (T1: when they disagree, Kalshi is right ~64% of the
  time). Kalshi's quotes react to the settlement index faster than a 1-minute Binance model can.
- **Chart indicators lose** (T3, T9) once real prices and fees are used; Round 30's small signal was the model
  price, not Kalshi's.
- **Buying long shots is the worst idea tested** (T5: −$23k to −$32k): lottery tickets are overpriced slightly
  and the fee does the rest. That is the flip side of the only edge we have found: being the 99c bid that sells
  them (the hourly live bot).

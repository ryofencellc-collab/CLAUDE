# Round 30 pre-registration: do chart indicators predict Kalshi's 15-minute BTC/ETH markets beyond the price?

Written 2026-11-07, prompted by a TikTok screenshot of a 1-minute BTC chart (SuperTrend 7/2, Fibonacci levels,
moving-average ribbons, RSI 2/7) used to trade Kalshi's 15-minute "up or down" markets.

## The right question

A 15-minute market asks whether the price at the end beats the price at the start. Its own price already knows
where spot sits against the strike and how much time is left (z = ln(spot/strike) / (σ√τ)). An indicator only
helps if it predicts the outcome **beyond z**. Then it must beat the cost of trading at ~50c: Kalshi's taker
fee (7% × P × (1−P) ≈ 1.75c) plus ~1c of spread.

## Data and features

Binance 1-minute closes, BTC and ETH, 2024-01 → 2026-10. Every 15-minute window; strike = price at the window
start; outcome = end price ≥ strike. Decision at 3, 5, 8 and 10 minutes into the window. Features: z (baseline),
RSI(2), RSI(7), SuperTrend(7,2) direction (ATR from closes), EMA(9) − EMA(21), 3- and 5-minute momentum,
distance to the window's high/low.

## Test

Logistic regression, fit 2024–2025, judged on 2026 (never seen):
- **Model A:** z only (stands in for the market price).
- **Model B:** z + all indicators.
Bet only when B's probability differs from A's by more than 2.75c (fee + spread), buying the side B favours
at A's price + 1c, paying the fee; $10 per bet.

**Indicators help if:** B's holdout log-loss beats A's, and the betting simulation is profitable on 2026.

Prediction written now: the indicators add almost nothing beyond z, and the betting loses to fees.

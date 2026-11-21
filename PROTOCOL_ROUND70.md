# Round 70 pre-registration: Kalshi S&P close markets vs the SPXW 0DTE option chain

Written 2026-11-20, before any Kalshi S&P quote has been joined to any option quote.

## Idea
Kalshi lists "S&P 500 at 4 pm" markets:
- **KXINXU-…H1600:** "≥ K" thresholds every 5 pt.
- **KXINX:** 25-pt close brackets.

They settle on the same official close as SPXW PM-settled 0DTE options. The option chain is the professional market's price of that close, so it gives a fair probability for every Kalshi market: P(S ≥ K) ≈ −∂C/∂K. Kalshi is a retail venue with small sizes, sized for a $1k–10k account. If its prices stray from the option-implied probability by more than the fee, buying the cheap side is a structural edge, not a chart pattern.

## Data
- **Options:** real SPXW 1-minute quotes (Cboe, 2026-11-09 → 11-19, 9 days; t = the market time of the quote, feed lag removed).
- **Kalshi:** 1-minute yes bid/ask candles from Kalshi's live endpoint for every KXINXU H1600 and KXINX market on those days; settlement results from Kalshi.

## Fair value
- At each minute, compute digitals D(K) = P(S_close ≥ K) from SPXW mids, using only strikes with bid > 0 and ask ≥ bid:
  - calls: D(K) ≈ (C(K−5) − C(K+5)) / 10;
  - puts: D(K) ≈ 1 − (P(K+5) − P(K−5)) / 10;
  - D = the mean of the available pair. A bracket [a, b] = D(a) − D(b).
- **Variant S (simultaneous):** the option snapshot at the same minute as the Kalshi quote. This is the upper bound.
- **Variant L (live-feasible):** the option snapshot 15 minutes older than the Kalshi quote, which is what free delayed data allows.

## Trade (taker, 1 contract, per market at most one entry: the first qualifying minute 10:00–15:45 ET)
- Buy YES at the yes ask if D − ask − fee(ask) ≥ m.
- Buy NO at 1 − yes bid if (1 − D) − (1 − bid) − fee(1 − bid) ≥ m.
- Skip quotes with ask ≤ 0.02 or ≥ 0.98, or bid ≤ 0.
- Kalshi taker fee: ceil(0.07·p·(1−p)·100)/100. Settle at Kalshi's result.
- Margin m ∈ {0.02, 0.03, 0.05, 0.08}, chosen on dev by total P&L, separately for S and L.

## Split and pass
- **Dev:** 11-09 → 11-13 (5 days). **Holdout:** 11-16 → 11-19 (4 days).
- **Pass (variant L decides; S is reported):**
  - holdout total P&L > 0;
  - market-level t ≥ 2;
  - positive on ≥ 3 of the 4 holdout days;
  - and the option-implied D must score a lower Brier score than Kalshi's mid on the holdout traded markets.
- **A pass goes to a live paper tracker** (real Kalshi quotes, option chain as fair value, no money). Nine days cannot prove an edge, only show whether one is worth tracking.

## Calibration (before real data)
Synthetic days with a true close distribution; options priced from the truth plus small noise.
- **Null:** Kalshi quotes = truth ± a 2–4c spread with symmetric noise. Nothing may pass.
- **Planted:** Kalshi mid biased 6c toward 50% (a longshot bias). It must pass.

## Also reported
- Calibration of Kalshi mid vs option D vs outcome, by price band.
- Average |Kalshi mid − D| by hour.
- The number of minutes where a gap ≥ m exists.

## Verdict (2026-11-21): FAIL
- Kalshi tracks the option chain closely: the median |Kalshi mid − option fair| is 1¢ (1–1.5¢ all day) across 107,272 market-minutes. The two are equally calibrated (bands match to ≤ 0.5¢).
- **Variant S (same-minute fair value, upper bound):** dev lost at every margin. Holdout +$4.23 on 91 trades, t 1.31, 2 of 4 days positive.
- **Variant L (15-minute-old options, the free-data reality):** holdout −$42.16 on 245 trades, t −6.43. Kalshi moves faster than delayed option data, so the "gaps" are just stale fair values.
- Methodology note: a 20-market one-day sample was run end to end before the full run. It found the missing-candle gaps, which are now forward-filled.

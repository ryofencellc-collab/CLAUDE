# Round 67 pre-registration: which days does selling 0DTE premium win, and why?

Written 2026-11-20, before any Round 67 data is fetched or any filter is evaluated.

## Why
The user's framing: don't hunt for one rule. Take every day, see which days win and why, and trade only when the winning conditions hold. 66 rounds show that direction patterns are priced in. The only 0DTE effect with structural backing is the **variance risk premium**: 0DTE options charge more than the move they insure. Round 39a found that selling the ATM straddle at the open won 62% of days, averaging +3.2 SPX points (t 3.8 over 2022–2026). But the holdout t was only 1.7 and the worst day was −330 points. So the question for this round: can conditions known at the open pick out the days that lose?

## Data (free)
- VIX1D, VIX9D, VIX and SPX daily OHLC from Cboe index histories, with yfinance (^VIX1D, ^VIX9D, ^VIX, ^GSPC) as the fallback.
- FOMC decision dates from federalreserve.gov (`edge/factory_strats.fomc_dates`).
- CPI and jobs-report release dates from the BLS news-release archives (release date parsed from the archive file names). If BLS is unreachable, those two flags are left out and the report says so.
- Period: VIX1D start (2022-05) → latest. Dev = before 2024-08-12 (as in 39a); holdout = from 2024-08-12.

## The trade (per SPX 1-lot, index points; ×$100)
- **A, short ATM straddle, open → close (primary):** premium = O · VIX1D_open/100 · sqrt(1/252) · sqrt(2/π); P&L = premium − |C − O| − 0.6.
- **F, iron fly (defined risk, reported):** A plus long wings at ±2σ (σ = O · VIX1D_open/100 · sqrt(1/252)), wings priced by Bachelier. P&L = premium − wings − min(|C − O|, 2σ) + … (exact: short straddle settles at −|C−O|; the long wings pay max(|C−O| − 2σ, 0)) − 1.2.
  - The normal model ignores skew and so underprices the put wing. F is therefore optimistic and is shown, not passed.
- **Real-quote cross-check:** on every recorded SPXW day, the real ATM straddle mid at the first snapshot from 09:31 vs the model premium. This is descriptive: it reports how far the model premium is from real prices.

## Features known at 09:31 (no look-ahead)
- **Volatility levels and ratios:** VIX1D open; VIX and VIX9D prior closes; VIX1D/VIX and VIX9D/VIX; VIX1D open vs its prior close.
- **Today's open:** overnight gap (bp) and |gap|/σ.
- **Yesterday:** |C − O|/σ, its (H − L)/σ, its A P&L, and the streak of A wins.
- **Recent history:** 5-day mean of |C − O|/σ; 20-day trend; distance from the 252-day high; VIX percentile over 252 days.
- **Calendar:** weekday, FOMC day, FOMC eve, CPI day, jobs-report day, monthly OPEX (third Friday), month-end.

## Search
- **Filters:** "trade only on days where feature ≥ q" or "≤ q", with q at the dev 10/20/30/70/80/90th percentiles; binary flags use = 1 and = 0. Pairs are tried among the top 40 single filters.
- **Size floor:** a filter must keep ≥ 25% of dev days (≥ 2–3 trades a week).
- **Ranking:** dev t of A on the kept days.
- **Holdout test:** the top 10 by dev t go to the holdout once.

## Pass (all of these, on A)
- Holdout kept-day mean > 0 and holdout t ≥ 2.5.
- Holdout kept-day mean > the unfiltered holdout mean (the filter must add value, not just ride the base effect).
- Holdout max drawdown ≤ the unfiltered holdout max drawdown.
- Both holdout halves have a positive mean.
- Holdout t > the 95th percentile of the best holdout t under the **time-shift null**: the whole pipeline re-run 50 times with the features shifted by a random 60–500 trading days.

A pass is not a go-live. It goes to the real-quote forward test (39b data plus Yahoo, real bid/ask), then live paper. No real money.

## Calibration (before real data)
Synthetic 1,100 days with a 10% variance premium and a day-level move multiplier k.
- **Null:** every feature is noise, and no configuration may pass.
- **Planted:** one feature = log k + noise (corr ≈ 0.5), and it must pass.

## Report ("which days win and why", reported whatever the verdict)
- Per feature: quintile table of mean A, win rate and worst day (dev and all).
- The 25 worst days with their features.
- Year-by-year results.

Calibration note (before any real data was fetched): in the first null draft, the synthetic VIX1D varied, so high-vol days had larger point P&L. That is real structure, not a null, and one null configuration passed. The null world now holds vol constant, with the vol-index feature columns as pure noise. Across seeds 3, 4 and 5 the null passes nothing and the planted signal passes every time (null 95th-percentile best holdout t: 2.11 / 3.52 / 2.52).

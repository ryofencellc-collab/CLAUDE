# Round 66: the 0DTE "million ways" search on 14 years of S&P minutes, option prices calibrated to real 0DTE quotes (written 2026-11-20, before any results)

**The user's ask:** "Focus on 0DTE. Give me answers. Try a million different ways. Use all resources."
Nine days of real quotes cannot support a million-way search without finding luck, so this round runs the search on **14 years of minute data**. The options are priced
by a model **calibrated to our real recorded 0DTE quotes**.

## Data
- **Underlying:** HistData 1-minute S&P 500 (SPXUSD), 2012 → latest, regular session 09:30–16:00 New York.
- **Cross-market:** Nasdaq-100 (NSXUSD) for the transfer check.
- **Implied-volatility anchor:** the prior session's VIX close (Yahoo daily ^VIX; ^VXN for Nasdaq).

## Option-pricing model (`cal66.py`, `cal66b.py`, fitted on 246,915 real SPXW 0DTE quotes over 9 days)
- **IV(K, t)** = VIX_prev/100 × A(minutes to close) × S(z), where z = ln(K/S)/(VIX_prev/100·√T).
  - A is the time-to-close curve: 1.45 in the last 15 min, about 1.11–1.13 mid-day, about 1.40 at the open.
  - S is the smile: 2.0 at z = −6, 1.0 at the money, 1.85 at z = +6.
- **Bid/ask:** half the calibrated spread on each side of the model mid. The spread is $0.05 below a $2 mid, $0.10 up to $8, $0.20 up to $32, and $0.30 above.
- **Fees:** $1.00 per contract per side.
- **Measured honestly:** leave-one-day-out ATM IV error is a median **18%**. Day-to-day 0DTE IV varies more than VIX explains, so absolute P&L levels from the model are **not
  trusted**.
- **Bias control:** every pass criterion is **relative to an unconditional baseline** (the same option, bought on the same schedule, with no signal). A premium-level bias then
  hits rule and baseline alike.

## Trades
- **Entry slots:** every 15 minutes from 10:00 to 15:30 (23 slots).
- **Options:** buy an ATM, 30-delta OTM or 70-delta ITM call or put, at the model ask.
- **Exits:** the first of profit target PT ∈ {+25, +50, +100, +200%, none}, stop SL ∈ {−25, −50, −75%, none}, max hold ∈ {15, 30, 60, 120 min, to 15:55}, at the model bid.
  That makes 100 exit rules.
- One trade per rule per day: the first slot where the signal is true.

## Signals
- **Features (~30, known at the slot):**
  - returns over 1, 5, 15, 30, 60 min;
  - distance from the open, the day's high and low, the 30-minute opening range, and the session mean;
  - RSI(14), MACD histogram and its 5-minute slope, EMA9−EMA21, Bollinger %B;
  - realized vol over the last 30 min, over the day so far, and their ratio;
  - minutes since the high and since the low;
  - gap, prior-day return and range;
  - prior VIX and its change from the 5-day average;
  - prior close vs its 20-day average;
  - distance to the nearest 25-point level;
  - minutes to close; weekday.
- **Conditions:** a feature ≤ its p10/p20/p30 or ≥ its p70/p80/p90, with **percentiles from dev years only**.
- **Signals:**
  - every single condition (about 180);
  - every pair from the 60 best singles per side (different features; about 3,500);
  - plus "always" (the baseline).
- **Search size:** about 3,700 signals × 6 option types × 100 exits ≈ **2.2 million configurations**.

## Dev / holdout
- **Dev:** 2012–2019. **Holdout:** 2020 → latest. Nothing in the holdout influences any choice.
- **Selection:** rank configurations by the dev day-clustered t of **(rule P&L − baseline P&L)**, where the baseline is the same option type and exit bought at the same slot on
  the same days without the signal. Require ≥ 200 dev trades. Take the **top 20** to holdout.
- **PASS** (any of the 20, Bonferroni over 20), all required on the holdout:
  1. mean P&L per trade > 0;
  2. mean excess over the baseline > 0 with t ≥ 3.0;
  3. positive in both halves of the holdout (2020–2022 and 2023 → latest);
  4. on Nasdaq-100 (same rule, VXN anchor), holdout excess over the baseline > 0;
  5. the deflated Sharpe ratio over 2.2 million trials, on the dev excess series, ≥ 0.95.
- **A pass** is then tested on **real quotes**: our recorded Cboe days, plus the Yahoo days collected from 2026-11-20. After that comes a live paper test. No real money.

## Calibration (synthetic, before the real run)
- **Null:** the same pipeline on random-walk minute data (same length) must produce **no PASS**.
- **Planted:** a feature equal to the sign of the next 30-minute move plus noise must produce a PASS.

## Amendment 1 (2026-11-20, calibration stage, before any real data)
- **Problem:** criterion 5 as written (a deflated Sharpe over all ≈2.2M dev trials) **fails a planted edge**.
  - In the planted world the edge was found, with holdout t of about 20–25, both halves positive and the second market positive. DSR was still 0.00.
  - The reason: the threshold scales with the spread of Sharpe ratios across trials, and the many correlated trials of one strong signal inflate that spread.
- **Fix:** criterion 5 now uses a deflated Sharpe on the **holdout** excess series, with N equal to the number of configurations actually tested on the holdout (20), the Sharpe-ratio
  variance taken across those 20, and each series' skew and kurtosis.
- **Why this is sound:** dev-stage multiplicity is handled by the untouched holdout plus Bonferroni (t ≥ 3 over 20). Criteria 1–4 are unchanged.

## Amendment 2 (2026-11-20, after the search PASS, before any real-quote check is run)

The search passed (15 of the top 20 meet all five criteria). Nearly all of them are "rv30 high → buy calls, quick profit target". That is exactly where the model is weakest. The model sets IV from yesterday's VIX and never lets IV react to today's realized volatility. If real IV rises with intraday realized vol, the model underprices options on high-rv30 minutes. Any minute-data noise would also inflate both rv30 and the profit-target hits. So before the real-quote replay, two pre-registered checks:

- **M1, IV reacts to realized vol (real Cboe SPXW quotes, 9 days):** at each 1-minute snapshot from 10:00 to 15:30, take ATM IV (|z| < 0.25, median), divide it by the model IV, and regress log(ratio) on log(rv30 / VIXprev). rv30 uses the same formula as the search, computed from the recorded spot. Report β and the implied mispricing at rv30 = 0.16.
- **Re-price:** rebuild the outcome tables with IV × (rv30_t / VIXprev)^β at entry and at every exit minute, β from M1. Then re-test the same top-20 configurations, unchanged, on the holdout with the same five criteria.
  - If none passes, the verdict is **FAIL (model artifact)**.
  - If any passes, it goes to the real-quote replay on the recorded days, then a live paper test.
- **Real-quote replay (reported whatever happens):** run every PASS configuration on the recorded 1-minute SPXW quotes. Enter at the real ask of the strike nearest the type's delta and exit at the real bid. Compare with the same trade taken unconditionally at the same slot. With ≤ 9 days this is descriptive only and can veto but never confirm.

## Verdict (2026-11-20): FAIL (model artifact)

- **Original prices:** 15 of 20 PASS, nearly all "rv30 high → buy calls, quick profit target" ([ROUND66.md](reports/ROUND66.md)).
- **M1, real quotes:** real/model ATM IV rises with rv30, from 0.59 in the lowest quintile to 1.24 in the highest. Pooled β 0.457, corr 0.72.
- **Re-priced with the pooled β (pre-registered):** **0 of 20 PASS**. Best: holdout t 3.30, but NDX −47 and DSR 0.89 ([ROUND66_REPRICE.md](reports/ROUND66_REPRICE.md)).
- **Within-day β 0.093 (sensitivity only):** 19 of 20 pass. This β removes the day-level IV rise on high-rv days, and that rise is exactly what these entries are exposed to. So the pooled β is the right pricing model, and the verdict stands on it.
- **Real-quote replay (9 days):** 11 of the 15 rules have negative excess over the same trade taken unconditionally ([ROUND66_REPLAY.md](reports/ROUND66_REPLAY.md)).
- **Follow-up (66b):**
  - β comes from only 9 days. Re-estimate it once ≥ 20 recorded days exist and re-run the reprice with nothing else changed.
  - Forward paper tracking of the single rule that was positive in both the reprice (t 3.30) and the real replay: macd_slope ≤ −0.5211 AND rv30 ≥ 0.1596 → buy the ATM SPXW call at the first 15-minute slot, take +50% or sell at the 15:55 bid.
  - Pass after 20 new trigger days: mean excess over the unconditional same-slot trade > 0 and t ≥ 2.

# Round 62: every-variable analysis of 0DTE SPY/SPX trades on real recorded quotes (written 2026-11-20, before any results)

**The user's ask:** "a full analysis of every single variable … create the perfect algorithm."

**Data:** every recorded day of Cboe SPY and SPXW 0DTE quotes, about one snapshot a minute on the corrected clock, from 09:45 to 15:30 ET.
New days are added nightly.

## Variables (computed at each snapshot from information available then)

| Group | Variables |
|---|---|
| Price action | returns over 1/3/5/10/30 min; distance from open, session mean (VWAP proxy), session high and low, and opening-range high and low; minutes since the session low and high; distance to the nearest $5 (SPY) or $25 (SPX) round number; realized vol over the last 30 min |
| Indicators | RSI(14); EMA9−EMA21; MACD histogram; Bollinger %B; MACD-histogram slope |
| Greeks / IV | ATM IV; ATM IV change over 15 min; 25-delta skew (put IV − call IV); ATM gamma; ATM theta proxy (theo decay per minute); ATM bid-ask spread (absolute and %) |
| Options flow | put/call volume ratio for the day so far, and its 15-min change; volume in the last 15 min (calls, puts); open-interest put/call ratio; distance to the max-OI strike ("pin"); distance to the max-gamma strike; net dealer gamma (GEX ≈ Σ γ·OI·S², calls +, puts −) and its sign |
| Order book | ATM bid-size/ask-size imbalance (calls, puts) |
| Context | gap from the prior recorded close; prior day's range; minutes to close; weekday |

The calendar (Fed/CPI/OPEX) and true volume-weighted VWAP are **not available** in our feed and are reported as gaps.

## Targets
1. **Direction:** the sign of the 30-minute forward underlying return.
2. **Trade P&L:** buy the ATM call, or the ATM put, at the ask. Exit at the bid on the first of +50%, −25%, 30 minutes or 15:45. This is Round 61's X2.

## Analyses
- **A. Univariate:** for each variable, the per-day Spearman correlation (IC) with the 30-minute forward return and with (call P&L − put P&L). Report the
  mean IC across days, a t-stat across days, and pooled quintile tables. Bonferroni over all variables × 2 targets.
- **B. Model ("the algorithm"):** gradient-boosted trees on all variables, with **leave-one-day-out** cross-validation (train on the other days, predict
  the held-out day). Trading rule: P(up) ≥ 0.60 buys the ATM call; ≤ 0.40 buys the ATM put. One position at a time, X2 exits.
  - Also: the same rule with the walk-away overlay (stop after the first winner).
  - **Null:** 20 runs where each training day's labels are circularly shifted by a random 60–240 minutes, which breaks the feature→label link but keeps
    the structure. The real out-of-fold P&L must beat the 95th percentile of the null.
- **C. Feature importance:** permutation importance, out of fold.

## Pass
At ≥ 20 recorded days, the leave-one-day-out P&L must meet all of these:
1. positive on both roots;
2. above the null's 95th percentile;
3. positive in both halves of the days;
4. day-clustered t ≥ 2.5.

A pass freezes the model (trained on all days to that date) and starts a live paper test on new days. Before 20 days everything is **interim**.

## Calibration
- **Planted:** a synthetic variable equal to the next 30-min return plus noise is added to the real feature table. The model must find it (top importance) and profit.
- **Null:** a pure-noise variable must not rank top, and with all real labels shuffled across days the rule must not beat the null.

## Amendment 1 (2026-11-20, during the first interim run, before any verdict)
**The bug:** the univariate test as written (per-day IC, t across days) is biased for **level** variables such as distance from the open, the session mean or OI ratios.
Within one day a pure random walk gives IC −0.36 with t −7 between level and forward change. The first run flagged 31 "significant" variables for this
reason.

**The fix:** each variable's mean IC is now compared with a null distribution from the same days with the target circularly shifted by 60–240 minutes
(100 draws), and only the z against that null counts. Part B already used a time-shift null. The rest of the protocol is unchanged.

## Amendment 2 (2026-11-20, same interim run)
The circular-shift null does **not** remove the level-variable bias: it still showed 28 "significant" variables. Section A is therefore labelled
descriptive only.

The univariate verdict now comes from a **tradable test**:
1. On the first half of the days, learn whether values above each variable's median favour calls or puts.
2. On the second half, buy the favoured ATM side every 30 minutes (10:00–15:00) at real bid/ask with X2 exits.

A martingale yields zero expected P&L under any feature, so this test cannot be fooled by the bias.

## Interim (2026-11-20, 9 days, 41 variables, 6,127 snapshots): **nothing beats "just be bearish"**
- **Tradable test:** 0 of 41 variables beat the better of "always buy puts" / "always buy calls" on the holdout days, on either root.
  - The best-looking rules (low IV → calls, high → puts; recent put-volume surge → puts) earned *exactly* the always-puts baseline: SPX +$16,465, SPY +$1,255.
  - On a falling week they reduce to "buy puts".
- **The algorithm** (gradient-boosted trees on all 41 variables, leave-one-day-out): **−$11,034** on 216 trades, 29% win, 6/18 green days.
  The time-shift null's 95th percentile was +$4,407, so it is **worse than chance**. The walk-away variant made −$11,494.
- **Data gaps:** event calendar; true SPY share volume.
- **Reading:** 9 days of one regime (a steady sell-off) cannot teach direction. Any model learns "it goes down", and the one day it doesn't is where it
  loses. The analysis refreshes nightly with the 0DTE scorer and is judged at 20 and 40 days, when up, flat and down days are all represented.

## Amendment 3 (2026-11-20, user request): every instrument, selectivity and long/short combination
Added labels for buying the ATM straddle (call + put), selling the ATM straddle, and long/short shares (~$74k notional) over 30 minutes.

**Model policies:**
- options calls/puts;
- calls only (long only);
- puts only (short only);
- shares long/short;
- shares long only;
- straddles (buy when a big move is predicted, sell when quiet, from a second model).

**Variants:**
- selectivity: every 30-minute slot, ≥60% confident, ≥70% confident;
- with and without walk-away.

There are 6 no-model baselines on the same grid.

**Interim (9 days):**
- The best row is still **BASELINE always puts** (SPX +$15,501). Next are baseline short shares (+$4,460 SPX, +$4,151 SPY).
- The only model policy positive on both roots is **straddle timing (≥60%)**: SPX +$5,235 and SPY +$620, with t 0.6 and 0.9. That is noise-level and below the baseline.
- Every directional model policy (options or shares; long, short or both; any selectivity; with or without walk-away) **lost**.

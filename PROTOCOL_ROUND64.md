# Round 64: "when X happens, we win": win-condition mining on 0DTE trades (written 2026-11-20, before any results)

**The user's framing:** don't look for one master algorithm. Look at every day's winning and losing trades, find the conditions the winners shared, trade only
when those conditions hit (a couple of trades a day), and apply the pattern to every ticker with 0DTE options.

## Data
- **Round 62 snapshots:** about one per minute from 09:45 to 15:30 ET, on every recorded day, for SPY and SPXW.
- **Variables:** the 72 Round 62 variables.
- **Trade labels:**
  - buy the ATM call, or the ATM put, at the ask;
  - exit at the bid on the first of +50% / −25% / 30 min / 15:45 (X2);
  - real fees.
- **Universe growth:** from 2026-11-20 the collector also records QQQ and IWM daily, and AAPL, MSFT, NVDA, AMZN, META, GOOGL and TSLA on Fridays. Those are added to
  the test once the feature builder supports them (amendment to follow, before their results are seen).

## Rule space
- **A condition** is one variable compared to a threshold, `var ≥ q` or `var ≤ q`. q is that variable's 10/20/30/70/80/90th percentile in the *training*
  days.
- **Rules:**
  - every single condition × side (call or put);
  - every pair of conditions drawn from the 40 best single conditions in training, same side;
  - a single condition has about 72 × 6 × 2 = 864 rules; pairs add up to about 780 × 2 more.
- **Trading a rule:**
  - take the first time the condition is true each day;
  - then at most 1 more, at least 30 minutes later;
  - so ≤ 2 trades per day.
- **Score:** total P&L on the training days. A rule must trigger on at least half the training days, and on at least 4.

## Out-of-sample tests (the verdict)
1. **Leave-one-day-out (LODO):** for each day, mine all rules on the other days of the same root, pick the single best, and trade it on the held-out day. The total
   held-out P&L is the result.
2. **Cross-ticker:** mine on all SPY days, apply the top rule to all SPXW days; and the reverse. This is the "apply it to every 0DTE stock" test.
3. **Null:** the whole LODO pipeline is repeated 20 times with each day's labels circularly shifted by a random 60–240 minutes. The real LODO total must beat the
   null's 95th percentile. This measures how good the best mined rule looks by luck.
4. **Baselines on the same ≤ 2/day schedule:** always call, always put.

**PASS (judged at ≥ 20 recorded days; earlier runs are interim):**
- LODO total > 0 on both roots;
- above the null's 95th percentile;
- above both baselines;
- cross-ticker P&L > 0 in both directions;
- day-clustered t ≥ 2.5.

A PASS freezes the rule (mined on all days) and starts a live paper test on new days and new tickers.

## Descriptive (no verdict): "why winners win"
For calls and puts separately, compare each variable's standardized mean at entry between winning and losing trades. Report the top 15 per side.

## Calibration (before real results)
- **Planted:** a variable equal to the call−put P&L sign plus noise must be found, with LODO P&L > 0 and above the null.
- **Null:** pure-noise variables only must not beat the null's 95th percentile.

## Amendment 1 (written while coding, before the real run)
**Cross-ticker thresholds:** the rule's percentile levels (for example p20) are recomputed on the target root's own data, because level variables differ in scale between SPY and SPX.
This uses the target's whole-period distribution, a mild look-ahead in the threshold only (not in labels). It is noted here and kept for the 20-day verdict.

## Interim (2026-11-20, 9 days): **FAIL** (held-out rules are not above luck), but one recurring pattern worth tracking
- **SPY, leave-one-day-out:** +$323 on 17 trades, 6/9 green, t 0.95.
  - Luck test 95th percentile: +$353, so it is **not above luck**.
  - It is also below the always-put baseline on the same schedule (+$518).
- **SPXW, leave-one-day-out:** +$3,225 on 15 trades, 4/9 green, t 0.72, against a luck 95th percentile of +$8,939. Below the always-put baseline (+$4,176).
- **Stability:**
  - SPY picked the same family in 6 of 9 folds: **momentum continuation, "BUY PUT when MACD slope ≤ p20 AND the 3–5-minute return ≤ p10/p30"**. That is the move
    accelerating down.
  - SPXW's folds were unstable (8 different rules).
- **Cross-ticker:**
  - SPY's rule on SPXW: +$7,246, 7/9 green, t 2.57.
  - SPXW's rule on SPY: +$1,027, 7/9 green, t 2.40.
  - Caveat: SPY and SPX are the same index on the same 9 days, so this is not an independent test. QQQ, IWM and Friday single-stock 0DTE are now being recorded for a real
    one.
- **"Why winners win":** the top separators are calendar variables (OPEX week, days to FOMC). With 9 days they only identify *which days fell*, so this is a
  day-level confound, not a cause.
- **Next:** the analysis re-runs nightly. At 20 days the verdict is scored on SPY/SPXW, and as soon as QQQ/IWM have days, the frozen momentum rule is tested on them.

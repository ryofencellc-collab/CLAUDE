# Round 43 pre-registration: riskless arbitrage inside Kalshi and Polymarket

Written 2026-11-09, before the scanner has run.

**Why.** To prove an AI can make money, the cleanest proof is a profit that does not depend on predicting anything:
prices that contradict each other, bought so every outcome pays more than the cost after fees. This is not a bet on
outcomes. Each trade is provable on its own: cost, payout and fees are known when it is placed.

**Checks** (`edge/arb.py`, every 3 minutes, all open events, top-of-book size only, taker fees included):
- **K-MONO:** strike ladders (BTC above $74k / $75k …). A lower strike's YES ask below a higher strike's YES bid means
  buying YES low + NO high pays ≥ $1 whatever happens.
- **K-NOALL / P-NOALL:** mutually exclusive events (Kalshi `mutually_exclusive`, Polymarket negative-risk). If the
  YES bids sum to more than 1, buying NO on every market pays at least n−1.
- **K-YESALL / P-YESALL:** YES asks summing below 1. That is riskless only if the listed outcomes are exhaustive, which
  the API does not guarantee, so these are logged as *conditional* and never counted toward the pass.
Fees: Kalshi `ceil(0.07 × n × p × (1−p))` per order. Polymarket is treated as 0, and each hit's fee schedule is checked
by hand before any trade. Risks noted for each hit: one leg filling without the other, capital locked until close,
voided markets.

**Pass (detection stage, after 5 market days):** ≥ 20 distinct riskless opportunities of ≥ $1 net each, seen on ≥ 2
consecutive scans (so a person or bot could actually act), totalling ≥ $100 net at top-of-book size, and annualized
return ≥ 20% on the capital locked. A pass leads to an execution bot (all legs at once, cancel and unwind on a
partial fill), tested in dry-run first. A fail means these markets are efficiently arbitraged and we say so.

## Amendment 1 (2026-11-09, after the 60-second smoke run, before the real scan)
The first scan reported 17,477 "riskless" ladders worth $605k: a grouping bug. NFL spread and player-prop events
hold one ladder per team or player inside one event, and the scanner compared strikes across them. Ladders are now
grouped by the full ticker minus its trailing number, and a group whose neighbouring mid-prices disagree more than 20% of
the time is skipped as "not a real ladder". Re-scored on the smoke data, real ladder violations are 10, the best
worth $0.004. The smoke log is discarded. The pass rule is unchanged.

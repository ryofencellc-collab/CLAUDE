# Round 22 pre-registration: Round 21 with larger size on the 15-minute markets (forward only)

Written 2026-10-30 23:10 UTC, before any data it will be judged on exists.

## Why

Round 21's live paper bot records two things for every market it bids on:

- the queue resting at 99c ahead of us when we bid;
- every later long-shot purchase.

In its first ~28 hours (39 filled markets, 0 losing fills), the flow left
after the queue was often far bigger than our 1,000-contract cap. This was
mostly in the 15-minute markets: 69k contracts on one BTC market, 27k on
XRP, 16k on DOGE.

| Size per market | Paper profit |
|---|---:|
| 1k | $119 |
| 10k | $553 |
| 25k | $818 |

Those hours chose this rule, so they are **not** part of this test.

## The rule

Same signal, placement, cancellation, fill accounting (only after the queue
ahead) and settlement as Round 21's forward test. The only change is order
size:

- **10,000 contracts** per market on the 15-minute series (KXBTC15M,
  KXETH15M, KXSOL15M, KXXRP15M, KXDOGE15M), about $9,900 at risk;
- **1,000 contracts** per market on the hourly series, as in Round 21.

It is computed from the same ledger: filled = min(size, seen − queue ahead).

## Window

**2026-10-31 00:00 UTC to 2026-11-13 24:00 UTC** (14 days). Markets are
assigned by close time.

## Pass rule (all must hold)

1. Paper profit ≥ $1,400 (≈ $100/day).
2. At most one losing filled market. Each loss is reported in full.
3. Profitable on ≥ 70% of days.
4. The worst day is at least −$2,000.

## Risk stated now

A wrong call that is filled at 10,000 contracts loses about $9,900, which is
the whole $10k stage-two bankroll. Live, the bot has already seen 6 wrong
calls at z ≥ 6, all during a market-wide drop, and none of them filled
because the bids were cancelled first. Whether that keeps happening is what
this test measures.

## Prediction written now

PASS on profit, at about $150–400/day. The risk is one filled wrong call;
about a 30% chance of that within 14 days.

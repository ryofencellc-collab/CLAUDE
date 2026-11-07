# Round 27 pre-registration: scan every Kalshi market for the 99c maker edge, honestly counted

Written 2026-11-07, before any data it will be judged on is fetched.

## Question

Where else does a 99c resting bid on the side that is already winning make money, now that we know:
1. only long-shot trades at >= 1c can reach a 99c bid (0.1c price steps elsewhere: reports/FILLCHECK.md);
2. the long shot has to lose nearly always: each loss costs ~99 wins;
3. queues of incumbent 99c bids can eat all the flow (weather, Round 18/19).

## Data

Every Kalshi series with recent volume (GET /series), markets that settled yes/no with close times in two
windows, and every trade in those markets (live and historical trade endpoints):

- **dev (selection):** closes in [run − 15 days, run − 8 days)
- **holdout (confirmation):** closes in [run − 7 days, run − 1 day)

Up to 40 markets per series per window (evenly spaced; weight recorded).

## Counting (identical for every series)

A long-shot trade: a taker buys the cheap side at a price in [1c, 2c]. Our counterfactual 99c bid on the
other side takes 25% of each such trade (as in Rounds 21/25), at most 1,000 contracts per market. P&L per
contract: +1c if the long shot loses, −99c if it wins, minus Kalshi's maker fee (quadratic, times the
series' fee multiplier). No queue model: the scan finds candidates; a forward paper test with real queues
decides.

## Selection (dev) and confirmation (holdout)

A series is a **candidate** if on dev: P&L > $0, ≥ 10 markets with long-shot fills, long-shot win rate (by
contracts) < 0.5%. It is **confirmed** if on holdout: P&L > $0 and no single market lost more than the series'
total holdout profit. Known crypto series are included as a control (hourly should confirm, 15-minute should
not).

## What happens next

Confirmed series go into a forward paper test with real queues (the Round 21 paper method) before any money.
Prediction written now: few series confirm; the favorite-longshot edge is strongest where a price signal
lets us bid before the crowd (crypto) and weakest where incumbents already sit at 99c (weather, sports).

## Result (2026-11-07, reports/ROUND27.md)

407 series, 20,499 markets. Long-shot buyers at 1–2c lose almost everywhere: 202 of 260 dev candidates
confirmed on the holdout, mostly sports (spreads, totals, tennis), plus commodities and a few weather series.
Big losers where long shots win often: TV/news "mention" markets, some weather highs, esports, golf leaders.

**The control failed:** the 15-minute crypto series "confirmed", although queue-aware recounts show they barely
fill (reports/FILLCHECK.md). Without the line of 99c bids ahead of us, the scan cannot tell where a newcomer
gets filled. So no series is accepted from this scan alone. Next: a live queue survey of the confirmed
whole-cent series (PROTOCOL_ROUND28.md).

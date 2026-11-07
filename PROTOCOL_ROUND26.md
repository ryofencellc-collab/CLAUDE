# Round 26 pre-registration: the live trader moves to the hourly crypto markets

Written 2026-11-07 ~16:30 UTC, before the dry run it will be judged on.

## Why (reports/FILLCHECK.md)

Kalshi's 15-minute crypto markets quote 0.1c steps between 90c and $1 (`tapered_deci_cent`). A long-shot buyer
paying under 1c trades with a bid above 99c, never with ours. Recounting all 433 paper fills from Kalshi's own
trade records, only trades that can reach a 99c bid:

| | paper count | honest count |
|---|---:|---:|
| 15-minute markets, 10k per market | ~$6,300 | **$150–270** (lower/upper bound) |
| hourly markets, 1k per market | $935 | **$935** (unchanged) |

The hourly markets (KXBTCD, KXETHD, KXSOLD, KXXRPD) are priced in whole cents (`linear_cent`): 99c is the top
bid, so the flow reaches it. Bidding above 99c on the 15-minute markets earns at most $270–770 at 10k per
market over the same 8 days, and a single loss at 99.9c costs ~1,000 wins: not worth it.

## The rule (live trader, `edge/live21.py`)

- Markets: hourly KXBTCD, KXETHD, KXSOLD, KXXRPD, "above strike" type, closing within the hour.
- Entry: the paper rule, z ≥ 6, where z is the **smallest** lead over Coinbase, Kraken and Bitstamp
  (`edge/prices.py`: ≥ 2 fresh exchanges, agreeing within 0.3%). Post-only 99c buy, expiring at the close.
- Cancel: the moment that z < 6, or prices are stale or disagree.
- One market at a time: among markets with ≤ 1,000 contracts already at 99c, the smallest z ≥ 6 (amended 2026-11-07 18:00 UTC, before the window: see below). Size = the governor's stake (0.5 for the first 14 live days)
  × balance / 99c. No Round 25 Kelly here (its table covers only the last 15 minutes).
- All other guards unchanged (governor, cash audit, pause/half size, daily stop, control file, veto).

## Expectation stated now

Replaying the paper ledger (Oct 31 – Nov 7) with one market at a time and half the balance per market,
starting at $1,000: **~$21/day**. Two or three at once do not help ($22–23/day): each gets less capital. Real
results should be lower, because a resting bid that never fills still blocks the one slot.

## Dry-run test (must pass before any money)

Window: the first 7 full UTC days the dry run runs this code, starting 2026-11-08 00:00 UTC.

1. 0 errors in `paper/live21_log.csv` that are not recovered within 5 minutes.
2. At most one losing filled market.
3. Dry P&L ≥ 50% of the one-at-a-time replay of the paper ledger over the same window and sizing.
4. Then, with the real key: the self-test passes and 24 hours of dry run with keys are clean.

Round 22 keeps running as a record, but no longer decides going live: its 15-minute profit was mostly flow
our bid could never have received.

## Amendment before the window (2026-11-07 ~18:00 UTC)

The first dry-run hours picked by shortest queue and chose ETH strikes at z = 18–26: queue 0, but lottery buyers
rarely touch strikes that far away (paper hourly fills: ~280–300 contracts per filled market at z 6–10, ~90 at
z > 15, ~40 at z > 30). The choice is now: queue ≤ 1,000 first, then the smallest z (still ≥ 6), then the
shorter queue. Entry and cancel rules are unchanged. Made before the 2026-11-08 00:00 UTC window opens.

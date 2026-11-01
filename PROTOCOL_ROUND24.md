# Round 24 pre-registration: binary options on the S&P 500 and Nasdaq-100, bid only once decided

Written 2026-11-01, before any Round 24 code ran on real data.

## Why

Round 14 tested 11 SPY option strategies on real or index-priced data and
none passed. Premium selling won about 91% of the time but never beat SPY,
because of its rare large losses.

Kalshi's S&P 500 and Nasdaq-100 markets (KXINXU, KXINX, KXNASDAQ100U,
KXNASDAQ100) are cash-settled binary options on the index, with fixed close
times. Round 21's edge (bid 99c only once the outcome is effectively decided
by the live price) passed its holdout on crypto and is +$332 on paper with
no losing fills. This round tests the same rule on index binaries.

## The trade

Round 21's rule, unchanged, with these inputs:

- **Index data:** 5-minute Yahoo bars for ^GSPC and ^NDX. Each bar is known
  only after it has closed. If no bar is less than 10 minutes old (overnight
  or on weekends), there is no signal.
- **Volatility:** the trailing 12 bars (one hour), converted to per-minute.
- **Decided side by market type:**
  - above a strike: YES is decided when z ≥ Z; NO when z ≤ −Z.
  - below a strike: the mirror image.
  - inside a range: NO is decided when the index is Z or more typical moves
    outside the range. A YES ("inside") is never treated as decided.
- **Sizing and accounting:** 25% of each long-shot fill (a taker buying at
  ≤ 2c), capped at 1,000 contracts per market. The maker fee is rounded up
  per fill, and long-shot wins count fully as losses.

## Split

Yahoo serves 5-minute bars only for the last 60 days.

- **Dev, 2026-09-03 to 2026-10-09:** choose Z from {2, 3, 4, 5, 6}, the
  highest dev net profit whose worst dev day is ≥ −$150.
- **Holdout, 2026-10-10 to 2026-10-30** (15 trading days).

## Pass rule (holdout, chosen Z, all must hold)

1. Net profit ≥ $300.
2. Profitable on ≥ 80% of days with fills.
3. Worst day ≥ −$150.
4. Long shots win ≤ 0.5% of our fills.

## Prediction written now

Fewer fills than crypto, because the market trades only 6.5 hours a day and
there are fewer lottery buyers. The calls should be very reliable near the
4 pm close. My guess: PASS at about $15–40/day, and a FAIL on profit is
quite possible.

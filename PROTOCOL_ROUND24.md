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

## Result (2026-11-01)

PASS. Z = 2 was chosen on dev. Holdout: $474.70 over 15 trading days, all of
them green, worst day +$4.31, long shots won 0.44% of fills. KXINXU (hourly
S&P) gave $430 of it. These are backtest fills at 25% capture. Round 21's
live test shows that the real queue at 99c sharply limits that capture, so
any live use needs its own forward test first.

## Forward test (amendment, 2026-11-02, before any live index bid)

The four index series join the Round 21 paper bot (`edge/paper21.py`), with
the same placement, queue, cancellation and settlement logic and these
inputs:

- Z = 2;
- Yahoo 1-minute index bars, the last completed minute only, with no bids
  when the latest bar is more than 5 minutes old;
- above, below and range markets, where a range's "inside" is never treated
  as decided;
- 1,000 contracts per market.

**Window:** 2026-11-02 to 2026-11-15 (10 trading days).

**Gate:**
1. Paper profit ≥ $150.
2. At most one losing filled market.
3. Profitable on ≥ 70% of days with fills.

## Fix during the forward test (2026-11-05)

Three filled losses came from KXINXU-26NOV05H1000 bids placed at 14:33 UTC, 3 minutes after the open.
With only 3 one-minute bars, the volatility estimate was near zero and z was inflated (4.8–6.1). The S&P
then fell, and the bids were cancelled at 14:36, after 1 contract each had filled (−$3 in total).

Fix: no index bids until today's session has at least 30 one-minute bars, i.e. from 10:00 ET. This
corrects a data-sufficiency bug. The rule itself (Z = 2, sizing, accounting) is unchanged. The three
losses stay in the record and count toward the gate (at most one losing filled market), so Round 24's
forward test now fails on that rule, and the result will be reported as such.

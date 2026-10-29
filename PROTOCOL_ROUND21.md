# Round 21 pre-registration: maker bids on crypto markets already decided by the spot price

Written 2026-10-29, before any Round 21 code ran on real data.

## Why

Round 20 (FAIL): blind 98–99c bids made money on fills within 15 minutes of
close (+$4.9M) and lost on earlier ones (−$4.8M). For games, the close time
is only known in hindsight, so that split can't be traded.

Kalshi's crypto markets close at fixed, known times. They settle on a
60-second average of the CF Benchmarks index against a strike, so whether
the outcome is effectively decided can be judged live from the spot price.
This is Round 18's idea applied to crypto.

## The trade

At each long-shot fill in Round 20's sense (a taker buys one side at
px ≤ 2c, filling a ≥ 98c bid on the other side):

1. Take the Binance spot price from the last **completed** minute before the
   fill, nothing later.
2. Compute z = ln(spot / strike) / (σ × √τ). σ is the per-minute volatility
   over the trailing 60 minutes; τ is the minutes left to close, with a
   floor of 0.5.
3. We are in the fill only if the spot price says **our** side is winning
   by z ≥ Z.

Our share is 25% of each fill, capped at **1,000 contracts per market**
(about $990 at risk, a realistic size). The maker fee is rounded up per
fill, and every long-shot win counts as our loss.

## Universe

- **15-minute "up or down" markets:** KXBTC15M, KXETH15M, KXSOL15M,
  KXXRP15M, KXDOGE15M, KXBNB15M.
- **Hourly "above strike" markets:** KXBTCD, KXETHD, KXSOLD, KXXRPD.

Only "greater" and "greater or equal" markets are included, and only coins
with Binance spot data. Series with more than 1,500 markets per period are
sampled evenly, as in Round 20.

## Split

- **Dev, 2026-04-01 to 2026-09-29:** choose Z from {1, 2, 3, 4, 5, 6}. Pick
  the Z with the highest pooled net profit among those whose worst dev day
  is ≥ −$150. If none qualifies, FAIL.
- **Holdout, 2026-10-01 to 2026-10-27:** never used by Round 20. The
  probe19c hours fall in it, but they only gave series totals.

## Pass rule (holdout, at the chosen Z, all must hold)

1. Net profit ≥ $500 over 27 days.
2. Profitable on ≥ 80% of days.
3. Worst day ≥ −$150.
4. Long shots win ≤ 0.5% of our fills.

## Prediction written now

PASS at Z of about 3–4, roughly $20–60 a day. Basis risk between Binance and
CF Benchmarks shows up as a few losses at low Z.

## Result and forward test (amendment, 2026-10-29, after the backtest and before any live run)

**Backtest result:** PASS. Z = 6 was chosen on dev. Holdout: $16,255 in 27 days,
100% green days, 0 long-shot wins in 61,923 fills. KXBTC15M timed out and is
not in the result.

**Forward test.** `edge/paper21.py` runs in back-to-back ~5.5-hour GitHub
Actions jobs and polls every ~15 seconds:

1. Find open markets in the 10 series that close within the hour.
2. Compute z from the **Coinbase** spot price, using its last completed
   minute and the trailing 60-minute volatility. (Binance blocks US servers.
   Coinbase is also a constituent of the CF Benchmarks index the markets
   settle on.)
3. If z ≥ 6 for a side, place a paper bid of 1,000 contracts at 99c for that
   side, and record the queue resting at ≥ 99c ahead of us.
4. We are filled only by later public trades where a taker bought the other
   side at ≤ 2c, after the queue ahead is used up.
5. Settle on Kalshi's result.

**Gate (14 calendar days of results):**

1. No more than one losing filled market.
2. Paper profit ≥ $300 (≈ $21/day, about 1/30 of the backtest's pace).
3. A profit on ≥ 80% of days with fills.

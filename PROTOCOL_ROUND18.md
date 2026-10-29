# Round 18 pre-registration: rest bids on decided Kalshi weather outcomes (maker side)

Written 2026-10-28, before any Round 18 run.

Round 17 showed that after an outcome is decided, almost nobody *sells* the
winning side cheaply (only 386 trades in 12 months). Most later trades are
takers buying the *losing* side for 1–2c as lottery tickets. The other side of
each of those trades is a resting bid for the winning side at 98–99c.

## The trade

Once an outcome is decided (Round 15's rule unchanged), rest a bid for the
decided side at 99c. Each later trade where a taker bought the losing side at
price q fills resting bids at 1 − q. Profit per contract = q − Kalshi's maker
fee. We assume the maker fee formula 0.0175 × C × P × (1 − P), rounded up to
the cent per fill, which is conservative where maker fees are zero.

## Simulation

We take a 25% share of each such fill (other bids share the queue), with 100%
shown for reference. Each fill is capped at $100. Window and cities as in
Round 15. The pass rule is identical to Rounds 15 and 17.

## Prediction written now

Accuracy and days pass easily. Profit is the question. Lottery tickets are
small, so I expect roughly $3–$15 a day at 25% capture, short of $2,000 a year.

## Forward test (amendment, 2026-10-28, written after the backtest passed and before any live run)

The backtest can't see queue position: historical order books don't exist, so
"25% capture" is an assumption. The forward test measures it live, with no money.

**Bot:** `edge/paper18.py`, run every ~10 minutes by `.github/workflows/paper18.yml`.

1. It reads live ASOS reports and finds markets newly decided by Round 15's rule.
2. It places a paper bid of 1,000 contracts at 99c on the decided side.
3. At that moment it records the live order-book size already resting at
   99c or better on that side (the queue ahead).
4. A later public trade fills us only once it is a taker buying the losing
   side at 1c, and only after the whole recorded queue ahead is used up.
   Cancels ahead of us are ignored, which is conservative.
5. Orders settle on Kalshi's official result. Pnl = filled × (payout − 0.99) −
   the maker fee.

**Window:** 30 calendar days of settled climate days, starting with the first run.

**Pass rule (all must hold):**

1. No settled filled order lost; every miss is reported in full.
2. Paper profit ≥ $600 over the 30 days (≈ $20/day, under a third of the
   backtest's $65.70/day).
3. Profit on ≥ 60% of days that had any fill.
4. Fills on ≥ 20 of the 30 days.

**If it passes:** go live small. Up to $1,000 of capital, same rules, scaled
to what the fills show.

**If it fails:** the queue at 99c is too deep, and Round 18 is not a money printer.

**Prediction:** the queue ahead at 99c will often be large, because existing
market makers sit there. I expect a fill on some days but under $20/day, so
probably FAIL on rule 2.

**Operational note (2026-10-29).** GitHub ran the 10-minute cron only 3 times
on day 1 (10:39, 10:40, 17:04 UTC), so day-1 bids were placed late. From
2026-10-29 ~18:45 UTC each job instead loops the bot every 5 minutes for
about 5.75 hours, with jobs queued back to back. The rules and gate are
unchanged. Day 1 counts in the window, flagged as sparse coverage.

# Round 39 pre-registration: 0DTE / short-dated index options, without a paid data account

Written 2026-11-09 (Sunday), before any 0DTE quote has been collected and before the 39a data is fetched.

## Why this round exists
No free source has *historical* intraday option quotes (paid: ThetaData, Cboe DataShop, optionsDX intraday files).
Two things are free and reachable from GitHub Actions without an account:
1. **Cboe's delayed-quote feed** (`cdn.cboe.com/api/global/delayed_quotes/options/_SPX.json`, `SPY.json`), which carries every
   listed contract's bid/ask/size/IV/delta, ~15 minutes delayed. 0DTE SPX lives under root `SPXW`. Delay does not
   matter for a paper test: every decision uses only the snapshot it sees, and fills use that snapshot's bid/ask.
2. **Cboe index histories** (VIX1D, VIX9D, VIX, SPX daily OHLC).

## 39a: historical screen (model-priced; can rule things out, cannot prove them)
Question: do 0DTE options charge more than the move they insure? VIX1D is computed from 0DTE/1DTE SPX prices, so it is
the market's own price of the day's move.
- **A (open → close):** sell an ATM straddle at the open, priced `S_open · VIX1D_open/100 · sqrt(1/252) · sqrt(2/π)`;
  P&L = premium − |close − open| − 0.6 index points (half the bid/ask on entry; held to the cash-settled close).
- **B (close → next close):** the same from the prior close with VIX1D_close (includes the overnight gap).
- **C (short strangle ±1 implied move, open → close):** strikes at ±premium-equivalent move, normal-model price, no
  skew. The model underprices puts, so C is *optimistic* for the seller; it is shown, not passed.
Dev = first half of the VIX1D dates, holdout = second half. Pass (A, B only): mean P&L > 0 on both halves, holdout
t-stat ≥ 3. A pass only earns the strategy family a slot in 39b; it is never a go-live signal.

## 39b: forward test on real collected quotes (the real test)
Collector `edge/odte.py` (workflow `odte.yml`): Mon–Fri 13:20–21:20 UTC, every 60 s, SPX + SPY chains, expiries ≤ 3
calendar days, strikes within ±4% of spot, stored under `data/odte/`.

Strategies (each on SPXW and on SPY; entries at 10:00, 11:30, 13:00, 14:30 ET, using the first snapshot whose feed
time is at or after the entry time):
- **I1 iron condor, hold to expiry:** sell the ~10-delta put and call, buy wings 25 SPX points / 2.5 SPY points out.
- **I2** I1 with a stop: close all legs when the cost to close ≥ 2× the credit (buy at ask, sell at bid).
- **I3** I1 at ~20 delta.
- **T1 trend credit spread:** if spot > the 09:45 snapshot, sell the ~15-delta put spread; otherwise the call spread;
  same widths; hold to expiry.
- **L1 long straddle** (the other side of the trade): buy the ATM call + put at the entry; sell at 15:45 ET at bid.
- **B1 breakout:** after 10:00 ET, the first snapshot with spot above the 09:30–10:00 high (below the low) buys the
  ATM 0DTE call (put) at ask; exit at bid at +100%, −50%, or 15:45 ET; one trade per day.
Fills: sell at bid, buy at ask, from the same snapshot. Commissions $0.65/contract (SPY), $1.50/contract (SPX, incl.
exchange fees). Expiry value from the last snapshot at/after 16:00 ET (SPXW PM-settled, SPY intrinsic at the close).
Days with fewer than 60% of the expected snapshots are reported and excluded.

Pass (each config, scored after ≥ 20 and again at 40 trading days): mean P&L per trade > 0 with a 90% bootstrap lower
bound > 0, profitable in both the first and second half of the days, and worst day ≥ −3× the mean credit or debit.
Reported for every config: win rate, average win/loss, worst day, $/day on $25k and $1k (SPY/XSP-sized).
With ~4 entries a day × 20 days, only a strong effect can pass at 20 days; that is the point.

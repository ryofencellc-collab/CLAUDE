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

## Amendments (before any market-hours data)
- 2026-11-09: collector smoke test showed `data/` is git-ignored; snapshots are now force-added and also uploaded as a
  90-day artifact. First daily job moved to 12:50 UTC so a late cron cannot miss the 09:30 ET open. No strategy changes.

- 2026-11-09 (day one): GitHub's cron never fired the 12:50 UTC start; started by hand at 14:32 UTC (feed ~15 min
  behind, so the feed's 09:30 ET open is still captured). The collector now chains itself job to job (waits between
  windows) instead of relying on cron. No strategy changes.

## 39a result (2026-11-09) — model screen: **A fail, B fail**
SPX + VIX1D 2022-05 → 2026-11, 1,126 days (`reports/ROUND39A.md`). Selling the 0DTE straddle at the VIX1D price earned
on average +3.2 index points a day (≈ +$320 per SPX 1-lot, t = 3.8 over all days, 62% win rate), but the holdout half
only reached t = 1.7 (needs 3), and the worst day was −330 points (−$33,000 on one SPX straddle). 0DTE options do look
slightly overpriced on average, but the margin is about 10% of the premium and one bad day erases roughly 100 good
ones. It goes to 39b as planned (I1–I3 are the defined-risk version) but is not a go-live signal.

## Amendment (2026-11-17 23:40 UTC): breakout filter variants B2–B5 (registered after 7 days of B1 data)
B2: breakout by 11:00 ET only. B3: only breakouts in the day's direction (call above the prior close, put below; a
misaligned breakout is skipped and the next aligned one taken). B4: only on days when VIX1D opens at or above its prior
20-day median. B5: −50% stop, no profit target, exit 15:45. The scorer also fills them in for Nov 9–17, but those days
were already seen. **Their verdict counts only trading days from 2026-11-18 onward** (20 days → about Dec 16). Same
pass rule as B1.

## Amendment 2026-11-18: feed-time bug fix + F1 added
- **Bug:** the Cboe feed timestamp is its publish time, and the quotes in it are exactly 15.0 minutes older. `last_trade_time` lags `ts_feed` by
  15.0 min all session on every day checked. Every strategy's clock was therefore 15 minutes late. Entries labelled 10:00 really used
  09:45 prices, and B1's "09:30–10:00 opening range" really covered 09:15–09:45, a quarter of it pre-open.
  `odte_score.load_day` now subtracts 15 minutes, and all days are re-scored under the corrected clock. The rules themselves are unchanged.
- **F1, from Reddit r/options:** a 0DTE SPX iron butterfly entered at 14:50 ET with ATM shorts and ±$15 wings (±$1.5 on SPY), taking profit at 15% of the
  credit, else held to expiry, skipping FOMC days. It is scored with bid/ask fills (F1) and with mid fills (F1m, as no-code platforms do).
  The same pass rule applies at 20 and 40 trading days.

## Amendment 2026-11-20: S1 trend-pullback scalper (reverse-engineered from a Reddit trader's Nov 16 SPY put day)
- **Trend mode** (after 10:00 ET): DOWN if spot is below the 09:30–10:00 range low and below the session mean; UP is the mirror.
- **Entry:** a 0.10% bounce off the running low (DOWN) or high (UP) buys the ATM put (or call) at the ask.
- **Exit:** at the bid, on the first of +25%, −15%, 10 minutes, or 15:45.
- **Sizing:** one position at a time, 1 contract, re-entry allowed until 15:30. It is scored with the other 39b strategies (20/40-day pass rule).

**Backfill on the 9 recorded days (Nov 9–19), corrected clock:**
- SPY: 107 trades, **−$638** (−$6 a trade, 36% win).
- SPXW: 112 trades, **−$1,846** (41% win).
- On Nov 16 itself, the trend day the Reddit trader posted, the rule took the same strikes at about the same times ($745/$746 puts mid-morning, $739/$740 puts after 13:40) and still **lost $46**.

The posted profit came from discretion and sizing (2 → 42 contracts), not from a repeatable entry/exit rule.

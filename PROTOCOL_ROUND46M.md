# Round 46m: forward paper test of the Mentions favourite-maker cell (written 2026-11-18, before any data)

**Why:** Round 45b found one Mentions cell that passed on holdout: makers holding the 85–95¢ favourite with less than 1 hour to close earned
+7.3% per dollar (t 9.1). The cell was never forward-tested because Round 46 covers only Sports and Entertainment.

**Rule.** This is the Round 46 engine (`edge/fav.py`) with `R46_TAG=m`, `R46_CATS=Mentions`, `R46_MAX_HOURS=1`.
- **Scan:** every 5 minutes, scan open Mentions markets that close within 1 hour.
- **Bid:** rest a paper maker bid at the favourite's best bid when it is inside 85–95¢. Re-peg while it stays in the band.
- **Limits:** $200 per market, at most 3 per event, 1 per ladder, $10,000 budget.
- **Fills:** from real trades at or through our price, after the queue ahead of us is used up.

**Pass (after 14 calendar days):** the same as Round 46. Every one of these must hold:
1. at least 100 filled events;
2. return of at least +2% per dollar, with event-clustered t ≥ 2;
3. positive in each week;
4. worst day no worse than −$400.

## Result (2026-11-18): **STOPPED, not implementable** (0 bids in 9 hours)
Kalshi Mentions markets **close early, when the event ends**. Settled markets carry actual close times such as 17:24:31, while open
markets show only their later scheduled close. Round 45/45b binned "hours to close" against the *actual* close, which is unknowable
in real time, so the "< 1 h" Mentions cell used hindsight timing. A live bot can't see which markets are about to resolve. The
tracker never found a market inside the window, as expected given that.

**Knock-on:** Round 45b cells that use time-to-close in early-closing categories (Mentions, and partly Sports, where games end early)
share this flaw. Round 46 (Sports/Entertainment, scheduled close within 7 days) is unaffected as a forward test. Its own live
results are the honest measure, but its motivation from Round 45's "1–24 h" bins is weaker than it looked.

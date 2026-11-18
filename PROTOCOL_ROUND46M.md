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

# Round 46 pre-registration: rest bids on the favourite in Sports and Entertainment (forward paper)

Written 2026-11-10, after Round 45/45b (11 of 485 cells passed; all of them are "maker holds the favourite at
.70–.95" in Sports, Entertainment, Elections, Politics and Mentions) and before any forward data.

**Rule.** Every 15 minutes, scan open markets in Sports and Entertainment series that close within 7 days. If the
favourite side's best bid is between 85c and 95c (the YES bid, or the NO bid = 1 − YES ask), rest a paper bid for that
side at the best bid, behind the queue already there, with ~$200 per market (≤ 50 markets, $10,000 budget). Every
2 minutes, fill from the public trade tape (the queue ahead goes first; a trade through our price fills us), re-peg to
the new best bid while it stays inside 85–95c, otherwise cancel. Stop at the market's close. Filled contracts are held to
settlement. P&L = filled × (1[side wins] − price) − maker fee (0.0175·p(1−p), charged even where the series has none).
**Reported:** fills, events, return per dollar, event-clustered t, by category and week; capital used; daily P&L.
**Pass (after 14 calendar days):** ≥ 100 filled events, return ≥ +2% per dollar with event-clustered t ≥ 2, positive
in each week, and worst day ≥ −$400. A pass makes it the live candidate (with Round 44 if that passes too).
**Known gap:** the queue model ignores cancellations ahead of us (conservative) and assumes we see every trade.

## Amendment 1 (2026-11-10, after a 15-minute smoke run, before the forward test)
The smoke run placed all 48 bids on one NFL game's receiving-yards props, several of them strikes of the same
player's ladder: one correlated bet. Now at most 1 market per ladder (ticker minus its trailing number) and 3 per
event, and the series are scanned in a shuffled order so bids spread across games. The smoke ledger is discarded.

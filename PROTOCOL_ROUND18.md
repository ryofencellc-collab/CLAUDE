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

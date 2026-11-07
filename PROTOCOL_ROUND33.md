# Round 33 pre-registration: a price-honesty map of Kalshi (where are prices wrong by more than the fee?)

Written 2026-11-07, after forum/paper research (Polymarket weather favourites overpriced in the last 1–12 h,
arXiv 2610.13593; favourite–longshot bias strong in crypto/politics, absent in sports, arXiv 2609.12878;
practitioner claims about Kalshi's 88–95c NO range). Round 31 showed 15-minute crypto is honest; this checks
everything else.

## Data

Every series in Round 27's scan (407) except the 15-minute crypto ones. Settled yes/no markets closing
2026-09-10 → 2026-11-07 (after Kalshi's historical cutoff, so batch candles work), up to 150 per series, evenly
spaced. Hourly candlesticks for the last 48 hours; YES bid/ask at 48, 24, 12, 6, 3 and 1 hour(s) before close.

## Test

For each category × hours-before-close × price band of the side bought (2–5, 5–10, 10–20, 20–40, 40–60, 60–80,
80–90, 90–95, 95–99c): buy that side at its ask, pay Kalshi's taker fee, $1 contracts, one bet per market per
horizon. **Dev:** closes before 2026-10-15; **holdout:** from 2026-10-15.

**A cell is an edge if:** dev P&L > 0, holdout P&L > 0 with ≥ 100 holdout markets, and holdout t-stat ≥ 3.5
(strict: ~540 cells are tried). Also reported, as an optimistic upper bound: the same bet as a resting order at
the bid with the maker fee (fills not verified).

Prediction written now: most cells lose by about the fee; any edge is in weather/climate favourites near the
close or in long shots being overpriced (which favours our maker 99c approach, not taking).

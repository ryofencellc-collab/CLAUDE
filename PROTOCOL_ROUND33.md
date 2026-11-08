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

## Fix after the first run (2026-11-07, before any result was used)

The first run had almost no dev data (market listing pages ran newest-first, so the dev window was crowded out)
and was dominated by empty books quoted as bid 3c / ask 97c (both sides then look like 97c favourites that win
half the time). Now: dev and holdout are listed separately (75 markets each per series), and only quotes with a
spread ≤ 5c count. Same cells, same pass rule.

## Result (2026-11-08, reports/ROUND33.md): no edge

With only tradable quotes (spread ≤ 5c), 2,437 markets in 148 series. The dev window still loaded almost no
quotes (Kalshi's batch candlestick endpoint returned little for markets that closed before mid-October), so
the formal pass test could not run. It does not matter for the verdict: on the holdout alone, **no cell is off
by more than ~3c and no cell has a t-stat above 1.2** across every category, horizon and price band. Buying at
Kalshi's quoted price, anywhere, pays about the fee to the house. Kalshi's prices are honest; the money is on
the maker side.

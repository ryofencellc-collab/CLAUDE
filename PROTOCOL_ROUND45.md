# Round 45 pre-registration: where do Kalshi makers earn? (favourite–longshot bias by category, price and timing)

Written 2026-11-09, before the data is fetched.

**Why.** Published work (Bürgi–Deng–Whelan 2025, >300k Kalshi contracts; Becker, 72M Kalshi trades; Le 2026)
finds longshots overpriced and favourites underpriced, but makers as a group still lose ~10%. The question is whether
any well-defined slice (category × the maker's price × time to close) earns after fees, robustly enough to trade or to
tilt the Round 44 quoting.

**Data.** Every Kalshi series (`/series`, with category and fee type). Settled markets closing 2025-11-01 → 2026-11-01
(live and historical endpoints). Up to 80 random markets per series, shuffled and fetched within a 5-hour budget (a
cut-off run is still a random sample). At most 5,000 trades per market. Dev: closes before 2026-07-01. Holdout: after.
**Measure.** For every trade, the maker holds the side the taker did not buy, at price x (the taker's YES price p →
maker holds NO at 1−p; taker's NO price → maker holds YES at p). Maker P&L per contract = 1[maker's side wins] − x −
maker fee (0.0175·x(1−x) where the series charges maker fees, else 0). Return = P&L / x per dollar risked.
**Cells.** Category × maker price bucket {.01–.05, .05–.15, .15–.30, .30–.50, .50–.70, .70–.85, .85–.95, .95–.99} ×
time to close {< 1 h, 1–24 h, 1–7 d, > 7 d}. Statistics are clustered by event (outcomes within an event are one draw).
**Pass.** A cell is a candidate if on dev it has ≥ 100 events, contract-weighted return ≥ +3% per dollar and
event-clustered t ≥ 3. It passes if the holdout has ≥ 30 events, return > 0 and t ≥ 2. Reported for all: the overall
calibration curve (a sanity check against the literature: longshots should win less often than their price implies).
**Caveat.** These are returns of makers who got filled. Our own fills depend on the queue, as Round 41b showed. A
passing cell becomes a forward paper test (or a tilt in Round 44), not a funded strategy.

## Amendment 1 (2026-11-09 21:10 UTC, no data seen)
The first run downloaded 11.4M trades from 44k of the 84k sampled markets, then crashed while saving. A loop variable
had overwritten the file path. Nothing was analysed and the data was lost. Fixed, checked offline with stubbed
endpoints, and the download now checkpoints every 5,000 markets. Re-run unchanged otherwise.

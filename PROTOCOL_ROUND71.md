# Round 71 pre-registration: share-class pairs, a high-win-rate stock strategy with a structural reason

Written 2026-11-21, before any result beyond a GOOG/GOOGL data check (3,179 days; GOOGL−GOOG log gap 1st–99th pct −2.8% → +4.7%; 351 days with |z| ≥ 2).

## Idea
Two share classes of one company have the same business, the same earnings and nearly the same dividends; only voting rights and liquidity differ. Their price gap can stretch but has no reason to wander off, so trading the gap back should win most of the time. Round 38 showed that plain dip-buys win 56–65% and make ~0. This round tests a gap anchored by the company itself.

## Universe (both classes US-listed; fixed now)
GOOGL/GOOG, FOXA/FOX, NWSA/NWS, LEN/LEN-B, HEI/HEI-A, BF-B/BF-A, Z/ZG, FWONK/FWONA, LBRDK/LBRDA, CWEN/CWEN-A, UHAL-B/UHAL, MOG-A/MOG-B, GEF/GEF-B, LGF-A/LGF-B, BATRK/BATRA, RUSHA/RUSHB, MKC/MKC-V, TAP/TAP-A, BIO/BIO-B.
- Pairs with < 500 overlapping days are dropped, and the drops are reported.
- **Survivorship:** pairs that were collapsed into one class (e.g. DISCA/DISCK, VIAB, LSXM) are missing from free data. They usually collapsed at or near parity, so the bias should be small, but it is noted.

## Rule (primary, fixed)
- r = ln(A) − ln(B) on adjusted closes.
- z = (r − its 60-day mean) / its 60-day sd, both from days before t.
- **Entry:** |z| ≥ 2 at the close on day t. Trade at the **next day's close**: buy the cheap class, sell the rich class, $1 each side.
- **Exit:** when z crosses 0 (trade at the next close), or after 20 trading days.
- At most one open trade per pair.
- **Costs per leg per trade side:** half the Corwin–Schultz high-low spread estimate (20-day median, ≥ 1 bp). Short borrow 2%/yr on the short leg.
- **Trade return** = long return − short return − costs.

## Small grid (reported; the dev choice gets one holdout look)
Window {20, 60, 120} × entry {1.5, 2.0, 2.5}, with exits as above. The best dev mean net trade return (≥ 50 dev trades) is the "dev choice".

## Split
Dev 2010-01-01 → 2017-12-31; holdout 2018-01-01 → 2026-11-20.

## Pass (primary rule, holdout; the dev choice is reported with the same tests)
- win rate ≥ 70%;
- mean net trade > 0 with t ≥ 2.5;
- profit factor ≥ 1.5;
- ≥ 20 trades/yr;
- portfolio, capital split equally over the pairs, each open trade using its pair's slot:
  - Sharpe ≥ 1.0;
  - max drawdown ≤ 15%.

A pass goes to a live paper tracker (real quotes, next-close fills), not money.

## Calibration (synthetic, before real data)
- **Null:** independent random walks with equal volatility. It must FAIL; mean reversion on unrelated stocks can still win often but loses big.
- **Planted:** B·exp(OU gap, half-life 10 days, sd 1.5%). It must PASS.

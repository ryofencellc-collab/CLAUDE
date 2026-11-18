# Round 56: mega-search: every intraday combination we can enumerate (written 2026-11-18, before any data)

The user asked to test "as much as we possibly can". To keep a huge search honest, this round uses a three-way split. The final period
is untouched until the search and selection are frozen.

| Period | Years | Use |
|---|---|---|
| Search | 2012–2019 | every configuration is scored |
| Selection | 2020–2022 | shortlist |
| Final exam | 2023 → now | only the 20 shortlisted configurations are evaluated |

## Grammar (per market)

| Part | Choices | Count |
|---|---|---|
| Entry time (bar open) | every 15 min, 09:45 → 15:30 ET | 24 |
| Signal | overnight gap; since open; last 15/30/60 min; prior day; prior 5 days. Each as momentum or reversal | 7 × 2 = 14 |
| Filter | none; \|signal\| ≥ its trailing 1-year median; \|signal\| ≥ its trailing 75th percentile; prior-day range above/below its 60-day median; each weekday; above/below the 20-day average | 12 |
| Hold | 15, 30, 60 or 120 minutes, or to 15:59 | 5 |
| Stop | none, 0.25%, 0.5%, 1% | 4 |

- **Per market:** 24 × 14 × 12 × 5 × 4 = **80,640** configurations.
- **Markets:** S&P, Nasdaq, gold, oil, EURUSD, USDJPY, GBPUSD (HistData 1-minute bars; costs as in Round 54), so ≈ **564,000** in total.

All signals use only data before the entry bar. P&L is in basis points after costs.

## Selection (frozen)
1. Search: mean > 0 and t ≥ 2.
2. Selection: mean > 0 and t ≥ 2.
3. Rank the survivors by the smaller of the two t values. Take the top 20, at most 5 per market and at most 1 per (market, signal, entry time).

## Final exam
A shortlisted configuration **passes** if it has final-period mean > 0, t ≥ 2.81 (Bonferroni over 20, one-sided 0.0025) and at least 100 trades.

## Calibration (run in every job's smoke step)
The full pipeline is run on synthetic data:
- On a random walk, nothing should pass.
- With a planted "10:30 reversal of the since-open move" (k = 0.3), it must be shortlisted and pass.

## Amendment (2026-11-18, before any real data): bigger grammar and more markets
The first engine ran in 7 seconds per market, so the grammar was enlarged before any real run.

| Part | Choices | Count |
|---|---|---|
| Entry time | every 5 min, 09:35 → 15:50 | 76 |
| Signal | adds last 5 / last 120 min and prior 20 days (10 signals), each as momentum or reversal | 10 × 2 = 20 |
| Filter | adds a 90th percentile, gap up, gap down and the last 3 trading days of the month | 16 |
| Hold | 5, 15, 30, 60, 120 or 240 minutes, or to the close | 7 |
| Stop | none, 0.1%, 0.25%, 0.5%, 1% | 5 |

- **Per market:** **851,200** configurations.
- **Markets added:** silver (3 bp), Brent (3), AUDUSD (1.5), USDCAD (1.5), DAX (1.5), FTSE (1.5) and Nikkei (2), all during NY hours. That makes **14 markets ≈ 11.9 M configurations**.

The selection and final-exam rules are unchanged.

**Calibration, 2-year synthetic data, enlarged grammar:**
- Planted lunch reversal: recovered and passed.
- 6 random-walk null runs: 1 false pass, in line with the ~5% family-wise rate that Bonferroni over 20 gives.

Every market job's smoke step asserts that the planted edge is recovered.

# Round 60: "quiet traders": modest, steady, low-risk winners (user's idea, written 2026-11-19 before any results)

**Idea:** in Round 59 the loudest winners (top PnL or ROI) did worst afterwards. The user suggests looking below the top, at traders with modest but
steady gains, small drawdowns and moderate activity.

**Data.** The same 6,000-account sample as Round 59 (seed 59, all-time volume ≥ $5M), from the `portfolio` all-time PnL and account-value history,
plus each account's monthly volume from the leaderboard.

**Quiet-trader groups**, defined on a selection window with all inputs known at its end:
- **Q1 "steady earners":** ROI in the window between +5% and +60%; ≥ 70% of PnL increments positive (≥ 8 increments); max drawdown ≤ 10% of
  account value.
- **Q2 "low-turnover winners":** ROI > +5%; monthly volume / account value below the eligible median (less churn and leverage); max drawdown ≤ 20%.
- **Q3 "small and steady":** account $10k–$250k, ROI > +5%, max drawdown ≤ 15%, ≥ 60% of increments positive.

Max drawdown = the largest peak-to-trough fall in cumulative PnL inside the window, divided by account value at the window start.

**Tests.**
- **Historical split 1:** select Jun 1 → Sep 1, test Sep 1 → now. This is Round 59's split. Its aggregate was already seen (every ROI decile lost), so
  this split alone cannot pass.
- **Historical split 2:** select Jul 15 → Oct 1, test Oct 1 → now.
- **Forward test (the real one):** select the groups on Aug 18 → Nov 19 data, freeze the address lists today, and score Nov 19 → Dec 19.

**Scoring** is the same as Round 59. Groups take all qualifying accounts, capped at 50 by highest steadiness.
- ROI in the test window is winsorized to [−1, 3].
- Group mean ROI t ≥ 2.4 (Bonferroni over 3 groups).
- Welch t ≥ 2.4 against the eligible universe.
- At least 55% of the group profitable.

**Pass** = split 2 passes AND the forward test passes. Only then is a copy simulation (delays, fees) built.

**Calibration:** a synthetic population. Null (luck only) must not pass. With 5% "quiet skill" accounts planted (small positive drift, low
volatility), the matching group must pass.

# Round 59: do Hyperliquid's winning traders keep winning? (written 2026-11-19, before any results)

**The user's ask:** "see what others are doing and tweak their process."
**Source:** Hyperliquid is a public on-chain futures exchange. Its leaderboard (48,003 accounts) and every account's PnL and
account-value history are public and free.

**Question.** If you picked last quarter's best traders, would they make money *next* quarter? If they do, copying them
(Round 59b, which simulates delayed copying with fees) is a strategy. If they don't, the leaderboard is luck.

**Sample.** 6,000 accounts drawn at random (seed 59) from leaderboard accounts with all-time volume ≥ $5M. Dead and empty accounts
are included, so the sample has no survivorship bias. Data comes from the `portfolio` endpoint: the all-time `pnlHistory` and
`accountValueHistory`, each a step series.

**Windows.**
- Selection window A: 2026-06-01 → 2026-09-01.
- Test window B: 2026-09-01 → data end (~2026-11-18).

**Eligibility, all known at the start of B:**
- account value at the start of A is at least $1k;
- account value at the start of B is at least $10k (still alive, so copyable);
- at least 4 PnL points inside A.

**Measures.**
- PnL_A = pnl(B start) − pnl(A start).
- ROI_A = PnL_A / mean(account value at A start, account value at B start).
- ROI_B = PnL_B / account value at B start, winsorized to [−1, +3].

**Groups (50 accounts each).**
- G1: top PnL_A.
- G2: top ROI_A among accounts with PnL_A ≥ $10k.
- G3: top "steadiness", meaning the mean / std of PnL increments in A (at least 6 increments), with PnL_A > 0.

**Pass (for any group; Bonferroni over 3 groups, so the t bar is 2.4).** All three must hold:
1. The group's mean ROI_B > 0 with t ≥ 2.4.
2. The group's mean ROI_B beats the eligible-universe mean, Welch t ≥ 2.4.
3. At least 55% of the group is profitable in B.

A pass sends that group to Round 59b, a copy simulation using real fills, a 1–5 minute delay and taker fees.

**Calibration.** A synthetic population of 6,000 accounts:
- Null: pure luck, with no skill. Must not pass.
- Planted: 5% of accounts carry persistent skill. Must pass.

## Result (2026-11-19): **FAIL**: top traders do not persist (`reports/ROUND59.md`)
- **Sample:** 5,999 accounts sampled; 1,399 were eligible (still holding ≥ $10k on Sep 1).
- **Universe in the test window:** mean ROI −12%, and only 30% of accounts profitable.
- **All three groups lost money in the test window:**
  - biggest PnL: −15%, 24% profitable;
  - best ROI: −28%;
  - steadiest: −15%.
- **Decile table:** the selection window's best-ROI decile did the *worst* in the test window (−26%) and its worst decile did about average.
  That is mild reversal with no persistence. The reversal is not significant against the universe (Welch t −0.5 to −1.6), so "fade the winners" is
  not supported either.
- **Takeaway:** on a perp exchange, a quarter of leaderboard success is mostly leverage plus luck. Copying past winners would have lost money.

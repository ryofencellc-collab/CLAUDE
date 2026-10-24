# Round 2 results

Official run: GitHub Actions run
[40097238226](https://github.com/ryofencellc-collab/CLAUDE/actions/runs/40097238226),
2026-10-24. Rules: [PROTOCOL_ROUND2.md](../PROTOCOL_ROUND2.md).
Cumulative trials across both rounds: 160 (used for all deflation).
Full per-config tables are in the run's logs and `round2-*` artifacts.

**Verdict: 0 of 5 families passed.** One family (football value betting)
produced the first result in this experiment worth a forward test.

## Correction (2026-10-24, run 40101597740)

The original section A numbers were produced by a bug. The window-id code
assumed nanosecond timestamps; the data loaded at microsecond resolution, so
every day fell into one long "window". The fair-value / opening price became
the **first open of 2012**, so ORB went long almost every day and JJ's
"above/below fair value" was nearly constant. In a bull market that gave a
fake ~52% ORB win rate. Fixed in commit 0df5fee (resolution-independent day
ids) and re-run. **Corrected numbers:**

| | In-sample 2012–2022 | Holdout 2023–2026 |
|---|---|---|
| JJ variants with positive Sharpe | **0 of 72** (all −0.67 to −2.19) | 13 of 72; best +0.57 (571 trades, +29R): nowhere near 1.0, and that config was −1.0 Sharpe in-sample |
| JJ win rates | 36–44% | 40–46% |
| ORB, all 12 variants | Sharpe −0.13 to −3.96 | Sharpe −0.02 to −0.94; win rate 16–42% |
| Null test passes | | 0 of 2 seeds |

Verdict unchanged, and if anything stronger: no edge. Football (B) and
Polymarket (C) did not use this code and are unaffected. The original
(buggy) section is kept below for the record.

## A. (ORIGINAL, superseded by the correction above) The TikTok strategy (JJ Simon "Fair Value Theory") on Nasdaq-100

Data: 4,753,177 one-minute bars, 2012-01-03 → 2026-10-01 (HistData NSXUSD).
Costs 1.25 points per round trip. 72 mechanised variants + 12 opening-range
breakout variants.

| | In-sample 2012–2022 | Holdout 2023–2026 |
|---|---|---|
| JJ variants with positive Sharpe | **0 of 72** | 11 of 72 (best +0.38, none close to 1.0) |
| JJ win rate range | 34–47% | 40–49% |
| Win rate needed to break even at 1.5R incl. costs | ~42% | ~42% |
| Best JJ variant (by holdout, for reference only) | — | +0.027 R/trade on 451 trades: indistinguishable from zero |
| Opening range breakout, all 12 variants | Sharpe −0.28 to +0.15 | Sharpe −0.67 to +0.16 |
| Null test (shuffled minutes), 2 seeds | | 0 passes, best Sharpe 0.27 |

The real market data performed about the same as shuffled noise. With costs
removed entirely the best selected variant made +0.08 R per trade, which
1.25 points of real-world costs reduce to +0.009. The strategy's public
claims (a 52% win rate, profit factor 1.66) depend on discretionary judgment
that can't be tested. The rules as described, applied mechanically, have
no edge over 14 years.

## B. Football betting (22 leagues, 2012/13 → 2025/26)

| Strategy | In-sample ROI (bets) | Holdout ROI (bets) | Holdout win rate | p (one test) | Verdict |
|---|---|---|---|---|---|
| Value vs Pinnacle, edge ≥ 10%, odds ≤ 5 *(selected)* | +26.7% (453) | +18.5% (96) | 35% | 0.14 | fail: too few bets |
| Value vs Pinnacle, edge ≥ 2%, odds ≤ 5 | +3.7% (21,808) | **+3.5% (4,240)** | 30% | 0.08 | not selected; not significant after deflation |
| Value vs Pinnacle, edge ≥ 5%, odds ≤ 5 | +9.0% (4,687) | +1.5% (834) | 29% | 0.40 | |
| Value vs Pinnacle, no odds cap (3 variants) | +2.5% to +11.8% | −5% to −19% | 9–22% | > 0.97 | uncapped long shots collapse in the holdout |
| Favourites at Pinnacle close, ≤ 1.3 *(selected)* | +0.4% (3,550) | +0.4% (1,459) | **83%** | 0.36 | fail: no real edge |
| Favourites ≤ 1.5 / ≤ 2.0 | +0.2% / −1.7% | −0.1% / −1.5% | 76% / 62% | | |

**The lead:** betting the best available price when it beats Pinnacle's
de-vigged line, odds capped at 5.0, was positive in both periods: about
+3.5% ROI over 26,000 bets. That is the classic "+EV betting" edge,
and it is real enough that sportsbooks limit accounts that exploit it. It
does **not** pass: the pre-registered selection rule picked the 10%-edge
variant (too few bets), and the 2% variant's p = 0.08 doesn't survive
deflation across 160 trials. It earns a **forward test** in Round 3, as
one pre-registered config with no further tuning.

Caveat: "best price" here is the maximum across ~40 bookmakers at a
snapshot. A real bettor needs accounts at the books that offered it, and
the price must still be there when the bet is placed.

## C. Polymarket "buy the near-certain side" (favourite–longshot)

| Strategy | In-sample ROI | Holdout ROI (bets) | Holdout win rate |
|---|---|---|---|
| Buy side ≥ 80¢, 24h before end | −2.5% | −2.2% (621) | 91% |
| Buy side ≥ 90¢, 24h before end | −1.0% | −2.5% (401) | 95% |
| Buy side ≥ 95¢, 24h before end | −0.5% | −1.5% (263) | **97%** |
| (same at 1h before end) | −0.2% to −1.5% | −3.0% to −3.9% | 89–95% |

**This is the clearest demonstration in the experiment that a high win rate
is not profit.** Winning 95–97% of bets still loses money, because each
win pays only about 3–5¢ and each loss costs the whole 95¢.

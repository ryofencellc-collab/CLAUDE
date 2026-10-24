# Round 2 pre-registration

Written 2026-10-24, after Round 1 failed (0/9) and **before any Round 2 data
was downloaded**. Same rules as [PROTOCOL.md](PROTOCOL.md) unless stated.

## Why a Round 2 is legitimate

Round 1's holdout (daily crypto/ETF data 2023+) has been looked at and is
burned: nothing from Round 1 is re-tested on it. Round 2 tests **different
hypotheses on different data** (intraday Nasdaq futures, football betting
odds, prediction markets), none of which has been examined yet.

The trial count is cumulative. Deflated Sharpe in Round 2 is deflated by
Round 1's 61 trials **plus** every Round 2 trial.

## The owner's definition of "edge"

The owner asked for a strategy that "prints money": a high win rate, or
profitable most days. Both are reported for every strategy (win rate, % of
green days, profit factor, average R). **They are not pass criteria on
their own**, because a high win rate is easy to fake: a tight target and a
wide stop wins 90% of the time and still loses money. What decides is
whether total profit after costs is real and not luck.

## Families

### A. Intraday NQ (Nasdaq-100), 1-minute bars

Data: HistData.com NSXUSD 1-minute bars (Nasdaq-100 quote feed; tracks NQ
futures to within the basis), 2012 onward, converted to New York time.
IS ≤ 2022-12-31, holdout 2023-01-01 onward. (Amended before any download:
Dukascopy, the first choice, blocks GitHub's servers with HTTP 503/429.)

Costs: **1.25 index points per round trip** (NQ futures: 1 tick spread
0.25 + commission ≈0.2 + 0.8 slippage on market/stop fills). Sensitivity
at 0 and 2.5 points is reported but does not change the verdict.
Fill rules: entry at the next bar's open after a signal. If stop and target
are both inside the same 1-minute bar, the **stop** is assumed hit first.

1. **jj_fair_value** (the TikTok strategy, "JJ Simon Fair Value Theory"),
   mechanised from public descriptions:
   - Fair value (FV) = window open price. Windows: `am` 09:30–11:00,
     `pm` 14:00–15:00, `asia` 20:00–21:30 (the comment "works with 8pm Asia
     open").
   - Displacement candle: 1-minute bar whose counter-wick is < 20% of its
     range, with range ≥ `disp` × mean range of the prior 20 bars.
   - Break of structure: that bar closes beyond the highest high (bull) /
     lowest low (bear) of the prior `L` bars.
   - Phase: first 15 minutes of a window = **continuation** (only trade
     away from FV); after = **mean reversion** (only trade toward FV).
     `phases` ∈ {both, continuation, reversion}.
   - Risk: `stops=regime` uses ATR(14, 1-min): ATR > 20 → 50/75 pt,
     7–20 → 25/37.5 pt, < 7 → 16.5/24.75 pt. `stops=fixed` uses 25/37.5.
     1.5R target always, no management, flat at window end.
   - One position at a time; max 3 trades per window.
   - Grid: windows {am, am+pm, asia} × stops {regime, fixed} × disp {1.0, 1.5}
     × L {5, 10} × phases {both, continuation, reversion} = **72 trials**.

2. **orb** (opening range breakout, the Zarattini–Aziz 2023 family):
   direction of the first `n`-minute range after 09:30; enter at its end,
   stop at the other side of the range, target `k`×R or exit at 16:00.
   Grid: n {5, 15, 30} × k {1.5, 3, 10, eod} = **12 trials**.

Pass criteria for A: Round 1 criteria applied to **daily P&L in R units**
(Sharpe ≥ 1.0 OOS, DSR ≥ 0.95 with cumulative trials, IS Sharpe > 0,
≥ 2 years and ≥ 100 trades OOS). Max-drawdown check is in R:
OOS max drawdown ≤ 20R (sized at 1% risk/trade this is ≈ 20%).

### B. Football betting

Data: football-data.co.uk, ~22 European leagues, seasons 2005/06 onward.
IS = seasons up to 2021/22, holdout = 2022/23 onward. Flat 1-unit stakes.

1. **value_vs_pinnacle**: Pinnacle's pre-match odds, de-vigged
   (proportional), are taken as fair probability. Bet an outcome when the
   best market price (`Max`/`BbMx` columns, collected at the **same time**
   as the Pinnacle pre-match price, so no look-ahead) exceeds fair odds by
   ≥ `edge`. Grid: edge {2%, 5%, 10%} × max odds {any, ≤ 5.0} = **6 trials**.
2. **favourite_bias**: bet every outcome with Pinnacle **closing** odds
   ≤ `cap` at the Pinnacle closing price. Grid cap {1.3, 1.5, 2.0} = **3 trials**.

Pass criteria for B: holdout ROI > 0 with bootstrap p < 0.05 after
deflating for cumulative trials (Bonferroni), IS ROI > 0, ≥ 1,000 holdout bets.
Known real-world caveat, stated now: soft bookmakers limit or close
accounts that win consistently. A pass here would show the edge exists in
the data, not that it can be scaled.

### C. Prediction markets (Kalshi / Polymarket)

Only if the data can be pulled. Hypothesis: the favourite–longshot bias.
Contracts priced ≥ `p` some fixed time before close settle YES more often
than `p` implies, after fees. Grid p {0.80, 0.90, 0.95} × timing
{1 day, 1 hour before close} = **6 trials**. Holdout: markets closing in
the last 12 months of available data. Pass: holdout ROI after fees > 0 with
bootstrap p < 0.05 (Bonferroni-deflated), ≥ 500 holdout bets.

## Gates after a pass

Same as PROTOCOL.md: paper trading (Phase 2) → $1,000 live → $10,000 live,
with the same hard stops. A Round 2 pass is a ticket to paper trading,
not proof.

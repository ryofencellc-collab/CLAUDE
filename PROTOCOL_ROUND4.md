# Round 4 pre-registration: "beat the retail trader"

Written 2026-10-24, before any Round 4 data was downloaded.

## The owner's hypothesis

Retail traders trade by hand, on emotion, using the same popular indicators
and setups. A machine that trades strictly on data can take the other side
of their predictable mistakes.

## What "emotionless" does and does not buy (stated before testing)

Rounds 1–2 already ran 14 strategy families with zero emotion: 0 passed.
Discipline only helps if the rule itself has an edge. So Round 4 does not
test "being a machine". It tests whether **retail behaviour is predictably
wrong**, using data that measures retail behaviour directly.

## Families

### A. Crowd fade (crypto): trade against retail positioning

Data: Binance USD-M futures `metrics` archive (5-minute), resampled hourly:
`count_long_short_ratio` (all accounts, which is mostly retail) and
`count_toptrader_long_short_ratio` (Binance's largest accounts). Prices:
hourly perp klines. Coins: BTC, ETH, SOL, XRP, DOGE. Costs: 0.05% per side
(taker) + 0.02% slippage per side, plus funding paid/received while held.
IS = start of data → 2023-12-31; holdout = 2024-01-01 on.

1. `retail_fade`: z = 30-day z-score of the all-accounts long/short ratio.
   z > k → short, z < −k → long, hold `h` hours. Grid k {1.5, 2.0} × h {4, 24}
   = 4 trials.
2. `follow_whales`: when top traders and retail disagree (their z-scores have
   opposite signs and differ by > 2), trade with the top traders, hold `h`.
   Grid h {4, 24} = 2 trials.

### B. Liquidity sweep fade (Nasdaq-100, 1-minute): trade against retail stops

Retail traders famously put stops just beyond the prior day's high/low
(and many now trade the "liquidity grab" idea from social media themselves).
Rule: during the window, if price trades above the prior regular-session
high and a 1-minute bar then **closes back below it**, go short. Stop 1 point
beyond the sweep extreme; mirror for lows. One trade per side per day. Target
`r`×R. Grid window {09:30–11:00, 09:30–16:00} × r {1.5, 3} = 4 trials.
Same data, costs (1.25 pt) and fill rules as Round 2.

### Not testable here: options premium selling

The best-known "beat retail" trade is selling the overpriced lottery-ticket
options retail buys. It does "print daily", until a crash. Free option-price
history isn't available here. Round 1's `vix_carry` (holding inverse VIX)
is the closest proxy already tested: holdout Sharpe 0.32 with a −43%
drawdown. That's the typical profile of daily-printing strategies.

## Pass criteria

Same as Round 2 family A, on daily P&L: holdout Sharpe ≥ 1.0, Deflated Sharpe
≥ 0.95 with cumulative trials (160 + 1 + 10 = **171**), IS Sharpe > 0,
≥ 100 holdout trades, holdout max drawdown ≤ 20R (B) or ≤ 25% (A).
Also reported for every config, as the owner asked: win rate and % green days.

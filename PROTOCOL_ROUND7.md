# Round 7 pre-registration: every remaining rock

Written 2026-10-25, before any Round 7 data was downloaded or analysed.
(The weather contract data reused in 7A was downloaded in Round 5, but its
bracket sums have never been computed or looked at.)

Cumulative trials before this round: 199. Round 7 adds 12 → **211**.

## 7A. Kalshi bracket arbitrage (2 trials)

Each Kalshi daily-high event is a set of mutually exclusive brackets, exactly
one of which pays $1. Using the 09:00-local quotes already collected
(Round 5 data, run 40116008981), and only for events where **every** bracket
has a quote:
- `buy_all`: if Σ yes_ask + fees < $1, buy one of each → guaranteed profit
  1 − Σ ask − fees.
- `sell_all`: if Σ yes_bid − fees > $1, buy every NO → guaranteed profit
  Σ bid − 1 − fees.
Fees: Kalshi taker formula on a 100-contract order per bracket. The data is
also checked for a sanity condition: exactly one bracket settled YES.
**Pass:** ≥ 30 opportunities and total profit > 0 (riskless, so no
significance test), reported with count, profit per opportunity, and $/year
at 100 contracts.

## 7B. Tennis value betting (4 trials), replicating the football lead

tennis-data.co.uk ATP + WTA, 2010 onward. Fair probability = Pinnacle
(`PSW/PSL`) de-vigged; bet a player when best price (`MaxW/MaxL`) ≥ fair ×
(1 + edge). Both players are evaluated symmetrically, so the winner/loser
column layout can't leak the result. Grid: edge {2%, 5%} × max odds {none,
3.0}. IS < 2022, holdout 2022 on, config chosen on IS ROI. **Pass:** holdout
ROI > 0, bootstrap p × 211 < 0.05, IS ROI > 0, ≥ 1,000 holdout bets.

## 7C. Cross-exchange funding arbitrage, Hyperliquid vs Binance (4 trials)

BTC, ETH, SOL, XRP, DOGE. Daily funding sums per venue. Signal: trailing
`w`-day mean of (Hyperliquid − Binance) funding. If |signal| > `thr`, short the
perp on the venue that pays more funding, long on the other, and earn the next day's
realised difference. Costs: 4 taker legs × 0.05% on each entry and on each
exit. Return is on capital = notional (1× each leg, collateral split).
Grid: w {3, 7} × thr {0.0003, 0.001} per day. IS until 2024-12-31,
holdout 2025 on. **Pass:** Round 1 rules (holdout Sharpe ≥ 1, DSR ≥ 0.95
with 211 trials, IS Sharpe > 0, max drawdown ≤ 25%, ≥ 30 position changes).

## 7D. Crypto pairs trading (2 trials)

All 10 pairs of BTC, ETH, SOL, XRP, DOGE (daily, Binance spot). Spread =
log(A) − β·log(B), with β from a rolling `n`-day OLS; enter when the spread's
n-day z-score crosses ±2, exit at 0; market-neutral, equal capital per
pair, 0.1% per side per leg. Grid n {30, 60}. IS ≤ 2022, holdout 2023 on.
**Pass:** Round 1 rules.

## 7E. Matched betting (not a backtest)

Sportsbook sign-up bonuses hedged on an exchange or a second book. Its
expected value is arithmetic, not statistics: it is reported as a worked
calculation from public offer terms, clearly labelled as not tested here.

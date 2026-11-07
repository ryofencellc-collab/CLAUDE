# Round 25 pre-registration: confidence-scaled sizing for the 15-minute crypto trade

Written 2026-11-06, before any Round 25 code ran on real data.

## Question

The live rule bids a fixed share of the account whenever z ≥ 6. Can chart features predict *which* decided
markets might still reverse, so we bet more when it is safest and less (or nothing) otherwise? That would
mean faster growth with less risk.

## 1. Reversal model (Binance only, no Kalshi data)

**Samples.** Every minute inside every 15-minute window, 2024-01-01 to 2026-10-27, for ETH, SOL, XRP,
DOGE and BTC. Features are seen through the last completed minute only. The label is "flip": the side that
was winning at that minute lost at the close.

**Features:**

- |z| and minutes left;
- distance from the strike in basis points;
- momentum over 1, 3 and 5 minutes, signed (positive = moving away from the strike);
- volatility ratio (5-minute vs 60-minute);
- largest 1-minute jump in the last 10 minutes, relative to normal volatility;
- volatility level;
- hour of day, day of week, and coin.

**Models.** All three are fit on 2024-01-01 to 2026-03-31, using rows with |z| ≥ 2:

1. a |z| × minutes-left table with a prior;
2. logistic regression;
3. gradient-boosted trees, forced monotone: more |z| never raises the risk, and more time left never
   lowers it.

## 2. Policies (91)

Each policy is applied to Round 21's real Kalshi long-shot fills (ETH, SOL, XRP and DOGE 15-minute markets;
BTC timed out in Round 21). For each fill it decides whether we are in, and the most our position in that
market may be, as a share of the account. Positions may grow with later fills as confidence grows, but
never shrink. One market at a time. The account starts at $1,000, profits are compounded, we capture 25% of
each fill, and the maker fee is charged on each fill.

| Group | Policies | Count |
|---|---|---:|
| Fixed rules | z ≥ {4, 5, 6, 8, 10} × stake {0.5, 0.95} | 10 |
| Kelly sizing from each model | model {table, logit, GBM} × Kelly multiplier {0.25, 0.5, 1} × cap {0.5, 0.75, 0.95} × entry only when predicted flip risk < {0.1%, 0.3%, 1%} | 81 |

## 3. Selection on dev (2026-04-01 to 2026-09-29)

1. **Scoring model:** the one with the lowest log-loss on the dev Binance samples.
2. **Score:** each policy's expected log-growth under the scoring model's predicted risks. This is used
   instead of realized profit, so that rare flips not happening in the sample cannot reward reckless sizing.
3. **Choice:** the highest-scoring policy among those with a dev max drawdown ≤ 30%.

## 4. Verdict on the holdout (2026-10-01 to 2026-10-27)

**PASS** only if all hold:

1. The chosen policy's final balance is ≥ the current live rule's (z ≥ 6, stake 0.5) on the same fills.
2. The chosen policy's max drawdown is ≤ 30%.
3. The scoring model is calibrated on the holdout's Binance samples: in every risk bin with ≥ 20 flips,
   actual is within 0.5× to 2× of predicted.
4. In the chosen policy's entry region, actual flips are ≤ max(2 × predicted, predicted + 3).

All 91 policies are reported, with dev and holdout results side by side.

## Prediction written now

The z × minutes-left table captures most of the gain. Momentum against our side will be the most useful
extra feature. Kelly sizing will bet large near the close and small with more than about 5 minutes left. I
expect a PASS with faster growth than the fixed rule and similar drawdown. The model will likely be
under-confident at very high |z|, because flips there are almost nonexistent.

## Result and deployment (2026-11-07)

**PASS.** The rule chosen on dev was "z-bin table, Kelly ×1.0, cap 0.95, enter only when the predicted
reversal risk is < 0.3%".

| October holdout, $1,000 start | Chosen rule | Live rule (z ≥ 6, stake 0.5) |
|---|---:|---:|
| Final balance | $30,155 | $4,111 |
| Markets traded / lost | 993 / 0 | 424 / 0 |
| Max drawdown | 0% | 0% |

On dev the chosen rule had 3 losing markets and a −14% max drawdown. The scoring model was well calibrated
on the holdout.

These dollar figures assume we capture 25% of every long-shot fill at any size, so they overstate
capacity. The comparison between the two rules is what matters.

**Deployment to the live trader.** `edge/live21.py` now uses the z-bin table (`control/r25_zbins.json`, fit
on 2024-01 to 2026-03) for three things:

1. **Entry:** risk < 0.3%.
2. **Cancel:** when the risk rises to ≥ 0.3%.
3. **Size:** min(Claude's stake cap, Kelly(risk)).

The stake cap stays under `control/RULES.md` (0.5 for the first 14 live days). If the table file is
missing, the trader falls back to Round 21's z ≥ 6.

**Live differences from the backtest:** one order per market, sized at placement (the backtest allowed
adding to a position), and one market at a time.

**Forward check:** the trader's dry run until go-live is the forward test, compared side by side with the
Round 21 paper bot on the same markets.

### Amendment (Nov 7, deployment)
The live trader reads the table with one change: risk is made non-increasing in |z| within each tau column. This only lowers risk in cells that sit above a safer, smaller-|z| cell (sparse cells dominated by the prior). The fitted table file is unchanged.

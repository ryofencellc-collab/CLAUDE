# Round 12 pre-registration: stock core plus a crypto trend sleeve

Written 2026-10-27, before any Round 12 code ran on real data.

## Why this round, and its bias

Rounds 9–11 found two return streams that are decent on their own but fall
short of the bar:

- US stocks: SPY Sharpe about 0.9 since 2012.
- A crypto trend sleeve: BTC+ETH held only above their trend, with a
  volatility limit. Round 10 out-of-sample Sharpe was 0.85.

They are only loosely correlated, so a mix should have a higher Sharpe than
either one alone. **Honest bias note:** both streams were picked after seeing
earlier results, so this idea is informed by data already seen. It counts as a
new trial (268), and the deflated Sharpe test applies in full.

## Data

Daily Yahoo adjusted closes for SPY, BTC-USD (from 2014-09) and ETH-USD (from
2017-11), aligned on US trading days. Costs: SPY 0.02% per side, crypto 0.10%.
Weights are set at the close of day t and earn day t+1.

## Strategy family (fixed now, `edge/round12.py`)

The book is (1 − α) × the stock core plus α × the crypto sleeve:

- **Stock core** (one of three modes):
  - buy and hold SPY;
  - volatility-managed: weight min(1, 15% / SPY's 20-day volatility);
  - trend: hold SPY only while it is above its SMA 200.
- **Crypto sleeve:**
  - hold each of BTC and ETH (once its data exists) while it is above its SMA *n*;
  - equal weight between the coins held;
  - scale the sleeve to 40% target volatility using the held basket's 20-day volatility, capped at 1.

The grid is 3 × 2 × 3 = 18 configs:

| Parameter | Values |
|---|---|
| Stock core | buy & hold; volatility-managed; trend (SMA 200) |
| Crypto trend SMA *n* | 50, 100 |
| Crypto share α | 10%, 20%, 30% |

Gross exposure never exceeds 1 (no leverage).

## Test: walk-forward selection

Every 6 months from 2016-01-01, the config with the best net Sharpe on all
data from 2014-10-01 up to that date is chosen. It trades the next 6 months.
Out-of-sample runs from 2016-01-01 to latest, 252 days a year.

## Pass rule (OOS series, all must hold)

1. Annualised Sharpe after costs ≥ 1.0
2. Deflated Sharpe ≥ 0.95, deflated by 268 trials
3. CAGR beats T-bills (4%/yr)
4. Max drawdown ≤ 25%
5. At least 30 position changes
6. Sharpe higher than buy-and-hold SPY over the same OOS days

## Prediction written now

Coin flip. Sharpe 1.0+ and beating SPY look reachable. The deflated Sharpe
(~0.9 needed over ~10.8 years at 268 trials) and the 25% drawdown limit
(2020 and 2022) are the risks.

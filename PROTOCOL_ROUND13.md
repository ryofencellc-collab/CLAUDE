# Round 13 pre-registration: three-stream portfolio (stock core, multi-asset trend, crypto trend)

Written 2026-10-27, before any Round 13 code ran on real data.

## Why this round, and its bias

Round 12 (stock core + crypto trend sleeve) passed 5 of 6 rules out of sample
2016–2026: Sharpe 1.28 vs SPY 0.88, worst drop −24.9%. It missed only the
deflated Sharpe (0.905 vs 0.95). Two principled ways to firm up the evidence:

- **A third, unrelated stream.** Round 11's multi-asset trend was very stable
  (the same config chosen in 26 of 30 refits) and has low correlation to
  stocks and crypto.
- **A longer out-of-sample period.** Starting in 2012 gives about 15 years,
  which lowers the luck bar fairly.

**Bias note:** all three streams were picked after seeing earlier results.
This counts as trial 269, and the deflated test applies in full. The crypto
share is **not** raised above Round 12's 30% cap, even though Round 12 always
chose 30%. Raising it now would be fitting to the result.

## Data

Daily Yahoo adjusted closes: SPY, EFA, EEM, TLT, IEF, GLD, DBC, VNQ, BTC-USD
(from 2014-09) and ETH-USD (from 2017-11), on US trading days. Costs are 0.02%
per side for ETFs and 0.10% for crypto. Weights are set at the close of day t
and earn day t+1.

## Strategy family (fixed now, `edge/round13.py`)

The book = (1 − α − β) × stock core + β × trend sleeve + α × crypto sleeve.
Weights are summed per asset.

- **Stock core:** as in Round 12 (buy & hold SPY, or volatility-managed SPY).
- **Trend sleeve:** Round 11's rule fixed at its most-chosen setting: SMA 100
  trend, inverse-volatility weights, an 8% vol target, no Bitcoin.
- **Crypto sleeve:** Round 12's rule (BTC+ETH above SMA *n*, 40% target vol),
  with *n* ∈ {50, 100}. It is zero before crypto data exists.

The grid is 2 × 2 × 3 × 2 = 24 configs:

| Parameter | Values |
|---|---|
| Stock core | buy & hold; volatility-managed |
| Crypto trend SMA *n* | 50, 100 |
| Crypto share α | 10%, 20%, 30% |
| Trend sleeve share β | 20%, 40% |

Gross exposure never exceeds 1.

## Test: walk-forward selection

Every 6 months from 2012-01-01, the config with the best net Sharpe on all
data from 2007-07-01 up to that date is chosen. It trades the next 6 months.
Out-of-sample runs from 2012-01-01 to latest, 252 days a year.

## Pass rule (OOS series, all must hold)

1. Annualised Sharpe after costs ≥ 1.0
2. Deflated Sharpe ≥ 0.95, deflated by 269 trials
3. CAGR beats T-bills (4%/yr)
4. Max drawdown ≤ 25%
5. At least 30 position changes
6. Sharpe higher than buy-and-hold SPY over the same OOS days

## Prediction written now

Lean PASS on drawdown and beating SPY. The deflated Sharpe is the risk:
2012–2014 has no crypto and SPY was very strong then, so the early years may
dilute the Sharpe.

## Forward test (added 2026-10-27 after the backtest PASS, before the bot's first run)

The backtest passed. The next step is a live paper test on data nobody has
seen, using the unchanged procedure (`edge/paper13.py`):

- $10,000 paper, starting with target weights set at the 2026-10-27 close.
- Run each US trading day after the crypto daily bar closes (00:23 UTC). The
  config is re-chosen on 1 January and 1 July exactly as in the backtest.
- `paper/r13_ledger.csv` is append-only, so git timestamps every position
  before the returns it earns.
- Review at 6 months (2027-04-27), then at 12 months. To advance to the
  owner's $1,000 live stage, at 6 months:
  1. return at least T-bills (≥ +2% over the 6 months);
  2. drawdown no worse than −15%;
  3. the realised daily returns match the backtest's own replay of the same
     days within 0.1% a day. This checks that the bot does what the
     backtest assumed.
- These thresholds are fixed now. A 6-month result is too short to prove an
  edge on its own; its job is to catch errors and regime breaks before any
  real money is used.

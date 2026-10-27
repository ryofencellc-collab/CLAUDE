# Round 9 pre-registration: let the data pick the trade gates

Written 2026-10-27, before any Round 9 code ran on real data.

## The owner's idea

A trade happens only when several conditions ("gates") all agree. The owner
asked that the data, not Claude, decide **which** gates and **how many**.

## Why this needs care

Letting the data choose gates is exactly how backtests get overfit: keep the
gates that would have dodged past losers and the past looks perfect. So the
thing under test is not a set of gates but the **choosing procedure**. It is
judged only on periods it never saw when it chose.

## Market and data

Crypto, daily, Binance public archive (`edge/data.py`, 30 coins including
dead ones such as LUNA and FTT, so there is no survivorship bias). Perp funding
starts 2019-09, so the gate data starts 2019-10-01. A coin is tradable on a day
only if its 30-day median daily spot volume is at least $5M. Costs: 0.10% per side.
Weights are set at the close of day t and earn day t+1 (`edge/backtest.py`).

## Gate library (fixed now, in `edge/gates.py`)

Each gate is a yes/no per coin per day, built only from data up to that close.
They come from different kinds of information, and each is offered in both
directions (for example "above its 100-day average" and "below it"):

| Family | Gates |
|---|---|
| Trend | close above SMA 50 / 100 / 200; 20-day and 60-day return positive |
| Market regime | BTC above its SMA 100; SPY above its SMA 200 |
| Volatility | 20-day vol below its 1-year median; 20-day vol below 60-day vol |
| Crowd positioning | 7-day mean funding below 0; below its own 90-day median |
| Short-term move | 3-day return below 0 |
| Activity | 7-day volume above 30-day volume |
| Basis | perp trading below spot |
| Calendar | weekday (Mon–Fri close) |

That is 15 base gates and 30 with both directions.

## The procedure (what is being tested)

Given training data up to a date:

1. **Strategy for a gate set:** hold an equal weight in every tradable coin
   whose gates are all "yes"; cash otherwise. No gates means hold every
   tradable coin.
2. **Greedy path:** start with no gates; at each step add the one gate that
   most raises the net Sharpe on the training data; repeat up to 6 gates. A
   gate set must keep at least 60 position changes in training.
3. **How many gates (data decides):** build the greedy path on the first 75%
   of the training data, then score paths of length 0 to 6 on the last 25%.
   The length with the best Sharpe there is used. The path is then rebuilt on
   all the training data and cut at that length.

## The test: walk-forward

Refit every 6 months (1 January and 1 July) on an expanding window starting
2019-10-01. The first refit trains through 2020-12-31 and trades
January–June 2021. Each 6-month block is traded with gates chosen without it.
The out-of-sample (OOS) series runs from 2021-01-01 to latest. Every refit's
chosen gates are reported, to show whether the choice is stable.

## Pass rule (OOS series, all must hold)

1. Annualised Sharpe after costs ≥ 1.0
2. Deflated Sharpe ≥ 0.95, deflated by 264 trials (263 before + this procedure)
3. CAGR beats T-bills (4%/yr)
4. Max drawdown ≤ 25%
5. At least 30 position changes
6. Sharpe higher than buy-and-hold BTC over the same OOS days (it must beat
   simply holding Bitcoin)

## Self-checks (must hold or no result counts)

- On random-walk prices, the procedure must fail.
- On synthetic data with a planted gate effect, it must pick that gate and pass.

## Honesty notes

- Round 1 already looked at 2023+ crypto prices with other strategies, so no
  crypto data is untouched. The walk-forward does not need untouched data: it
  needs the procedure to stay fixed. Any change to the gate library or the
  procedure after seeing OOS results is a new trial, is logged, and is
  disclosed.
- A pass here earns a forward paper test on live data, with the gates refit on
  all data up to the start. That is the truly unseen test.

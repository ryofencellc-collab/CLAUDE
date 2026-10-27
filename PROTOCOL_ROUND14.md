# Round 14 pre-registration: SPY options, honest version of the TikTok trades

Written 2026-10-27, before any Round 14 code ran on real data.

## Question

Is there an SPY/SPX options strategy that makes money most days and passes
the same rules as every other round? Separately, what does the TikTok
approach, buying short-dated out-of-the-money calls, really look like when
every trade is counted, not just the screenshots?

## Part A: Cboe's official strategy indexes (real option prices)

Cboe publishes daily track records of rules-based S&P 500 option strategies,
priced from actual market quotes:

- **PUT:** sell monthly at-the-money puts, cash-secured.
- **WPUT:** the same, weekly.
- **BXM:** buy the index and sell monthly at-the-money calls (covered call).
- **CNDR:** sell a monthly iron condor.
- **BFLY:** sell a monthly iron butterfly.
- **PPUT:** buy the index plus monthly 5%-out-of-the-money puts (protection).
- **CLL:** a collar.

Each one Yahoo or Cboe serves is tested as published (no parameters, so no
fitting). Each counts as one trial. Period: 2012-01-01 to latest, the same
window as Round 13, so the results compare directly.

## Part B: modeled short-dated trades (TikTok style)

There's no free history of individual SPY option prices, so these are priced
with Black-Scholes. The volatility input is the market's own implied
volatility for that horizon: VIX9D (9-day, from 2011) for weekly options and
VIX1D (1-day, from 2023-04) for 0DTE. Costs are half the bid-ask spread,
taken as **5% of the option price** each way for buys and sells (a realistic
retail fill for short-dated options).

**Bias of the model, stated now:** using one volatility number ignores the
"skew". Real out-of-the-money puts cost more than the model says, and real
out-of-the-money calls cost less. So the model makes **put selling look
slightly worse** and **call buying look slightly better** than reality.

| ID | Trade | Data from |
|---|---|---|
| B1 | Every Friday close, buy a 1-week call 2% above the price; hold to expiry | 2011 |
| B2 | Every day at the open, buy a 0DTE call 0.5% above the open; settles at the close | 2023-04 |
| B3 | Every day at the open, sell a 0DTE iron condor: short strikes ±1%, long wings ±2% | 2023-04 |
| B4 | Every Friday close, sell a 1-week put 2% below the price, cash-secured | 2011 |

The sizing is the same for every trade:

- **Buyers (B1, B2):** spend a fixed 2% of the account per trade.
- **Sellers (B3, B4):** risk the full account as collateral, one contract per
  $100 of account per $1 of maximum loss.

We report:

- win rate;
- best single-trade multiple, the "screenshot";
- total return, Sharpe and worst drop.

## Pass rule (same as Rounds 9–13, each strategy on its own)

1. Annualised Sharpe ≥ 1.0
2. Deflated Sharpe ≥ 0.95, deflated by 269 trials plus this round's strategies
3. CAGR beats T-bills (4%/yr)
4. Max drawdown ≤ 25%
5. At least 30 trades
6. Sharpe higher than buy-and-hold SPY over the same days

## Prediction written now

- **B1 and B2 (buying calls):** high-multiple winners exist, but the win rate
  is well under 50% and the account loses money over time.
- **B4, PUT and WPUT (selling puts):** win rates of 70–85% and modest returns,
  with drawdowns in 2020 and 2022 that likely break the 25% limit.
- **BXM, CNDR and BFLY:** below SPY on Sharpe.
- **Overall:** FAIL.

# Round 7 results: every remaining rock

Rules: [PROTOCOL_ROUND7.md](../PROTOCOL_ROUND7.md). Run
[40160845343](https://github.com/ryofencellc-collab/CLAUDE/actions/runs/40160845343)
(7A, 7C, 7D; re-run 40161370400 to diagnose 7B). Cumulative trials: 211.

**Verdict: 0 of 3 testable families passed; 1 blocked by data access.**

## 7A. Kalshi bracket arbitrage: there is none

1,081 weather events had every bracket quoted at 09:00 and settled cleanly.

| | |
|---|---|
| Sum of asks (cost to buy every bracket) | median **$1.07**, cheapest ever $0.96 before fees |
| Sum of bids (value of selling every bracket) | median **$0.97**, highest ever $1.05 |
| Buy-all opportunities after fees | **0** of 1,081 |
| Sell-all opportunities after fees | **1** of 1,081, worth $0.19 on 100 sets |

Kalshi's market makers keep the bracket set priced about 3–7% above $1. The
riskless arbitrage doesn't exist at these snapshots.

## 7C. Cross-exchange funding arbitrage: real in 2023–24, gone since

| Config | 2023–24 Sharpe | 2023–24 return/yr | 2025–26 Sharpe | 2025–26 return/yr |
|---|---:|---:|---:|---:|
| 3-day signal, >0.03%/day | 10.2 | +9.8% | −3.6 | −1.2% |
| 3-day signal, >0.1%/day | 7.3 | +4.5% | +0.3 | 0.0% (6 trades) |
| **7-day signal, >0.03%/day** *(selected)* | **12.1** | **+11.2%** | **−1.3** | **−0.3%** |
| 7-day signal, >0.1%/day | 7.9 | +4.8% | +0.8 | +0.1% (2 trades) |

This is the clearest "it used to print money" result in the experiment. In
Hyperliquid's first two years its funding diverged from Binance's in a
persistent, predictable way: **~11% a year with a 0.3% max drawdown, a
Sharpe ratio of 12.** From 2025 the gap stopped persisting from one week to
the next. The average daily gap is still large (10–18% a year in absolute
size), but you can no longer tell in advance which way it will go. Same story
as Round 1's funding carry: the edge got arbitraged away once the venue
matured.

## 7D. Crypto pairs trading: no edge

All 10 pairs of BTC/ETH/SOL/XRP/DOGE, z-score ±2 entries. In-sample Sharpe
0.16 / 0.04, holdout −0.13 / −0.08, about −2% a year with −23% drawdowns.

## 7B. Tennis value betting: blocked, can be unblocked by the owner

tennis-data.co.uk returns HTTP 403 to cloud/datacenter servers, so the test
couldn't run here. The files are free in a normal browser
(`tennis-data.co.uk/<year>/<year>.xlsx` and `<year>w/<year>.xlsx` for WTA).
Uploading them to `data/tennis/` would let this pre-registered test run
unchanged.

## 7E. Matched betting

See [ROUND7_matched_betting.md](ROUND7_matched_betting.md): real, one-time,
capped at roughly a few hundred to ~$1,500 per person.

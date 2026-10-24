# Phase 1 analysis

**Verdict: 0 of 9 strategy families passed. Per PROTOCOL.md, round 1 ends here.**
The null test was clean (0 passes on shuffled data across 3 seeds) and the
power test passed (a planted edge is detected), so this is a real negative
result, not a broken framework.

## Near misses (and why they still don't count)

| Strategy | OOS Sharpe | OOS max DD | Missed on |
|---|---:|---:|---|
| BTC above 50-day average | 1.46 | -26.5% | DSR 0.69, drawdown 1.5 pts over limit |
| SPY RSI(2) dip-buying | 1.29 | -7.5% | DSR 0.58 |
| SPY/TLT/GLD rotation | 1.37 | -19.4% | DSR 0.62, only 6 trades |

None of these is a hidden edge. All three are well-known public strategies.
The Deflated Sharpe Ratio of about 0.6 means that, given 61 configurations
tried, there is roughly a 40% chance a result this good is luck. Also,
holding BTC or SPY outright did about as well over the same holdout
(Sharpe 1.16 and 1.38), so a strong bull market explains most of these
numbers.

## Funding carry: the textbook "free money" trade, and why it died

Diagnostic (`diagnose_carry.py`), P&L as a fraction of capital per year:

| Year | Funding earned | Basis P&L | Trading costs | Net |
|---|---:|---:|---:|---:|
| 2020 | +14.2% | +0.1% | -4.0% | **+10.3%** |
| 2021 | +25.0% | -0.0% | -5.5% | **+19.6%** |
| 2022 | +2.7% | +0.1% | -5.2% | -2.4% |
| 2023 | +5.0% | -0.1% | -4.2% | +0.7% |
| 2024 | +7.3% | -0.7% | -4.5% | +2.2% |
| 2025 | +2.7% | -5.0% | -4.2% | -6.4% |
| 2026 | +1.2% | -0.0% | -3.9% | -2.7% |

Raw BTC funding went from ~31%/yr (2021) to ~5% (2025) to ~2% (2026). The
trade got crowded: delta-neutral products such as Ethena's USDe now
arbitrage it at scale. Even with zero trading costs, holdout-period funding
income (~4%/yr on capital) is no better than T-bills. This is what a real
edge looks like after "everyone sees it."

## What this says about the original question

Simple systematic trading on free public data, with honest costs and honest
statistics, did not produce an edge. That is the expected result: such
data is the most heavily mined in the world. The holdout (2023 onward) has
now been looked at, so any new or tweaked strategy **cannot** be validated
on it. Re-testing on it would be the same overfitting this protocol exists
to prevent. Any round 2 has to be validated on data that doesn't exist
yet (forward paper trading) or on genuinely different data.

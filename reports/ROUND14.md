# Round 14: SPY options, honestly counted

Rules: [PROTOCOL_ROUND14.md](../PROTOCOL_ROUND14.md). Deflated over 280 trials. Part B is Black-Scholes priced from VIX9D / VIX1D with a 5% half-spread; it ignores skew, which flatters call buying and penalises put selling.

| Strategy | From | Win rate | Sharpe | SPY Sharpe | Yearly | Worst drop | $1,000 → | Deflated Sharpe | Best trade | 10x+ trades | Pass |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| Cboe PUT | 2012-01-03 | 65% | 0.75 | 0.93 | +8.4% | -29% | $3,283 | 0.511 |  |  | **FAIL** |
| Cboe WPUT | 2012-01-03 | 65% | 0.47 | 0.93 | +4.6% | -26% | $1,959 | 0.147 |  |  | **FAIL** |
| Cboe BXM | 2012-01-03 | 61% | 0.68 | 0.93 | +7.7% | -30% | $2,983 | 0.401 |  |  | **FAIL** |
| Cboe CNDR | 2012-01-03 | 62% | 0.14 | 0.93 | +0.7% | -19% | $1,112 | 0.010 |  |  | **FAIL** |
| Cboe BFLY | 2012-01-03 | 54% | -0.21 | 0.92 | -3.0% | -50% | $641 | 0.000 |  |  | **FAIL** |
| Cboe PPUT | 2012-01-03 | 53% | 0.94 | 0.93 | +11.4% | -22% | $4,920 | 0.774 |  |  | **FAIL** |
| Cboe CLL | 2012-01-03 | 52% | 0.92 | 0.92 | +10.2% | -17% | $4,222 | 0.738 |  |  | **FAIL** |
| B1 buy weekly 2% OTM calls | 2012-01-06 | 12% | -3.53 | 0.93 | -47.3% | -100% | $0 | 0.000 | 11x | 1 | **FAIL** |
| B2 buy 0DTE 0.5% OTM calls | 2023-04-24 | 16% | -3.01 | 1.36 | -86.6% | -100% | $1 | 0.000 | 25x | 6 | **FAIL** |
| B3 sell 0DTE iron condor | 2023-04-24 | 91% | 0.78 | 1.36 | -100.0% | -100% | $0 | 0.031 |  |  | **FAIL** |
| B4 sell weekly 2% OTM puts | 2012-01-06 | 91% | 0.81 | 0.93 | +4.9% | -23% | $2,024 | 0.569 |  |  | **FAIL** |

Failed checks per strategy:

- Cboe PUT: sharpe>=1, dsr>=0.95, max_dd<=25%, beats_spy_sharpe
- Cboe WPUT: sharpe>=1, dsr>=0.95, max_dd<=25%, beats_spy_sharpe
- Cboe BXM: sharpe>=1, dsr>=0.95, max_dd<=25%, beats_spy_sharpe
- Cboe CNDR: sharpe>=1, dsr>=0.95, beats_tbills, beats_spy_sharpe
- Cboe BFLY: sharpe>=1, dsr>=0.95, beats_tbills, max_dd<=25%, beats_spy_sharpe
- Cboe PPUT: sharpe>=1, dsr>=0.95
- Cboe CLL: sharpe>=1, dsr>=0.95, beats_spy_sharpe
- B1 buy weekly 2% OTM calls: sharpe>=1, dsr>=0.95, beats_tbills, max_dd<=25%, beats_spy_sharpe
- B2 buy 0DTE 0.5% OTM calls: sharpe>=1, dsr>=0.95, beats_tbills, max_dd<=25%, beats_spy_sharpe
- B3 sell 0DTE iron condor: sharpe>=1, dsr>=0.95, beats_tbills, max_dd<=25%, beats_spy_sharpe
- B4 sell weekly 2% OTM puts: sharpe>=1, dsr>=0.95, beats_spy_sharpe

## The screenshots: B1's five best weeks (each would make a viral post)

| Bought | Expired | Multiple |
|---|---|---:|
| 2026-07-31 | 2026-08-07 | 10.6x |
| 2026-04-10 | 2026-04-17 | 9.4x |
| 2023-10-27 | 2023-11-03 | 7.7x |
| 2017-12-29 | 2018-01-05 | 7.4x |
| 2016-12-02 | 2016-12-09 | 7.2x |

Weeks that expired worthless: 86% of 773.

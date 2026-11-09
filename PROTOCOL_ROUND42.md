# Round 42 pre-registration: a trend-following portfolio outside Kalshi (stocks, bonds, gold, commodities, crypto)

Written 2026-11-09, before this data is fetched. US-accessible instruments only, long-only (no shorting, no perps).

**Why.** Trend following (time-series momentum) is the best-documented edge a small account can use: it has worked
across asset classes for a century (Moskowitz–Ooi–Pedersen 2012; Hurst–Ooi–Pedersen 2017). Our near-misses are trend
rules (crypto 55-day breakout, SPY trend put spread). Each alone is too weak; a diversified portfolio may not be.

**Instruments.** ETFs (Yahoo, dividends included): SPY, QQQ, IWM, EFA, EEM, TLT, IEF, GLD, SLV, DBC, USO, UUP, VNQ.
Crypto (Binance daily as the price source, traded on a US exchange): BTC, ETH, SOL.
**Costs.** ETFs 0.05% per side; crypto 0.40% per side (Kraken Pro taker); leverage pays 8%/yr on the borrowed part.
Cash earns nothing (conservative).

**Rules (fixed; signals at the close, traded at the next close).**
- E1: 12-month momentum. Monthly, hold each ETF whose 252-day return > 0, weighted by inverse 63-day volatility.
- E2: 10-month average. Monthly, hold each ETF whose close > its 210-day average, equal weight.
- C1: Donchian 55/20. Daily, buy a coin when close > prior 55-day high, sell when close < prior 20-day low; 1/3 each.
- C2: 100-day average. Daily, hold a coin while close > its 100-day average; 1/3 each.
- Benchmarks: SPY buy-and-hold, BTC buy-and-hold, 60/40 SPY/IEF.

**Periods.** Dev 2018-07 → 2022-12, holdout 2023-01 → 2026-10 (SOL from 2020-08). ETF rules are also shown on
2008 → 2026 for context.
**Portfolio.** Pick the dev-best ETF rule and the dev-best crypto rule (by dev Sharpe). Fix capital weights on dev so
each sleeve has equal volatility. Rebalance monthly. Score at 1×, 1.5× and 2× leverage.
**Pass (holdout, 1×):** Sharpe ≥ 1.0, CAGR ≥ 15%, worst drop no worse than −25%, dev CAGR > 0, and better holdout
Sharpe than both buy-and-hold benchmarks. A pass goes to forward paper trading; it is not funded on this test alone.
Reported for all: CAGR, Sharpe, worst drop, $/day on $1k, $10k and $25k.

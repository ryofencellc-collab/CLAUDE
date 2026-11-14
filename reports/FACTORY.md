# Strategy factory leaderboard

Rules: [PROTOCOL_FACTORY.md](../PROTOCOL_FACTORY.md). Trials so far: **17**. Passing: **0**. Holdout = 2022 → today. ROI as CAGR; bench = SPY (ETFs), equal-weight universe (stocks) or BTC (crypto).

| name                                                  | market   |   batch | dev_cagr   |   dev_sharpe | hold_cagr   |   hold_sharpe | hold_dd   | bench_cagr   |   bench_sharpe |   dsr | PASS   |
|:------------------------------------------------------|:---------|--------:|:-----------|-------------:|:------------|--------------:|:----------|:-------------|---------------:|------:|:-------|
| Momentum + low vol (rank sum, top 10%)                | stocks   |       1 | 11.2%      |         0.7  | 8.2%        |          0.64 | -15.7%    | 7.0%         |           0.44 |  0.94 |        |
| Sector rotation (top 3 SPDR sectors by 3m return)     | etfs     |       1 | 10.3%      |         0.62 | 9.4%        |          0.63 | -18.7%    | 11.4%        |           0.71 |  0.92 |        |
| Volatility-managed SPY (15% vol target, max 1.5x)     | etfs     |       1 | 11.5%      |         0.78 | 8.5%        |          0.59 | -19.4%    | 11.4%        |           0.71 |  0.95 |        |
| Low volatility (lowest 10% 60d vol)                   | stocks   |       1 | 12.6%      |         0.85 | 6.3%        |          0.57 | -15.8%    | 7.0%         |           0.44 |  0.96 |        |
| XS momentum 12-1 (top 10%)                            | stocks   |       1 | 17.5%      |         0.72 | 13.0%       |          0.55 | -32.3%    | 7.0%         |           0.44 |  0.93 |        |
| Dual momentum GEM (SPY/EFA by 12m, else AGG)          | etfs     |       1 | 6.6%       |         0.47 | 6.4%        |          0.48 | -23.0%    | 11.4%        |           0.71 |  0.81 |        |
| 52-week-high proximity (top 10%)                      | stocks   |       1 | 10.5%      |         0.65 | 6.2%        |          0.45 | -21.2%    | 7.0%         |           0.44 |  0.88 |        |
| Momentum 12-1, top 20 names only                      | stocks   |       1 | 15.9%      |         0.58 | 8.9%        |          0.42 | -43.8%    | 7.0%         |           0.44 |  0.83 |        |
| SPY above 200-day average, else IEF                   | etfs     |       1 | 10.5%      |         0.86 | 4.5%        |          0.41 | -31.9%    | 11.4%        |           0.71 |  0.94 |        |
| Turn-of-month SPY (last 4 + first 3 days)             | etfs     |       1 | 5.0%       |         0.55 | 3.1%        |          0.37 | -17.0%    | 11.4%        |           0.71 |  0.81 |        |
| XS momentum 6-1 (top 10%)                             | stocks   |       1 | 19.7%      |         0.8  | 6.6%        |          0.36 | -33.9%    | 7.0%         |           0.44 |  0.91 |        |
| 2x SPY above 200-day average, else cash               | etfs     |       1 | 13.0%      |         0.63 | 5.6%        |          0.35 | -45.4%    | 11.4%        |           0.71 |  0.84 |        |
| Anti-lottery (lowest monthly max daily return, 10%)   | stocks   |       1 | 10.4%      |         0.69 | 3.3%        |          0.31 | -16.0%    | 7.0%         |           0.44 |  0.87 |        |
| Sell in May: SPY Nov-Apr, IEF May-Oct                 | etfs     |       1 | 7.6%       |         0.56 | 2.2%        |          0.22 | -19.9%    | 11.4%        |           0.71 |  0.76 |        |
| Crypto: BTC+ETH 50/200 golden cross, else cash        | crypto   |       1 | 64.6%      |         0.94 | 0.5%        |          0.16 | -44.5%    | 11.3%        |           0.39 |  0.91 |        |
| Crypto XS momentum: top 5 of 30 by 30d return, weekly | crypto   |       1 | 85.6%      |         1.07 | -23.5%      |          0.03 | -89.6%    | 11.3%        |           0.39 |  0.8  |        |
| Short-term reversal (weekly losers, 10%)              | stocks   |       1 | 8.1%       |         0.41 | -4.0%       |          0.02 | -42.3%    | 7.0%         |           0.44 |  0.54 |        |

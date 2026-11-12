# Round 47: strategies from community Claude trading skills (rebuilt, not their code)

Rules: [PROTOCOL_ROUND47.md](../PROTOCOL_ROUND47.md). US stocks, real price ≥ $10, $20M/day; 0.10%/side; dev 2015–2021, holdout 2022→.

| rule                               |   dev_trades | dev_mean   |   hold_trades | hold_mean   |   hold_t | hold_win   | dev_port_CAGR   | hold_port_CAGR   |   hold_port_Sharpe | hold_port_drop   | PASS   |
|:-----------------------------------|-------------:|:-----------|--------------:|:------------|---------:|:-----------|:----------------|:-----------------|-------------------:|:-----------------|:-------|
| S1a momentum burst, 3 days         |        27620 | 0.05%      |         39377 | -0.10%      |    -0.89 | 44%        | -17.1%          | -9.2%            |              -0.2  | -54.9%           |        |
| S1b momentum burst, 5 days         |        27620 | 0.09%      |         39377 | -0.21%      |    -1.52 | 41%        | -4.9%           | -14.2%           |              -0.43 | -56.6%           |        |
| S2 exhaustion hammer, 2R / 10 days |          911 | 0.06%      |          1219 | -0.02%      |    -0.05 | 38%        | 0.4%            | -1.6%            |              -0.04 | -21.9%           |        |
| S3a earnings-gap drift, 20 days    |         2007 | -0.29%     |          2490 | -1.41%      |    -3.24 | 32%        | -10.5%          | -40.2%           |              -1.66 | -91.8%           |        |
| S3b earnings-gap drift, 60 days    |         2007 | 0.59%      |          2490 | -0.02%      |    -0.02 | 24%        | -3.5%           | -26.4%           |              -0.74 | -77.3%           |        |

## S5 O'Neil market timing on SPY

| rule                       | period   | CAGR   |   Sharpe | worst_drop   | in_market   |
|:---------------------------|:---------|:-------|---------:|:-------------|:------------|
| S5 FTD/distribution timing | dev      | -1.8%  |    -0.59 | -12.0%       | 3%          |
| S5 FTD/distribution timing | holdout  | -0.1%  |    -0.05 | -2.1%        | 2%          |
| SPY buy-and-hold           | dev      | 14.8%  |     0.87 | -33.7%       | 100%        |
| SPY buy-and-hold           | holdout  | 11.5%  |     0.72 | -24.5%       | 100%        |

**Passing: none.**

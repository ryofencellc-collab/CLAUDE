# Round 29: three documented stock/crypto effects, tested for daily income

Rules: [PROTOCOL_ROUND29.md](../PROTOCOL_ROUND29.md). All numbers after costs.

## 1. Crypto big-move reversal

Dev 2024-01-01..2026-01-01, holdout 2026-01-01..2026-11-01. Chosen on dev: **H2_k4**.

**Verdict: FAIL** — net > 0: yes, Sharpe >= 1: yes, max DD > -30%: yes, deflated Sharpe >= 0.95: no

Holdout: 10.6% total, Sharpe 1.40, worst drop -4%, **$0.34/day on $1,000**; $100/day would need 292x exposure, where its worst drop (-4%) becomes a total wipe-out

| config   |   dev Sharpe | dev total   |   hold Sharpe | hold total   |   hold $/day on $1k | hold max DD   |
|:---------|-------------:|:------------|--------------:|:-------------|--------------------:|:--------------|
| H1_k2    |        -2.24 | -62.9%      |         -3.43 | -35.1%       |               -1.4  | -36%          |
| H1_k3    |        -1.16 | -29.6%      |         -1.24 | -10.8%       |               -0.36 | -13%          |
| H1_k4    |        -1.09 | -23.0%      |         -0.17 | -1.6%        |               -0.04 | -8%           |
| H2_k2    |        -1.59 | -52.4%      |         -1.62 | -22.1%       |               -0.78 | -24%          |
| H2_k3    |        -1.07 | -30.0%      |          0.71 | 7.5%         |                0.26 | -7%           |
| H2_k4    |        -0.64 | -13.7%      |          1.4  | 10.6%        |                0.34 | -4%           |
| H4_k2    |        -1.59 | -52.2%      |         -1.23 | -22.0%       |               -0.75 | -31%          |
| H4_k3    |        -1.13 | -28.0%      |         -0.66 | -8.2%        |               -0.25 | -15%          |
| H4_k4    |        -1.12 | -23.6%      |          0.33 | 2.6%         |                0.1  | -7%           |

## 2. Intraday momentum (Nasdaq-100)

Dev 2012-01-01..2020-01-01, holdout 2020-01-01..2026-12-31. Chosen on dev: **q0.8**.

**Verdict: FAIL** — net > 0: yes, Sharpe >= 1: no, max DD > -30%: yes, deflated Sharpe >= 0.95: no

Holdout: 17.0% total, Sharpe 0.55, worst drop -6%, **$0.10/day on $1,000**; $100/day would need 991x exposure, where its worst drop (-6%) becomes a total wipe-out

| config   |   dev Sharpe | dev total   |   hold Sharpe | hold total   |   hold $/day on $1k | hold max DD   |
|:---------|-------------:|:------------|--------------:|:-------------|--------------------:|:--------------|
| q0.0     |        -2.06 | -41.2%      |          0.34 | 12.9%        |                0.08 | -11%          |
| q0.5     |        -1.09 | -19.8%      |          0.52 | 18.6%        |                0.11 | -8%           |
| q0.8     |        -0.34 | -5.3%       |          0.55 | 17.0%        |                0.1  | -6%           |

## 3. Overnight drift

Dev 2000-01-01..2016-01-01, holdout 2016-01-01..2026-12-31. Chosen on dev: **IWM_after_down**.

**Verdict: FAIL** — net > 0: yes, Sharpe >= 1: no, max DD > -30%: yes, deflated Sharpe >= 0.95: no

Holdout: 82.1% total, Sharpe 0.59, worst drop -20%, **$0.24/day on $1,000**; $100/day would need 415x exposure, where its worst drop (-20%) becomes a total wipe-out

| config         |   dev Sharpe | dev total   |   hold Sharpe | hold total   |   hold $/day on $1k | hold max DD   |
|:---------------|-------------:|:------------|--------------:|:-------------|--------------------:|:--------------|
| SPY_all        |         0.08 | 3.6%        |          0.43 | 58.2%        |                0.19 | -30%          |
| SPY_after_up   |        -0.45 | -45.1%      |          0.08 | 3.9%         |                0.03 | -22%          |
| SPY_after_down |         0.54 | 88.7%       |          0.5  | 51.7%        |                0.17 | -20%          |
| QQQ_all        |         0.41 | 118.2%      |          0.55 | 104.1%       |                0.3  | -31%          |
| QQQ_after_up   |         0.14 | 15.6%       |          0.31 | 30.1%        |                0.11 | -29%          |
| QQQ_after_down |         0.43 | 93.7%       |          0.46 | 55.2%        |                0.18 | -20%          |
| IWM_all        |         0.57 | 169.7%      |          0.73 | 175.5%       |                0.41 | -29%          |
| IWM_after_up   |         0.08 | 5.0%        |          0.45 | 52.4%        |                0.17 | -20%          |
| IWM_after_down |         0.66 | 146.5%      |          0.59 | 82.1%        |                0.24 | -20%          |


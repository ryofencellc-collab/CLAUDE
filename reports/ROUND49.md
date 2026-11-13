# Round 49: the options wheel on real end-of-day chains

Rules: [PROTOCOL_ROUND49.md](../PROTOCOL_ROUND49.md). One cash-secured contract per symbol; natural fills; $0.65/contract.

## Equal-weight portfolio of the 8 symbols

| variant | period | wheel CAGR | wheel Sharpe | wheel drop | buy-hold CAGR | buy-hold Sharpe | buy-hold drop |
|---|---|---:|---:|---:|---:|---:|---:|
| W1 wheel d0.30 | dev | 4.4% | 0.43 | -36.3% | 26.0% | 1.26 | -41.0% |
| W1 wheel d0.30 | holdout | 12.7% | 0.74 | -24.1% | 29.7% | 1.24 | -27.7% |
| W2 wheel d0.16 | dev | -0.5% | 0.08 | -39.5% | 26.0% | 1.26 | -41.0% |
| W2 wheel d0.16 | holdout | 11.6% | 0.77 | -18.2% | 29.7% | 1.24 | -27.7% |
| W3 wheel d0.30, calls >= cost | dev | 16.3% | 1.10 | -33.2% | 26.0% | 1.26 | -41.0% |
| W3 wheel d0.30, calls >= cost | holdout | 19.3% | 1.08 | -24.0% | 29.7% | 1.24 | -27.7% |

**Passing: none.**

## Per symbol

| variant                       | period   | symbol   |   trades | wheel_CAGR   |   wheel_Sharpe | wheel_drop   | hold_CAGR   |   hold_Sharpe | hold_drop   |
|:------------------------------|:---------|:---------|---------:|:-------------|---------------:|:-------------|:------------|--------------:|:------------|
| W1 wheel d0.30                | dev      | SPY      |       50 | 6.7%         |           0.62 | -22.9%       | 11.9%       |          0.83 | -28.7%      |
| W1 wheel d0.30                | dev      | AAPL     |       51 | 6.8%         |           0.69 | -21.1%       | 28.1%       |          1.21 | -30.8%      |
| W1 wheel d0.30                | dev      | MSFT     |       51 | 15.6%        |           0.97 | -30.8%       | 22.5%       |          1.1  | -35.9%      |
| W1 wheel d0.30                | dev      | NVDA     |       51 | 20.8%        |           1.16 | -22.7%       | 67.3%       |          1.59 | -66.4%      |
| W1 wheel d0.30                | dev      | AMZN     |       51 | -31.5%       |          -0.28 | -88.1%       | 12.2%       |          0.64 | -56.0%      |
| W1 wheel d0.30                | dev      | META     |       20 | 34.5%        |           1.44 | -32.7%       | 70.1%       |          1.76 | -50.5%      |
| W1 wheel d0.30                | dev      | TSLA     |       40 | 6.2%         |           0.45 | -39.5%       | 0.7%        |          0.4  | -72.3%      |
| W1 wheel d0.30                | dev      | GOOGL    |       52 | nan%         |          -0.42 | -121.2%      | 20.1%       |          0.94 | -42.3%      |
| W1 wheel d0.30                | holdout  | SPY      |       38 | 8.9%         |           0.8  | -19.0%       | 17.1%       |          1.16 | -19.0%      |
| W1 wheel d0.30                | holdout  | AAPL     |       38 | 10.8%        |           0.58 | -33.8%       | 24.3%       |          0.96 | -33.2%      |
| W1 wheel d0.30                | holdout  | MSFT     |       38 | 5.2%         |           0.36 | -27.0%       | 13.4%       |          0.63 | -34.9%      |
| W1 wheel d0.30                | holdout  | NVDA     |       38 | 7.4%         |           0.59 | -22.0%       | 61.6%       |          1.32 | -36.9%      |
| W1 wheel d0.30                | holdout  | AMZN     |       38 | 16.6%        |           0.72 | -24.8%       | 21.6%       |          0.8  | -30.9%      |
| W1 wheel d0.30                | holdout  | META     |       38 | 13.3%        |           0.55 | -29.4%       | 22.2%       |          0.74 | -34.2%      |
| W1 wheel d0.30                | holdout  | TSLA     |       38 | 14.4%        |           0.54 | -52.3%       | 15.4%       |          0.56 | -53.8%      |
| W1 wheel d0.30                | holdout  | GOOGL    |       38 | -0.7%        |           0.17 | -39.6%       | 28.7%       |          1.01 | -30.4%      |
| W2 wheel d0.16                | dev      | SPY      |       50 | 10.4%        |           0.97 | -17.8%       | 11.9%       |          0.83 | -28.7%      |
| W2 wheel d0.16                | dev      | AAPL     |       51 | 11.5%        |           1.27 | -15.6%       | 28.1%       |          1.21 | -30.8%      |
| W2 wheel d0.16                | dev      | MSFT     |       51 | 6.1%         |           0.49 | -30.2%       | 22.5%       |          1.1  | -35.9%      |
| W2 wheel d0.16                | dev      | NVDA     |       51 | 10.9%        |           1    | -27.1%       | 67.3%       |          1.59 | -66.4%      |
| W2 wheel d0.16                | dev      | AMZN     |       51 | nan%         |          -0.57 | -108.8%      | 12.2%       |          0.64 | -56.0%      |
| W2 wheel d0.16                | dev      | META     |       20 | 34.7%        |           1.43 | -30.5%       | 70.1%       |          1.76 | -50.5%      |
| W2 wheel d0.16                | dev      | TSLA     |       40 | 21.4%        |           1.28 | -16.1%       | 0.7%        |          0.4  | -72.3%      |
| W2 wheel d0.16                | dev      | GOOGL    |       52 | nan%         |          -0.59 | -131.2%      | 20.1%       |          0.94 | -42.3%      |
| W2 wheel d0.16                | holdout  | SPY      |       38 | 7.8%         |           1.15 | -6.8%        | 17.1%       |          1.16 | -19.0%      |
| W2 wheel d0.16                | holdout  | AAPL     |       38 | 8.6%         |           0.53 | -25.2%       | 24.3%       |          0.96 | -33.2%      |
| W2 wheel d0.16                | holdout  | MSFT     |       38 | 5.5%         |           0.41 | -21.0%       | 13.4%       |          0.63 | -34.9%      |
| W2 wheel d0.16                | holdout  | NVDA     |       38 | 11.4%        |           0.75 | -11.7%       | 61.6%       |          1.32 | -36.9%      |
| W2 wheel d0.16                | holdout  | AMZN     |       38 | 16.5%        |           0.78 | -20.3%       | 21.6%       |          0.8  | -30.9%      |
| W2 wheel d0.16                | holdout  | META     |       38 | 13.5%        |           0.59 | -31.7%       | 22.2%       |          0.74 | -34.2%      |
| W2 wheel d0.16                | holdout  | TSLA     |       38 | 6.3%         |           0.39 | -46.0%       | 15.4%       |          0.56 | -53.8%      |
| W2 wheel d0.16                | holdout  | GOOGL    |       38 | 3.3%         |           0.27 | -38.2%       | 28.7%       |          1.01 | -30.4%      |
| W3 wheel d0.30, calls >= cost | dev      | SPY      |       50 | 11.4%        |           0.89 | -22.1%       | 11.9%       |          0.83 | -28.7%      |
| W3 wheel d0.30, calls >= cost | dev      | AAPL     |       51 | 10.5%        |           0.99 | -21.1%       | 28.1%       |          1.21 | -30.8%      |
| W3 wheel d0.30, calls >= cost | dev      | MSFT     |       47 | 18.4%        |           1    | -37.4%       | 22.5%       |          1.1  | -35.9%      |
| W3 wheel d0.30, calls >= cost | dev      | NVDA     |       41 | 27.5%        |           1.35 | -29.5%       | 67.3%       |          1.59 | -66.4%      |
| W3 wheel d0.30, calls >= cost | dev      | AMZN     |       42 | 16.6%        |           0.9  | -41.2%       | 12.2%       |          0.64 | -56.0%      |
| W3 wheel d0.30, calls >= cost | dev      | META     |       20 | 36.2%        |           1.62 | -33.6%       | 70.1%       |          1.76 | -50.5%      |
| W3 wheel d0.30, calls >= cost | dev      | TSLA     |       22 | 1.0%         |           0.4  | -71.1%       | 0.7%        |          0.4  | -72.3%      |
| W3 wheel d0.30, calls >= cost | dev      | GOOGL    |       42 | 12.4%        |           0.65 | -51.1%       | 20.1%       |          0.94 | -42.3%      |
| W3 wheel d0.30, calls >= cost | holdout  | SPY      |       38 | 10.7%        |           0.91 | -19.9%       | 17.1%       |          1.16 | -19.0%      |
| W3 wheel d0.30, calls >= cost | holdout  | AAPL     |       38 | 18.0%        |           0.81 | -32.6%       | 24.3%       |          0.96 | -33.2%      |
| W3 wheel d0.30, calls >= cost | holdout  | MSFT     |       38 | 13.4%        |           0.67 | -26.8%       | 13.4%       |          0.63 | -34.9%      |
| W3 wheel d0.30, calls >= cost | holdout  | NVDA     |       38 | 13.3%        |           0.77 | -22.0%       | 61.6%       |          1.32 | -36.9%      |
| W3 wheel d0.30, calls >= cost | holdout  | AMZN     |       38 | 25.4%        |           1.05 | -26.4%       | 21.6%       |          0.8  | -30.9%      |
| W3 wheel d0.30, calls >= cost | holdout  | META     |       37 | 19.4%        |           0.69 | -29.8%       | 22.2%       |          0.74 | -34.2%      |
| W3 wheel d0.30, calls >= cost | holdout  | TSLA     |       35 | 22.1%        |           0.68 | -45.2%       | 15.4%       |          0.56 | -53.8%      |
| W3 wheel d0.30, calls >= cost | holdout  | GOOGL    |       38 | 7.4%         |           0.4  | -32.7%       | 28.7%       |          1.01 | -30.4%      |

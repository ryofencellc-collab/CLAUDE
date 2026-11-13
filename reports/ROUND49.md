# Round 49: the options wheel on real end-of-day chains

Rules: [PROTOCOL_ROUND49.md](../PROTOCOL_ROUND49.md). One cash-secured contract per symbol; natural fills; $0.65/contract.

## Equal-weight portfolio of the 8 symbols

| variant | period | wheel CAGR | wheel Sharpe | wheel drop | buy-hold CAGR | buy-hold Sharpe | buy-hold drop |
|---|---|---:|---:|---:|---:|---:|---:|
| W1 wheel d0.30 | dev | nan% | -0.08 | -26760.3% | 25.0% | 1.38 | -33.1% |
| W1 wheel d0.30 | holdout | nan% | -0.79 | -105.2% | 0.0% | nan | 0.0% |
| W2 wheel d0.16 | dev | nan% | 0.79 | -79875.2% | 25.0% | 1.38 | -33.1% |
| W2 wheel d0.16 | holdout | nan% | -0.45 | -101.9% | 0.0% | nan | 0.0% |
| W3 wheel d0.30, calls >= cost | dev | -81.2% | -0.10 | -1913.7% | 25.0% | 1.38 | -33.1% |
| W3 wheel d0.30, calls >= cost | holdout | nan% | -0.73 | -105.2% | 0.0% | nan | 0.0% |

**Passing: none.**

## Per symbol

| variant                       | period   | symbol   |   trades | wheel_CAGR   |   wheel_Sharpe | wheel_drop   | hold_CAGR   |   hold_Sharpe | hold_drop   |
|:------------------------------|:---------|:---------|---------:|:-------------|---------------:|:-------------|:------------|--------------:|:------------|
| W1 wheel d0.30                | dev      | SPY      |       50 | 6.6%         |           0.61 | -22.9%       | 11.9%       |          0.83 | -28.7%      |
| W1 wheel d0.30                | dev      | AAPL     |       51 | nan%         |          -0.08 | -300.3%      | 28.1%       |          1.21 | -30.8%      |
| W1 wheel d0.30                | dev      | MSFT     |       51 | 15.5%        |           0.96 | -30.7%       | 22.5%       |          1.1  | -35.9%      |
| W1 wheel d0.30                | dev      | NVDA     |       51 | 143.7%       |          -0.35 | -4195.6%     | 67.3%       |          1.59 | -66.4%      |
| W1 wheel d0.30                | dev      | AMZN     |       51 | nan%         |          -0.72 | -1814.5%     | 12.2%       |          0.64 | -56.0%      |
| W1 wheel d0.30                | dev      | META     |       20 | 34.5%        |           1.44 | -32.8%       | 70.1%       |          1.76 | -50.5%      |
| W1 wheel d0.30                | dev      | TSLA     |       40 | 9.1%         |           1.21 | -166.9%      | nan%        |        nan    | nan%        |
| W1 wheel d0.30                | dev      | GOOGL    |       51 | nan%         |          -0.71 | -1865.5%     | 20.1%       |          0.94 | -42.3%      |
| W1 wheel d0.30                | holdout  | SPY      |       38 | 8.8%         |           0.75 | -19.3%       | nan%        |        nan    | nan%        |
| W1 wheel d0.30                | holdout  | AAPL     |       38 | 10.8%        |           0.57 | -34.2%       | nan%        |        nan    | nan%        |
| W1 wheel d0.30                | holdout  | MSFT     |       38 | 5.2%         |           0.36 | -27.0%       | nan%        |        nan    | nan%        |
| W1 wheel d0.30                | holdout  | NVDA     |       38 | nan%         |          -0.97 | -848.2%      | nan%        |        nan    | nan%        |
| W1 wheel d0.30                | holdout  | AMZN     |       38 | 17.5%        |           0.75 | -24.3%       | nan%        |        nan    | nan%        |
| W1 wheel d0.30                | holdout  | META     |       38 | 8.8%         |           0.43 | -32.6%       | nan%        |        nan    | nan%        |
| W1 wheel d0.30                | holdout  | TSLA     |       38 | 16.4%        |           0.58 | -52.6%       | nan%        |        nan    | nan%        |
| W1 wheel d0.30                | holdout  | GOOGL    |       38 | -0.8%        |           0.18 | -39.8%       | nan%        |        nan    | nan%        |
| W2 wheel d0.16                | dev      | SPY      |       50 | 10.3%        |           0.97 | -17.6%       | 11.9%       |          0.83 | -28.7%      |
| W2 wheel d0.16                | dev      | AAPL     |       51 | nan%         |          -1.05 | -281.8%      | 28.1%       |          1.21 | -30.8%      |
| W2 wheel d0.16                | dev      | MSFT     |       51 | 6.1%         |           0.48 | -30.1%       | 22.5%       |          1.1  | -35.9%      |
| W2 wheel d0.16                | dev      | NVDA     |       51 | nan%         |           0.26 | -3597.4%     | 67.3%       |          1.59 | -66.4%      |
| W2 wheel d0.16                | dev      | AMZN     |       51 | nan%         |           0.59 | -1703.0%     | 12.2%       |          0.64 | -56.0%      |
| W2 wheel d0.16                | dev      | META     |       20 | 44.1%        |           1.73 | -30.7%       | 70.1%       |          1.76 | -50.5%      |
| W2 wheel d0.16                | dev      | TSLA     |       40 | -35.5%       |           0.66 | -157.5%      | nan%        |        nan    | nan%        |
| W2 wheel d0.16                | dev      | GOOGL    |       51 | nan%         |          -0.67 | -1751.0%     | 20.1%       |          0.94 | -42.3%      |
| W2 wheel d0.16                | holdout  | SPY      |       38 | 11.0%        |           1.04 | -13.3%       | nan%        |        nan    | nan%        |
| W2 wheel d0.16                | holdout  | AAPL     |       38 | 8.6%         |           0.52 | -25.5%       | nan%        |        nan    | nan%        |
| W2 wheel d0.16                | holdout  | MSFT     |       38 | 5.6%         |           0.41 | -21.2%       | nan%        |        nan    | nan%        |
| W2 wheel d0.16                | holdout  | NVDA     |       38 | nan%         |          -0.66 | -834.4%      | nan%        |        nan    | nan%        |
| W2 wheel d0.16                | holdout  | AMZN     |       38 | 18.1%        |           0.84 | -19.2%       | nan%        |        nan    | nan%        |
| W2 wheel d0.16                | holdout  | META     |       38 | 13.5%        |           0.59 | -31.7%       | nan%        |        nan    | nan%        |
| W2 wheel d0.16                | holdout  | TSLA     |       38 | 10.9%        |           0.47 | -40.1%       | nan%        |        nan    | nan%        |
| W2 wheel d0.16                | holdout  | GOOGL    |       38 | -0.4%        |           0.16 | -41.0%       | nan%        |        nan    | nan%        |
| W3 wheel d0.30, calls >= cost | dev      | SPY      |       50 | 10.4%        |           0.81 | -23.0%       | 11.9%       |          0.83 | -28.7%      |
| W3 wheel d0.30, calls >= cost | dev      | AAPL     |        7 | -31.8%       |          -0.43 | -300.3%      | 28.1%       |          1.21 | -30.8%      |
| W3 wheel d0.30, calls >= cost | dev      | MSFT     |       47 | 18.3%        |           0.99 | -37.3%       | 22.5%       |          1.1  | -35.9%      |
| W3 wheel d0.30, calls >= cost | dev      | NVDA     |       42 | 120.2%       |          -0    | -4195.6%     | 67.3%       |          1.59 | -66.4%      |
| W3 wheel d0.30, calls >= cost | dev      | AMZN     |       30 | nan%         |          -0.73 | -1814.5%     | 12.2%       |          0.64 | -56.0%      |
| W3 wheel d0.30, calls >= cost | dev      | META     |       20 | 36.2%        |           1.62 | -33.7%       | 70.1%       |          1.76 | -50.5%      |
| W3 wheel d0.30, calls >= cost | dev      | TSLA     |       22 | 11.5%        |           0.39 | -166.9%      | nan%        |        nan    | nan%        |
| W3 wheel d0.30, calls >= cost | dev      | GOOGL    |       32 | nan%         |          -0.71 | -1865.5%     | 20.1%       |          0.94 | -42.3%      |
| W3 wheel d0.30, calls >= cost | holdout  | SPY      |       38 | 10.6%        |           0.86 | -20.3%       | nan%        |        nan    | nan%        |
| W3 wheel d0.30, calls >= cost | holdout  | AAPL     |       38 | 17.1%        |           0.77 | -32.8%       | nan%        |        nan    | nan%        |
| W3 wheel d0.30, calls >= cost | holdout  | MSFT     |       38 | 15.2%        |           0.72 | -27.0%       | nan%        |        nan    | nan%        |
| W3 wheel d0.30, calls >= cost | holdout  | NVDA     |        6 | nan%         |          -0.97 | -848.2%      | nan%        |        nan    | nan%        |
| W3 wheel d0.30, calls >= cost | holdout  | AMZN     |       38 | 26.1%        |           1.09 | -25.9%       | nan%        |        nan    | nan%        |
| W3 wheel d0.30, calls >= cost | holdout  | META     |       37 | 15.4%        |           0.58 | -33.0%       | nan%        |        nan    | nan%        |
| W3 wheel d0.30, calls >= cost | holdout  | TSLA     |       35 | 25.3%        |           0.73 | -45.8%       | nan%        |        nan    | nan%        |
| W3 wheel d0.30, calls >= cost | holdout  | GOOGL    |       38 | 7.3%         |           0.4  | -33.0%       | nan%        |        nan    | nan%        |

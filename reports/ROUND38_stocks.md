# Round 38: simple swing strategies (2–3 trades a week)

Rules: [PROTOCOL_ROUND38.md](../PROTOCOL_ROUND38.md). Next-open entries, stop-before-target, 0.10% per side, ≤ 3 new trades/week, ≤ 5 open, risk 2% to the stop (breakouts) or 20% of equity per trade (dip-buys).

**0 of 13 configs pass.**

## STOCKS (dev 2015-01-01–2022-01-01, holdout 2022-01-01–2026-12-01)

| strategy                                 |   dev %/yr |   dev win % |   hold %/yr |   hold Sharpe | hold worst drop   |   trades/wk |   win % | avg win   | avg loss   | avg trade   |     t |   $25k/day | PASS   |
|:-----------------------------------------|-----------:|------------:|------------:|--------------:|:------------------|------------:|--------:|:----------|:-----------|:------------|------:|-----------:|:-------|
| D4 IBS<0.2 in uptrend                    |       -0.1 |          62 |        12.2 |          0.76 | -13%              |        3.01 |      61 | 2.8%      | -3.5%      | 0.40%       |  2.03 |      10.51 |        |
| D2 RSI(2)<5 in uptrend                   |       -3.1 |          64 |         2.4 |          0.22 | -20%              |        2.99 |      62 | 2.9%      | -4.4%      | 0.13%       |  0.65 |       1.7  |        |
| D1 RSI(2)<10 in uptrend                  |       -0.9 |          64 |         1.7 |          0.19 | -21%              |        3    |      62 | 2.8%      | -4.2%      | 0.11%       |  0.56 |       1.23 |        |
| B1 breakout 20d, exit trail              |       -2.2 |          37 |        -0.4 |          0.16 | -72%              |        2.1  |      30 | 19.5%     | -8.4%      | 0.05%       |  0.04 |      -0.24 |        |
| B3 squeeze breakout, exit trail          |       12.1 |          35 |        -3   |          0.01 | -43%              |        1.77 |      30 | 13.0%     | -5.4%      | 0.15%       |  0.27 |      -1.93 |        |
| D3 3 down closes in uptrend              |       -7.7 |          56 |        -2.1 |          0.01 | -52%              |        3.01 |      57 | 3.8%      | -5.0%      | -0.00%      | -0.02 |      -1.39 |        |
| B2 breakout 55d, exit trail              |       -9   |          34 |       -10.4 |         -0.17 | -56%              |        2.05 |      32 | 16.0%     | -7.5%      | -0.03%      | -0.04 |      -5.84 |        |
| D5 gap down >=2% in uptrend, open->close |      -10.9 |          49 |        -8   |         -0.25 | -44%              |        3.01 |      48 | 4.7%      | -4.7%      | -0.19%      | -0.73 |      -4.71 |        |
| B3 squeeze breakout, exit 2R             |       13.5 |          40 |        -9.9 |         -0.32 | -50%              |        2.04 |      35 | 10.3%     | -5.8%      | -0.14%      | -0.36 |      -5.61 |        |
| B2 breakout 55d, exit 2R                 |       -6   |          39 |       -16.8 |         -0.53 | -73%              |        2.45 |      35 | 13.2%     | -8.0%      | -0.59%      | -1.15 |      -8.33 |        |
| B1 breakout 20d, exit 2R                 |       -3   |          39 |       -18.8 |         -0.58 | -70%              |        2.49 |      36 | 13.3%     | -8.9%      | -0.98%      | -1.81 |      -8.97 |        |
| B2 breakout 55d, exit 1R                 |      -15.7 |          48 |       -18.2 |         -0.78 | -65%              |        2.81 |      47 | 7.4%      | -8.0%      | -0.75%      | -2.15 |      -8.81 |        |
| B1 breakout 20d, exit 1R                 |       -4.8 |          49 |       -19.8 |         -0.86 | -68%              |        2.84 |      47 | 7.5%      | -8.5%      | -0.96%      | -2.68 |      -9.29 |        |

## Risk per trade (holdout): what the best three (none passed) make at 1%, 2%, 5%

| market   | strategy                | risk   | start   |   %/yr | worst drop   |   $/day | end     |
|:---------|:------------------------|:-------|:--------|-------:|:-------------|--------:|:--------|
| stocks   | D4 IBS<0.2 in uptrend   | 1%     | $25,000 |   12.2 | -13%         |   10.51 | $43,586 |
| stocks   | D4 IBS<0.2 in uptrend   | 1%     | $1,000  |   12.2 | -13%         |    0.42 | $1,743  |
| stocks   | D4 IBS<0.2 in uptrend   | 2%     | $25,000 |   12.2 | -13%         |   10.51 | $43,586 |
| stocks   | D4 IBS<0.2 in uptrend   | 2%     | $1,000  |   12.2 | -13%         |    0.42 | $1,743  |
| stocks   | D4 IBS<0.2 in uptrend   | 5%     | $25,000 |   12.2 | -13%         |   10.51 | $43,586 |
| stocks   | D4 IBS<0.2 in uptrend   | 5%     | $1,000  |   12.2 | -13%         |    0.42 | $1,743  |
| stocks   | D2 RSI(2)<5 in uptrend  | 1%     | $25,000 |    2.4 | -20%         |    1.7  | $27,997 |
| stocks   | D2 RSI(2)<5 in uptrend  | 1%     | $1,000  |    2.4 | -20%         |    0.07 | $1,120  |
| stocks   | D2 RSI(2)<5 in uptrend  | 2%     | $25,000 |    2.4 | -20%         |    1.7  | $27,997 |
| stocks   | D2 RSI(2)<5 in uptrend  | 2%     | $1,000  |    2.4 | -20%         |    0.07 | $1,120  |
| stocks   | D2 RSI(2)<5 in uptrend  | 5%     | $25,000 |    2.4 | -20%         |    1.7  | $27,997 |
| stocks   | D2 RSI(2)<5 in uptrend  | 5%     | $1,000  |    2.4 | -20%         |    0.07 | $1,120  |
| stocks   | D1 RSI(2)<10 in uptrend | 1%     | $25,000 |    1.7 | -21%         |    1.23 | $27,175 |
| stocks   | D1 RSI(2)<10 in uptrend | 1%     | $1,000  |    1.7 | -21%         |    0.05 | $1,087  |
| stocks   | D1 RSI(2)<10 in uptrend | 2%     | $25,000 |    1.7 | -21%         |    1.23 | $27,175 |
| stocks   | D1 RSI(2)<10 in uptrend | 2%     | $1,000  |    1.7 | -21%         |    0.05 | $1,087  |
| stocks   | D1 RSI(2)<10 in uptrend | 5%     | $25,000 |    1.7 | -21%         |    1.23 | $27,175 |
| stocks   | D1 RSI(2)<10 in uptrend | 5%     | $1,000  |    1.7 | -21%         |    0.05 | $1,087  |

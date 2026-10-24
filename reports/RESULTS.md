# Phase 1 results

Official run: GitHub Actions run
[40095145481](https://github.com/ryofencellc-collab/CLAUDE/actions/runs/40095145481),
commit `3ad08cc`, 2026-10-24. Data: Binance archive to 2026-09-30, Yahoo to 2026-10-23.

Trials run: **61** across **9** families. In-sample ≤ 2022-12-31, holdout after.
Rules: see [PROTOCOL.md](../PROTOCOL.md).

## Verdict per family (best in-sample config, judged on holdout)

| family        | market | params                                     | is_sharpe | oos_sharpe | oos_cagr | oos_max_dd | oos_years | oos_trades |  dsr | passed | failed                                       |
|:--------------|:-------|:-------------------------------------------|----------:|-----------:|:---------|:-----------|----------:|-----------:|-----:|:-------|:---------------------------------------------|
| btc_trend     | crypto | {"sma": 50}                                |      1.25 |       1.46 | +55.6%   | -26.5%     |      3.75 |         79 | 0.69 | False  | dsr>=0.95, max_dd<=25%                       |
| xs_momentum   | crypto | {"lookback": 30, "regime": true, "top": 5} |      1.50 |       0.69 | +26.3%   | -56.6%     |      3.75 |        125 | 0.15 | False  | oos_sharpe>=1, dsr>=0.95, max_dd<=25%        |
| xs_reversal   | crypto | {"lookback": 1, "top": 5}                  |      0.09 |      -0.76 | -52.4%   | -97.2%     |      3.75 |       1369 | 0.00 | False  | oos_sharpe>=1, dsr>=0.95, beats_tbill, max_dd<=25% |
| funding_carry | crypto | {"threshold": 0.0, "top": 10, "window": 14} |     6.54 |      -0.79 | -1.7%    | -9.0%      |      3.75 |        698 | 0.00 | False  | oos_sharpe>=1, dsr>=0.95, beats_tbill        |
| overnight     | etf    | {"ticker": "IWM"}                          |      0.24 |       0.31 | +3.3%    | -21.0%     |      3.79 |        956 | 0.04 | False  | oos_sharpe>=1, dsr>=0.95, beats_tbill        |
| rsi2          | etf    | {"entry": 10, "exit_": 50, "trend": false} |      0.61 |       1.29 | +11.1%   | -7.5%      |      3.79 |        106 | 0.58 | False  | dsr>=0.95                                    |
| vix_carry     | etf    | {"smooth": 5, "threshold": 0.9}            |      0.84 |       0.32 | +4.3%    | -42.8%     |      3.79 |         57 | 0.04 | False  | oos_sharpe>=1, dsr>=0.95, max_dd<=25%        |
| turn_of_month | etf    | {"after": 3, "before": 3}                  |      0.47 |       0.61 | +4.4%    | -15.5%     |      3.79 |         92 | 0.13 | False  | oos_sharpe>=1, dsr>=0.95                     |
| rotation      | etf    | {"lookback": 126}                          |      0.52 |       1.37 | +26.5%   | -19.4%     |      3.79 |          6 | 0.62 | False  | dsr>=0.95, evidence                          |

**Passed Phase 1: 0 / 9**

## Benchmarks (not trials)

| benchmark    | segment | sharpe | cagr  | max_dd |
|:-------------|:--------|-------:|------:|-------:|
| buy&hold BTC | IS      |   0.72 | +29%  | -83%   |
| buy&hold BTC | OOS     |   1.16 | +54%  | -53%   |
| buy&hold SPY | IS      |   0.40 | +6%   | -55%   |
| buy&hold SPY | OOS     |   1.38 | +21%  | -19%   |

## Null test (same pipeline on shuffled, zero-drift data)

| seed | families | passed | best_oos_sharpe |
|-----:|---------:|-------:|----------------:|
|    0 |        9 |      0 |            0.20 |
|    1 |        9 |      0 |            0.89 |
|    2 |        9 |      0 |            0.76 |

Null test clean: the framework does not manufacture passes from noise.

Per-config results for all 61 trials are in the run log and the
`phase1-reports` artifact of the run above.

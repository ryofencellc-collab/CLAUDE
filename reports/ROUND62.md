# Round 62: every-variable analysis of 0DTE trades (real recorded quotes)

Rules: [PROTOCOL_ROUND62.md](../PROTOCOL_ROUND62.md).
Recorded days: **9** (INTERIM: pass needs 20 days); snapshots analysed: 6,127; variables: 41.

## A. Which variables predict? (per-day Spearman IC vs a time-shift null)

Each IC is compared with a null built from the same day's target shifted in time (raw within-day ICs of level variables are biased). Bonferroni bar |z| ≥ 3.41 over 76 tests. Significant: **28**.

| variable      | target       |   mean_IC |   null_mean |   excess |   z_vs_null |   days | significant   |
|:--------------|:-------------|----------:|------------:|---------:|------------:|-------:|:--------------|
| vs_orh        | fwd30        |    -0.515 |       0.082 |   -0.597 |     -13.024 |     18 | True          |
| vs_open       | call−put P&L |    -0.488 |       0.086 |   -0.574 |     -12.952 |     18 | True          |
| vs_orl        | fwd30        |    -0.515 |       0.088 |   -0.603 |     -12.223 |     18 | True          |
| dist_maxoi    | call−put P&L |    -0.43  |       0.094 |   -0.524 |     -11.258 |     18 | True          |
| pcr_oi        | call−put P&L |     0.475 |      -0.088 |    0.562 |      11.054 |     18 | True          |
| vs_orh        | call−put P&L |    -0.488 |       0.095 |   -0.582 |     -10.76  |     18 | True          |
| vs_open       | fwd30        |    -0.515 |       0.088 |   -0.603 |     -10.716 |     18 | True          |
| gex           | call−put P&L |    -0.386 |       0.066 |   -0.451 |     -10.645 |     18 | True          |
| vs_orl        | call−put P&L |    -0.488 |       0.09  |   -0.578 |     -10.546 |     18 | True          |
| pcr_oi        | fwd30        |     0.506 |      -0.074 |    0.581 |      10.275 |     18 | True          |
| dist_maxoi    | fwd30        |    -0.45  |       0.096 |   -0.545 |      -8.804 |     18 | True          |
| pcr_vol       | fwd30        |     0.332 |      -0.086 |    0.417 |       8.356 |     18 | True          |
| gex           | fwd30        |    -0.39  |       0.044 |   -0.434 |      -8.347 |     18 | True          |
| vs_mean       | fwd30        |    -0.378 |       0.031 |   -0.41  |      -7.8   |     18 | True          |
| vs_low        | fwd30        |    -0.318 |       0.042 |   -0.361 |      -7.521 |     18 | True          |
| vs_high       | fwd30        |    -0.37  |       0.012 |   -0.382 |      -7.293 |     18 | True          |
| pcr_vol       | call−put P&L |     0.29  |      -0.071 |    0.361 |       6.711 |     18 | True          |
| vs_high       | call−put P&L |    -0.308 |       0.02  |   -0.329 |      -6.257 |     18 | True          |
| vs_low        | call−put P&L |    -0.279 |       0.04  |   -0.319 |      -6.054 |     18 | True          |
| vs_mean       | call−put P&L |    -0.299 |       0.022 |   -0.32  |      -5.92  |     18 | True          |
| atm_iv        | fwd30        |     0.178 |      -0.053 |    0.231 |       4.924 |     18 | True          |
| macd_slope    | call−put P&L |     0.11  |       0.001 |    0.109 |       4.827 |     18 | True          |
| atm_gamma     | fwd30        |    -0.097 |       0.053 |   -0.149 |      -4.054 |     18 | True          |
| atm_iv        | call−put P&L |     0.154 |      -0.056 |    0.211 |       3.984 |     18 | True          |
| min_since_low | fwd30        |    -0.127 |       0.069 |   -0.196 |      -3.948 |     18 | True          |
| atm_spread    | fwd30        |     0.046 |      -0.016 |    0.062 |       3.665 |     18 | True          |
| min_since_low | call−put P&L |    -0.101 |       0.057 |   -0.158 |      -3.622 |     18 | True          |
| ret30         | fwd30        |    -0.247 |      -0.072 |   -0.175 |      -3.416 |     18 | True          |
| theta_proxy   | fwd30        |     0.097 |      -0.045 |    0.141 |       3.352 |     18 | False         |
| ema9_21       | fwd30        |    -0.226 |      -0.076 |   -0.15  |      -3.187 |     18 | False         |

## A2. Tradable test per variable (learn direction on the first half of the days, trade the second half every 30 min, real bid/ask)

This is the unbiased test. The table in A is descriptive only (its within-day ICs are inflated for level variables, see amendments).

Variables that beat the better of 'always puts' / 'always calls' on the same holdout: SPY 0, SPXW 0.

Variables profitable in holdout: SPY 15/41, SPXW 20/41. Profitable on BOTH roots: BASELINE always puts, atm_iv, bb_pctb, dist_maxgamma, ema9_21, imb_put, iv_chg15, ret1, ret10, ret3, rsi, vol15_put, vs_high.

| root   | variable              | rule                                |   holdout_trades |   holdout_total |   per_trade | green_days   |     t |   beats_best_baseline |
|:-------|:----------------------|:------------------------------------|-----------------:|----------------:|------------:|:-------------|------:|----------------------:|
| SPXW   | BASELINE always puts  | no signal (trend tilt)              |               55 |         16465   |      299.36 | 4/5          |  2.28 |                       |
| SPXW   | atm_iv                | below dev median → calls, else puts |               55 |         16465   |      299.36 | 4/5          |  2.28 |                     0 |
| SPXW   | rv30                  | below dev median → calls, else puts |               55 |         15835   |      287.91 | 4/5          |  2.34 |                     0 |
| SPXW   | vol15_put             | below dev median → calls, else puts |               55 |         12535   |      227.91 | 5/5          |  3.78 |                     0 |
| SPXW   | vs_high               | above dev median → calls, else puts |               55 |         10775   |      195.91 | 4/5          |  1.82 |                     0 |
| SPXW   | iv_chg15              | below dev median → calls, else puts |               55 |          9465   |      172.09 | 4/5          |  2.4  |                     0 |
| SPXW   | bb_pctb               | above dev median → calls, else puts |               55 |          8605   |      156.45 | 4/5          |  1.87 |                     0 |
| SPXW   | dist_maxoi            | above dev median → calls, else puts |               55 |          8145   |      148.09 | 3/5          |  0.87 |                     0 |
| SPXW   | ret3                  | above dev median → calls, else puts |               55 |          7495   |      136.27 | 4/5          |  1.23 |                     0 |
| SPXW   | ret5                  | above dev median → calls, else puts |               55 |          6705   |      121.91 | 3/5          |  1.34 |                     0 |
| SPXW   | vol15_call            | below dev median → calls, else puts |               55 |          6375   |      115.91 | 4/5          |  1.87 |                     0 |
| SPXW   | ret1                  | above dev median → calls, else puts |               55 |          6285   |      114.27 | 4/5          |  1.23 |                     0 |
| SPXW   | ret10                 | above dev median → calls, else puts |               55 |          5755   |      104.64 | 3/5          |  1.25 |                     0 |
| SPXW   | ret30                 | above dev median → calls, else puts |               55 |          5585   |      101.55 | 3/5          |  1.36 |                     0 |
| SPXW   | rsi                   | above dev median → calls, else puts |               55 |          5575   |      101.36 | 4/5          |  1.27 |                     0 |
| SPXW   | imb_put               | above dev median → calls, else puts |               55 |          3085   |       56.09 | 3/5          |  0.47 |                     0 |
| SPXW   | ema9_21               | above dev median → calls, else puts |               55 |          2965   |       53.91 | 3/5          |  0.75 |                     0 |
| SPXW   | dist_maxgamma         | above dev median → calls, else puts |               55 |          2325   |       42.27 | 3/5          |  0.46 |                     0 |
| SPXW   | dist_round            | above dev median → calls, else puts |               55 |          1855   |       33.73 | 3/5          |  0.36 |                     0 |
| SPY    | gex                   | above dev median → calls, else puts |               55 |          1254.5 |       22.81 | 4/5          |  2    |                     0 |
| SPY    | BASELINE always puts  | no signal (trend tilt)              |               55 |          1254.5 |       22.81 | 4/5          |  2    |                       |
| SPY    | atm_iv                | below dev median → calls, else puts |               55 |          1254.5 |       22.81 | 4/5          |  2    |                     0 |
| SPY    | vs_high               | above dev median → calls, else puts |               55 |           829.5 |       15.08 | 4/5          |  1.6  |                     0 |
| SPY    | vol15_put             | below dev median → calls, else puts |               55 |           815.5 |       14.83 | 4/5          |  2.85 |                     0 |
| SPY    | ret3                  | above dev median → calls, else puts |               55 |           628.5 |       11.43 | 3/5          |  0.93 |                     0 |
| SPXW   | imb_call              | above dev median → calls, else puts |               55 |           625   |       11.36 | 2/5          |  0.06 |                     0 |
| SPY    | pcr_oi                | below dev median → calls, else puts |               55 |           503.5 |        9.15 | 3/5          |  0.66 |                     0 |
| SPY    | imb_put               | below dev median → calls, else puts |               55 |           403.5 |        7.34 | 4/5          |  0.84 |                     0 |
| SPY    | ret1                  | above dev median → calls, else puts |               55 |           340.5 |        6.19 | 3/5          |  0.74 |                     0 |
| SPY    | bb_pctb               | above dev median → calls, else puts |               55 |           317.5 |        5.77 | 3/5          |  0.74 |                     0 |
| SPY    | iv_chg15              | below dev median → calls, else puts |               55 |           260.5 |        4.74 | 2/5          |  0.5  |                     0 |
| SPY    | ret10                 | above dev median → calls, else puts |               55 |           208.5 |        3.79 | 3/5          |  0.52 |                     0 |
| SPY    | dist_maxgamma         | below dev median → calls, else puts |               55 |            72.5 |        1.32 | 2/5          |  0.12 |                     0 |
| SPY    | rsi                   | above dev median → calls, else puts |               55 |            15.5 |        0.28 | 3/5          |  0.03 |                     0 |
| SPY    | ema9_21               | above dev median → calls, else puts |               55 |             9.5 |        0.17 | 3/5          |  0.02 |                     0 |
| SPY    | pcr_chg15             | below dev median → calls, else puts |               55 |           -22.5 |       -0.41 | 3/5          | -0.07 |                     0 |
| SPY    | ret5                  | above dev median → calls, else puts |               55 |           -89.5 |       -1.63 | 2/5          | -0.16 |                     0 |
| SPY    | ret30                 | above dev median → calls, else puts |               55 |           -99.5 |       -1.81 | 2/5          | -0.21 |                     0 |
| SPY    | dist_round            | below dev median → calls, else puts |               55 |          -125.5 |       -2.28 | 3/5          | -0.23 |                     0 |
| SPY    | imb_call              | below dev median → calls, else puts |               55 |          -592.5 |      -10.77 | 1/5          | -1.28 |                     0 |
| SPY    | macd_h                | below dev median → calls, else puts |               55 |          -657.5 |      -11.95 | 2/5          | -1.03 |                     0 |
| SPY    | min_since_high        | above dev median → calls, else puts |               55 |          -759.5 |      -13.81 | 2/5          | -0.91 |                     0 |
| SPY    | vs_low                | below dev median → calls, else puts |               55 |          -787.5 |      -14.32 | 2/5          | -1.24 |                     0 |
| SPY    | macd_slope            | above dev median → calls, else puts |               55 |          -807.5 |      -14.68 | 1/5          | -1.04 |                     0 |
| SPY    | atm_spread            | above dev median → calls, else puts |               55 |          -831.5 |      -15.12 | 3/5          | -0.89 |                     0 |
| SPY    | dist_maxoi            | below dev median → calls, else puts |               55 |          -852.5 |      -15.5  | 1/5          | -1.97 |                     0 |
| SPY    | weekday               | below dev median → calls, else puts |               55 |          -937.5 |      -17.05 | 1/5          | -2.2  |                     0 |
| SPY    | min_to_close          | above dev median → calls, else puts |               55 |         -1105.5 |      -20.1  | 1/5          | -1.82 |                     0 |
| SPY    | skew25                | above dev median → calls, else puts |               55 |         -1112.5 |      -20.23 | 1/5          | -1.6  |                     0 |
| SPY    | vol15_call            | above dev median → calls, else puts |               55 |         -1224.5 |      -22.26 | 2/5          | -1.27 |                     0 |
| SPY    | min_since_low         | below dev median → calls, else puts |               55 |         -1357.5 |      -24.68 | 0/5          | -2.72 |                     0 |
| SPY    | atm_spread_pct        | below dev median → calls, else puts |               55 |         -1365.5 |      -24.83 | 0/5          | -3.07 |                     0 |
| SPY    | vs_mean               | below dev median → calls, else puts |               55 |         -1397.5 |      -25.41 | 1/5          | -2.03 |                     0 |
| SPY    | vs_orl                | below dev median → calls, else puts |               55 |         -1523.5 |      -27.7  | 0/5          | -2.44 |                     0 |
| SPY    | rv30                  | above dev median → calls, else puts |               55 |         -1632.5 |      -29.68 | 0/5          | -2.62 |                     0 |
| SPY    | atm_gamma             | below dev median → calls, else puts |               55 |         -1718.5 |      -31.25 | 0/5          | -2.95 |                     0 |
| SPY    | theta_proxy           | above dev median → calls, else puts |               55 |         -1718.5 |      -31.25 | 0/5          | -2.95 |                     0 |
| SPY    | pcr_vol               | above dev median → calls, else puts |               55 |         -1719.5 |      -31.26 | 0/5          | -3.16 |                     0 |
| SPY    | vs_orh                | below dev median → calls, else puts |               55 |         -1745.5 |      -31.74 | 0/5          | -3.08 |                     0 |
| SPY    | vs_open               | below dev median → calls, else puts |               55 |         -1745.5 |      -31.74 | 0/5          | -3.08 |                     0 |
| SPY    | BASELINE always calls | no signal (trend tilt)              |               55 |         -1745.5 |      -31.74 | 0/5          | -3.08 |                       |
| SPXW   | macd_slope            | above dev median → calls, else puts |               55 |         -3135   |      -57    | 3/5          | -0.55 |                     0 |
| SPXW   | min_since_high        | above dev median → calls, else puts |               55 |         -3765   |      -68.45 | 3/5          | -0.39 |                     0 |
| SPXW   | weekday               | below dev median → calls, else puts |               55 |         -4105   |      -74.64 | 2/5          | -0.58 |                     0 |
| SPXW   | skew25                | above dev median → calls, else puts |               55 |         -4555   |      -82.82 | 2/5          | -0.63 |                     0 |
| SPXW   | min_to_close          | above dev median → calls, else puts |               55 |         -5265   |      -95.73 | 1/5          | -1.29 |                     0 |
| SPXW   | pcr_chg15             | above dev median → calls, else puts |               55 |         -5295   |      -96.27 | 2/5          | -0.7  |                     0 |
| SPXW   | vs_low                | below dev median → calls, else puts |               55 |         -5705   |     -103.73 | 2/5          | -0.8  |                     0 |
| SPXW   | macd_h                | below dev median → calls, else puts |               55 |         -6335   |     -115.18 | 2/5          | -1.03 |                     0 |
| SPXW   | atm_spread_pct        | below dev median → calls, else puts |               55 |        -10345   |     -188.09 | 1/5          | -1.43 |                     0 |
| SPXW   | atm_spread            | above dev median → calls, else puts |               55 |        -11045   |     -200.82 | 1/5          | -1.44 |                     0 |
| SPXW   | vs_mean               | below dev median → calls, else puts |               55 |        -11425   |     -207.73 | 2/5          | -1.55 |                     0 |
| SPXW   | min_since_low         | below dev median → calls, else puts |               55 |        -11525   |     -209.55 | 1/5          | -1.93 |                     0 |
| SPXW   | vs_orl                | below dev median → calls, else puts |               55 |        -12445   |     -226.27 | 1/5          | -1.84 |                     0 |
| SPXW   | vs_open               | below dev median → calls, else puts |               55 |        -14815   |     -269.36 | 1/5          | -2.33 |                     0 |
| SPXW   | vs_orh                | below dev median → calls, else puts |               55 |        -14815   |     -269.36 | 1/5          | -2.33 |                     0 |
| SPXW   | pcr_oi                | above dev median → calls, else puts |               55 |        -14815   |     -269.36 | 1/5          | -2.33 |                     0 |
| SPXW   | pcr_vol               | above dev median → calls, else puts |               55 |        -14815   |     -269.36 | 1/5          | -2.33 |                     0 |
| SPXW   | gex                   | below dev median → calls, else puts |               55 |        -14815   |     -269.36 | 1/5          | -2.33 |                     0 |
| SPXW   | BASELINE always calls | no signal (trend tilt)              |               55 |        -14815   |     -269.36 | 1/5          | -2.33 |                       |
| SPXW   | theta_proxy           | above dev median → calls, else puts |               55 |        -14995   |     -272.64 | 1/5          | -2.39 |                     0 |
| SPXW   | atm_gamma             | below dev median → calls, else puts |               55 |        -14995   |     -272.64 | 1/5          | -2.39 |                     0 |

## B. The algorithm (gradient-boosted trees on all variables, leave-one-day-out, real bid/ask, X2 exits)

All trades: {'trades': 216, 'total': np.float64(-11034.399999999998), 'per_trade': np.float64(-51.085185185185175), 'win': np.float64(0.2916666666666667), 'green': '6/18', 't': np.float64(-1.7139490478690744)}

Walk-away (stop after first winner): {'trades': 80, 'total': np.float64(-11494.2), 'per_trade': np.float64(-143.6775), 'win': np.float64(0.225), 'green': '7/18', 't': np.float64(-2.0333066148911185)}

By root: SPXW: {'trades': 108, 'total': np.float64(-10373.999999999998), 'per_trade': np.float64(-96.05555555555554), 'win': np.float64(0.26851851851851855), 'green': '3/9', 't': np.float64(-1.6958011013592538)}; SPY: {'trades': 108, 'total': np.float64(-660.3999999999999), 'per_trade': np.float64(-6.114814814814814), 'win': np.float64(0.3148148148148148), 'green': '3/9', 't': np.float64(-0.7794665314174877)}

Null (labels time-shifted, 20 runs): 95th percentile total $4,407; real total $-11,034 → **does NOT beat the null**.

## C. Variable importance (permutation, last 2 days held out)

|               |    SPXW |     SPY |   mean |
|:--------------|--------:|--------:|-------:|
| ret30         |  0.0238 |  0.0269 | 0.0253 |
| min_to_close  |  0.0149 |  0.0128 | 0.0138 |
| rv30          |  0.0144 |  0.0047 | 0.0095 |
| atm_gamma     |  0.0032 |  0.0148 | 0.009  |
| ema9_21       |  0.0082 |  0.0087 | 0.0084 |
| skew25        |  0.006  |  0.0062 | 0.0061 |
| dist_maxgamma |  0.0038 |  0.0057 | 0.0047 |
| gex           |  0.009  |  0.0002 | 0.0046 |
| prev_range    |  0.0109 | -0.002  | 0.0044 |
| vs_mean       | -0.0043 |  0.0131 | 0.0044 |
| min_since_low | -0.0027 |  0.01   | 0.0037 |
| vs_low        |  0.0044 |  0.0027 | 0.0036 |
| theta_proxy   |  0.0034 |  0.0035 | 0.0034 |
| dist_round    | -0.0024 |  0.0091 | 0.0034 |
| pcr_chg15     |  0.0099 | -0.0033 | 0.0033 |
| iv_chg15      |  0.0018 |  0.0023 | 0.0021 |
| ret5          |  0.0008 |  0.0021 | 0.0015 |
| rsi           |  0.0007 |  0.002  | 0.0013 |
| vs_orh        |  0.0007 |  0.0018 | 0.0012 |
| vs_orl        |  0.0027 | -0.0004 | 0.0012 |

Gaps: no event calendar (Fed/CPI/OPEX), no true volume-weighted VWAP (feed has option volume, not SPY share volume).

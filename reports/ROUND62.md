# Round 62: every-variable analysis of 0DTE trades (real recorded quotes)

Rules: [PROTOCOL_ROUND62.md](../PROTOCOL_ROUND62.md).
Recorded days: **9** (INTERIM: pass needs 20 days); snapshots analysed: 6,127; variables: 72.

## A. Which variables predict? (per-day Spearman IC vs a time-shift null)

Each IC is compared with a null built from the same day's target shifted in time (raw within-day ICs of level variables are biased). Bonferroni bar |z| ≥ 3.54 over 126 tests. Significant: **35**.

| variable      | target       |   mean_IC |   null_mean |   excess |   z_vs_null |   days | significant   |
|:--------------|:-------------|----------:|------------:|---------:|------------:|-------:|:--------------|
| vs_orh        | fwd30        |    -0.515 |       0.082 |   -0.597 |     -13.024 |     18 | True          |
| vs_orl        | fwd30        |    -0.515 |       0.088 |   -0.603 |     -12.223 |     18 | True          |
| vs_orl        | call−put P&L |    -0.488 |       0.102 |   -0.59  |     -12.198 |     18 | True          |
| vs_open       | call−put P&L |    -0.488 |       0.093 |   -0.581 |     -11.901 |     18 | True          |
| vs_orh        | call−put P&L |    -0.488 |       0.093 |   -0.581 |     -11.83  |     18 | True          |
| vix           | call−put P&L |     0.451 |      -0.074 |    0.524 |      11.679 |     18 | True          |
| vs_open       | fwd30        |    -0.515 |       0.088 |   -0.603 |     -10.716 |     18 | True          |
| pcr_oi        | fwd30        |     0.506 |      -0.074 |    0.581 |      10.275 |     18 | True          |
| dist_maxoi    | call−put P&L |    -0.43  |       0.098 |   -0.528 |     -10.161 |     18 | True          |
| gex           | call−put P&L |    -0.386 |       0.068 |   -0.454 |     -10.088 |     18 | True          |
| pcr_oi        | call−put P&L |     0.475 |      -0.098 |    0.573 |       9.716 |     18 | True          |
| vix           | fwd30        |     0.458 |      -0.055 |    0.514 |       9.621 |     18 | True          |
| dist_maxoi    | fwd30        |    -0.45  |       0.096 |   -0.545 |      -8.804 |     18 | True          |
| pcr_vol       | call−put P&L |     0.29  |      -0.067 |    0.358 |       8.49  |     18 | True          |
| pcr_vol       | fwd30        |     0.332 |      -0.086 |    0.417 |       8.356 |     18 | True          |
| gex           | fwd30        |    -0.39  |       0.044 |   -0.434 |      -8.347 |     18 | True          |
| vs_mean       | fwd30        |    -0.378 |       0.031 |   -0.41  |      -7.8   |     18 | True          |
| vs_low        | fwd30        |    -0.318 |       0.042 |   -0.361 |      -7.521 |     18 | True          |
| vs_high       | fwd30        |    -0.37  |       0.012 |   -0.382 |      -7.293 |     18 | True          |
| vs_vwap_true  | fwd30        |    -0.345 |       0.023 |   -0.368 |      -7.102 |     18 | True          |
| vs_vwap_true  | call−put P&L |    -0.29  |       0.015 |   -0.305 |      -6.705 |     18 | True          |
| vs_mean       | call−put P&L |    -0.299 |       0.032 |   -0.331 |      -6.664 |     18 | True          |
| vs_low        | call−put P&L |    -0.279 |       0.043 |   -0.322 |      -6.394 |     18 | True          |
| vs_high       | call−put P&L |    -0.308 |       0.023 |   -0.332 |      -6.064 |     18 | True          |
| atm_iv        | call−put P&L |     0.154 |      -0.063 |    0.217 |       5.255 |     18 | True          |
| macd_slope    | call−put P&L |     0.11  |       0.001 |    0.109 |       5.048 |     18 | True          |
| atm_iv        | fwd30        |     0.178 |      -0.053 |    0.231 |       4.924 |     18 | True          |
| tnx_chg30     | fwd30        |    -0.193 |       0.014 |   -0.207 |      -4.143 |     16 | True          |
| atm_gamma     | fwd30        |    -0.097 |       0.053 |   -0.149 |      -4.054 |     18 | True          |
| min_since_low | fwd30        |    -0.127 |       0.069 |   -0.196 |      -3.948 |     18 | True          |

## A2. Tradable test per variable (learn direction on the first half of the days, trade the second half every 30 min, real bid/ask)

This is the unbiased test. The table in A is descriptive only (its within-day ICs are inflated for level variables, see amendments).

Variables that beat the better of 'always puts' / 'always calls' on the same holdout: SPY 0, SPXW 0.

Variables profitable in holdout: SPY 22/69, SPXW 36/69. Profitable on BOTH roots: BASELINE always puts, atm_iv, bb_pctb, bdays_to_opex, days_since_fomc, days_to_fomc, dist_maxgamma, dxy_chg30, ema9_21, flow_call15, flow_net15, imb_put, iv_chg15, iwm_vs_spy15, ret1, ret10, ret3, rsi, vol15_put, vs_high.

| root   | variable              | rule                                |   holdout_trades |   holdout_total |   per_trade | green_days   |     t |   beats_best_baseline |
|:-------|:----------------------|:------------------------------------|-----------------:|----------------:|------------:|:-------------|------:|----------------------:|
| SPXW   | days_since_fomc       | below dev median → calls, else puts |               55 |         16465   |      299.36 | 4/5          |  2.28 |                     0 |
| SPXW   | atm_iv                | below dev median → calls, else puts |               55 |         16465   |      299.36 | 4/5          |  2.28 |                     0 |
| SPXW   | bdays_to_opex         | above dev median → calls, else puts |               55 |         16465   |      299.36 | 4/5          |  2.28 |                     0 |
| SPXW   | BASELINE always puts  | no signal (trend tilt)              |               55 |         16465   |      299.36 | 4/5          |  2.28 |                       |
| SPXW   | days_to_fomc          | above dev median → calls, else puts |               55 |         16465   |      299.36 | 4/5          |  2.28 |                     0 |
| SPXW   | rv30                  | below dev median → calls, else puts |               55 |         15835   |      287.91 | 4/5          |  2.34 |                     0 |
| SPXW   | vol15_put             | below dev median → calls, else puts |               55 |         12535   |      227.91 | 5/5          |  3.78 |                     0 |
| SPXW   | vs_high               | above dev median → calls, else puts |               55 |         10775   |      195.91 | 4/5          |  1.82 |                     0 |
| SPXW   | iv_chg15              | below dev median → calls, else puts |               55 |          9465   |      172.09 | 4/5          |  2.4  |                     0 |
| SPXW   | mega_ret5             | above dev median → calls, else puts |               55 |          8685   |      157.91 | 4/5          |  1.35 |                     0 |
| SPXW   | bb_pctb               | above dev median → calls, else puts |               55 |          8605   |      156.45 | 4/5          |  1.87 |                     0 |
| SPXW   | btc_ret30             | above dev median → calls, else puts |               55 |          8505   |      154.64 | 3/5          |  1.38 |                     0 |
| SPXW   | dist_maxoi            | above dev median → calls, else puts |               55 |          8145   |      148.09 | 3/5          |  0.87 |                     0 |
| SPXW   | iwm_vs_spy15          | below dev median → calls, else puts |               55 |          7595   |      138.09 | 3/5          |  1.04 |                     0 |
| SPXW   | ret3                  | above dev median → calls, else puts |               55 |          7495   |      136.27 | 4/5          |  1.23 |                     0 |
| SPXW   | ret5                  | above dev median → calls, else puts |               55 |          6705   |      121.91 | 3/5          |  1.34 |                     0 |
| SPXW   | vix_chg30             | below dev median → calls, else puts |               55 |          6555   |      119.18 | 3/5          |  1.39 |                     0 |
| SPXW   | vol15_call            | below dev median → calls, else puts |               55 |          6375   |      115.91 | 4/5          |  1.87 |                     0 |
| SPXW   | ret1                  | above dev median → calls, else puts |               55 |          6285   |      114.27 | 4/5          |  1.23 |                     0 |
| SPXW   | ret10                 | above dev median → calls, else puts |               55 |          5755   |      104.64 | 3/5          |  1.25 |                     0 |
| SPXW   | dxy_chg30             | below dev median → calls, else puts |               55 |          5595   |      101.73 | 4/5          |  0.82 |                     0 |
| SPXW   | ret30                 | above dev median → calls, else puts |               55 |          5585   |      101.55 | 3/5          |  1.36 |                     0 |
| SPXW   | rsi                   | above dev median → calls, else puts |               55 |          5575   |      101.36 | 4/5          |  1.27 |                     0 |
| SPXW   | flow_net15            | below dev median → calls, else puts |               55 |          4825   |       87.73 | 2/5          |  0.76 |                     0 |
| SPXW   | vix_chg5              | below dev median → calls, else puts |               55 |          4075   |       74.09 | 2/5          |  0.73 |                     0 |
| SPXW   | vix_chg15             | below dev median → calls, else puts |               55 |          3675   |       66.82 | 4/5          |  1.62 |                     0 |
| SPXW   | flow_call15           | above dev median → calls, else puts |               55 |          3525   |       64.09 | 3/5          |  0.47 |                     0 |
| SPXW   | qqq_vs_spy15          | above dev median → calls, else puts |               55 |          3245   |       59    | 4/5          |  0.84 |                     0 |
| SPXW   | aapl_ret15            | above dev median → calls, else puts |               55 |          3105   |       56.45 | 4/5          |  0.55 |                     0 |
| SPXW   | imb_put               | above dev median → calls, else puts |               55 |          3085   |       56.09 | 3/5          |  0.47 |                     0 |
| SPXW   | ema9_21               | above dev median → calls, else puts |               55 |          2965   |       53.91 | 3/5          |  0.75 |                     0 |
| SPXW   | dist_maxgamma         | above dev median → calls, else puts |               55 |          2325   |       42.27 | 3/5          |  0.46 |                     0 |
| SPXW   | dist_round            | above dev median → calls, else puts |               55 |          1855   |       33.73 | 3/5          |  0.36 |                     0 |
| SPXW   | flow_put15            | above dev median → calls, else puts |               55 |          1805   |       32.82 | 3/5          |  0.57 |                     0 |
| SPY    | days_since_fomc       | below dev median → calls, else puts |               55 |          1254.5 |       22.81 | 4/5          |  2    |                     0 |
| SPY    | days_to_fomc          | above dev median → calls, else puts |               55 |          1254.5 |       22.81 | 4/5          |  2    |                     0 |
| SPY    | atm_iv                | below dev median → calls, else puts |               55 |          1254.5 |       22.81 | 4/5          |  2    |                     0 |
| SPY    | gex                   | above dev median → calls, else puts |               55 |          1254.5 |       22.81 | 4/5          |  2    |                     0 |
| SPY    | BASELINE always puts  | no signal (trend tilt)              |               55 |          1254.5 |       22.81 | 4/5          |  2    |                       |
| SPY    | bdays_to_opex         | above dev median → calls, else puts |               55 |          1254.5 |       22.81 | 4/5          |  2    |                     0 |
| SPXW   | hyg_ret15             | above dev median → calls, else puts |               55 |          1235   |       22.45 | 4/5          |  0.4  |                     0 |
| SPY    | vs_high               | above dev median → calls, else puts |               55 |           829.5 |       15.08 | 4/5          |  1.6  |                     0 |
| SPY    | vol15_put             | below dev median → calls, else puts |               55 |           815.5 |       14.83 | 4/5          |  2.85 |                     0 |
| SPY    | ret3                  | above dev median → calls, else puts |               55 |           628.5 |       11.43 | 3/5          |  0.93 |                     0 |
| SPXW   | imb_call              | above dev median → calls, else puts |               55 |           625   |       11.36 | 2/5          |  0.06 |                     0 |
| SPY    | pcr_oi                | below dev median → calls, else puts |               55 |           503.5 |        9.15 | 3/5          |  0.66 |                     0 |
| SPY    | imb_put               | below dev median → calls, else puts |               55 |           403.5 |        7.34 | 4/5          |  0.84 |                     0 |
| SPY    | flow_call15           | above dev median → calls, else puts |               55 |           384.5 |        6.99 | 3/5          |  1.04 |                     0 |
| SPY    | ret1                  | above dev median → calls, else puts |               55 |           340.5 |        6.19 | 3/5          |  0.74 |                     0 |
| SPY    | dxy_chg30             | below dev median → calls, else puts |               55 |           327.5 |        5.95 | 3/5          |  0.49 |                     0 |
| SPY    | bb_pctb               | above dev median → calls, else puts |               55 |           317.5 |        5.77 | 3/5          |  0.74 |                     0 |
| SPY    | iwm_vs_spy15          | below dev median → calls, else puts |               55 |           309.5 |        5.63 | 2/5          |  0.43 |                     0 |
| SPY    | iv_chg15              | below dev median → calls, else puts |               55 |           260.5 |        4.74 | 2/5          |  0.5  |                     0 |
| SPY    | ret10                 | above dev median → calls, else puts |               55 |           208.5 |        3.79 | 3/5          |  0.52 |                     0 |
| SPY    | dist_maxgamma         | below dev median → calls, else puts |               55 |            72.5 |        1.32 | 2/5          |  0.12 |                     0 |
| SPY    | flow_net15            | above dev median → calls, else puts |               55 |            22.5 |        0.41 | 2/5          |  0.05 |                     0 |
| SPY    | rsi                   | above dev median → calls, else puts |               55 |            15.5 |        0.28 | 3/5          |  0.03 |                     0 |
| SPY    | ema9_21               | above dev median → calls, else puts |               55 |             9.5 |        0.17 | 3/5          |  0.02 |                     0 |
| SPY    | pcr_chg15             | below dev median → calls, else puts |               55 |           -22.5 |       -0.41 | 3/5          | -0.07 |                     0 |
| SPXW   | tlt_ret15             | above dev median → calls, else puts |               55 |           -35   |       -0.64 | 2/5          | -0.01 |                     0 |
| SPY    | vix_chg5              | below dev median → calls, else puts |               55 |           -87.5 |       -1.59 | 2/5          | -0.18 |                     0 |
| SPY    | ret5                  | above dev median → calls, else puts |               55 |           -89.5 |       -1.63 | 2/5          | -0.16 |                     0 |
| SPY    | vix_chg15             | below dev median → calls, else puts |               55 |           -89.5 |       -1.63 | 3/5          | -0.27 |                     0 |
| SPY    | ret30                 | above dev median → calls, else puts |               55 |           -99.5 |       -1.81 | 2/5          | -0.21 |                     0 |
| SPY    | mega_ret30            | below dev median → calls, else puts |               50 |          -119   |       -2.38 | 2/5          | -0.14 |                     0 |
| SPY    | dist_round            | below dev median → calls, else puts |               55 |          -125.5 |       -2.28 | 3/5          | -0.23 |                     0 |
| SPY    | msft_ret15            | above dev median → calls, else puts |               55 |          -142.5 |       -2.59 | 3/5          | -0.32 |                     0 |
| SPY    | qqq_vs_spy15          | above dev median → calls, else puts |               55 |          -225.5 |       -4.1  | 3/5          | -0.67 |                     0 |
| SPY    | nvda_ret15            | below dev median → calls, else puts |               55 |          -228.5 |       -4.15 | 3/5          | -0.31 |                     0 |
| SPY    | hyg_ret15             | above dev median → calls, else puts |               55 |          -231.5 |       -4.21 | 3/5          | -0.56 |                     0 |
| SPXW   | msft_ret15            | below dev median → calls, else puts |               55 |          -235   |       -4.27 | 2/5          | -0.05 |                     0 |
| SPY    | aapl_ret15            | above dev median → calls, else puts |               55 |          -280.5 |       -5.1  | 3/5          | -0.62 |                     0 |
| SPY    | mega_lead15           | below dev median → calls, else puts |               55 |          -317.5 |       -5.77 | 2/5          | -0.65 |                     0 |
| SPY    | tnx_chg30             | below dev median → calls, else puts |               55 |          -410.5 |       -7.46 | 3/5          | -0.73 |                     0 |
| SPY    | tlt_ret15             | above dev median → calls, else puts |               55 |          -523.5 |       -9.52 | 2/5          | -0.88 |                     0 |
| SPY    | spy_vol_rel15         | above dev median → calls, else puts |               55 |          -529.5 |       -9.63 | 2/5          | -0.66 |                     0 |
| SPY    | mega_breadth15        | below dev median → calls, else puts |               55 |          -579.5 |      -10.54 | 1/5          | -1.09 |                     0 |
| SPY    | imb_call              | below dev median → calls, else puts |               55 |          -592.5 |      -10.77 | 1/5          | -1.28 |                     0 |
| SPY    | macd_h                | below dev median → calls, else puts |               55 |          -657.5 |      -11.95 | 2/5          | -1.03 |                     0 |
| SPY    | vix_chg30             | above dev median → calls, else puts |               55 |          -669.5 |      -12.17 | 1/5          | -1.06 |                     0 |
| SPXW   | mega_ret30            | below dev median → calls, else puts |               50 |          -670   |      -13.4  | 2/5          | -0.08 |                     0 |
| SPY    | mega_ret5             | below dev median → calls, else puts |               55 |          -672.5 |      -12.23 | 1/5          | -1.33 |                     0 |
| SPY    | mega_ret15            | below dev median → calls, else puts |               55 |          -708.5 |      -12.88 | 1/5          | -1.28 |                     0 |
| SPY    | min_since_high        | above dev median → calls, else puts |               55 |          -759.5 |      -13.81 | 2/5          | -0.91 |                     0 |
| SPY    | vs_low                | below dev median → calls, else puts |               55 |          -787.5 |      -14.32 | 2/5          | -1.24 |                     0 |
| SPY    | macd_slope            | above dev median → calls, else puts |               55 |          -807.5 |      -14.68 | 1/5          | -1.04 |                     0 |
| SPY    | atm_spread            | above dev median → calls, else puts |               55 |          -831.5 |      -15.12 | 3/5          | -0.89 |                     0 |
| SPY    | btc_ret30             | below dev median → calls, else puts |               55 |          -849.5 |      -15.45 | 2/5          | -1.15 |                     0 |
| SPY    | dist_maxoi            | below dev median → calls, else puts |               55 |          -852.5 |      -15.5  | 1/5          | -1.97 |                     0 |
| SPY    | weekday               | below dev median → calls, else puts |               55 |          -937.5 |      -17.05 | 1/5          | -2.2  |                     0 |
| SPY    | tsla_ret15            | below dev median → calls, else puts |               55 |         -1065.5 |      -19.37 | 0/5          | -3.39 |                     0 |
| SPY    | min_to_close          | above dev median → calls, else puts |               55 |         -1105.5 |      -20.1  | 1/5          | -1.82 |                     0 |
| SPY    | skew25                | above dev median → calls, else puts |               55 |         -1112.5 |      -20.23 | 1/5          | -1.6  |                     0 |
| SPXW   | mega_lead15           | below dev median → calls, else puts |               55 |         -1175   |      -21.36 | 2/5          | -0.19 |                     0 |
| SPY    | vol15_call            | above dev median → calls, else puts |               55 |         -1224.5 |      -22.26 | 2/5          | -1.27 |                     0 |
| SPY    | flow_put15            | above dev median → calls, else puts |               55 |         -1266.5 |      -23.03 | 2/5          | -1.6  |                     0 |
| SPY    | min_since_low         | below dev median → calls, else puts |               55 |         -1357.5 |      -24.68 | 0/5          | -2.72 |                     0 |
| SPY    | vs_vwap_true          | below dev median → calls, else puts |               55 |         -1364.5 |      -24.81 | 1/5          | -1.84 |                     0 |
| SPY    | atm_spread_pct        | below dev median → calls, else puts |               55 |         -1365.5 |      -24.83 | 0/5          | -3.07 |                     0 |
| SPY    | vs_mean               | below dev median → calls, else puts |               55 |         -1397.5 |      -25.41 | 1/5          | -2.03 |                     0 |
| SPY    | vs_orl                | below dev median → calls, else puts |               55 |         -1523.5 |      -27.7  | 0/5          | -2.44 |                     0 |
| SPY    | rv30                  | above dev median → calls, else puts |               55 |         -1632.5 |      -29.68 | 0/5          | -2.62 |                     0 |
| SPY    | theta_proxy           | above dev median → calls, else puts |               55 |         -1718.5 |      -31.25 | 0/5          | -2.95 |                     0 |
| SPY    | atm_gamma             | below dev median → calls, else puts |               55 |         -1718.5 |      -31.25 | 0/5          | -2.95 |                     0 |
| SPY    | pcr_vol               | above dev median → calls, else puts |               55 |         -1719.5 |      -31.26 | 0/5          | -3.16 |                     0 |
| SPY    | vix                   | above dev median → calls, else puts |               55 |         -1745.5 |      -31.74 | 0/5          | -3.08 |                     0 |
| SPY    | vs_orh                | below dev median → calls, else puts |               55 |         -1745.5 |      -31.74 | 0/5          | -3.08 |                     0 |
| SPY    | vs_open               | below dev median → calls, else puts |               55 |         -1745.5 |      -31.74 | 0/5          | -3.08 |                     0 |
| SPY    | BASELINE always calls | no signal (trend tilt)              |               55 |         -1745.5 |      -31.74 | 0/5          | -3.08 |                       |
| SPXW   | spy_vol_rel15         | above dev median → calls, else puts |               55 |         -2135   |      -38.82 | 2/5          | -0.28 |                     0 |
| SPXW   | nvda_ret15            | below dev median → calls, else puts |               55 |         -2295   |      -41.73 | 3/5          | -0.29 |                     0 |
| SPXW   | tnx_chg30             | below dev median → calls, else puts |               55 |         -2505   |      -45.55 | 3/5          | -0.38 |                     0 |
| SPXW   | macd_slope            | above dev median → calls, else puts |               55 |         -3135   |      -57    | 3/5          | -0.55 |                     0 |
| SPXW   | mega_breadth15        | below dev median → calls, else puts |               55 |         -3635   |      -66.09 | 2/5          | -0.58 |                     0 |
| SPXW   | min_since_high        | above dev median → calls, else puts |               55 |         -3765   |      -68.45 | 3/5          | -0.39 |                     0 |
| SPXW   | weekday               | below dev median → calls, else puts |               55 |         -4105   |      -74.64 | 2/5          | -0.58 |                     0 |
| SPXW   | mega_ret15            | below dev median → calls, else puts |               55 |         -4355   |      -79.18 | 2/5          | -0.68 |                     0 |
| SPXW   | skew25                | above dev median → calls, else puts |               55 |         -4555   |      -82.82 | 2/5          | -0.63 |                     0 |
| SPXW   | min_to_close          | above dev median → calls, else puts |               55 |         -5265   |      -95.73 | 1/5          | -1.29 |                     0 |
| SPXW   | pcr_chg15             | above dev median → calls, else puts |               55 |         -5295   |      -96.27 | 2/5          | -0.7  |                     0 |
| SPXW   | vs_low                | below dev median → calls, else puts |               55 |         -5705   |     -103.73 | 2/5          | -0.8  |                     0 |
| SPXW   | macd_h                | below dev median → calls, else puts |               55 |         -6335   |     -115.18 | 2/5          | -1.03 |                     0 |
| SPXW   | tsla_ret15            | below dev median → calls, else puts |               55 |         -7815   |     -142.09 | 1/5          | -1.66 |                     0 |
| SPXW   | atm_spread_pct        | below dev median → calls, else puts |               55 |        -10345   |     -188.09 | 1/5          | -1.43 |                     0 |
| SPXW   | vs_vwap_true          | below dev median → calls, else puts |               55 |        -10515   |     -191.18 | 1/5          | -1.22 |                     0 |
| SPXW   | atm_spread            | above dev median → calls, else puts |               55 |        -11045   |     -200.82 | 1/5          | -1.44 |                     0 |
| SPXW   | vs_mean               | below dev median → calls, else puts |               55 |        -11425   |     -207.73 | 2/5          | -1.55 |                     0 |
| SPXW   | min_since_low         | below dev median → calls, else puts |               55 |        -11525   |     -209.55 | 1/5          | -1.93 |                     0 |
| SPXW   | vs_orl                | below dev median → calls, else puts |               55 |        -12445   |     -226.27 | 1/5          | -1.84 |                     0 |
| SPXW   | vs_open               | below dev median → calls, else puts |               55 |        -14815   |     -269.36 | 1/5          | -2.33 |                     0 |
| SPXW   | vs_orh                | below dev median → calls, else puts |               55 |        -14815   |     -269.36 | 1/5          | -2.33 |                     0 |
| SPXW   | vix                   | above dev median → calls, else puts |               55 |        -14815   |     -269.36 | 1/5          | -2.33 |                     0 |
| SPXW   | BASELINE always calls | no signal (trend tilt)              |               55 |        -14815   |     -269.36 | 1/5          | -2.33 |                       |
| SPXW   | pcr_vol               | above dev median → calls, else puts |               55 |        -14815   |     -269.36 | 1/5          | -2.33 |                     0 |
| SPXW   | gex                   | below dev median → calls, else puts |               55 |        -14815   |     -269.36 | 1/5          | -2.33 |                     0 |
| SPXW   | pcr_oi                | above dev median → calls, else puts |               55 |        -14815   |     -269.36 | 1/5          | -2.33 |                     0 |
| SPXW   | atm_gamma             | below dev median → calls, else puts |               55 |        -14995   |     -272.64 | 1/5          | -2.39 |                     0 |
| SPXW   | theta_proxy           | above dev median → calls, else puts |               55 |        -14995   |     -272.64 | 1/5          | -2.39 |                     0 |

## B. The algorithm (gradient-boosted trees on all variables, leave-one-day-out, real bid/ask, X2 exits)

All trades: {'trades': 216, 'total': np.float64(-3397.399999999995), 'per_trade': np.float64(-15.728703703703681), 'win': np.float64(0.3055555555555556), 'green': '7/18', 't': np.float64(-0.45740473531222253)}

Walk-away (stop after first winner): {'trades': 65, 'total': np.float64(-3470.1000000000004), 'per_trade': np.float64(-53.38615384615385), 'win': np.float64(0.27692307692307694), 'green': '10/18', 't': np.float64(-0.6386336433511469)}

By root: SPXW: {'trades': 108, 'total': np.float64(-3123.9999999999964), 'per_trade': np.float64(-28.925925925925892), 'win': np.float64(0.28703703703703703), 'green': '3/9', 't': np.float64(-0.4119963251456899)}; SPY: {'trades': 108, 'total': np.float64(-273.4), 'per_trade': np.float64(-2.531481481481481), 'win': np.float64(0.32407407407407407), 'green': '4/9', 't': np.float64(-0.349172564792563)}

Null (labels time-shifted, 20 runs): 95th percentile total $8,699; real total $-3,397 → **does NOT beat the null**.

## B2. Every instrument × selectivity × walk-away (model out-of-fold, leave-one-day-out) vs no-model baselines

Instruments: options (calls/puts), calls only, puts only, shares long/short, shares long only, straddles (buy when a big move is predicted, sell when quiet). Selectivity: every 30-min slot, ≥60% confident, ≥70% confident. Walk-away = stop after the first winning trade of the day.

| policy                                             | selectivity           | walk_away   | root   |   trades |   total |   win | green   |     t |
|:---------------------------------------------------|:----------------------|:------------|:-------|---------:|--------:|------:|:--------|------:|
| BASELINE always put                                | every 30-min slot     | False       | SPXW   |      108 |   15501 |  0.44 | 5/9     |  1.47 |
| BASELINE always shares_short                       | every 30-min slot     | False       | SPXW   |      108 |    4460 |  0.5  | 7/9     |  1.51 |
| BASELINE always shares_short                       | every 30-min slot     | False       | SPY    |      108 |    4151 |  0.5  | 6/9     |  1.37 |
| options: puts only (short only)                    | very confident (≥70%) | False       | SPXW   |       62 |    3284 |  0.37 | 5/9     |  0.46 |
| straddles: buy if big move expected, sell if quiet | confident (≥60%)      | False       | SPXW   |      108 |    1987 |  0.42 | 3/9     |  0.34 |
| straddles: buy if big move expected, sell if quiet | every 30-min slot     | False       | SPXW   |      108 |    1692 |  0.43 | 5/9     |  0.23 |
| straddles: buy if big move expected, sell if quiet | every 30-min slot     | True        | SPXW   |       20 |    1640 |  0.45 | 4/9     |  0.4  |
| straddles: buy if big move expected, sell if quiet | confident (≥60%)      | True        | SPXW   |       20 |    1350 |  0.45 | 4/9     |  0.35 |
| options: puts only (short only)                    | every 30-min slot     | True        | SPXW   |       31 |    1347 |  0.29 | 6/9     |  0.26 |
| BASELINE always put                                | every 30-min slot     | False       | SPY    |      108 |    1150 |  0.4  | 5/9     |  1.18 |
| options: puts only (short only)                    | every 30-min slot     | False       | SPXW   |       77 |     959 |  0.32 | 5/9     |  0.13 |
| straddles: buy if big move expected, sell if quiet | very confident (≥70%) | True        | SPXW   |       20 |     730 |  0.45 | 4/9     |  0.17 |
| shares: long up / short down                       | every 30-min slot     | True        | SPXW   |       20 |     541 |  0.45 | 6/9     |  0.43 |
| options: calls only (long only)                    | every 30-min slot     | True        | SPY    |       11 |     499 |  0.64 | 6/7     |  3.54 |
| options: puts only (short only)                    | confident (≥60%)      | False       | SPY    |       72 |     338 |  0.35 | 5/9     |  0.46 |
| options: puts only (short only)                    | every 30-min slot     | False       | SPY    |       78 |     338 |  0.33 | 5/9     |  0.39 |
| options: calls up / puts down                      | every 30-min slot     | False       | SPY    |      108 |     301 |  0.36 | 4/9     |  0.32 |
| shares: long up / short down                       | very confident (≥70%) | True        | SPY    |       21 |     188 |  0.43 | 7/9     |  0.14 |
| shares: long up / short down                       | very confident (≥70%) | True        | SPXW   |       32 |     178 |  0.28 | 6/9     |  0.15 |
| options: calls only (long only)                    | every 30-min slot     | False       | SPY    |       55 |     163 |  0.38 | 5/7     |  0.76 |
| options: puts only (short only)                    | every 30-min slot     | True        | SPY    |       28 |     141 |  0.32 | 6/9     |  0.3  |
| options: calls up / puts down                      | very confident (≥70%) | True        | SPY    |       24 |     120 |  0.38 | 6/9     |  0.3  |
| shares: long only                                  | confident (≥60%)      | True        | SPXW   |       14 |     120 |  0.5  | 4/8     |  0.14 |
| options: calls only (long only)                    | confident (≥60%)      | True        | SPY    |       14 |      96 |  0.43 | 5/7     |  0.22 |
| shares: long up / short down                       | confident (≥60%)      | True        | SPY    |       21 |      81 |  0.43 | 7/9     |  0.06 |
| options: puts only (short only)                    | confident (≥60%)      | True        | SPY    |       28 |      62 |  0.29 | 5/9     |  0.13 |
| options: calls up / puts down                      | confident (≥60%)      | True        | SPY    |       27 |       4 |  0.33 | 6/9     |  0.01 |
| shares: long only                                  | very confident (≥70%) | True        | SPXW   |       13 |      -6 |  0.38 | 3/6     | -0.01 |
| shares: long up / short down                       | confident (≥60%)      | True        | SPXW   |       24 |     -45 |  0.38 | 6/9     | -0.04 |
| options: calls up / puts down                      | very confident (≥70%) | False       | SPXW   |      100 |     -50 |  0.33 | 4/9     | -0.01 |
| options: calls only (long only)                    | confident (≥60%)      | False       | SPY    |       51 |    -160 |  0.31 | 4/7     | -0.33 |
| options: puts only (short only)                    | very confident (≥70%) | True        | SPY    |       25 |    -180 |  0.28 | 5/9     | -0.43 |
| options: calls up / puts down                      | every 30-min slot     | True        | SPY    |       29 |    -209 |  0.31 | 5/9     | -0.41 |
| straddles: buy if big move expected, sell if quiet | every 30-min slot     | True        | SPY    |       24 |    -239 |  0.38 | 4/9     | -0.58 |
| options: calls up / puts down                      | confident (≥60%)      | False       | SPY    |      108 |    -273 |  0.32 | 4/9     | -0.35 |
| shares: long up / short down                       | every 30-min slot     | True        | SPY    |       21 |    -333 |  0.43 | 6/9     | -0.26 |
| straddles: buy if big move expected, sell if quiet | confident (≥60%)      | True        | SPY    |       28 |    -345 |  0.32 | 4/9     | -0.77 |
| shares: long only                                  | every 30-min slot     | True        | SPXW   |       14 |    -366 |  0.5  | 4/8     | -0.36 |
| BASELINE always straddle                           | every 30-min slot     | False       | SPY    |      108 |    -374 |  0.31 | 4/9     | -0.63 |
| options: puts only (short only)                    | very confident (≥70%) | False       | SPY    |       63 |    -401 |  0.3  | 3/9     | -0.85 |
| options: puts only (short only)                    | very confident (≥70%) | True        | SPXW   |       30 |    -450 |  0.27 | 5/9     | -0.09 |
| straddles: buy if big move expected, sell if quiet | very confident (≥70%) | True        | SPY    |       30 |    -456 |  0.27 | 4/9     | -0.93 |
| shares: long only                                  | confident (≥60%)      | True        | SPY    |       12 |    -602 |  0.58 | 4/7     | -0.58 |
| options: calls only (long only)                    | very confident (≥70%) | True        | SPY    |       30 |    -672 |  0.13 | 3/7     | -1.4  |
| shares: long only                                  | every 30-min slot     | True        | SPY    |       10 |    -743 |  0.7  | 4/7     | -0.68 |
| shares: long up / short down                       | confident (≥60%)      | False       | SPXW   |      107 |    -862 |  0.42 | 2/9     | -0.34 |
| BASELINE always short_straddle                     | every 30-min slot     | False       | SPY    |      108 |    -873 |  0.61 | 4/9     | -1.12 |
| straddles: buy if big move expected, sell if quiet | every 30-min slot     | False       | SPY    |      108 |    -934 |  0.39 | 2/9     | -2.94 |
| straddles: buy if big move expected, sell if quiet | very confident (≥70%) | False       | SPXW   |       96 |   -1006 |  0.41 | 4/9     | -0.12 |
| straddles: buy if big move expected, sell if quiet | very confident (≥70%) | False       | SPY    |       97 |   -1044 |  0.26 | 2/9     | -1.39 |
| straddles: buy if big move expected, sell if quiet | confident (≥60%)      | False       | SPY    |      106 |   -1052 |  0.35 | 2/9     | -1.93 |
| options: calls up / puts down                      | very confident (≥70%) | False       | SPY    |      105 |   -1087 |  0.29 | 3/9     | -1.38 |
| options: calls only (long only)                    | very confident (≥70%) | False       | SPY    |       47 |   -1241 |  0.17 | 2/7     | -2.19 |
| shares: long up / short down                       | every 30-min slot     | False       | SPY    |      108 |   -1306 |  0.46 | 2/9     | -0.51 |
| shares: long only                                  | very confident (≥70%) | True        | SPY    |       17 |   -1372 |  0.41 | 3/7     | -1.52 |
| shares: long up / short down                       | every 30-min slot     | False       | SPXW   |      108 |   -1414 |  0.46 | 2/9     | -0.67 |
| shares: long up / short down                       | very confident (≥70%) | False       | SPY    |      104 |   -1725 |  0.42 | 2/9     | -0.55 |
| shares: long up / short down                       | very confident (≥70%) | False       | SPXW   |      100 |   -1946 |  0.38 | 2/9     | -1.54 |
| BASELINE always call                               | every 30-min slot     | False       | SPY    |      108 |   -2018 |  0.27 | 1/9     | -1.94 |
| shares: long up / short down                       | confident (≥60%)      | False       | SPY    |      108 |   -2267 |  0.41 | 1/9     | -0.74 |
| shares: long only                                  | every 30-min slot     | False       | SPXW   |       63 |   -2577 |  0.49 | 2/8     | -1.72 |
| options: calls up / puts down                      | every 30-min slot     | True        | SPXW   |       33 |   -2639 |  0.27 | 4/9     | -0.5  |
| options: puts only (short only)                    | confident (≥60%)      | False       | SPXW   |       68 |   -2654 |  0.25 | 4/9     | -0.32 |
| shares: long only                                  | very confident (≥70%) | False       | SPXW   |       49 |   -2671 |  0.29 | 0/6     | -2.33 |
| options: calls up / puts down                      | every 30-min slot     | False       | SPXW   |      108 |   -2714 |  0.31 | 4/9     | -0.3  |
| shares: long only                                  | confident (≥60%)      | False       | SPXW   |       57 |   -2789 |  0.39 | 2/8     | -2.1  |
| options: calls up / puts down                      | confident (≥60%)      | False       | SPXW   |      108 |   -3124 |  0.29 | 3/9     | -0.41 |
| shares: long only                                  | every 30-min slot     | False       | SPY    |       55 |   -3197 |  0.44 | 2/7     | -2.07 |
| shares: long only                                  | very confident (≥70%) | False       | SPY    |       46 |   -3341 |  0.35 | 2/7     | -2.46 |
| shares: long only                                  | confident (≥60%)      | False       | SPY    |       51 |   -3382 |  0.37 | 1/7     | -2.41 |
| options: calls up / puts down                      | confident (≥60%)      | True        | SPXW   |       38 |   -3474 |  0.24 | 4/9     | -0.63 |
| options: calls up / puts down                      | very confident (≥70%) | True        | SPXW   |       38 |   -3834 |  0.21 | 5/9     | -0.58 |
| options: puts only (short only)                    | confident (≥60%)      | True        | SPXW   |       36 |   -4238 |  0.19 | 4/9     | -0.77 |
| BASELINE always shares_long                        | every 30-min slot     | False       | SPXW   |      108 |   -4504 |  0.5  | 2/9     | -1.52 |
| BASELINE always shares_long                        | every 30-min slot     | False       | SPY    |      108 |   -4583 |  0.49 | 2/9     | -1.51 |
| BASELINE always straddle                           | every 30-min slot     | False       | SPXW   |      108 |   -4598 |  0.3  | 3/9     | -0.81 |
| options: calls only (long only)                    | very confident (≥70%) | True        | SPXW   |       21 |   -6223 |  0.19 | 3/6     | -0.9  |
| BASELINE always short_straddle                     | every 30-min slot     | False       | SPXW   |      108 |   -6798 |  0.65 | 4/9     | -0.84 |
| options: calls only (long only)                    | confident (≥60%)      | True        | SPXW   |       29 |   -9157 |  0.21 | 3/8     | -1.33 |
| options: calls only (long only)                    | every 30-min slot     | True        | SPXW   |       31 |  -10043 |  0.19 | 3/8     | -1.5  |
| options: calls only (long only)                    | very confident (≥70%) | False       | SPXW   |       49 |  -10937 |  0.2  | 1/6     | -1.76 |
| options: calls only (long only)                    | confident (≥60%)      | False       | SPXW   |       57 |  -13201 |  0.21 | 1/8     | -2.22 |
| options: calls only (long only)                    | every 30-min slot     | False       | SPXW   |       63 |  -13229 |  0.22 | 2/8     | -1.87 |
| BASELINE always call                               | every 30-min slot     | False       | SPXW   |      108 |  -15804 |  0.26 | 2/9     | -1.61 |

## B3. Strike (ATM / OTM 30-delta / ITM 70-delta) × exit (X1 +25/−15/10m, X2 +50/−25/30m, X3 hold to 15:45), 5-minute grid

| strike   | exit   | root   | policy                |   trades |   total | green   |     t |
|:---------|:-------|:-------|:----------------------|---------:|--------:|:--------|------:|
| ITM      | X3     | SPXW   | BASELINE always puts  |       63 |   69771 | 4/9     |  1.03 |
| ATM      | X3     | SPXW   | BASELINE always puts  |       63 |   53986 | 4/9     |  0.95 |
| OTM      | X3     | SPXW   | BASELINE always puts  |       63 |   35416 | 4/9     |  0.88 |
| ITM      | X2     | SPXW   | BASELINE always puts  |      108 |   27696 | 5/9     |  1.32 |
| ITM      | X3     | SPXW   | model ≥60%            |        9 |   20483 | 3/9     |  0.89 |
| ATM      | X3     | SPXW   | model ≥60%            |        9 |   18208 | 3/9     |  0.87 |
| OTM      | X3     | SPXW   | model ≥60%            |        9 |   17463 | 3/9     |  1.04 |
| ATM      | X2     | SPXW   | BASELINE always puts  |      108 |   16591 | 6/9     |  1.6  |
| ITM      | X3     | SPY    | BASELINE always puts  |       63 |    6970 | 4/9     |  1.02 |
| OTM      | X2     | SPXW   | BASELINE always puts  |      108 |    6946 | 6/9     |  1.22 |
| ATM      | X3     | SPY    | BASELINE always puts  |       63 |    5157 | 4/9     |  0.92 |
| OTM      | X3     | SPY    | BASELINE always puts  |       63 |    3333 | 4/9     |  0.83 |
| ITM      | X2     | SPY    | BASELINE always puts  |      108 |    3127 | 6/9     |  1.54 |
| ITM      | X1     | SPXW   | BASELINE always puts  |      313 |    2661 | 4/9     |  0.14 |
| ITM      | X3     | SPY    | model ≥60%            |        9 |    1835 | 3/9     |  0.76 |
| ATM      | X3     | SPY    | model ≥60%            |        9 |    1795 | 3/9     |  0.86 |
| OTM      | X3     | SPY    | model ≥60%            |        9 |    1674 | 3/9     |  1.01 |
| ATM      | X2     | SPY    | BASELINE always puts  |      108 |    1150 | 5/9     |  1.18 |
| OTM      | X2     | SPY    | BASELINE always puts  |      108 |     777 | 6/9     |  1.59 |
| ITM      | X1     | SPY    | BASELINE always puts  |      315 |      -4 | 4/9     | -0    |
| ATM      | X1     | SPY    | BASELINE always puts  |      315 |    -122 | 3/9     | -0.12 |
| OTM      | X1     | SPY    | BASELINE always puts  |      315 |    -489 | 3/9     | -0.94 |
| OTM      | X2     | SPY    | model ≥60%            |      102 |    -628 | 2/9     | -1.75 |
| ATM      | X2     | SPY    | model ≥60%            |      102 |    -807 | 2/9     | -1.04 |
| OTM      | X1     | SPY    | BASELINE always calls |      315 |    -996 | 3/9     | -1.77 |
| ITM      | X2     | SPY    | model ≥60%            |      102 |   -1043 | 3/9     | -0.74 |
| OTM      | X2     | SPY    | BASELINE always calls |      108 |   -1126 | 1/9     | -2.26 |
| OTM      | X1     | SPY    | model ≥60%            |      280 |   -1317 | 0/9     | -4.95 |
| ATM      | X1     | SPY    | BASELINE always calls |      315 |   -1862 | 3/9     | -1.66 |
| ATM      | X2     | SPY    | BASELINE always calls |      108 |   -2016 | 1/9     | -1.94 |
| OTM      | X1     | SPXW   | BASELINE always puts  |      313 |   -2019 | 4/9     | -0.42 |
| OTM      | X3     | SPY    | BASELINE always calls |       63 |   -2277 | 2/9     | -1.53 |
| ATM      | X1     | SPY    | model ≥60%            |      280 |   -2304 | 1/9     | -4.31 |
| ITM      | X2     | SPY    | BASELINE always calls |      108 |   -2559 | 2/9     | -1.5  |
| ITM      | X1     | SPY    | model ≥60%            |      280 |   -2770 | 0/9     | -4.06 |
| ITM      | X1     | SPY    | BASELINE always calls |      315 |   -3022 | 3/9     | -1.64 |
| ATM      | X3     | SPY    | BASELINE always calls |       63 |   -4170 | 3/9     | -1.45 |
| ATM      | X1     | SPXW   | BASELINE always puts  |      313 |   -4859 | 3/9     | -0.64 |
| OTM      | X2     | SPXW   | model ≥60%            |      101 |   -6053 | 1/9     | -1.39 |
| ITM      | X3     | SPY    | BASELINE always calls |       63 |   -6089 | 3/9     | -1.39 |
| OTM      | X1     | SPXW   | model ≥60%            |      277 |  -10181 | 2/9     | -2.76 |
| ATM      | X2     | SPXW   | model ≥60%            |      101 |  -10833 | 2/9     | -1.33 |
| OTM      | X1     | SPXW   | BASELINE always calls |      313 |  -11054 | 2/9     | -2.2  |
| OTM      | X2     | SPXW   | BASELINE always calls |      108 |  -12969 | 1/9     | -3.03 |
| ATM      | X2     | SPXW   | BASELINE always calls |      108 |  -16334 | 2/9     | -1.66 |
| ATM      | X1     | SPXW   | model ≥60%            |      277 |  -18246 | 2/9     | -2.2  |
| ATM      | X1     | SPXW   | BASELINE always calls |      313 |  -18259 | 3/9     | -1.95 |
| ITM      | X2     | SPXW   | model ≥60%            |      101 |  -18573 | 1/9     | -1.59 |
| OTM      | X3     | SPXW   | BASELINE always calls |       63 |  -21869 | 2/9     | -1.4  |
| ITM      | X1     | SPXW   | model ≥60%            |      277 |  -23871 | 2/9     | -1.78 |
| ITM      | X2     | SPXW   | BASELINE always calls |      108 |  -27014 | 2/9     | -1.69 |
| ITM      | X1     | SPXW   | BASELINE always calls |      313 |  -29699 | 3/9     | -1.89 |
| ATM      | X3     | SPXW   | BASELINE always calls |       63 |  -40444 | 2/9     | -1.39 |
| ITM      | X3     | SPXW   | BASELINE always calls |       63 |  -60119 | 3/9     | -1.35 |

## C. Variable importance (permutation, last 2 days held out)

|               |    SPXW |     SPY |   mean |
|:--------------|--------:|--------:|-------:|
| btc_ret30     |  0.0233 |  0.0129 | 0.0181 |
| ret30         |  0.019  |  0.0129 | 0.0159 |
| rv30          |  0.0294 | -0.0024 | 0.0135 |
| vs_high       |  0.0234 |  0.0018 | 0.0126 |
| pcr_chg15     |  0.0225 |  0.0011 | 0.0118 |
| hyg_ret15     |  0.0104 |  0.0074 | 0.0089 |
| atm_gamma     | -0.0005 |  0.0167 | 0.0081 |
| atm_iv        |  0      |  0.0108 | 0.0054 |
| vs_low        |  0.0043 |  0.0057 | 0.005  |
| flow_net15    |  0.0102 | -0.0004 | 0.0049 |
| pcr_oi        |  0.0024 |  0.0063 | 0.0044 |
| dxy_chg30     |  0.0008 |  0.0078 | 0.0043 |
| vs_vwap_true  |  0.0021 |  0.0058 | 0.0039 |
| gex           |  0.0051 |  0.0025 | 0.0038 |
| flow_put15    |  0.0047 |  0.0017 | 0.0032 |
| theta_proxy   |  0.0001 |  0.0058 | 0.0029 |
| qqq_vs_spy15  |  0.0027 |  0.0031 | 0.0029 |
| vs_orh        |  0.0024 |  0.0032 | 0.0028 |
| min_since_low |  0.0069 | -0.0017 | 0.0026 |
| skew25        |  0.003  |  0.0016 | 0.0023 |

Still unavailable: CPI/jobs release calendar (FOMC and OPEX are included), NYSE TICK/ADD breadth, futures order flow and dark-pool prints, news headlines.

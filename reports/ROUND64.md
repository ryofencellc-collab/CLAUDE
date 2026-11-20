# Round 64: "when X happens, we win" (win-condition mining on 0DTE trades)

Rules: [PROTOCOL_ROUND64.md](../PROTOCOL_ROUND64.md).
Recorded days: **9** (INTERIM: verdict needs 20 days); snapshots 6,127; variables 72; rules searched per fold ≈ 2,424. ATM, X2 exits, real bid/ask, ≤ 2 trades/day.

**Verdict: FAIL (interim).**

## SPXW

- **Held-out (leave-one-day-out) P&L: $3,225** on 15 trades; green days 4/9; t 0.72.
- Luck test (same search on time-shifted labels, 20 runs): 95th percentile $8,939 → real is **NOT above** luck.
- Baselines on the same ≤ 2/day schedule: always call $-3,014, always put $4,176.
- Best rule on ALL days (in-sample, for reference only): BUY PUT when macd_slope <= -1.089 (p10) AND nvda_ret15 <= -31.9 (p30) → $11,355 in-sample.

Rule picked for each held-out day (mined on the other days):

| day        | rule                                                                       |   pnl |   trades |
|:-----------|:---------------------------------------------------------------------------|------:|---------:|
| 2026-11-09 | BUY PUT when dist_maxgamma >= 8.511 (p70) AND theta_proxy >= 18.74 (p70)   |  -573 |        1 |
| 2026-11-10 | BUY PUT when dist_maxgamma >= 8.625 (p70) AND theta_proxy >= 18.69 (p70)   |  -663 |        1 |
| 2026-11-11 | BUY PUT when ret5 <= -13.14 (p10) AND dxy_chg30 >= 2.709 (p70)             |  -493 |        1 |
| 2026-11-12 | BUY PUT when macd_slope <= -1.117 (p10) AND nvda_ret15 <= -32.45 (p30)     |   584 |        2 |
| 2026-11-13 | BUY PUT when macd_h <= -1.165 (p20) AND vix_chg30 <= -0.21 (p30)           |  -966 |        2 |
| 2026-11-16 | BUY PUT when ret5 <= -12.75 (p10) AND imb_call >= 0.7184 (p80)             | -1066 |        2 |
| 2026-11-17 | BUY PUT when macd_slope <= -1.061 (p10) AND mega_breadth15 <= 0.1429 (p20) |  3264 |        2 |
| 2026-11-18 | BUY PUT when vol15_put >= 7.969e+04 (p80) AND macd_slope <= -1.051 (p10)   |  1244 |        2 |
| 2026-11-19 | BUY PUT when tnx_chg30 >= 0.004 (p70) AND vol15_put >= 7.864e+04 (p80)     |  1894 |        2 |

## SPY

- **Held-out (leave-one-day-out) P&L: $323** on 17 trades; green days 6/9; t 0.95.
- Luck test (same search on time-shifted labels, 20 runs): 95th percentile $353 → real is **NOT above** luck.
- Baselines on the same ≤ 2/day schedule: always call $-402, always put $518.
- Best rule on ALL days (in-sample, for reference only): BUY PUT when macd_slope <= -0.6238 (p20) AND ret3 <= -9.395 (p10) → $1,241 in-sample.

Rule picked for each held-out day (mined on the other days):

| day        | rule                                                                          |    pnl |   trades |
|:-----------|:------------------------------------------------------------------------------|-------:|---------:|
| 2026-11-09 | BUY PUT when macd_slope <= -0.6623 (p20) AND atm_spread_pct <= 0.005907 (p30) |  -52.3 |        1 |
| 2026-11-10 | BUY PUT when macd_slope <= -0.6244 (p20) AND ret3 <= -9.533 (p10)             |   35.4 |        2 |
| 2026-11-11 | BUY PUT when macd_slope <= -0.6632 (p20) AND ret5 <= -4.939 (p30)             |  -80.6 |        2 |
| 2026-11-12 | BUY PUT when macd_slope <= -0.6392 (p20) AND skew25 >= 0.0298 (p70)           | -128.6 |        2 |
| 2026-11-13 | BUY PUT when macd_slope <= -0.6306 (p20) AND ret3 <= -9.448 (p10)             |   63.4 |        2 |
| 2026-11-16 | BUY PUT when macd_slope <= -0.6168 (p20) AND ret3 <= -9.466 (p10)             |   61.4 |        2 |
| 2026-11-17 | BUY PUT when ret3 <= -9.124 (p10) AND imb_call >= 0.4993 (p70)                |  239.4 |        2 |
| 2026-11-18 | BUY PUT when ret3 <= -9.003 (p10) AND imb_call >= 0.5042 (p70)                |   37.4 |        2 |
| 2026-11-19 | BUY PUT when rv30 >= 4.379 (p70) AND mega_ret30 >= 20.07 (p80)                |  147.4 |        2 |

## Cross-ticker SPXW->SPY

Rule mined on all of SPXW: BUY PUT when macd_slope <= -1.089 (p10) AND nvda_ret15 <= -31.9 (p30)

Applied to SPY: **$1,027** on 15 trades, green days 7/9, t 2.4.

## Cross-ticker SPY->SPXW

Rule mined on all of SPY: BUY PUT when macd_slope <= -0.6238 (p20) AND ret3 <= -9.395 (p10)

Applied to SPXW: **$7,246** on 18 trades, green days 7/9, t 2.57.

## Why winners win (descriptive, no verdict): variables that differ most at entry between winning and losing trades

std_diff = (winners' mean − losers' mean) / std. Within-day level variables are biased here (see Round 62 amendment 1); read with care.

| side   | variable        |   winners_mean |   losers_mean |   std_diff |
|:-------|:----------------|---------------:|--------------:|-----------:|
| call   | days_to_fomc    |        25.9457 |       24.6859 |     0.3635 |
| call   | days_since_fomc |        16.0543 |       17.3141 |    -0.3635 |
| call   | bdays_to_opex   |         5.6104 |        4.6874 |     0.3592 |
| call   | opex_week       |         0.3324 |        0.5007 |    -0.3388 |
| call   | spy_vol_rel15   |         1.0758 |        0.766  |     0.2459 |
| call   | vix_chg30       |         0.1942 |        0.0235 |     0.2293 |
| call   | mega_ret30      |       -12.2913 |       -4.7438 |    -0.1865 |
| call   | macd_slope      |         0.1283 |       -0.0574 |     0.1814 |
| call   | pcr_chg15       |         0.0094 |       -0.0011 |     0.1739 |
| call   | vix_chg15       |         0.0996 |        0.0093 |     0.1637 |
| call   | dist_maxoi      |       -21.9466 |      -57.2216 |     0.1631 |
| call   | atm_iv          |         0.2526 |        0.2671 |    -0.1508 |
| call   | msft_ret15      |        -7.3179 |       -1.9159 |    -0.1477 |
| call   | btc_ret30       |        -9.8251 |       -2.889  |    -0.146  |
| call   | ret30           |        -6.7997 |       -2.605  |    -0.1431 |
| put    | opex_week       |         0.6047 |        0.3442 |     0.5242 |
| put    | days_to_fomc    |        24.1081 |       25.7329 |    -0.4689 |
| put    | days_since_fomc |        17.8919 |       16.2671 |     0.4689 |
| put    | bdays_to_opex   |         4.3174 |        5.4212 |    -0.4296 |
| put    | vix_chg30       |        -0.0532 |        0.1644 |    -0.2922 |
| put    | mega_ret30      |         0.0155 |      -11.7955 |     0.2918 |
| put    | atm_iv          |         0.2778 |        0.2525 |     0.2634 |
| put    | vix             |        22.1065 |       21.3137 |     0.2557 |
| put    | prev_range      |       137.781  |      129.642  |     0.2528 |
| put    | btc_ret30       |         2.1417 |       -9.8039 |     0.2515 |
| put    | rv30            |         4.5686 |        4.024  |     0.2454 |
| put    | ret30           |         0.213  |       -6.632  |     0.2335 |
| put    | gex             |        -3.3894 |       -1.1457 |    -0.2313 |
| put    | macd_slope      |        -0.1408 |        0.0959 |    -0.2312 |
| put    | vix_chg15       |        -0.0279 |        0.0817 |    -0.1986 |

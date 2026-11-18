# Round 57: AAA gas nowcast vs Kalshi daily gas markets

Rules: [PROTOCOL_ROUND57.md](../PROTOCOL_ROUND57.md).

Markets: 46,883 settled (51 series, 2026-09-11 → 2026-11-17); with an ask-side trade after 12:00 ET: YES 18,896, NO 19,946.

**Verdict: FAIL.**
Dev choice: mom7, edge 0.2. Holdout: 2014 trades, mean P&L -0.016 $/contract, day-clustered t -0.94. Brier: model 0.1430 vs market 0.0465 on 11503 markets. Contracts available at the trade prices: 188,554.

## Dev grid

| variant   |   edge |   dev_trades |   dev_mean |   dev_t |
|:----------|-------:|-------------:|-----------:|--------:|
| persist   |   0.05 |         4145 |     0.0059 |  0.2435 |
| persist   |   0.1  |         3539 |     0.0104 |  0.3736 |
| persist   |   0.15 |         3105 |     0.0155 |  0.5013 |
| persist   |   0.2  |         2688 |     0.0195 |  0.5742 |
| mom3      |   0.05 |         3751 |     0.0169 |  0.5265 |
| mom3      |   0.1  |         3077 |     0.0239 |  0.6266 |
| mom3      |   0.15 |         2621 |     0.0282 |  0.6826 |
| mom3      |   0.2  |         2238 |     0.0324 |  0.7189 |
| mom7      |   0.05 |         3341 |     0.0133 |  0.4407 |
| mom7      |   0.1  |         2806 |     0.0183 |  0.5126 |
| mom7      |   0.15 |         2443 |     0.0242 |  0.6114 |
| mom7      |   0.2  |         2119 |     0.0337 |  0.7506 |

## Holdout by series (top 15 by trades)

| series      |   count |   mean |    sum |
|:------------|--------:|-------:|-------:|
| KXAAAGASD   |     105 | -0.002 |  -0.26 |
| KXAAAGASDFL |      89 |  0.116 |  10.35 |
| KXAAAGASDWI |      77 | -0.035 |  -2.73 |
| KXAAAGASDNE |      74 |  0.005 |   0.35 |
| KXAAAGASDIL |      74 | -0.19  | -14.07 |
| KXAAAGASDOH |      71 | -0.085 |  -6.03 |
| KXAAAGASDMI |      69 |  0.074 |   5.08 |
| KXAAAGASDIN |      63 | -0.138 |  -8.72 |
| KXAAAGASDWY |      58 | -0.031 |  -1.8  |
| KXAAAGASDDE |      56 | -0.109 |  -6.13 |
| KXAAAGASDSD |      51 |  0.003 |   0.17 |
| KXAAAGASDSC |      50 | -0.059 |  -2.96 |
| KXAAAGASDMD |      49 | -0.042 |  -2.04 |
| KXAAAGASDUT |      47 | -0.008 |  -0.36 |
| KXAAAGASDIA |      45 | -0.024 |  -1.08 |

## Holdout by side

| side   |   count |   mean |    sum |
|:-------|--------:|-------:|-------:|
| no     |     735 |  0.001 |   0.95 |
| yes    |    1279 | -0.026 | -32.94 |

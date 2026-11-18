# Round 58: mention markets vs each word's settlement record

Rules: [PROTOCOL_ROUND58.md](../PROTOCOL_ROUND58.md).

Markets: 44,043 settled in 212 series (2025-01-31 → 2026-11-17); with ≥ 3 earlier settlements of the same word: 24,796.

**Verdict: FAIL.**
Dev choice: edge 0.3, n_min 3, split 2026-06-16. Holdout: 1759 trades, mean P&L +0.062 $/contract, event-clustered t 5.15. Brier on traded markets: prior 0.302 vs price 0.188.

## Dev grid

|   edge |   nmin |   dev_trades |   dev_mean |   dev_t |
|-------:|-------:|-------------:|-----------:|--------:|
|   0.05 |      3 |         6114 |    -0.0131 | -2.0314 |
|   0.05 |      5 |         5061 |    -0.0166 | -2.3966 |
|   0.1  |      3 |         4301 |    -0.0047 | -0.599  |
|   0.1  |      5 |         3435 |    -0.0097 | -1.1337 |
|   0.15 |      3 |         3044 |     0.0055 |  0.5841 |
|   0.15 |      5 |         2360 |    -0.0033 | -0.3109 |
|   0.2  |      3 |         2180 |     0.0105 |  0.9623 |
|   0.2  |      5 |         1692 |     0.0043 |  0.3447 |
|   0.3  |      3 |         1070 |     0.0449 |  2.9704 |
|   0.3  |      5 |          800 |     0.0344 |  2.0125 |

## Holdout by side

| side   |   count |   mean |   sum |
|:-------|--------:|-------:|------:|
| no     |     962 |  0.036 | 34.9  |
| yes    |     797 |  0.093 | 74.04 |

## Holdout by series (top 15)

| series                |   count |   mean |   sum |
|:----------------------|--------:|-------:|------:|
| KXTRUMPMENTION        |     440 |  0.024 | 10.7  |
| KXWCMENTION           |     244 |  0.172 | 41.95 |
| KXTRUMPMENTIONB       |     133 | -0.002 | -0.25 |
| KXWORLDNEWSMENTION    |     125 | -0.029 | -3.67 |
| KXVANCEMENTION        |     104 |  0.037 |  3.85 |
| KXMAMDANIMENTION      |      74 |  0.223 | 16.5  |
| KXBERNIEMENTION       |      66 |  0.185 | 12.24 |
| KXTRUMPSAY            |      60 |  0.018 |  1.07 |
| KXHEARINGMENTION      |      51 | -0.06  | -3.04 |
| KXPOLITICSMENTION     |      50 |  0.026 |  1.31 |
| KXLASTWORDMENTION     |      49 |  0.11  |  5.37 |
| KXPSAKIMENTION        |      38 |  0.07  |  2.67 |
| KXTHEWEEKNIGHTMENTION |      30 |  0.041 |  1.23 |
| KXFOXNEWSMENTION      |      23 |  0.059 |  1.36 |
| KXALLINMENTION        |      18 |  0.122 |  2.2  |

## Holdout by price band

| band       |   count |   mean |
|:-----------|--------:|-------:|
| (0.0, 0.1] |     351 |  0.004 |
| (0.1, 0.3] |     827 |  0.045 |
| (0.3, 0.5] |     502 |  0.121 |
| (0.5, 0.7] |      79 |  0.117 |

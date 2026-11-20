# Round 63: chart #1 markets — incumbent repeat rate vs price

Rules: [PROTOCOL_ROUND63.md](../PROTOCOL_ROUND63.md).

Settled markets: 31,779 in 11 series. Incumbent markets: 1,904; priced: 1,646.

**Verdict: FAIL.**
Dev choice: edge 0.3, n_min 10, split 2025-11-24. Holdout: 187 trades, mean P&L -0.007 $/contract, event-clustered t -0.28. Brier on traded markets: prior 0.379 vs price 0.130.

## Descriptive: incumbent repeat rate vs first price, by series × streak bucket

|                                       |   events |   repeat_rate |   mean_yes_price |
|:--------------------------------------|---------:|--------------:|-----------------:|
| ('KXNETFLIXRANKMOVIE', '1')           |       62 |         0.339 |            0.43  |
| ('KXNETFLIXRANKMOVIE', '2-3')         |       26 |         0.231 |            0.398 |
| ('KXNETFLIXRANKMOVIE', '4+')          |        1 |         0     |            0.94  |
| ('KXNETFLIXRANKMOVIEGLOBAL', '1')     |       17 |         0.529 |            0.571 |
| ('KXNETFLIXRANKMOVIEGLOBAL', '2-3')   |        9 |         0.222 |            0.509 |
| ('KXNETFLIXRANKMOVIERUNNERUP', '1')   |       29 |         0.138 |            0.334 |
| ('KXNETFLIXRANKMOVIERUNNERUP', '2-3') |        3 |         0     |            0.327 |
| ('KXNETFLIXRANKSHOW', '1')            |       53 |         0.302 |            0.322 |
| ('KXNETFLIXRANKSHOW', '2-3')          |       14 |         0.071 |            0.284 |
| ('KXNETFLIXRANKSHOWRUNNERUP', '1')    |       26 |         0.231 |            0.426 |
| ('KXNETFLIXRANKSHOWRUNNERUP', '2-3')  |        5 |         0     |            0.096 |
| ('KXSPOTIFY2D', '1')                  |      145 |         0.462 |            0.531 |
| ('KXSPOTIFY2D', '2-3')                |      131 |         0.527 |            0.67  |
| ('KXSPOTIFY2D', '4+')                 |      158 |         0.671 |            0.702 |
| ('KXSPOTIFYD', '1')                   |       98 |         0.531 |            0.629 |
| ('KXSPOTIFYD', '2-3')                 |       92 |         0.707 |            0.778 |
| ('KXSPOTIFYD', '4+')                  |      318 |         0.821 |            0.808 |
| ('KXSPOTIFYGLOBALD', '1')             |       71 |         0.563 |            0.67  |
| ('KXSPOTIFYGLOBALD', '2-3')           |       82 |         0.695 |            0.757 |
| ('KXSPOTIFYGLOBALD', '4+')            |      350 |         0.88  |            0.849 |
| ('KXSPOTIFYW', '1')                   |       32 |         0.406 |            0.471 |
| ('KXSPOTIFYW', '2-3')                 |       18 |         0.444 |            0.523 |
| ('KXSPOTIFYW', '4+')                  |        5 |         0.2   |            0.318 |
| ('KXTOPALBUM', '1')                   |       41 |         0.268 |            0.376 |
| ('KXTOPALBUM', '2-3')                 |       15 |         0.533 |            0.535 |
| ('KXTOPALBUM', '4+')                  |       11 |         0.364 |            0.547 |
| ('KXTOPSONG', '1')                    |       30 |         0.367 |            0.464 |
| ('KXTOPSONG', '2-3')                  |       26 |         0.654 |            0.662 |
| ('KXTOPSONG', '4+')                   |       36 |         0.722 |            0.703 |

## Dev grid

|   edge |   nmin |   dev_trades |   dev_mean |   dev_t |
|-------:|-------:|-------------:|-----------:|--------:|
|   0.05 |      5 |          518 |    -0.0063 | -0.4143 |
|   0.05 |     10 |          460 |    -0.0086 | -0.5327 |
|   0.1  |      5 |          454 |    -0.0023 | -0.1357 |
|   0.1  |     10 |          403 |    -0.0069 | -0.3893 |
|   0.15 |      5 |          360 |     0.0054 |  0.2714 |
|   0.15 |     10 |          316 |     0.0027 |  0.1269 |
|   0.2  |      5 |          299 |     0.0107 |  0.4621 |
|   0.2  |     10 |          258 |     0.0095 |  0.3723 |
|   0.3  |      5 |          198 |     0.0534 |  1.842  |
|   0.3  |     10 |          163 |     0.0618 |  1.9025 |

## Holdout by side

| side   |   count |   mean |   sum |
|:-------|--------:|-------:|------:|
| no     |      69 |  0.026 |  1.78 |
| yes    |     118 | -0.027 | -3.17 |

## Holdout by series

| series                     |   count |   mean |   sum |
|:---------------------------|--------:|-------:|------:|
| KXNETFLIXRANKMOVIE         |      11 | -0.101 | -1.11 |
| KXNETFLIXRANKMOVIEGLOBAL   |       5 |  0.044 |  0.22 |
| KXNETFLIXRANKMOVIERUNNERUP |       2 | -0.01  | -0.02 |
| KXNETFLIXRANKSHOW          |       5 | -0.26  | -1.3  |
| KXNETFLIXRANKSHOWRUNNERUP  |       3 |  0.19  |  0.57 |
| KXSPOTIFY2D                |      43 |  0.064 |  2.76 |
| KXSPOTIFYD                 |      33 | -0.028 | -0.93 |
| KXSPOTIFYGLOBALD           |      37 | -0.011 | -0.39 |
| KXSPOTIFYW                 |      18 | -0.036 | -0.64 |
| KXTOPALBUM                 |       8 |  0.095 |  0.76 |
| KXTOPSONG                  |      22 | -0.06  | -1.31 |

## Holdout by streak bucket

| bucket   |   count |   mean |   sum |
|:---------|--------:|-------:|------:|
| 1        |      87 |  0.004 |  0.31 |
| 2-3      |      51 | -0.05  | -2.54 |
| 4+       |      49 |  0.017 |  0.84 |

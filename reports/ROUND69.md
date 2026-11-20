# Round 69: blind test of the frozen 0DTE strategy

Rules: [PROTOCOL_ROUND69.md](../PROTOCOL_ROUND69.md). Strategy: sell the SPX 0DTE ATM straddle at the open; skip Thursdays and mega-cap earnings mornings.

**Verdict: FAIL.**

## Test 1: real recorded quotes (sold at the real bid, settled at the official close, $3 fees)

| day        | weekday   | source                     | entry   |   spot |   strike |   credit |   close |   move |    pnl | skip                    |
|:-----------|:----------|:---------------------------|:--------|-------:|---------:|---------:|--------:|-------:|-------:|:------------------------|
| 2026-11-09 | Mon       | Cboe 1-min                 | 09:32   | 7440.9 |     7440 |     51.8 | 7549.94 |  109.9 |  -5817 |                         |
| 2026-11-10 | Tue       | Cboe 1-min                 | 09:31   | 7495.2 |     7495 |     52.6 | 7520.93 |   25.9 |   2664 |                         |
| 2026-11-11 | Wed       | Cboe 1-min                 | 09:31   | 7595.5 |     7595 |     31.3 | 7619.38 |   24.4 |    689 |                         |
| 2026-11-12 | Thu       | Cboe 1-min                 | 09:31   | 7564.1 |     7565 |     44.7 | 7592.4  |   27.4 |   1727 | Thursday                |
| 2026-11-13 | Fri       | Cboe 1-min                 | 09:31   | 7611.2 |     7610 |     39.5 | 7561.67 |  -48.3 |   -886 |                         |
| 2026-11-16 | Mon       | Cboe 1-min                 | 09:31   | 7493.6 |     7495 |     55.9 | 7416.59 |  -78.4 |  -2254 |                         |
| 2026-11-17 | Tue       | Cboe 1-min                 | 09:31   | 7399.3 |     7400 |     55.6 | 7340.53 |  -59.5 |   -390 |                         |
| 2026-11-18 | Wed       | Cboe 1-min                 | 09:31   | 7360.2 |     7360 |     63.2 | 7323.63 |  -36.4 |   2680 | earnings morning (NVDA) |
| 2026-11-19 | Thu       | Cboe 1-min                 | 09:31   | 7400.7 |     7400 |     62.3 | 7175.83 | -224.2 | -16190 | Thursday                |
| 2026-11-20 | Fri       | Yahoo 5-min (starts 10:32) | 10:32   | 7142.9 |     7165 |     71.6 | 6910.39 | -254.6 | -18304 |                         |

Strategy (traded days only): 7 trades, total $-24,298, mean $-3,471, wins 2/7.  
Every day (the curve): 10 trades, total $-36,081, mean $-3,608.  
Without the 11-20 late-start day: strategy $-5,994, every day $-17,777.  
S&P buy-and-hold over the same days: -6.90%.

## Test 2: blind holdout 2024-08-12 → 2026-11-19 (rules fixed on 2022-06 → 2024-08 data; model-priced, P&L per SPX straddle)

| pricing                            | trade                                   |   days |   mean_pt |     t |   win |   total_pt |   total_usd |   maxdd_usd |   worst_usd |
|:-----------------------------------|:----------------------------------------|-------:|----------:|------:|------:|-----------:|------------:|------------:|------------:|
| model                              | STRATEGY (skip Thu + earnings mornings) |    443 |      2.93 |  1.95 | 0.628 |       1297 |      129737 |       70063 |      -32963 |
| model                              | every day (the curve)                   |    572 |      2.04 |  1.44 | 0.614 |       1164 |      116408 |       79115 |      -32963 |
| model × 0.895 (real-quote haircut) | STRATEGY (skip Thu + earnings mornings) |    443 |     -1.03 | -0.68 | 0.551 |       -456 |      -45609 |      101140 |      -34670 |
| model × 0.895 (real-quote haircut) | every day (the curve)                   |    572 |     -1.95 | -1.37 | 0.547 |      -1115 |     -111511 |      118757 |      -34670 |

S&P buy-and-hold over the holdout: +34.3%.


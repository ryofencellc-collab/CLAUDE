# Round 26 backtest: new live trader vs earlier versions

Every version runs through ONE simulator that copies the live bot (edge/live21.py):
  - one market at a time; the position grows with later fills in that market, up to stake x balance / 99c;
  - a fill counts only while the bid would be resting (the version's entry/keep rule holds at that moment);
  - the governor: stake 0.5 for the first 14 days, 0.95 after 14 days with P&L >= 0 and no loss in 14 days,
    0.25 for 14 days after a loss; 24 h pause and 7 days at half size after any loss; halt for good at 70%
    of the start or 2 losses within 7 days; no new market after a 10% loss on the day;
  - maker fee per fill (Kalshi's quadratic fee).
'honest' fills keep only trades whose long-shot price is >= 1c: the only ones that can reach a 99c bid (the
15-minute markets quote 0.1c steps above 90c; reports/FILLCHECK.md). Hourly markets trade in whole cents, so
'honest' changes nothing there.

Long-shot fills loaded: 1,894,906 (KXETH15M 750,079, KXXRP15M 431,982, KXSOL15M 397,185, KXDOGE15M 298,958, KXBTCD 14,410, KXETHD 1,098, KXXRPD 657, KXSOLD 537).
Share of 15-minute long-shot volume priced under 1c (can't reach 99c): 80.8%; hourly: 0.0%.

Sampling: Round 21 tested at most 1,500 markets per series per period (every k-th market), so these runs see a fraction of all markets: weights KXBTCD 1/356, KXDOGE15M 1/12, KXETH15M 1/12, KXETHD 1/407, KXSOL15M 1/12, KXSOLD 1/408, KXXRP15M 1/12, KXXRPD 1/210.

15-minute long-shot volume under 1c, by month: 2026-03 35%, 2026-04 32%, 2026-05 38%, 2026-06 42%, 2026-07 49%, 2026-08 74%, 2026-09 83%, 2026-10 83%

## Holdout Oct 1-28, capture 25%

| version                                                                  | $1,000 ->   |   $/day | daily growth   |   markets |   losses | max drawdown   | green days   | halted                      |
|:-------------------------------------------------------------------------|:------------|--------:|:---------------|----------:|---------:|:---------------|:-------------|:----------------------------|
| A. Round 25 as reported (15-min, Kelly cap 0.95, no governor, all fills) | $31,196     | 1120.03 | 13.61%         |      1011 |        3 | -28%           | 96%          | no                          |
| B. Old live bot (15-min, Round 25 rule + governor), all fills            | $3,426      |   90    | 4.67%          |       890 |        3 | -50%           | 88%          | Oct 26 (2 losses in 7 days) |
| C. Old live bot, honest fills                                            | $679        |  -11.9  | -1.43%         |       167 |        1 | -50%           | 90%          | Oct 10 (equity floor)       |
| D. 15-min, z>=6 + governor, honest fills                                 | $1,352      |   13.05 | 1.12%          |       100 |        0 | -0%            | 100%         | no                          |
| E. NEW: hourly, z>=6 + governor (Round 26)                               | $1,089      |    3.3  | 0.32%          |        97 |        0 | -0%            | 89%          | no                          |
| F. hourly + 15-min (15-min on the Round 25 rule), honest                 | $681        |  -11.85 | -1.42%         |       172 |        1 | -50%           | 90%          | Oct 10 (equity floor)       |

## Dev Apr-Sep, capture 25%

| version                                                                  | $1,000 ->   |   $/day | daily growth   |   markets |   losses | max drawdown   | green days   | halted                      |
|:-------------------------------------------------------------------------|:------------|--------:|:---------------|----------:|---------:|:---------------|:-------------|:----------------------------|
| A. Round 25 as reported (15-min, Kelly cap 0.95, no governor, all fills) | $12,114     |   61.13 | 1.38%          |      2005 |       10 | -22%           | 97%          | no                          |
| B. Old live bot (15-min, Round 25 rule + governor), all fills            | $3,265      |   12.46 | 0.65%          |      1133 |        3 | -2%            | 98%          | Aug 01 (2 losses in 7 days) |
| C. Old live bot, honest fills                                            | $1,621      |    3.42 | 0.27%          |       578 |        3 | -3%            | 97%          | Aug 01 (2 losses in 7 days) |
| D. 15-min, z>=6 + governor, honest fills                                 | $1,215      |    1.18 | 0.11%          |       167 |        1 | -0%            | 98%          | no                          |
| E. NEW: hourly, z>=6 + governor (Round 26)                               | $1,233      |    1.3  | 0.12%          |       171 |        0 | -0%            | 83%          | no                          |
| F. hourly + 15-min (15-min on the Round 25 rule), honest                 | $1,689      |    3.79 | 0.29%          |       645 |        3 | -3%            | 97%          | Aug 01 (2 losses in 7 days) |

## Holdout Oct 1-28, capture 10%

| version                                                                  | $1,000 ->   |   $/day | daily growth   |   markets |   losses | max drawdown   | green days   | halted                      |
|:-------------------------------------------------------------------------|:------------|--------:|:---------------|----------:|---------:|:---------------|:-------------|:----------------------------|
| A. Round 25 as reported (15-min, Kelly cap 0.95, no governor, all fills) | $13,664     |  469.72 | 10.18%         |      1011 |        3 | -20%           | 96%          | no                          |
| B. Old live bot (15-min, Round 25 rule + governor), all fills            | $3,593      |   96.17 | 4.86%          |       890 |        3 | -28%           | 88%          | Oct 26 (2 losses in 7 days) |
| C. Old live bot, honest fills                                            | $567        |  -16.06 | -2.08%         |       167 |        1 | -50%           | 90%          | Oct 10 (equity floor)       |
| D. 15-min, z>=6 + governor, honest fills                                 | $1,158      |    5.85 | 0.54%          |       100 |        0 | -0%            | 90%          | no                          |
| E. NEW: hourly, z>=6 + governor (Round 26)                               | $1,044      |    1.62 | 0.16%          |        97 |        0 | -0%            | 89%          | no                          |
| F. hourly + 15-min (15-min on the Round 25 rule), honest                 | $574        |  -15.8  | -2.04%         |       172 |        1 | -50%           | 90%          | Oct 10 (equity floor)       |

## Holdout Oct 1-28, capture 50%

| version                                                                  | $1,000 ->   |   $/day | daily growth   |   markets |   losses | max drawdown   | green days   | halted                      |
|:-------------------------------------------------------------------------|:------------|--------:|:---------------|----------:|---------:|:---------------|:-------------|:----------------------------|
| A. Round 25 as reported (15-min, Kelly cap 0.95, no governor, all fills) | $56,271     | 2050.14 | 16.12%         |      1011 |        3 | -38%           | 96%          | no                          |
| B. Old live bot (15-min, Round 25 rule + governor), all fills            | $3,824      |  104.75 | 5.10%          |       890 |        3 | -50%           | 88%          | Oct 26 (2 losses in 7 days) |
| C. Old live bot, honest fills                                            | $765        |   -8.72 | -0.99%         |       427 |        3 | -51%           | 88%          | Oct 24 (2 losses in 7 days) |
| D. 15-min, z>=6 + governor, honest fills                                 | $1,518      |   19.21 | 1.56%          |       100 |        0 | -0%            | 100%         | no                          |
| E. NEW: hourly, z>=6 + governor (Round 26)                               | $1,131      |    4.88 | 0.46%          |        97 |        0 | -0%            | 93%          | no                          |
| F. hourly + 15-min (15-min on the Round 25 rule), honest                 | $692        |  -11.42 | -1.36%         |       395 |        3 | -56%           | 88%          | Oct 24 (equity floor)       |


# Round 8, development period (2014 → 2021-12-31)

Run 2026-10-27T16:42:35+00:00. Sealed data (2022 onward) was cut before any calculation. Distinct dev configs logged so far: 52 (each adds to the trial count for the final test).

13F: no data yet (SEC blocks GitHub's servers; to be fetched from the owner's computer). Congress: 7,347 parsed transactions from 1,108 reports, 3,965 purchases, 122 members.

Columns: CAGR of the strategy and of SPY over the same days; excess = annual return over SPY; IR = information ratio (pass needs ≥ 0.5 in the sealed period); excess MDD = worst drop of the strategy relative to SPY; $1000 = what $1,000 grew to.

## Baselines

| id            | start      | end        | cagr   | spy_cagr   | excess_ann   |   ir | excess_mdd   | beat_spy_months   | usd_1000   | usd_1000_spy   |   trades |
|:--------------|:-----------|:-----------|:-------|:-----------|:-------------|-----:|:-------------|:------------------|:-----------|:---------------|---------:|
| Congress-base | 2018-04-27 | 2021-12-31 | +22.6% | +19.1%     | +3.2%        |  0.4 | -10.5%       | 60%               | $2,115     | $1,904         |     2519 |

## Congress tweaks

| id                                | start      | end        | cagr   | spy_cagr   | excess_ann   |    ir | excess_mdd   | beat_spy_months   | usd_1000   | usd_1000_spy   |   trades |
|:----------------------------------|:-----------|:-----------|:-------|:-----------|:-------------|------:|:-------------|:------------------|:-----------|:---------------|---------:|
| Congress-h120-ST+OP-min0-d15      | 2018-04-27 | 2021-12-31 | +30.2% | +19.1%     | +9.5%        |  0.8  | -12.6%       | 60%               | $2,641     | $1,904         |      606 |
| Congress-h120-ST-min0-d15         | 2018-04-27 | 2021-12-31 | +30.2% | +19.1%     | +9.5%        |  0.8  | -12.5%       | 60%               | $2,643     | $1,904         |      600 |
| Congress-h60-ST+OP-min0-d15       | 2018-04-27 | 2021-12-31 | +31.4% | +19.1%     | +10.6%       |  0.79 | -10.6%       | 60%               | $2,731     | $1,904         |      606 |
| Congress-h60-ST-min0-d15          | 2018-04-27 | 2021-12-31 | +31.3% | +19.1%     | +10.6%       |  0.78 | -10.8%       | 60%               | $2,725     | $1,904         |      600 |
| Congress-h60-ST+OP-min0-dany      | 2018-04-27 | 2021-12-31 | +22.7% | +19.1%     | +3.3%        |  0.41 | -10.3%       | 60%               | $2,125     | $1,904         |     2544 |
| Congress-h120-ST+OP-min0-dany     | 2018-04-27 | 2021-12-31 | +22.1% | +19.1%     | +2.7%        |  0.37 | -9.4%        | 58%               | $2,086     | $1,904         |     2544 |
| Congress-h120-ST-min0-dany        | 2018-04-27 | 2021-12-31 | +22.0% | +19.1%     | +2.7%        |  0.37 | -9.5%        | 62%               | $2,083     | $1,904         |     2519 |
| Congress-h20-ST-min0-d15          | 2018-04-27 | 2021-12-31 | +22.0% | +19.1%     | +3.0%        |  0.23 | -20.6%       | 49%               | $2,078     | $1,904         |      600 |
| Congress-h20-ST+OP-min0-d15       | 2018-04-27 | 2021-12-31 | +21.4% | +19.1%     | +2.5%        |  0.19 | -18.7%       | 49%               | $2,039     | $1,904         |      606 |
| Congress-h20-ST+OP-min0-dany      | 2018-04-27 | 2021-12-31 | +14.9% | +19.1%     | -3.4%        | -0.42 | -15.8%       | 42%               | $1,667     | $1,904         |     2544 |
| Congress-h20-ST-min0-dany         | 2018-04-27 | 2021-12-31 | +14.8% | +19.1%     | -3.4%        | -0.42 | -16.4%       | 44%               | $1,665     | $1,904         |     2519 |
| Congress-h5-ST+OP-min0-dany       | 2018-04-27 | 2021-12-31 | +7.4%  | +19.1%     | -9.7%        | -0.64 | -43.8%       | 40%               | $1,301     | $1,904         |     2544 |
| Congress-h5-ST-min0-d15           | 2018-04-27 | 2021-12-31 | +1.7%  | +19.1%     | -14.0%       | -0.71 | -56.7%       | 42%               | $1,063     | $1,904         |      600 |
| Congress-h5-ST-min0-dany          | 2018-04-27 | 2021-12-31 | +4.9%  | +19.1%     | -11.9%       | -0.81 | -48.9%       | 38%               | $1,195     | $1,904         |     2519 |
| Congress-h5-ST+OP-min0-d15        | 2018-04-27 | 2021-12-31 | -1.7%  | +19.1%     | -17.4%       | -0.89 | -59.5%       | 42%               | $937       | $1,904         |      606 |
| Congress-h5-ST-min15001-dany      | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h5-ST-min15001-d15       | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h5-ST-min50001-dany      | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h5-ST-min50001-d15       | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h5-ST+OP-min15001-dany   | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h5-ST+OP-min15001-d15    | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h5-ST+OP-min50001-dany   | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h5-ST+OP-min50001-d15    | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h20-ST-min15001-dany     | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h20-ST-min15001-d15      | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h20-ST-min50001-dany     | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h20-ST-min50001-d15      | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h20-ST+OP-min15001-dany  | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h20-ST+OP-min15001-d15   | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h20-ST+OP-min50001-dany  | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h20-ST+OP-min50001-d15   | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h60-ST-min15001-dany     | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h60-ST-min15001-d15      | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h60-ST-min50001-dany     | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h60-ST-min50001-d15      | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h60-ST+OP-min15001-dany  | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h60-ST+OP-min15001-d15   | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h60-ST+OP-min50001-dany  | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h60-ST+OP-min50001-d15   | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h120-ST-min15001-dany    | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h120-ST-min15001-d15     | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h120-ST-min50001-dany    | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h120-ST-min50001-d15     | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h120-ST+OP-min15001-dany | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h120-ST+OP-min15001-d15  | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h120-ST+OP-min50001-dany | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |
| Congress-h120-ST+OP-min50001-d15  | nan        | nan        |        |            |              |       |              |                   |            |                |        0 |

## Pelosi only

| id                | start      | end        | cagr    | spy_cagr   | excess_ann   |    ir | excess_mdd   | beat_spy_months   | usd_1000   | usd_1000_spy   |   trades |
|:------------------|:-----------|:-----------|:--------|:-----------|:-------------|------:|:-------------|:------------------|:-----------|:---------------|---------:|
| Pelosi-h60-ST+OP  | 2020-07-21 | 2021-12-31 | +127.8% | +31.9%     | +60.4%       |  1.77 | -19.2%       | 61%               | $3,317     | $1,496         |       11 |
| Pelosi-h120-ST+OP | 2020-07-21 | 2021-12-31 | +61.8%  | +31.9%     | +24.1%       |  0.96 | -12.9%       | 50%               | $2,015     | $1,496         |       11 |
| Pelosi-h5-ST+OP   | 2020-07-21 | 2021-12-31 | +31.4%  | +31.9%     | -0.2%        | -0.05 | -5.1%        | 17%               | $1,488     | $1,496         |       11 |
| Pelosi-h20-ST+OP  | 2020-07-21 | 2021-12-31 | +17.9%  | +31.9%     | -10.3%       | -0.71 | -17.0%       | 28%               | $1,271     | $1,496         |       11 |


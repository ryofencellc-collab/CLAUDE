# Round 8 SMOKE TEST (pipeline check: 2019-2020 filings, 60 tickers; not results)

Run 2026-10-27T16:35:52+00:00. Sealed data (2022 onward) was cut before any calculation. Distinct dev configs logged so far: 0 (each adds to the trial count for the final test).

13F: no data yet (SEC blocks GitHub's servers; to be fetched from the owner's computer). Congress: 4,060 parsed transactions from 582 reports, 2,055 purchases, 81 members.

Columns: CAGR of the strategy and of SPY over the same days; excess = annual return over SPY; IR = information ratio (pass needs ≥ 0.5 in the sealed period); excess MDD = worst drop of the strategy relative to SPY; $1000 = what $1,000 grew to.

## Baselines

| id            | start      | end        | cagr   | spy_cagr   | excess_ann   |   ir | excess_mdd   | beat_spy_months   | usd_1000   | usd_1000_spy   |   trades |
|:--------------|:-----------|:-----------|:-------|:-----------|:-------------|-----:|:-------------|:------------------|:-----------|:---------------|---------:|
| Congress-base | 2019-01-04 | 2021-12-31 | +41.8% | +27.0%     | +12.0%       | 0.93 | -7.9%        | 58%               | $2,846     | $2,046         |      432 |

## Congress tweaks

| id                                | start      | end        | cagr   | spy_cagr   | excess_ann   |    ir | excess_mdd   | beat_spy_months   | usd_1000   | usd_1000_spy   |   trades |
|:----------------------------------|:-----------|:-----------|:-------|:-----------|:-------------|------:|:-------------|:------------------|:-----------|:---------------|---------:|
| Congress-h120-ST-min0-dany        | 2019-01-04 | 2021-12-31 | +41.6% | +27.0%     | +11.6%       |  1    | -4.5%        | 53%               | $2,837     | $2,046         |      432 |
| Congress-h120-ST+OP-min0-dany     | 2019-01-04 | 2021-12-31 | +41.4% | +27.0%     | +11.4%       |  1    | -4.6%        | 53%               | $2,822     | $2,046         |      436 |
| Congress-h60-ST+OP-min0-dany      | 2019-01-04 | 2021-12-31 | +41.4% | +27.0%     | +11.6%       |  0.93 | -7.8%        | 58%               | $2,824     | $2,046         |      436 |
| Congress-h120-ST+OP-min0-d15      | 2019-01-04 | 2021-12-31 | +46.4% | +27.0%     | +15.6%       |  0.91 | -7.8%        | 47%               | $3,130     | $2,046         |      172 |
| Congress-h120-ST-min0-d15         | 2019-01-04 | 2021-12-31 | +46.5% | +27.0%     | +15.7%       |  0.91 | -7.8%        | 47%               | $3,140     | $2,046         |      171 |
| Congress-h60-ST-min0-d15          | 2019-01-04 | 2021-12-31 | +41.0% | +27.0%     | +12.4%       |  0.62 | -12.9%       | 44%               | $2,798     | $2,046         |      171 |
| Congress-h60-ST+OP-min0-d15       | 2019-01-04 | 2021-12-31 | +40.7% | +27.0%     | +12.0%       |  0.62 | -12.9%       | 44%               | $2,779     | $2,046         |      172 |
| Congress-h20-ST+OP-min0-d15       | 2019-01-04 | 2021-12-31 | +33.1% | +27.0%     | +5.5%        |  0.43 | -17.2%       | 36%               | $2,354     | $2,046         |      172 |
| Congress-h20-ST-min0-d15          | 2019-01-04 | 2021-12-31 | +32.1% | +27.0%     | +4.7%        |  0.38 | -17.2%       | 36%               | $2,300     | $2,046         |      171 |
| Congress-h20-ST+OP-min0-dany      | 2019-01-04 | 2021-12-31 | +26.9% | +27.0%     | +0.4%        |  0.04 | -12.8%       | 36%               | $2,044     | $2,046         |      436 |
| Congress-h20-ST-min0-dany         | 2019-01-04 | 2021-12-31 | +26.7% | +27.0%     | +0.4%        |  0.04 | -13.4%       | 39%               | $2,032     | $2,046         |      432 |
| Congress-h5-ST-min0-d15           | 2019-01-04 | 2021-12-31 | +9.4%  | +27.0%     | -13.3%       | -0.85 | -46.4%       | 22%               | $1,311     | $2,046         |      171 |
| Congress-h5-ST+OP-min0-d15        | 2019-01-04 | 2021-12-31 | +8.2%  | +27.0%     | -14.4%       | -0.92 | -47.9%       | 22%               | $1,268     | $2,046         |      172 |
| Congress-h5-ST+OP-min0-dany       | 2019-01-04 | 2021-12-31 | +9.6%  | +27.0%     | -14.1%       | -1.05 | -40.1%       | 22%               | $1,316     | $2,046         |      436 |
| Congress-h5-ST-min0-dany          | 2019-01-04 | 2021-12-31 | +5.7%  | +27.0%     | -17.2%       | -1.31 | -45.7%       | 22%               | $1,180     | $2,046         |      432 |
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

| id                | start      | end        | cagr   | spy_cagr   | excess_ann   |   ir | excess_mdd   | beat_spy_months   | usd_1000   | usd_1000_spy   |   trades |
|:------------------|:-----------|:-----------|:-------|:-----------|:-------------|-----:|:-------------|:------------------|:-----------|:---------------|---------:|
| Pelosi-h60-ST+OP  | 2020-07-21 | 2021-12-31 | +55.9% | +31.9%     | +19.4%       | 0.84 | -9.1%        | 17%               | $1,908     | $1,496         |        1 |
| Pelosi-h5-ST+OP   | 2020-07-21 | 2021-12-31 | +32.2% | +31.9%     | +0.3%        | 0.36 | -0.6%        | 6%                | $1,502     | $1,496         |        1 |
| Pelosi-h20-ST+OP  | 2020-07-21 | 2021-12-31 | +34.2% | +31.9%     | +1.9%        | 0.31 | -8.2%        | 11%               | $1,534     | $1,496         |        1 |
| Pelosi-h120-ST+OP | 2020-07-21 | 2021-12-31 | +29.4% | +31.9%     | +1.7%        | 0.06 | -28.4%       | 11%               | $1,455     | $1,496         |        1 |


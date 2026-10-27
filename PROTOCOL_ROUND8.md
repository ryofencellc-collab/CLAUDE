# Round 8 pre-registration: copy the funds, copy Congress (trader-skill)

Written 2026-10-27, before any 13F or congressional-trade data was
downloaded. Tests the two strategies automated by
github.com/Jakeschincariol/trader-skill (`trader-copycat`, `trader-pelosi`).

## The owner's request, and how it stays honest

The owner wants to look at the data and then tweak the strategies to make
them better. That's allowed, under a hard split:

| Period | Name | Who sees it | Use |
|---|---|---|---|
| 2014-01-01 → 2021-12-31 | **development** | owner + Claude, freely | build, inspect, tweak |
| 2022-01-01 → today | **sealed** | nobody until the freeze | one final run |

The code enforces this: in `dev` mode, all data after 2021-12-31 is cut off
**before** any calculation, so sealed numbers can't be printed by accident.
`final` mode only runs configs listed in `round8_frozen.json`, which must be
committed before it runs. Every config ever evaluated in dev mode is
appended to `reports/round8_dev_log.csv` and counts as a trial.

## Data (all free, primary sources)

- **13F**: SEC EDGAR, original 13F-HR filings (amendments ignored) of the 23
  funds in trader-skill's `filers.json`. Long stock positions only (no
  puts/calls); top 20 by value per filing. CUSIP→ticker via OpenFIGI.
- **Congress**: House Clerk annual index + electronically filed Periodic
  Transaction Report PDFs (scanned handwritten reports can't be parsed and
  are skipped), stock trades `[ST]` only.
- **Prices**: Yahoo Finance adjusted closes. Delisted tickers often have
  no data: they are dropped and the rest re-weighted, a survivorship bias
  that flatters both strategies. It is stated, not hidden.

## No look-ahead

- 13F: a portfolio is bought at the close of the first trading day **after
  the filing date** (not the quarter end), and held until the next filing.
- Congress: a trade is bought at the close of the first trading day **after
  the disclosure is filed** (not the trade date).

## Baselines (registered now, before any data)

- **13F-base**: each fund, top 10 by value, value-weighted. Also the
  equal-weight average across funds.
- **Congress-base**: every disclosed purchase of a stock by any House member,
  held 60 trading days, equal weight across open positions (SPY when none).

Costs: 0.05% per side on turnover. Benchmark: SPY (total return).

## Pass (final, sealed period only)

Measured on daily **excess return over SPY**:
1. sealed information ratio (annualised mean ÷ sd of excess) ≥ 0.5
2. sealed Deflated Sharpe of the excess series ≥ 0.95, deflated by all
   trials (211 before this round + every dev config + the baselines)
3. development information ratio > 0
4. sealed max drawdown of cumulative excess ≥ −25%

The owner sees the dev results, chooses tweaks with Claude, and then at
most **two** frozen configs (one 13F, one Congress) plus the two baselines
get the single sealed run.

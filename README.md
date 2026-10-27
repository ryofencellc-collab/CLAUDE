# Can an AI make money?

An experiment run by Claude: find a strategy with a real, net-of-cost edge,
then prove it in four escalating gates:

1. **Backtest:** pre-registered strategies, in-sample selection, untouched holdout,
   Deflated Sharpe Ratio across every trial, null test on shuffled data.
2. **Paper trade:** 60+ days of timestamped signals logged before the outcome is known.
3. **Live, $1,000:** 90 days, hard stop at -20%.
4. **Live, $10,000:** same strategy, same rules.

The experiment ends at the first failed gate. A failure is reported as plainly
as a success. All rules are in [PROTOCOL.md](PROTOCOL.md) and were committed
before any real data was looked at.

## Layout

| Path | What |
|---|---|
| `PROTOCOL.md` | Pass/fail rules for every phase, fixed in advance |
| `edge/data.py` | Binance public archive (spot, perps, funding) and Yahoo Finance loaders |
| `edge/backtest.py` | Daily backtester (one-day signal lag enforced in one place, costs on turnover) |
| `edge/stats.py` | Probabilistic and Deflated Sharpe Ratio, bootstrap |
| `edge/null.py` | Shuffled zero-drift data for the null test |
| `edge/strategies/` | Strategy families and their fixed parameter grids |
| `run_research.py` | Phase 1 runner → `reports/RESULTS.md`, `reports/trials.csv` |
| `tests/` | Pipeline must find nothing in noise **and** must find a planted edge |

## Running

```
pip install -r requirements.txt
python -m pytest -q tests
python run_research.py --refresh
```

Real-data runs happen in GitHub Actions (`.github/workflows/research.yml`).

## Status

| Round | What was tested | Result |
|---|---|---|
| 1 | 9 daily crypto/ETF strategy families, 61 configs | 0/9 pass: [RESULTS.md](reports/RESULTS.md), [analysis](reports/PHASE1_ANALYSIS.md) |
| 2 | TikTok NQ strategy (14 yrs of 1-min data), opening-range breakout, football betting, Polymarket | 0/5 pass (NQ section corrected after a timestamp bug; verdict unchanged); football value betting is a lead: [ROUND2.md](reports/ROUND2.md) |
| 3 | Forward paper test of football value betting (Betfair-referenced) | **running live**: [paper/SUMMARY.md](paper/SUMMARY.md), rules [PROTOCOL_ROUND3.md](PROTOCOL_ROUND3.md) |
| 4 | Beat retail: fade crypto crowd positioning, follow whales, fade NQ stop-hunt sweeps | 0/3 pass: [ROUND4.md](reports/ROUND4.md) |
| 5 | Kalshi weather markets: 1 vs 5 forecast models, major vs unpopular cities (24 configs) | 0/4 pass: [ROUND5.md](reports/ROUND5.md) |
| 5-live | Weather, live paper test with same-day forecasts | **running**: [paper/WEATHER.md](paper/WEATHER.md) |
| 6 | Sell a weekly Bitcoin put (3 strikes, real Deribit prices) | 0/1 pass; 96% winning weeks, ~0% return: [ROUND6.md](reports/ROUND6.md) |
| 7 | Bracket arbitrage, cross-exchange funding, pairs, tennis value, matched betting | 0/3 pass (tennis data blocked): [ROUND7.md](reports/ROUND7.md) |
| 8 | Copy Congress (House stock disclosures 2014–26, 52 tweaks on 2014–21, one frozen) and copy 13F funds | Congress: **0/1 pass, as predicted**. Sealed 2022–26: $1,000 → $1,633 vs SPY $1,726: [ROUND8_SEALED_CONGRESS.md](reports/ROUND8_SEALED_CONGRESS.md), [dev](reports/ROUND8_DEV.md). 13F: waiting on SEC data (hourly fetch) |
| 9 | Data-chosen trade gates (data picks which and how many, 0–6, from 30), walk-forward | Crypto: **FAIL** but closest yet: $1,000 → $13,052 vs BTC $2,891, Sharpe 0.89, worst drop −59%: [ROUND9.md](reports/ROUND9.md). Stocks: **FAIL**, $4,934 vs SPY $7,914; the data chose zero gates in 22 of 30 refits: [ROUND9B.md](reports/ROUND9B.md) |
| 10 | Crypto trend gate + volatility limit (72 configs, walk-forward) | **FAIL**: Sharpe 0.85, worst drop −34% (vs BTC −77%): [ROUND10.md](reports/ROUND10.md) |
| 11 | Multi-asset trend, risk-balanced (24 configs, OOS 2012+) | **FAIL**: Sharpe 0.75 vs SPY 0.93, worst drop only −17%: [ROUND11.md](reports/ROUND11.md) |
| 12 | SPY core + crypto trend sleeve (18 configs, OOS 2016+) | **FAIL (5 of 6)**: $1,000 → $6,434 vs SPY $4,489, Sharpe 1.28, worst drop −24.9%; missed only deflated Sharpe 0.905 < 0.95: [ROUND12.md](reports/ROUND12.md) |
| Business | Sell the honest report ($9) + done-for-you strategy tests ($49) | ready to launch: [business/LAUNCH.md](business/LAUNCH.md) |

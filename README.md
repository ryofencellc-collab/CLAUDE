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
| Business | Selling a product/service | proposed: [BUSINESS.md](BUSINESS.md) |

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
| 13 | SPY core + multi-asset trend + crypto trend (24 configs, OOS 2012+) | **PASS (first in 269 trials)**: Sharpe 1.19 vs SPY 0.93, worst drop −20% vs −34%, deflated Sharpe 0.957; but $1,000 → $6,335 vs SPY $7,913, and the stress audit shows the pass leans on 2017 and 2020: [ROUND13.md](reports/ROUND13.md), [audit](reports/ROUND13_ROBUST.md) |
| 13-live | Round 13 forward paper test, $10k, daily | **running**: [paper/ROUND13_PAPER.md](paper/ROUND13_PAPER.md); 6-month gate before any real money |
| 14 | SPY options: 7 Cboe strategy indexes + 4 TikTok-style trades (weekly/0DTE calls, 0DTE condor, weekly puts) | **0/11 pass**: call buying went to $0 despite 11x and 25x winners; condors and put sales won 91% of the time but never beat SPY: [ROUND14.md](reports/ROUND14.md) |
| 15 | Kalshi weather "first money in" (buy outcomes already decided by station data, 22 cities, 12 months) | **FAIL**: 7,619 decided calls all correct, but prices were already 99c by the time public data confirmed them; $545/yr even at 100% capture: [ROUND15.md](reports/ROUND15.md) |
| 16 | Kalshi vs Polymarket cross-venue arbitrage | **dropped**: no reliably matched markets with both sides liquid: [ROUND16_NOTE.md](reports/ROUND16_NOTE.md) |
| 17 | Round 15 at up to 99c (taker) | **FAIL**: only 386 cheap sells of decided outcomes in 12 months: [ROUND17.md](reports/ROUND17.md) |
| 18 | Rest 99c bids on decided weather outcomes (maker; fills from lottery-ticket buyers) | **PASS (backtest)**: 0 wrong calls in 7,619, profit every one of 365 days, $23,981/yr at an assumed 25% queue share; queue position is unverifiable from history: [ROUND18.md](reports/ROUND18.md) |
| 18-live | Round 18 forward paper test, live order-book queue measured, every 10 min | **running**: [paper/ROUND18_PAPER.md](paper/ROUND18_PAPER.md); 30-day gate ($600, no losing fills) before real money |
| 19 | Round 18 trade on 29 more series: daily lows and the remaining daily highs (dev screen, 6-month holdout) | **PASS**: 22 series eligible, 99.98% of 4,059 holdout calls right, $2,697 in 6 months at 25% capture (≈ $15/day), 99% of days green: [ROUND19.md](reports/ROUND19.md); now in the paper bot as round 19 |
| 20 | Blind 98-99c maker bids on favorites, 60 Kalshi series, Apr–Sep 2026 | **FAIL**: +$44k at 25% capture over 5.1M fills, but 79% green days and a −$1.02M worst day (long-shot comebacks in huge fills). Fills <15 min before close made +$4.9M; ≥15 min lost −$4.8M (for games the close time is hindsight, so that split isn't tradable as is): [ROUND20.md](reports/ROUND20.md) |
| 21 | 99c maker bids on crypto markets already decided by the spot price (z ≥ Z from Binance; Z chosen Apr–Sep) | **PASS**: Z=6 chosen on dev; Oct holdout $16,255 in 27 days (≈ $600/day) at 25% capture with a 1,000-contract cap, 100% green days, 0 long-shot wins in 61,923 fills (KXBTC15M timed out, not included): [ROUND21.md](reports/ROUND21.md) |
| 21-live | Round 21 forward paper test, Coinbase spot, live queue, continuous | **running**: [paper/ROUND21_PAPER.md](paper/ROUND21_PAPER.md); +$118 in the first ~28 h, 39 filled markets, 0 losing fills; queue ahead ~20k contracts limits fills |
| 22 | Round 21 at 10k contracts on 15-minute markets (forward only, Oct 31–Nov 13) | **pre-registered**: [PROTOCOL_ROUND22.md](PROTOCOL_ROUND22.md); scored in the Round 21 paper summary |
| 23 | The portfolio: A Kalshi crypto (2,500/market) + B Round 13 + C football, with a risk engine (pause after a losing fill, daily stop, drawdown halving), Nov 2026 | **pre-registered**: [PROTOCOL_PORTFOLIO.md](PROTOCOL_PORTFOLIO.md); live: [paper/PORTFOLIO.md](paper/PORTFOLIO.md) |
| 24 | Round 21's rule on Kalshi S&P 500 / Nasdaq-100 binary options (5-min index bars; Z chosen Sep 3–Oct 9) | **PASS**: Z=2 on dev; holdout Oct 10–30 $475 in 15 trading days (≈ $32/day) at 25% capture, 100% green days, worst day +$4, long shots won 0.44% of fills; mostly hourly S&P (KXINXU): [ROUND24.md](reports/ROUND24.md) |
| 25 | Confidence-scaled sizing: reversal models from 2 yrs of Binance minutes (z-bin table, logit, GBM) × 91 sizing policies on Round 21 Kalshi fills | **PASS**: chosen 'z-bin Kelly, cap 0.95, risk < 0.3%'; Oct holdout $1k→$30.2k vs $4.1k for the live rule (25% capture, overstates capacity), 993 markets, 0 losses; dev had 3 losses, −14% max DD; model calibrated: [ROUND25.md](reports/ROUND25.md). Deployed to the live trader under Claude's stake cap |
| fill check | Recount of every paper fill from Kalshi trade records, only trades that can reach a 99c bid (15-minute markets quote 0.1c steps above 90c) | **15-minute profit was overstated**: ~$6,300 → $150–270 at 10k; hourly markets unchanged ($935 at 1k): [FILLCHECK.md](reports/FILLCHECK.md). Round 22/25 15-minute numbers overstate real fills |
| 26 | Live trader moves to the hourly crypto markets (whole-cent prices), z ≥ 6 on the smallest lead of 3 exchanges, Kalshi API V2 | **pre-registered**: [PROTOCOL_ROUND26.md](PROTOCOL_ROUND26.md); expectation ~$21/day on $1,000 (replay); 7-day dry run from Nov 8 must pass before any money |
| 26 backtest | Live bot (hourly, z ≥ 6, governor) vs earlier versions on Apr–Oct fills, one simulator copying the live bot | **helps**: the old live bot (Round 25 rule) loses with honest fills ($1k→$679, Oct) and hits its stops; the new version had 0 losses and no halts in dev and holdout; its $ here are understated (1 in ~350 hourly markets sampled): [ROUND26_BACKTEST.md](reports/ROUND26_BACKTEST.md) |
| 29 | Documented effects: crypto big-move reversal (1–4 h), intraday momentum (Nasdaq-100), overnight drift (SPY/QQQ/IWM); funding carry ruled out by research (~0–8%/yr in 2026) | **0/3 pass**: reversal lost in all 9 configs on 2024–25; momentum Sharpe 0.55; overnight Sharpe 0.59. All $0.10–0.34/day on $1,000: [ROUND29.md](reports/ROUND29.md) |
| 30 | Chart indicators (RSI 2/7, SuperTrend, EMA, momentum) vs Kalshi 15-minute BTC/ETH, beyond the price, 2026 holdout | **small signal, eaten by fees**: +$7.6k/+$9.6k before costs, −$432 (BTC) / +$1,152 (ETH) after taker fees on ~15k $10 bets: [ROUND30.md](reports/ROUND30.md) |
| 31 | Theory factory on Kalshi 15-minute crypto with REAL 1-minute quotes: price gaps (taker/maker), chart indicators, favourites, long shots, fades, jumps, time of day, RSI, cross-coin lead (37 configs, 23,100 markets) | **0/37 pass**: Kalshi 15-minute prices are well calibrated (80c → 80.6%, 95c → 96.8%); Kalshi beats our own fair-value model; buying long shots loses most: [ROUND31.md](reports/ROUND31.md) |
| 32 | Independent test of a TikTok "AP3X 2.0" grid bot (XRP/SOL futures, 1% × 50 levels, 20% margin), mark-to-market, every start since 2023 | **loses**: liquidated in 69–100% of runs; true equity up 8–24% (XRP) of runs; unleveraged grids show realized profit in 100% of runs yet lose money in most: [ROUND32.md](reports/ROUND32.md) |
| 33 | Price-honesty map of Kalshi: every category × hours-left × price band, tradable quotes only | **no edge**: no cell off by more than ~3c (t ≤ 1.2); buying at Kalshi's quote anywhere just pays the fee (dev window failed to load; holdout alone decides): [ROUND33.md](reports/ROUND33.md) |
| 34 | Whale autopsy: the 250 most profitable Polymarket wallets, by archetype | snipers (politics, $240M, not copyable), market makers ($200M, mostly sports), **late-favourite weather bots** ($18M, $5–20 trades, 850–2,500/day): [ROUND34.md](reports/ROUND34.md) |
| 34b | Trade-by-trade autopsy of 13 top Polymarket bots + the 99.9c "certainty snipe" (wallet 0x50f7, +$568k) replicated on Kalshi 15-minute crypto | **types**: sell-certainty bots (99.5c+ in the last minute), weather/tweet-count NO-buyers, crypto market makers, sports favourite modellers. **Kalshi copy fails**: −$28 to −$80 over 2–6k bets (99.6–99.9% wins; fee + rare loss eat the margin): [ROUND34B.md](reports/ROUND34B.md), [ROUND31.md](reports/ROUND31.md) |
| 35 | Calls & puts on REAL option prices (DoltHub EOD chains, SPY + 7 mega-caps, 2020–2026), $25k, natural fills: put/call credit spreads (trend, IV-rank, VIX filters; managed vs held), iron condors, breakout debit spreads, earnings iron flies/condors/straddles (21 configs) | **0/21 pass** (SPY held 16.8%/yr). Best: 16-delta SPY put spread above the 200-day, held to expiry — Sharpe 1.67 dev / 1.51 holdout, worst drop −6%, 93% wins, but only 6.9%/yr: [ROUND35.md](reports/ROUND35.md) |
| 37 | Beating retail crypto traders, 685 Binance USDT pairs: pump fade, dump bounce, new-listing fade, weekly reversal, momentum, BTC weekend (13 configs) | **1/13 pass**: shorting ≥ 30% pumps for 3 days, +78%/yr holdout (Sharpe 1.31, t 3.08) but −41% drawdown, weak dev, and not tradable from the US on small coins. Dump bounce loses badly: [ROUND37.md](reports/ROUND37.md) |
| 38 | Simple swing strategies, ≤ 3 trades/week (breakouts 20/55-day with 1R/2R/trailing exits, squeeze breakouts, RSI(2)/IBS/3-down/gap-down dip-buys) on ETFs, crypto, stocks (39 configs) | **0/39 pass**. Dip-buys win 56–65% of trades but make ~0 (losses bigger than wins). Best: crypto 55-day breakout + trailing stop, +112%/yr dev, +44%/yr holdout, Sharpe 0.96, −32% drop, 33% win rate: [ROUND38.md](reports/ROUND38.md) |
| 18/19-live | weather forward test | **failing**: 0 fills in 27 settled markets; incumbent 99c queues (10k–215k) exceed the later lottery flow |
| Business | Sell the honest report ($9) + done-for-you strategy tests ($49) | ready to launch: [business/LAUNCH.md](business/LAUNCH.md) |

# Round 37 pre-registration: beating retail crypto traders (all Binance USDT pairs)

Written 2026-11-08, before any data is fetched. Companion to Round 36 (stocks).

## Data
Every Binance spot USDT pair in the public archive (data.binance.vision), daily klines 2018 → 2026-10; stablecoin and
leveraged-token pairs excluded. Tradable on a day if 20-day average dollar volume ≥ $2M. Delisted pairs are included
while they traded (the archive keeps them), so survivorship bias is small here.

## Execution
Same engine as Round 36: signal at the daily close (00:00 UTC), enter at the next open, exit at the close of the
holding day; 10 slots of 10%. Costs 0.10% per side; shorts (perpetual futures) pay 10%/yr for funding/borrow.

## Tests (14 configs)
1. **Pump fade:** 1-day return ≥ +20% (and ≥ +30%) with volume ≥ 5× its 50-day average → short, H ∈ {1, 3, 7}.
2. **Dump bounce:** ≤ −20% with volume ≥ 5× → long, H ∈ {1, 3, 7}.
3. **New-listing fade:** short each new pair from its 4th day to its 30th day of trading.
4. **Weekly reversal:** weekly, long the bottom decile of 7-day return, short the top decile.
5. **Momentum:** weekly, long the top decile of 30-day return, short the bottom decile.
6. **BTC weekend:** long BTC from Friday's close to Sunday's close.

Dev 2019-01 → 2022-12, holdout 2023-01 → 2026-10. Pass: dev return > 0; holdout return > 0, Sharpe ≥ 1.0,
t-stat ≥ 3.0. Prediction written now: pump fade and new-listing fade are the strongest candidates.

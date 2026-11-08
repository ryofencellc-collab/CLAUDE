# Round 38 pre-registration: simple swing strategies, 2–3 trades a week, high win rate

Written 2026-11-08, before any data is fetched.

## Markets and data
Daily OHLCV (Yahoo for stocks/ETFs, Binance archive for crypto):
- **Stocks:** the NASDAQ Trader universe (Round 36), tradable when price ≥ $10 and 20-day dollar volume ≥ $20M.
- **ETFs:** SPY, QQQ, IWM, DIA and the 11 SPDR sector ETFs.
- **Crypto:** 30 large Binance USDT pairs (BTC, ETH, SOL, XRP, BNB, DOGE, ADA, AVAX, LINK, DOT, LTC, TRX, MATIC/POL, ATOM,
  NEAR, UNI, ETC, FIL, APT, ARB, OP, INJ, SUI, AAVE, BCH, XLM, HBAR, ICP, RNDR/RENDER, TON where available).
Dev: stocks/ETFs 2015–2021, crypto 2019–2022. Holdout: stocks/ETFs 2022–2026, crypto 2023–2026.

## Execution (all strategies)
Signal at the daily close → enter at the next open. Stops and targets are checked against each day's high/low; if
both are touched the same day the **stop counts first**; a gap through a stop fills at the open. Costs 0.10% per
side (stocks/ETFs: spread + slippage; crypto: taker fee + slippage). At most **3 new trades per calendar week** and
**5 open at once**; when more setups appear the strongest is taken (rank below). Position size: risk R% of equity
to the stop (R ∈ {1%, 2%, 5%}, gross exposure capped at 100%); strategies without a stop use 20% of equity a trade.
R changes size, not the edge; the pass test uses R = 2%.

## Strategies (per market: stocks, ETFs, crypto)
Breakouts (rank: relative volume):
- **B1** close > 20-day high, volume ≥ 1.5× 50-day average; stop 1.5×ATR(14); exit at **+1R**, **+2R**, or **trailing**
  (close < 10-day low); 20-day time stop. (3)
- **B2** same with 55-day high. (3)
- **B3 squeeze:** 20-day Bollinger bandwidth in its lowest 10% of the last 120 days, then close > 20-day high; stop
  1.5×ATR; exit +2R or trailing. (2)
Dip-buys in an uptrend (close > 200-day average; rank: most oversold):
- **D1** RSI(2) < 10 → exit when close > 5-day average (or 10 days). No stop. (1)
- **D2** RSI(2) < 5, same exit. (1)
- **D3** three lower closes in a row → exit at the first up close (or 5 days). (1)
- **D4** IBS < 0.2 (close in the bottom 20% of the day's range) → exit at the next close above the prior high (or 5 days). (1)
- **D5** gap down ≥ 2% at the open → buy the open, sell the close. (1)
That is 13 per market × 3 markets = 39 configs.

## Pass (each config, holdout, R = 2%)
Return > 0 on dev and holdout; holdout Sharpe ≥ 1.0; t-stat of mean trade return ≥ 3.0; ≥ 1 trade a week on average.
Reported for everyone: trades/week, win rate, average win and loss in R, expectancy, worst drawdown, $/day on $25k
and $1k at 1%, 2% and 5% risk. "High win rate" (≥ 60%) is shown but is **not** a pass criterion: a high win rate with
small wins and big losses is how accounts die.

Prediction written now: dip-buys in uptrends (D1/D2/D4) on ETFs have high win rates and positive but modest returns;
breakouts win less often; nothing reaches $100/day on $1,000.

## Result (2026-11-08, reports/ROUND38.md): 0 of 39 pass

- **High win rate did not mean profit.** Every dip-buy (RSI(2), IBS, 3 down days) won 56–65% of its trades, yet made
  roughly nothing on ETFs (−4% to +1%/yr), little on stocks (−12% to +4%) and modest amounts on crypto (+3% to +11%):
  the average loss (−4.5% to −6.5%) is bigger than the average win (+3% to +4.5%).
- **Best: crypto 55-day breakout with a trailing stop** — dev +112%/yr, holdout +44%/yr, Sharpe 0.96, worst drop
  −32%, but it wins only **33%** of trades (avg win +31%, avg loss −9.5%) and trades ~1×/week. Fails on Sharpe (0.96
  < 1) and t-stat (1.89 < 3). The 20-day version: +158% dev / +35% holdout, −54% drop. Classic trend-following:
  few big winners, many small losers.
- **ETF breakouts and dip-buys:** all within about ±4%/yr.
- **Stock breakouts lose heavily** (−23% to −35%/yr holdout). Caveat: the stock data has the same adjusted-price /
  survivorship issue found in Round 36 (small caps that reverse-split pass the $10 filter); a strict rerun would be
  needed before reading the stock numbers literally.

## Stocks rerun on clean prices (2026-11-08)
The stock section used Yahoo prices whose "unadjusted" close is split-adjusted (Round 36's artefact). The stock part is
rerun with returns from split/dividend-adjusted prices and the price filter on the price that actually traded (split
history undone); report: reports/ROUND38_stocks.md. ETF and crypto results are unaffected.

### Stocks on clean prices: 0 of 13 pass (reports/ROUND38_stocks.md)
Best: IBS < 0.2 dip-buy in uptrends, −0.1%/yr dev, +12.2%/yr holdout (61% wins, Sharpe 0.76, −13% drop) — flat on dev,
so not stable; SPY made 10.9%/yr on the same holdout. Other dip-buys ~+2%/yr. Breakouts lose (−10% to −20%/yr) or ~0
with a trailing stop.

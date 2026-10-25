# I Let an AI Test 206 Trading Strategies. Here's What Actually Made Money.

*An honest, reproducible test of the strategies sold on TikTok, YouTube and
Reddit, run with the same rules a hedge fund would use to check its own work.*

---

## Why this exists

Every week another video promises a strategy with a "70% win rate" or "$100k
in 3 weeks". Almost none of them show you a test you could check. So we gave
an AI one job: find a strategy that makes money, **prove it**, and report the
result honestly even if the answer is "no".

The rules were written down *before* any data was looked at, and committed to
a public log so they couldn't be changed after the fact:

- Every strategy is tested on data it was **never tuned on** (the "holdout").
- **Every fee and every bit of slippage** is charged.
- The more strategies you try, the more likely one looks good by luck, so
  results are corrected for **every** strategy tried, not just the winners.
- The tester itself is checked twice: it must find **nothing** in random
  data, and it must **find** an edge we plant on purpose.

## The scoreboard

| Round | What was tested | Strategies | Passed |
|---|---|---:|---:|
| 1 | Crypto & stock classics: trend, momentum, mean reversion, funding carry, VIX, rotation | 61 | 0 |
| 2 | The viral TikTok NQ futures strategy, opening-range breakout, football betting, Polymarket | 105 | 0 |
| 3 | Football "value betting", **live paper test** | 1 | running |
| 4 | "Beat retail": fade the crowd, follow the whales, hunt stop-losses | 10 | 0 |
| 5 | Kalshi weather markets with 5 forecast models | 24 | 0 |
| 6 | Selling weekly Bitcoin options | 3 | 0 |
| 7 | Arbitrage: Kalshi brackets, cross-exchange funding, pairs trading | 8 | 0 |

## What we learned (the part worth paying for)

### 1. A high win rate is not profit
Buying the "near-certain" side of prediction markets **won 95–97% of the time
and still lost money**: each win paid 3–5¢, each loss cost 95¢. Football
favourites won 83% of bets and broke even. If a strategy is sold on its win
rate, ask for its **profit per trade after fees**. That's the only number
that matters.

### 2. The viral TikTok NQ strategy didn't survive contact with data
We turned the popular "fair value" 1-minute NQ setup into exact rules and
ran 72 versions on **14 years of 1-minute Nasdaq data (4.75 million bars)**.
**Zero** made money in 2012–2022. In 2023–2026 the best version was roughly
break-even. Win rates of 36–46% versus the ~42% needed just to cover costs.
The results you see online depend on hindsight and discretion that can't be
tested.

### 3. Edges that everyone knows about get competed away, and we watched it happen
The classic crypto "cash-and-carry" trade earned **+20% in 2021**, then decayed
to about **+2% a year by 2026** as large funds piled in. That's what any edge
looks like once it's famous.

### 4. "No emotions" isn't an edge
All 206 strategies were run by a machine with zero emotion and perfect
discipline. That buys consistency, not profit. A rule with no edge, followed
perfectly, just loses consistently.

### 5. Trading against retail traders didn't pay either
We used real data on what retail traders hold (Binance long/short ratios) and
where their stops sit. Fading the crowd made **+24% in 2022–23**, then
**lost 11% in 2024–26**. Stop-hunt reversals lost money in every version.
The people who reliably profit from retail flow are market makers and
exchanges, earning the spread rather than betting on direction.

### 6. Weather markets are priced by people with better data than you
Kalshi's daily temperature contracts looked like the perfect "beat retail
with data" market. A model using five professional forecast systems still
**lost 17–19% per bet**: by the morning, the market already knows the
overnight model runs and real temperatures.

### 7. "Profitable every week" is a warning sign, not a feature
Selling a Bitcoin put 10% below the price every Friday **won 96% of weeks**
from 2024 to 2026 and **made −0.3% in total**. A few crash weeks (−34% in
March 2020, −21% in June 2022) wiped out years of small wins. Strategies
that "print daily" are usually quietly selling crash insurance.

### 8. Arbitrage exists, until it doesn't
A cross-exchange funding trade (Hyperliquid vs Binance) earned **~11% a year
with a Sharpe ratio of 12** in 2023–24, about as close to "printing money"
as a strategy gets. In 2025–26 it **lost 0.3%**. Buying every bracket of a
Kalshi weather market for under $1 (a guaranteed profit) happened **0 times
in 1,081 events**. Real arbitrage is found by whoever is first and fastest,
and it closes fast.

### 9. The one lead: small, slow, and unproven
Betting football matches only when a bookmaker's price beats the sharp
exchange price made about **+3.5% to +4.7% per bet** in past seasons. That's
about $300–440 a season on a $1,000 bankroll at $10 bets. 56% of months were
profitable, and the worst losing streak would have wiped out a $1,000 account
at $10 stakes. It is now being **paper-traded live**, with every bet
timestamped before kickoff.

## How to test any strategy yourself (the checklist)

1. **Write the rules down before testing.** If you change them after seeing
   results, you're measuring your own hindsight.
2. **Split your data.** Tune on the old part; judge on the newer part *once*.
3. **Charge real costs.** Futures: ~1.25 index points per round trip on NQ.
   Crypto: ~0.1% per side. Betting/prediction markets: the fee schedule.
4. **Count every version you tried.** Testing 50 variations and keeping the
   best one is how most "80% win rate" backtests are made.
5. **Test it on random data.** If your "edge" also appears on shuffled
   prices, it's an illusion.
6. **Paper trade forward before risking money**, with entries logged *before*
   the outcome is known.
7. **Size for the worst streak, not the average.** Most strategies with a
   real edge still have losing runs long enough to bust a small account.

## Red flags in strategy marketing

- Win rate quoted without average win/loss size.
- Results shown only from the last few months (a bull market makes everything
  look good).
- No mention of fees, slippage, or how many variations were tried.
- "Funded account" payouts with no mention of how many evaluations failed.
- Any claim that a strategy is "profitable every day".

---

### Appendix: method and code

Every test, rule, data source and result is in a version-controlled
repository with timestamps. Data: Binance public archive, Yahoo Finance,
HistData (14 years of 1-minute Nasdaq-100), football-data.co.uk (22 leagues),
Polymarket, Kalshi, Open-Meteo/NOAA, Deribit. Statistics: holdout testing,
Deflated Sharpe Ratio (Bailey & López de Prado), bootstrap significance with
Bonferroni correction across all trials, null and power tests.

*This report is educational. It is not financial advice, and it makes no
promise that any strategy will make money. Its main finding is that most
don't.*

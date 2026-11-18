# Autonomous research loop (charter, 2026-11-18)

**Mandate from the user:** "Full autonomy. Find a money-making thing in any category, something a human wouldn't easily guess.
Prove it works first. $1k–$10k scale."

**Loop.** A recurring check-in every 3 hours does this:
1. Fix anything broken.
2. Take the top idea from the backlog below.
3. Pre-register it as a `PROTOCOL_ROUNDxx.md` (dev/holdout, or a locked final exam for big searches).
4. Calibrate on synthetic data (a null finds nothing, a planted edge is found).
5. Run on GitHub Actions and record the verdict in the README.
6. Promote or kill the idea.

The loop also adds new ideas, ranked by (chance of a real edge) × (testability with free data) ÷ (cost to build).

**Promotion ladder.**

| Stage | What happens | Gate to the next stage |
|---|---|---|
| Backtest | the pre-registered test | pass |
| Live paper | real quotes, real fills | 20–40 days with a positive lower bound |
| Real money | only inside a budget the user sets; never without one | positive with real fills |
| Scale | bigger stakes | — |

"Proof" means positive live results with real fills, not a backtest.

**Hard limits.**
- No account creation and no purchases.
- Secrets live only in GitHub secrets.
- No circumventing site blocks or terms.
- No real-money orders without an explicit budget from the user.

**Lesson of rounds 1–56.** Rules that predict prices from price bars don't beat costs. Edges that survived (rounds 18, 19, 21, 24, 45) are
*structural*: you are paid for providing liquidity, or the outcome is already (nearly) determined by public data that the market prices slowly.
The backlog therefore favours **"nowcast" markets**: contracts whose outcome is a public statistic that is largely predictable from data
released *before* the market closes, and that most traders don't track.

## Backlog (ranked)
- [ ] **62 Mention markets.** Kalshi "will <speaker> say <word>" markets (Fed press conferences, etc.) vs base rates from public transcripts.
  Hypothesis: market makers misprice rare and common words relative to how often the speaker actually says them. Free data: federalreserve.gov transcripts.
- [x] **57 Nowcast markets — gas: FAIL** (Round 57: market 3× more accurate than the nowcast; TGA/jobless markets have ~0 trades; mortgage only 9 events). Original idea:.** For Kalshi markets on weekly or monthly public statistics, measure how well a simple nowcast from earlier
  public data predicts the outcome, compared with the market price at the same moment.
  - **Statistics:** TSA checkpoint throughput (tsa.gov daily), AAA/EIA gas prices (daily/weekly), jobless claims (FRED), CPI (Cleveland Fed nowcast),
    GDP (Atlanta Fed GDPNow), mortgage rates (Freddie Mac), unemployment and payrolls.
  - Step 1 is the probe: list the series, count settled markets, check the data sources.
- [ ] **58 Chart/streaming nowcasts.** Spotify daily streams (kworb) → Billboard / Spotify weekly #1 markets; box-office tracking → opening-weekend markets.
- [ ] **59 Prediction-market lead-lag.** Do Polymarket moves predict Kalshi moves on the same event (or the reverse) within minutes? Signal only, not arbitrage
  (Round 16 found too few matched liquid pairs for arbitrage).
- [ ] **60 Prediction markets → stocks.** Do jumps in Kalshi/Polymarket Fed, CPI or election odds lead sector ETFs intraday?
- [ ] **61 Liquidity programs elsewhere.** Polymarket's liquidity rewards, run as paper market making, if Round 44b passes on Kalshi.

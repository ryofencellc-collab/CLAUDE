# Round 55: 2-year model backtest of the Reddit 0DTE SPX iron butterfly (written 2026-11-18, before any results)

**Source:** u/NeitherPossession288 on r/options. It sells an ATM iron butterfly on 0DTE SPX at 14:50 ET with ±$15 wings, takes profit
at 15% of the credit, skips FOMC days, and runs Aug 2024 → Aug 2026. The post claims +$95,620 on 4 lots, a 78% win rate and Sharpe 2.59.

**Problem:** free intraday SPX option history doesn't exist. **Method:**
- **Path:** the real SPX 1-minute path (HistData SPXUSD).
- **Pricing:** the butterfly is priced each minute with Black-Scholes at one implied vol per day: σ = c × VIX1D(prior close).
  VIX1D's prior close is known before the entry.
- **Calibration:** c is calibrated on our **real recorded Cboe quotes** (`data/odte`). On every collected day, the implied vol solves for the real mid credit at
  14:50 ET (corrected clock), and c = median(σ_real / VIX1D_prior). The calibration error is reported per day, along with the model vs real P&L
  on the same days.
- **Costs:** $0.20 per round trip of the whole fly on entry and again on a take-profit exit (from the real bid/ask vs mid gap,
  about $0.15–0.25), plus $1.50 per leg per side.

**Pass:** all four must hold.
1. Mean P&L per lot > 0 with t ≥ 3 over 2024-08 → now.
2. Both halves positive.
3. Calibration: median |model credit − real credit| / real credit ≤ 10%.
4. Robust to c ± 10%: still positive at c × 0.9.

Sensitivity rows (no take-profit; 14:00 or 15:15 entry; mid fills) are reported but do not count toward the pass.

**Known model limits:**
- A flat smile: no skew, and a constant σ through the last 70 minutes.
- The SPXUSD CFD stands in for the SPX cash index.

Both are tested only via the calibration days. A pass means "worth live paper trading" (F1 is already live in Round 39b), not "proven".

## Result (2026-11-18): **FAIL** (`reports/ROUND55.md`)
- **Calibration** passed: c = 0.523 from 7 real days, median credit error 9.3%.
- **As posted**, 2024-08 → 2026-10, 539 trades: a 79% win rate, matching the post's 78%, but **−$15 per lot per trade** (t −1.3). The second half lost.
- **With mid fills** the strategy roughly breaks even (+$2 per lot). The posted +$200 per trade on 4 lots (+$50 per lot) is not reproduced.
- **Model sensitivity:** a ±10% change in the vol scale swings the mean between −$31 and −$1, so even the sign is within model error. That is no edge.
- **Take-profit:** with no take-profit the strategy makes +$31 per lot at t 1.5, which is not significant. The 15% take-profit cuts winners short while losers run to −$900.
- F1 continues live in Round 39b with real quotes; that is the deciding test.

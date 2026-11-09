# Round 40 pre-registration: how often does a "decided" hourly crypto market (z ≥ 6) actually lose?

Written 2026-11-09, after the Nov 8 22:00 UTC crash (paper −$3,846) and before any of this data is fetched.

The live rule bids 99c whenever z = ln(spot/strike) / (σ₁ₘ·√minutes-left) ≥ 6, σ₁ₘ = std of the last 60 one-minute
log returns. Under a normal model z ≥ 6 loses about once in a billion. A 99c bid breaks even at a loss rate of ~0.98%
(win 1c minus the maker fee, lose 99c). The rule was never measured on long history for hourly markets.

**Data:** Binance 1-minute closes, BTC/ETH/SOL/XRP USDT, 2020-01 → 2026-10. Dev 2020–2023, holdout 2024–2026-10.
**Sample:** every minute e with 1–59 minutes to the next top of the hour H. Settlement ≈ mean of the closes at H−1m and
H (the CF RTI averages the last 60 s). r = ln(settle/spot_e) / (σ₁ₘ,e·√τ). A bet whose strike sits at z loses when the
price ends on the other side: r < −z (YES-above) or r > z (NO), so the per-side loss rate is P(|r| > z)/2.
**Reported:** loss rate at z = 6, 8, 10, 15, 20 by coin, period and minutes-left bins (1–5, 6–15, 16–30, 31–59); the
number of distinct losing hours; expected cents per contract = 1·(1−p) − 99·p − fee.

**Adverse selection (from the forward paper, not history):** fills arrive when sellers dump into a move toward the
strike, so the loss rate *given a fill* is higher than the unconditional one. The paper's contract-weighted loss rate
(lost contracts / filled contracts) is reported beside the historical figure.

**Pass (the hourly rule may go live only if all hold):** holdout per-side loss rate at z = 6 below 0.5% (half the
breakeven) for every coin; the same at the paper's actual entry mix; and the paper's contract-weighted loss rate below
1%. Otherwise the rule is not funded. If a stricter threshold z* passes on dev, it is checked once on the holdout and
then needs a fresh forward test before money.

## Result (2026-11-09): **FAIL** (`reports/ROUND40.md`)
On six years of 1-minute data, a random z ≥ 6 bet loses only **0.05–0.10%** of the time in the holdout (breakeven
0.98%). The z-rule itself is sound. But the bids that actually *get filled* lose **3.21%** of the contracts (paper,
Oct 29 → Nov 9), 30× the base rate and 3× breakeven. A 99c bid sits behind a large queue, and it only reaches the
front when someone sells hard into a move toward the strike. That is the adverse selection: fills are not a random
sample of decided minutes, they are concentrated in the crashes. This is structural (it comes from who trades with us),
so no z threshold fixes it from the data in hand. Per the rule above, the hourly 99c bot is **not funded**.

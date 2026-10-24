# Round 6 results: selling a weekly Bitcoin put

Rules: [PROTOCOL_ROUND6.md](../PROTOCOL_ROUND6.md). Run
[40127349113](https://github.com/ryofencellc-collab/CLAUDE/actions/runs/40127349113).
Real Deribit option trades, 394 Fridays 2019-04 → 2026-10. Cash-secured,
no leverage, Deribit fees, 5% haircut for selling at the bid. Cumulative
trials: 199.

**Verdict: fail.** Selected on in-sample Sharpe: the 10%-below-spot put.

| Strike | Winning weeks (holdout) | In-sample 2019–23 | Holdout 2024–26 | $1,000 → (holdout) | Worst week | Max drawdown (holdout) |
|---|---:|---:|---:|---:|---:|---:|
| 5% below | 88% | +76% (Sharpe 0.57) | +13% (Sharpe 0.35) | $1,132 | −16% | −28% |
| **10% below** *(selected)* | **96%** | +68% (Sharpe 0.61) | **−0.3%** (Sharpe 0.05) | **$997** | −13% | −20% |
| 15% below | 98% | +28% (Sharpe 0.40) | +1.0% (Sharpe 0.10) | $1,010 | −7% | −11% |

## The "prints every week" trap, measured

The selected strategy won **96% of weeks** in the holdout and made
**nothing**: 2.7 years of small wins were erased by a handful of crash weeks.
Worst weeks for the 10% put: March 2020 (−34% in one week), June 2022
(−21%), January 2026 (−13%). Even the best holdout version (+13% over 2.7
years, about 4.7% a year) roughly matched T-bills, with a 28% drawdown.

By year (10% put): 2019 +21%, 2020 −1%, 2021 +26%, 2022 +1%, 2023 +11%,
2024 +17%, 2025 −7%, 2026 so far −8%.

Option buyers aren't overpaying by enough. The premium roughly prices the
crash risk, which is what an efficient market would do.

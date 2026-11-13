# Strategy factory: one standing protocol for every strategy it tests

Written 2026-11-13, before the factory's first run. Each batch of strategies is listed in `edge/factory_strats.py`
with the date it was added, before it runs.

**Data.** US stocks: the Round 38 panel (current listings since 2014, adjusted OHLCV; tradable when the real price is
≥ $10 and 20-day dollar volume ≥ $20M; *survivorship bias flatters long-only stock strategies*). ETFs and indexes:
Yahoo, adjusted. Crypto: Binance daily.
**Engine.** Each strategy outputs daily target weights. A weight decided at day t's close is traded at day t+1's close,
so it earns from t+1 to t+2 (one-day delay, no look-ahead). Costs per unit of turnover: stocks/ETFs 0.10%, crypto
0.25%. Leverage is allowed only where the strategy says so, and pays 6%/yr on the borrowed part.
**Periods.** Dev 2015–2021, holdout 2022 → today (crypto: dev 2018–2021).
**Measured (ROI first).** CAGR, Sharpe, worst drawdown, and the asset-class benchmark (SPY, an equal-weight stock
universe, or BTC) over the same days.
**Pass (all required).** Holdout CAGR ≥ 15%; holdout Sharpe ≥ 1.0 and above the benchmark's; worst holdout drop
no deeper than −25%; dev Sharpe ≥ 0.5; deflated Sharpe ≥ 0.95 on the full sample across *every* trial the factory has
run so far (the bar rises as more is tested). A pass goes to the forward paper tracker; nothing is funded on a
backtest alone.

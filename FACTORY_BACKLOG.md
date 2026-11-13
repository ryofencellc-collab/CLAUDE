# Factory backlog (worked top-down by the recurring check-in; each batch is registered in edge/factory_strats.py before it runs)

Already covered elsewhere (do not repeat): rounds 1–49 in README.md (trend/breakouts/dip-buys, insider buys, Congress/13F
copying, wheel, put spreads/condors, 0DTE forward, Kalshi maker/LIP, arbitrage, crypto pump-fade/reversal/funding).

## Batch 2 — stock anomalies (daily panel)
- [ ] Industry momentum proxy (rank by 6m return of 20-stock price-correlation clusters)
- [ ] Idiosyncratic-volatility low decile (residual vs equal-weight market, 60d)
- [ ] Betting-against-beta long leg (lowest 60d beta decile)
- [ ] Time-series momentum on each stock (hold if 12m return > 0), equal weight top liquid 200
- [ ] Gap-fill: buy liquid stocks gapping down ≥ 3% at open, sell same close (needs O; open-to-close)
- [ ] Overnight-return momentum (rank by cumulative overnight returns 1m)
- [ ] Volume-shock reversal (abnormal volume + down day, 5-day hold)
- [ ] Earnings-season seasonality proxy (same-month-last-year return, Heston–Sadka)
- [ ] Dollar-volume (liquidity) premium: least liquid decile within the tradable set

## Batch 3 — ETFs / macro
- [ ] Risk parity SPY/TLT/GLD/DBC (inverse vol, monthly), 1x and 1.5x
- [ ] Defensive asset allocation (Keller DAA / VAA canary rules)
- [ ] Bond/stock momentum switching (SPY vs TLT by 3m)
- [ ] VIX term structure: hold SPY when VIX < VIX3M, else IEF
- [ ] FOMC pre-announcement drift (SPY day before FOMC; dates from federalreserve.gov calendar)
- [ ] Pre-holiday SPY
- [ ] Leveraged ETF decay short proxy / long-short pair (needs borrow; paper only)
- [ ] Gold/miners ratio, copper/gold timing for SPY

## Batch 4 — crypto
- [ ] Weekend effect long/short BTC, time-of-day (hourly) seasonality
- [ ] BTC dominance rotation (alts vs BTC by 30d)
- [ ] Funding-rate extremes as contrarian timing (spot only)
- [ ] Stablecoin supply growth as BTC timing

## Batch 5 — options (EOD chains, SPY + 7 mega-caps)
- [ ] Covered calls on SPY only when IV rank high
- [ ] Long straddles before earnings (IV ramp) closed before the event
- [ ] Put-write index replication (PUT index style) vs SPY
- [ ] Calendar spreads around earnings

## Batch 6 — prediction markets (Kalshi history)
- [ ] Favourite-side maker by category beyond Sports/Entertainment (Round 45 cells) — forward variants
- [ ] Mentions markets: base rates vs price
- [ ] Economic data markets vs Cleveland Fed nowcast (CPI)

## Ideas from outside sources (Reddit via the official API once REDDIT_CLIENT_ID/SECRET exist; otherwise user-pasted)

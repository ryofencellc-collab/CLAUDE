# Round 48 pre-registration: insider buying from SEC Form 4 filings (the "news" round)

Written 2026-11-12, before the data is fetched.

**Why.** It's the best-documented free news signal with complete history. Officers and directors buying their own
stock in the open market predict abnormal returns, most strongly for "opportunistic" buys and clusters of several
insiders (Lakonishok–Lee 2001; Cohen–Malloy–Pomorski 2012; Alldredge–Blank 2019). Prior rounds tested Congress and 13F
copying (Round 8) but never Form 4 insider purchases.

**Data.** SEC "Insider Transactions Data Sets" (Forms 3/4/5, quarterly, 2015Q1 → 2026Q3): open-market purchases
(transaction code P, acquired) of common stock, with filing date, issuer ticker, insider relationship/title, shares
and price. Prices come from the Round 38 Yahoo panel of current US listings, so delisted names are missing: a
survivorship bias that flatters results, stated here in advance. Entry is at the open of the first trading day after
the filing date (the filing is public on that date). Costs per side: liquid tier 0.10%, small tier 0.30%.
**Tiers.** Liquid: real price ≥ $10 and 20-day dollar volume ≥ $20M. Small: real price ≥ $5 and ≥ $1M.
**Rules** (each in both tiers; one trade per issuer per 30 days per rule):
- I1: any officer/director purchase ≥ $50k, hold 21 trading days.
- I2: the same, hold 63 days.
- I3: cluster, ≥ 3 different insiders buying within 30 days (entry after the 3rd filing), hold 63 days.
- I4: CEO or CFO purchase ≥ $100k, hold 63 days.
**Measured.** Return per trade net of costs, and excess over SPY for the same days. Equal-weight portfolio at 5% per
position, at most 20 open, taking the largest purchases first.
**Pass.** Holdout (2022 → 2026-10) mean excess return per trade ≥ +1% with t ≥ 3 (clustered by filing week), dev
(2015–2021) mean excess > 0, and holdout portfolio Sharpe ≥ 1 with CAGR ≥ SPY's + 5 points. A pass goes to forward
paper trading from live Form 4 filings.

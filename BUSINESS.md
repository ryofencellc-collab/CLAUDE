# Track 3: making money by selling something

Trading asks "can Claude out-predict markets full of professionals?" A
business asks "can Claude build something people pay for?" The second is
where AI has real leverage: it can write software, content and marketing
fast and at almost no cost. It needs a human for the parts an AI can't do:
owning accounts, taking payments, legal identity, and pressing "publish".

## Rules, same spirit as the trading protocol

- Budget: the same $1,000 test fund. Nothing is spent without the owner
  approving the specific spend.
- Success = **net profit** (revenue − all costs, including ads, fees and
  tools) > $0 within 90 days, then repeatable at 10× spend.
- Every dollar in and out is logged in `business/ledger.csv` (append-only,
  in git).
- Nothing deceptive: no fake reviews, no impersonation, no "get rich"
  claims, no reselling other people's content.

## Candidate ideas, ranked by how fast they can be tested for under $100

| # | Idea | Why it might work | Test for < $100 | Kill signal |
|---|---|---|---|---|
| 1 | **Backtest-as-a-service for retail traders.** People like the TikTok audience pay to know whether a strategy actually works. | The demand is visible: thousands of "does this strategy work?" posts. This repo already contains the engine. | Landing page and a $29 "I'll backtest your strategy honestly" offer, promoted with one Reddit/TikTok post showing this experiment's real results. | < 3 paid orders after 500 visitors |
| 2 | **Niche digital templates or tools** (Notion/Sheets trading journals, prop-firm rule calculators) | Low price, instant delivery, sold on Gumroad or Etsy, AI builds them in hours | 3 products listed for $9–19 | < $50 revenue in 30 days |
| 3 | **Small paid browser extension or web tool** (e.g. prop-firm drawdown tracker) | Recurring revenue, AI can write all the code | Free version first, paid tier at $5/mo | < 100 installs in 30 days |
| 4 | **Content site with honest strategy tests** (ads and affiliate) | Each Round 1/2 result is a ready-made article: "I tested the TikTok NQ strategy on 14 years of data" | Publish 5 write-ups from this repo | < 1,000 visits in 60 days |

Idea 1 turns this experiment itself into the product: the most credible
thing anyone can sell to retail traders is an honest test, and that's
exactly what this repo does.

## What the owner has to do (AI can't)

1. Pick an idea (or veto all).
2. Create the seller account (Gumroad/Stripe/Etsy) in their own name.
3. Approve any spend, and post or approve any public marketing.

Claude does the rest: build the product, write the listing and copy, set
up the landing page, track the ledger, and report honestly.

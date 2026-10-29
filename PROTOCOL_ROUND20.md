# Round 20 pre-registration: blind 98–99c maker bids on Kalshi favorites

Written 2026-10-29, before any Round 20 code ran.

## Discovery (probe19c, not a test)

A scan of every public Kalshi trade in 6 random hours of the last 30 days
found about 41,000 fills where a taker bought a long shot at 1–2c. In
15-minute crypto markets, 0 of 23,160 long shots won; in 15-minute
commodity markets, 0 of 1,842. Other series were similar.

The probe was capped at 60 pages per hour, so its dollar sizes are rough.
It chose this round's universe.

## The trade

Rest a bid at 98–99c for the favorite. Each public trade where a taker buys
the other side at price px ≤ 2c fills us at 1 − px; we take **25%** of it.

After settlement we earn px per contract if the long shot loses, and lose
1 − px if it wins. The maker fee 0.0175 × C × P × (1 − P) is rounded up to
the cent **per fill**, so tiny fills earn nothing.

**No outcome knowledge is used:** every long-shot win is counted as our loss.

## Universe

Every non-combo series with at least 20 fills in the probe's printed lists
(46 series; the multi-leg KXMVE combos are excluded because they are quoted
by request and can't hold resting bids):

- 15-minute crypto: BTC, ETH, SOL, XRP, DOGE, HYPE, NEAR, ZEC, BNB.
- 15-minute commodities and FX: gold, silver, oil (WTI), natural gas,
  copper, platinum, palladium, EUR/USD.
- Daily or range crypto: KXBTCD, KXETHD, KXBTC, KXSOLD, KXXRPD.
- Tennis: KXWTAMATCH, KXITFMATCH, KXITFWMATCH, KXATPCHALLENGERMATCH.
- Golf: KXPGAR1LEAD, KXPGATOUR.
- Soccer: KXUEFANLGAME, KXUEFANLTOTAL, KXINTLFRIENDLYGAME, KXEWSLGAME,
  KXURYPDGAME, KXJ2LEAGUEGAME, KXCANPLGAME.
- Football: KXNFL1H, KXNFL1HSPREAD, KXNFL1HTOTAL.
- Esports: KXLOLGAME, KXCS2GAME, KXCS2MAP.
- Other: KXTRUMPMENTION, KXTRUMPAPPROVE, KXRAIN, KXTEMPNYCHS, KXTEMPMIAH,
  KXHIGHCHI.

## Window

**2026-07-01 to 2026-09-29** (90 days). This ends before the probe's 30-day
window, so the test does not reuse the hours that suggested it.

## Pass rule (pooled, 25% capture, all must hold)

1. Net profit ≥ $3,000 over the 90 days (≈ $33/day).
2. Profitable on ≥ 80% of days.
3. Worst single day ≥ −$300.
4. Not fading: the last 30 days are ≥ 20% of the total.

Each series is also reported alone, together with its losses by minutes to
close, because a long shot that wins in the last seconds is the main risk.

## Smoke test first

KXBTC15M and KXWTAMATCH over 7 days: pipeline and loss counts only.

## Prediction written now

Long-shot wins will be rare, but not zero. Each one costs about 98c a
contract, so a single flip in a big BTC 15-minute fill can erase about 100
winning fills. I expect a pooled PASS with thin margins in crypto 15-minute
markets, and some sports series negative.

## Amendment 1 (2026-10-29, before any Round 20 result: the smoke test had not finished)

probe19b sized the hindsight long-shot pool per series over 30 days:

| Series | Pool |
|---|---:|
| KXNFLGAME | $1.23M |
| KXNBAGAME | $0.63M |
| KXMLBGAME | $0.54M |
| KXNHLGAME | $0.11M |
| KXHIGHNY (weather) | $21k |

The game series were missing from the universe because the 6-hour probe
missed them.

**Changes:**

- **Universe:** adds KXNFLGAME, KXNBAGAME, KXMLBGAME, KXNHLGAME,
  KXNCAAFGAME, KXEPLGAME, KXUCLGAME, KXUFCFIGHT, KXATPMATCH, KXMLSGAME,
  KXNFLSPREAD, KXNFLTOTAL and KXMLBTOTAL.
- **Window:** widens to **2026-04-01 to 2026-09-29** (182 days), so the NBA
  and NHL seasons are included.
- **Thresholds, scaled to the longer window:**
  1. net profit ≥ $6,000;
  2. profitable on ≥ 80% of days;
  3. worst day ≥ −$300;
  4. the last 60 days are ≥ 20% of the total.

## Amendment 2 (2026-10-29, implementation; the smoke test had shown WTA only)

The 15-minute series hit Kalshi's rate limit even for 7 days.

- **Sampling:** a series with more than 1,500 settled markets in the window is
  tested on an evenly spaced sample of 1,500 markets, ordered by close time.
  Its profit is scaled by the sampling step, and wins and losses are counted
  alike.
- **Request rate:** capped at about 8 requests a second per job.

Neither change touches the trade or the pass rule.

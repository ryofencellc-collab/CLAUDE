# Claude's operating rules for the live trader (written 2026-11-06, before any live trade)

The owner funds the account once with $1,000. Claude runs the bot by editing `control/live21.json`. The
running bot re-reads that file from GitHub every minute.

The owner keeps one override: setting the repository variable **`LIVE21` to `0`** forces dry run whatever
the file says. The owner also controls the account itself (deposits, withdrawals, keys).

## Going live: all must be true

1. Round 22's pre-registered paper gate passes at the end of its window (2026-11-13).
2. The 1c self-test passes on the real account.
3. At least 24 hours of dry run with the real keys: 0 errors, and its placements consistent with the paper
   bot's 15-minute placements.

## Stake (`stake_fraction` = share of the balance one market may use)

- First 14 live days: **0.5**, so one wrong fill cannot empty the account.
- After 14 live days with 0 losing fills and P&L ≥ 0: **0.95**.
- After any losing filled market: **0.25** for 14 days. This is on top of the bot's own 24 h pause and 7-day
  half size.

## Stopping (`stop` = true, which also sets `live` = false)

- The balance falls to ≤ 70% of the deposit ($700); or
- 2 losing filled markets within 7 days; or
- the live fill rate or P&L departs clearly from the paper bot for 7 days (worse than half of paper's P&L
  over the same markets); or
- anything unexplained in the logs (errors, orders the bot didn't place, mismatched positions).

Each change to `control/live21.json` is a commit with the reason in its message, so the decision trail is
public and auditable.

## Enforced by the bot itself (added 2026-11-07)

So the rules hold even when nobody is watching, `edge/live21.py` (`governor`) applies the stake and stopping
rules above every minute from Kalshi's own settlement records since `live_since`:

| Rule | Bot behaviour |
|---|---|
| First 14 live days | stake 0.5 |
| 14 days live, P&L ≥ 0, no loss in the last 14 days | stake 0.95 |
| A losing market in the last 14 days | stake 0.25 (plus the 24 h pause and 7-day half size) |
| Equity (deposit + settled P&L) ever ≤ 70% of the deposit | halt: pull orders, dry run, for good |
| 2 losing markets within 7 days | halt, for good |
| Kalshi settlements unreadable | keep the last answer; 0.25 until there is one |

The stake used is the smaller of the governor's and `stake_fraction` in the control file (Claude's cap).
A halt is recomputed from the whole history each minute, so it never wears off and survives lost state.

**Adding money (the $10k step):** set `deposit` to the new balance and `live_since` to that moment, in one
commit, with the reason. That starts a fresh history. It is never done to clear a halt.

The remaining stops (live vs paper drift, anything unexplained) stay Claude's judgment, reviewed daily.

# Going live with the Round 21/22 trader (edge/live21.py)

The trader is 1:1 with the paper bot: the signal code is imported from `edge/paper21.py`, not copied. It
trades only the 15-minute crypto markets, one position at a time.

| Guard | What it does |
|---|---|
| Order type | Post-only limit buy at 99c. It can only rest in the book; it never pays the spread. |
| Size | min(`LIVE21_MAX`, 95% of balance / 0.99). That's ~959 contracts on $1,000. |
| After any losing market | No new orders for 24 hours, then half size for 7 days. |
| Daily stop | No new orders after losing 10% of the day's starting balance. |
| Stale price data, or the price moves back | The order is cancelled. The loop runs every ~5 seconds. |
| Startup | Cancels any leftover order of ours. |
| Errors | Logged, and the open order is pulled. |
| Kill switch | Commit an empty file `paper/LIVE21_STOP`, or set `LIVE21` to `0`. |

## Steps (only after the Round 22 paper gate passes on Nov 13)

1. **Kalshi account.** Sign up at kalshi.com (US resident, ID check), then deposit **$1,000** by bank
   transfer.
2. **API key.** Kalshi → Account → **API Keys → Create key**. Copy the **Key ID** and download the
   **private key** (`.pem` file). Kalshi shows the private key only once.
3. **GitHub secrets.** Repo → Settings → Secrets and variables → Actions → **New repository secret**:
   - `KALSHI_KEY_ID`: the key id;
   - `KALSHI_PRIVATE_KEY`: the full contents of the `.pem` file, including the BEGIN and END lines.

   I never see these.
4. **Self-test, at most 1c of risk.** Actions → **live21** → Run workflow → `selftest` = `1`. Check the
   log for `selftest OK`.
5. **Dry run, 1–2 days.** Leave `LIVE21` unset. The trader logs every order it would send to
   `paper/LIVE21.md` and `paper/live21_log.csv`, using your real balance. I compare it against the paper
   bot.
6. **Go live.** Settings → Secrets and variables → Actions → **Variables** → `LIVE21` = `1`. Optional:
   `LIVE21_MAX` = the most contracts per order (default 1000).
7. **Scale.** After about 2 clean weeks, deposit more and raise `LIVE21_MAX`, for example to 10,000 at
   $10k.

## Cashing out

Kalshi → Withdraw to your bank. Only you can do this, and profits are taxable.

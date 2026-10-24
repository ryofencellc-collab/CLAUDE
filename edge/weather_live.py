"""Live paper trader for Kalshi daily-high markets (PROTOCOL_ROUND5.md, "Forward test").

Run hourly. For each city, the first run at/after 09:00 local (before 12:00)
logs at most one bet for today, using the forecasts available right now.
Open bets are settled from Kalshi's own result. Ledger rows are only ever
appended; settlement fills in result columns.
"""
from pathlib import Path

import numpy as np
import pandas as pd

from edge import weather as wx

ROOT = Path(__file__).resolve().parent.parent / "paper"
ROOT.mkdir(exist_ok=True)
LEDGER = ROOT / "weather_bets.csv"
EDGE, MIN_P, MAX_P, ENS_INFLATE = 0.10, 0.05, 0.95, 1.3
SD_FLOOR = {"fahrenheit": 1.5, "celsius": 0.8}
COLS = ["city_day", "logged_at_utc", "series", "city", "date", "ticker", "side", "price", "prob", "edge",
        "mu", "sd", "n_models", "stake", "status", "pnl", "settled_at_utc"]


def ledger() -> pd.DataFrame:
    if LEDGER.exists():
        d = pd.read_csv(LEDGER, dtype={"status": str, "settled_at_utc": str})
        d["settled_at_utc"] = d["settled_at_utc"].fillna("")
        return d
    return pd.DataFrame(columns=COLS)


def _event(series, day):
    return f"{series}-{day:%y}{day.strftime('%b').upper()}{day:%d}"


def live_forecast(lat, lon, tz, unit):
    r = wx._get("https://api.open-meteo.com/v1/forecast", dict(
        latitude=lat, longitude=lon, daily="temperature_2m_max", models=",".join(wx.MODELS),
        timezone=tz, forecast_days=1, temperature_unit=unit))
    d = r.json().get("daily", {}) if r is not None and r.status_code == 200 else {}
    vals = [d[k][0] for k in d if k.startswith("temperature_2m_max") and d[k] and d[k][0] is not None]
    e = wx._get("https://ensemble-api.open-meteo.com/v1/ensemble", dict(
        latitude=lat, longitude=lon, daily="temperature_2m_max", models="gfs_seamless",
        timezone=tz, forecast_days=1, temperature_unit=unit))
    ed = e.json().get("daily", {}) if e is not None and e.status_code == 200 else {}
    members = [ed[k][0] for k in ed if "member" in k and ed[k] and ed[k][0] is not None]
    if len(vals) < 2 or len(members) < 10:
        return None
    sd = max(ENS_INFLATE * float(np.std(members, ddof=1)), SD_FLOOR[unit])
    return float(np.mean(vals)), sd, len(vals)


def decide(series, city, tz, lat, lon, now):
    local = now.tz_convert(tz)
    day = local.normalize().tz_localize(None)
    r = wx._get(f"{wx.KALSHI}/markets", {"event_ticker": _event(series, day)})
    ms = r.json().get("markets", []) if r is not None and r.status_code == 200 else []
    ms = [m for m in ms if m.get("status") in ("active", "open")]
    if not ms:
        return None
    unit = wx._unit(ms[0])
    fc = live_forecast(lat, lon, tz, unit)
    if fc is None:
        return None
    mu, sd, n = fc
    best = None
    for m in ms:
        bid, ask = (pd.to_numeric(m.get(k), errors="coerce") for k in ("yes_bid_dollars", "yes_ask_dollars"))
        p = wx.prob_yes({"floor": m.get("floor_strike"), "cap": m.get("cap_strike"),
                         "strike_type": m.get("strike_type")}, mu, sd)
        if not np.isfinite(p):
            continue
        for side, prob, price in (("yes", p, ask), ("no", 1 - p, 1 - bid if pd.notna(bid) else np.nan)):
            if pd.notna(price) and MIN_P <= price <= MAX_P and prob - price >= EDGE:
                if best is None or prob - price > best["edge"]:
                    best = dict(ticker=m["ticker"], side=side, price=float(price), prob=float(prob),
                                edge=float(prob - price))
    if best is None:
        return dict(status="no_bet", ticker="", side="", price=np.nan, prob=np.nan, edge=np.nan,
                    mu=mu, sd=sd, n_models=n, date=day.date().isoformat())
    return {**best, "status": "open", "mu": mu, "sd": sd, "n_models": n, "date": day.date().isoformat()}


def settle(led, now):
    for i in led.index[led["status"] == "open"]:
        r = wx._get(f"{wx.KALSHI}/markets/{led.at[i, 'ticker']}")
        m = r.json().get("market", {}) if r is not None and r.status_code == 200 else {}
        if m.get("result") not in ("yes", "no"):
            continue
        won = m["result"] == led.at[i, "side"]
        price = float(led.at[i, "price"])
        n = wx.STAKE / price
        led.at[i, "status"] = "won" if won else "lost"
        led.at[i, "pnl"] = round(n * won - wx.STAKE - wx.fee(n, price), 2)
        led.at[i, "settled_at_utc"] = now.isoformat()
    return led


def summary(led, now):
    s = led[led["status"].isin(["won", "lost"])]
    pnl = s["pnl"].astype(float)
    lines = ["# Live paper test: Kalshi weather (forward, latest forecasts)", "",
             f"Updated {now:%Y-%m-%d %H:%M} UTC. Rules: PROTOCOL_ROUND5.md, \"Forward test\". $10 paper bets.", "",
             "| | |", "|---|---|",
             f"| City-days checked | {len(led)} |",
             f"| Bets placed | {int(led['status'].isin(['open', 'won', 'lost']).sum())} |",
             f"| Open | {int((led['status'] == 'open').sum())} |",
             f"| Settled | {len(s)} (won {int((s['status'] == 'won').sum())}) |",
             f"| **Profit** | **${pnl.sum():+,.2f}** |",
             f"| ROI | {pnl.sum() / (len(s) * wx.STAKE):+.1%} |" if len(s) else "| ROI | n/a |"]
    if len(s):
        daily = s.groupby("date")["pnl"].sum()
        lines += ["", f"Green days: {(daily > 0).sum()} of {len(daily)}", "",
                  "| Date | Bets | P&L |", "|---|---:|---:|"]
        lines += [f"| {d} | {int((s['date'] == d).sum())} | ${v:+.2f} |" for d, v in daily.items()]
    return "\n".join(lines) + "\n"


def run(now=None):
    now = now or pd.Timestamp.now(tz="UTC")
    led = ledger()
    new = []
    for series, city, tier, lat, lon, tz in wx.daily_high_series():
        local = now.tz_convert(tz)
        if not (9 <= local.hour < 12):
            continue
        key = f"{series}|{local:%Y-%m-%d}"
        if key in set(led["city_day"]):
            continue
        d = decide(series, city, tz, lat, lon, now)
        if d is None:
            continue
        new.append({**d, "city_day": key, "logged_at_utc": now.isoformat(), "series": series, "city": city,
                    "stake": wx.STAKE if d["status"] == "open" else 0.0, "pnl": np.nan, "settled_at_utc": ""})
    if new:
        led = pd.concat([led, pd.DataFrame(new)[COLS]], ignore_index=True)
    led = settle(led, now)
    led[COLS].to_csv(LEDGER, index=False)
    (ROOT / "WEATHER.md").write_text(summary(led, now))
    print(f"checked {len(new)} new city-days, bets {sum(x['status'] == 'open' for x in new)}; ledger {len(led)}")


if __name__ == "__main__":
    run()

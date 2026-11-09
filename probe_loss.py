"""One-off: what happened at the 2026-11-08 22:00 UTC KXBTCD settlement?"""
import json, os, requests
os.makedirs("probe/loss", exist_ok=True)
H = {"User-Agent": "Mozilla/5.0 (research probe)"}
out = {}
def g(k, url, **kw):
    try:
        r = requests.get(url, headers=H, timeout=30, **kw); out[k] = r.json() if "json" in r.headers.get("content-type", "") else r.text[:3000]
    except Exception as e:
        out[k] = repr(e)
for t in ["KXBTCD-26NOV0817-T74249.99", "KXBTCD-26NOV0817-T73999.99", "KXBTCD-26NOV0817-T74999.99", "KXXRPD-26NOV0817-T1.1199"]:
    g(t, f"https://api.elections.kalshi.com/trade-api/v2/markets/{t}")
g("kalshi_trades_74249", "https://api.elections.kalshi.com/trade-api/v2/markets/trades", params={"ticker": "KXBTCD-26NOV0817-T74249.99", "limit": 1000})
for p in ["BTC-USD", "XRP-USD"]:
    g(f"cb_{p}", f"https://api.exchange.coinbase.com/products/{p}/candles", params={"granularity": 60, "start": "2026-11-08T21:30:00Z", "end": "2026-11-08T22:05:00Z"})
g("kraken_btc", "https://api.kraken.com/0/public/OHLC", params={"pair": "XBTUSD", "interval": 1, "since": 1762637400})
g("bitstamp_btc", "https://www.bitstamp.net/api/v2/ohlc/btcusd/", params={"step": 60, "limit": 40, "start": 1762637400})
g("binance_btc", "https://data-api.binance.vision/api/v3/klines", params={"symbol": "BTCUSDT", "interval": "1m", "startTime": 1762637400000, "limit": 40})
json.dump(out, open("probe/loss/report.json", "w"), indent=1, default=str)

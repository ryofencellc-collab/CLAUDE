"""One-off probe: free intraday / 0DTE option-chain sources reachable from Actions."""
import json, os, time, requests
OUT = "probe/0dte"; os.makedirs(OUT, exist_ok=True)
H = {"User-Agent": "Mozilla/5.0 (research probe)", "Accept": "application/json,text/html,*/*"}
rep = []
def hit(name, url, save=None, **kw):
    try:
        r = requests.get(url, headers={**H, **kw.pop("headers", {})}, timeout=30, **kw)
        info = {"name": name, "url": url, "status": r.status_code, "bytes": len(r.content),
                "ctype": r.headers.get("content-type"), "head": r.text[:600]}
        if save and r.ok:
            open(f"{OUT}/{save}", "wb").write(r.content[:3_000_000])
    except Exception as e:
        info = {"name": name, "url": url, "error": repr(e)[:300]}
    rep.append(info); print(json.dumps(info)[:800]); return info

for sym in ["SPY", "_SPX", "QQQ", "IWM", "_XSP"]:
    hit(f"cboe {sym}", f"https://cdn.cboe.com/api/global/delayed_quotes/options/{sym}.json", save=f"cboe_{sym}.json")
hit("cboe quote SPY", "https://cdn.cboe.com/api/global/delayed_quotes/quotes/SPY.json")
hit("nasdaq chain SPY", "https://api.nasdaq.com/api/quote/SPY/option-chain?assetclass=etf&limit=60&fromdate=all&todate=undefined&excode=oprac&callput=callput&money=all&type=all", save="nasdaq_SPY.json")
hit("yahoo chain SPY", "https://query2.finance.yahoo.com/v7/finance/options/SPY")
hit("optionsdx", "https://www.optionsdx.com/", save="optionsdx.html")
hit("optionsdx spx", "https://www.optionsdx.com/product/spx-option-chain/", save="optionsdx_spx.html")
hit("twm2058 repo", "https://api.github.com/repos/twm2058/spx-0dte-archive/contents/")
hit("twm2058 readme", "https://raw.githubusercontent.com/twm2058/spx-0dte-archive/main/README.md", save="twm_readme.md")
hit("philippdubach", "https://api.github.com/repos/philippdubach/options-data/contents/")
hit("hf search", "https://huggingface.co/api/datasets?search=0dte&limit=50")
hit("hf search spx options", "https://huggingface.co/api/datasets?search=spx%20options&limit=50")
hit("hf search option chain", "https://huggingface.co/api/datasets?search=option%20chain&limit=50")
hit("kaggle spx 0dte", "https://www.kaggle.com/api/v1/datasets/list?search=0dte")
hit("kaggle spy options", "https://www.kaggle.com/api/v1/datasets/list?search=spy%20options%20intraday")
# Cboe: take two snapshots 70s apart to measure update cadence
try:
    a = requests.get("https://cdn.cboe.com/api/global/delayed_quotes/options/_SPX.json", headers=H, timeout=30).json()
    time.sleep(70)
    b = requests.get("https://cdn.cboe.com/api/global/delayed_quotes/options/_SPX.json", headers=H, timeout=30).json()
    rep.append({"cadence": [a.get("timestamp"), b.get("timestamp")], "n_opts": len(a.get("data", {}).get("options", []))})
    print(rep[-1])
except Exception as e:
    rep.append({"cadence_error": repr(e)[:300]})
json.dump(rep, open(f"{OUT}/report.json", "w"), indent=1)

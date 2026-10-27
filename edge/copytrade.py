"""Round 8 data: 13F holdings (SEC EDGAR) and House trade disclosures (House Clerk).

See PROTOCOL_ROUND8.md. Primary sources only. Network calls identify this
project in the User-Agent, as SEC requires.
"""
import io
import json
import re
import subprocess
import tempfile
import time
import xml.etree.ElementTree as ET
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
import requests

# SEC asks for "Company Name contact@domain"; a GitHub no-reply address keeps it impersonal
UA = {"User-Agent": "ryofencellc-collab-research 265339802+ryofencellc-collab@users.noreply.github.com",
      "Accept-Encoding": "gzip, deflate"}
_s = requests.Session()
_s.headers.update(UA)
TOP_N = 20  # holdings kept per filing


def _get(url, tries=5, **kw):
    for i in range(tries):
        try:
            r = _s.get(url, timeout=60, **kw)
            if r.status_code == 200:
                return r
            if r.status_code in (403, 404):
                return r
        except requests.RequestException:
            pass
        time.sleep(1.5 * 2 ** i)
    return None


# ------------------------------------------------------------------ 13F

class SecBlocked(RuntimeError):
    """SEC answered 403 (rate threshold). Stop and try again on a later schedule, never at once."""


def _sec(url):
    r = _get(url, tries=3)
    if r is not None and r.status_code == 403:
        raise SecBlocked(url)
    return r


def _filings(cik: str) -> list[dict]:
    base = "https://data.sec.gov/submissions/"
    r = _sec(f"{base}CIK{int(cik):010d}.json")
    if r is None or r.status_code != 200:
        raise RuntimeError(f"SEC submissions for {cik}: {None if r is None else (r.status_code, r.text[:200])}")
    j = r.json()
    blocks = [j["filings"]["recent"]] + [_sec(base + f["name"]).json() for f in j["filings"].get("files", [])]
    out = []
    for b in blocks:
        for acc, form, filed, period in zip(b["accessionNumber"], b["form"], b["filingDate"], b["reportDate"]):
            if form == "13F-HR":
                out.append(dict(accession=acc, filed=filed, period=period))
    return out


def _info_table(cik: str, acc: str) -> pd.DataFrame:
    folder = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace('-', '')}"
    idx = _sec(f"{folder}/index.json")
    if idx is None or idx.status_code != 200:
        return pd.DataFrame()
    items = idx.json()["directory"]["item"]
    xmls = [i for i in items if i["name"].lower().endswith(".xml") and i["name"].lower() != "primary_doc.xml"]
    if not xmls:
        return pd.DataFrame()
    name = max(xmls, key=lambda i: int(i.get("size") or 0))["name"]
    time.sleep(0.15)
    r = _sec(f"{folder}/{name}")
    if r is None or r.status_code != 200:
        return pd.DataFrame()
    root = ET.fromstring(r.content)
    rows = []
    for it in root.iter():
        if not it.tag.endswith("infoTable"):
            continue
        f = {c.tag.split("}")[-1]: c for c in it.iter()}
        if "putCall" in f and (f["putCall"].text or "").strip():
            continue  # options, not stock
        rows.append(dict(cusip=(f["cusip"].text or "").strip().upper(),
                         issuer=(f["nameOfIssuer"].text or "").strip(),
                         value=float(f["value"].text or 0),
                         shares=float(f["sshPrnamt"].text or 0) if "sshPrnamt" in f else 0.0))
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    return df.groupby(["cusip", "issuer"], as_index=False)[["value", "shares"]].sum()


def fetch_13f(cik: str, name: str) -> pd.DataFrame:
    parts = []
    for f in _filings(cik):
        if f["filed"] < "2013-10-01":
            continue
        t = _info_table(cik, f["accession"])
        time.sleep(0.15)
        if t.empty:
            continue
        t = t.sort_values("value", ascending=False).head(TOP_N)
        t["weight"] = t["value"] / t["value"].sum()   # within top 20; units changed in 2023, weights don't care
        t["rank"] = range(1, len(t) + 1)
        parts.append(t.assign(cik=cik, fund=name, **f))
    df = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
    print(f"  {name}: {len(parts)} filings, {len(df)} rows", flush=True)
    return df


def figi_map(cusips: list[str]) -> dict[str, str]:
    """CUSIP -> Yahoo ticker via OpenFIGI (no key: 10 ids per request, 25 requests a minute)."""
    out = {}
    for i in range(0, len(cusips), 10):
        chunk = cusips[i:i + 10]
        body = [{"idType": "ID_CUSIP", "idValue": c, "exchCode": "US"} for c in chunk]
        for attempt in range(5):
            r = requests.post("https://api.openfigi.com/v3/mapping", json=body, timeout=60)
            if r.status_code == 429:
                time.sleep(10)
                continue
            break
        if r.status_code == 200:
            for c, res in zip(chunk, r.json()):
                data = res.get("data") or []
                if data and data[0].get("ticker"):
                    out[c] = data[0]["ticker"].replace("/", "-").replace(" ", "-")
        time.sleep(2.5)
    return out


# ------------------------------------------------------------------ Congress (House PTRs)

CLERK = "https://disclosures-clerk.house.gov/public_disc"
TX_START = re.compile(r"\s(P|S \(partial\)|S|E)\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})(?:\s+(.*))?$")
TICKER = re.compile(r"\(([A-Z][A-Z0-9.\-]{0,6})\)\s*\[([A-Z]{2})\]")
# STOCK Act reporting brackets: the low end fixes the high end
BRACKETS = {1001: 15000, 15001: 50000, 50001: 100000, 100001: 250000, 250001: 500000, 500001: 1000000,
            1000001: 5000000, 5000001: 25000000, 25000001: 50000000}
AMOUNT = re.compile(r"\$([\d,]+)\s*-\s*\$([\d,]+)|Over \$([\d,]+)")


def _index(year: int) -> pd.DataFrame:
    r = _get(f"{CLERK}/financial-pdfs/{year}FD.zip")
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        xml = z.read(next(n for n in z.namelist() if n.lower().endswith(".xml")))
    rows = []
    for m in ET.fromstring(xml).iter("Member"):
        g = {c.tag: (c.text or "").strip() for c in m}
        if g.get("FilingType") == "P" and g.get("DocID", "").startswith("2"):  # electronic PTRs only
            rows.append(dict(doc_id=g["DocID"], member=f"{g.get('First', '')} {g.get('Last', '')}".strip(),
                             last=g.get("Last", ""), district=g.get("StateDst", ""),
                             filed=pd.to_datetime(g.get("FilingDate"), errors="coerce")))
    return pd.DataFrame(rows)


def parse_ptr_text(text: str) -> list[dict]:
    lines = text.splitlines()
    starts = [i for i, ln in enumerate(lines) if TX_START.search(ln)]
    out = []
    for k, i in enumerate(starts):
        block = lines[i:(starts[k + 1] if k + 1 < len(starts) else min(i + 6, len(lines)))][:6]
        m = TX_START.search(lines[i])
        btxt = " ".join(block)
        t = TICKER.search(btxt)
        if not t:
            continue
        lo = hi = None
        rest = m.group(4) or ""
        a = AMOUNT.search(rest)
        if a and a.group(3):
            lo = hi = float(a.group(3).replace(",", ""))
        elif a:
            lo, hi = float(a.group(1).replace(",", "")), float(a.group(2).replace(",", ""))
        else:
            half = re.search(r"\$([\d,]+)\s*-", rest)  # range split over lines; checkbox letters may follow
            if half:
                lo = float(half.group(1).replace(",", ""))
                hi = float(BRACKETS.get(int(lo), np.nan))
        if lo is None:  # amount on its own line below the dates
            a = AMOUNT.search(re.sub(r"\s+", " ", " ".join(block[1:])))
            if a and a.group(3):
                lo = hi = float(a.group(3).replace(",", ""))
            elif a:
                lo, hi = float(a.group(1).replace(",", "")), float(a.group(2).replace(",", ""))
        owner = re.match(r"\s*(SP|JT|DC)\s", lines[i])
        out.append(dict(type=m.group(1).split()[0], tx_date=m.group(2), ticker=t.group(1), asset_type=t.group(2),
                        owner=owner.group(1) if owner else "",
                        amount_low=lo, amount_high=hi,
                        raw="" if lo is not None else " | ".join(x.strip() for x in block)[:400]))
    return out


_DIAG = []  # (doc_id, status, text_len, n_tx, head) per report, for the fetch log


def _ptr(year: int, doc_id: str) -> list[dict]:
    r = _get(f"{CLERK}/ptr-pdfs/{year}/{doc_id}.pdf")
    if r is None or r.status_code != 200 or not r.content.startswith(b"%PDF"):
        _DIAG.append((doc_id, "no-pdf" if r is None else f"http {r.status_code} {r.content[:20]!r}", 0, 0, ""))
        return []
    with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
        f.write(r.content)
        f.flush()
        try:
            text = subprocess.run(["pdftotext", "-layout", f.name, "-"], capture_output=True, timeout=60).stdout
        except (OSError, subprocess.SubprocessError):
            _DIAG.append((doc_id, "pdftotext failed", 0, 0, ""))
            return []
    text = text.decode("utf-8", "replace")
    rows = parse_ptr_text(text)
    _DIAG.append((doc_id, "ok", len(text), len(rows), "" if rows else " / ".join(
        ln.strip() for ln in text.splitlines() if ln.strip())[:600]))
    return rows


def fetch_congress_year(year: int) -> pd.DataFrame:
    idx = _index(year)
    with ThreadPoolExecutor(6) as ex:
        trades = list(ex.map(lambda d: _ptr(year, d), idx["doc_id"]))
    rows = [dict(r, **m) for m, ts in zip(idx.to_dict("records"), trades) for r in ts]
    df = pd.DataFrame(rows)
    if len(df):
        df["tx_date"] = pd.to_datetime(df["tx_date"], format="%m/%d/%Y", errors="coerce")
    d = pd.DataFrame(_DIAG, columns=["doc", "status", "chars", "n_tx", "head"])
    print(f"  fetch status: {d['status'].str[:8].value_counts().to_dict()}; text chars median "
          f"{d['chars'].median():.0f}; reports with 0 trades: {(d['n_tx'] == 0).sum()}", flush=True)
    for _, x in d[(d["status"] == "ok") & (d["n_tx"] == 0)].head(3).iterrows():
        print(f"  ZERO-TRADE {x['doc']}: {x['head']}", flush=True)
    for _, x in d[d["status"] != "ok"].head(3).iterrows():
        print(f"  FAILED {x['doc']}: {x['status']}", flush=True)
    print(f"  {year}: {len(idx)} electronic PTRs, {len(df)} transactions, "
          f"{int((df['asset_type'] == 'ST').sum()) if len(df) else 0} stock trades", flush=True)
    return df

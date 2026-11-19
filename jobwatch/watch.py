"""Daily watch of official career boards for remote / NYC-area CT, MR, 3D and imaging jobs (user: RT(R)(CT)(MR), NYC, prefers remote).
Prints NEW matches since the last run and writes jobwatch/LATEST.md. State: jobwatch/seen.json."""
import json, os, re, subprocess, sys, time
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
SEEN = os.path.join(HERE, "seen.json")
UA = {"User-Agent": "Mozilla/5.0 (job-watch)"}

RELEVANT = re.compile(r"\b(CT|MRI?|MR|3D|imag\w*|radiolog\w*|technologist|applications? specialist|clinical (support|applications?|account|field|education)"
                      r"|post.?process\w*|visuali[sz]ation|core lab|scan\w*)\b", re.I)
EXCLUDE = re.compile(r"engineer|counsel|finance|payroll|marketing|product|data scien|director|recruit|HR |human resources|account executive|regional sales", re.I)
NYAREA = re.compile(r"new york|\bNY\b|NYC|new jersey|\bNJ\b|connecticut|northeast|tri.?state|long island|brooklyn|queens", re.I)
REMOTE = re.compile(r"^\s*(remote|virtual( us)?|united states|us remote|remote,? (us|usa|united states))\s*$", re.I)
REGION_IN_TITLE = re.compile(r" - |\(.*(region|territory)", re.I)


def greenhouse(board, label):
    r = requests.get(f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs", timeout=30, headers=UA)
    return [dict(source=label, title=j["title"], location=j["location"]["name"], url=j["absolute_url"]) for j in r.json().get("jobs", [])]


def ge():
    out = {}
    for kw in ["MRI clinical applications", "CT clinical applications", "clinical applications specialist", "remote technologist",
               "advanced visualization", "MR technologist", "CT technologist", "imaging specialist"]:
        for frm in range(0, 60, 10):
            s = requests.get("https://careers.gehealthcare.com/global/en/search-results", params={"keywords": kw, "from": frm}, timeout=30, headers=UA).text
            n = 0
            for m in re.finditer(r'"title":"([^"]+)","jobSeqNo":"([^"]+)"', s):
                win = s[m.end():m.end() + 1500]
                loc = re.search(r'"cityStateCountry":"([^"]+)"', win)
                multi = re.findall(r'"location":"([^"]+)"', win[:1200])
                out[m.group(2)] = dict(source="GE HealthCare", title=m.group(1), location="; ".join(dict.fromkeys(multi)) or (loc.group(1) if loc else ""),
                                       url=f"https://careers.gehealthcare.com/global/en/job/{m.group(2)}")
                n += 1
            if n < 10: break
            time.sleep(1)
    return list(out.values())


def browser_boards():
    try:
        r = subprocess.run(["node", os.path.join(HERE, "browser.js")], capture_output=True, text=True, timeout=900)
        return json.loads(r.stdout.strip().splitlines()[-1])
    except Exception as e:
        print("browser boards failed:", repr(e), file=sys.stderr); return []


def keep(j):
    loc = j.get("location", "") or ""
    t = j["title"]
    if j["source"] in ("3DR Labs",): return True                                   # every 3DR posting is remote post-processing
    if not RELEVANT.search(t) or EXCLUDE.search(t): return False
    if j["source"] == "GE HealthCare" and "United States" not in loc: return False
    if NYAREA.search(loc) or NYAREA.search(t) or (j["source"] == "Hologic" and NYAREA.search(j.get("text", ""))):
        return True                                                                  # NYC area (field or remote)
    return bool(REMOTE.match(loc) and not REGION_IN_TITLE.search(t))                 # nationwide remote, no other territory


def main():
    jobs, errors = [], []
    for fn, args in [(greenhouse, ("cleerlyhealth", "Cleerly")), (greenhouse, ("hyperfine53", "Hyperfine")),
                     (greenhouse, ("heartflowinc", "HeartFlow")), (ge, ()), (browser_boards, ())]:
        try: jobs += fn(*args)
        except Exception as e: errors.append(f"{fn.__name__}{args}: {e!r}")
    hits = [j for j in jobs if keep(j)]
    seen = json.load(open(SEEN)) if os.path.exists(SEEN) else {}
    new = [j for j in hits if j["url"] not in seen]
    now = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    for j in hits: seen.setdefault(j["url"], now)
    json.dump(seen, open(SEEN, "w"), indent=1)
    lines = [f"# Job watch ({now})", "", f"Boards checked: Cleerly, Hyperfine, HeartFlow, GE HealthCare, Hologic, 3DR Labs. Jobs scanned: {len(jobs)}. Matches: {len(hits)}. **New: {len(new)}**.", ""]
    for j in sorted(hits, key=lambda x: (x["url"] not in [n["url"] for n in new], x["source"])):
        lines.append(f"- {'🆕 ' if j in new else ''}**{j['source']}** – {j['title']} ({j['location']}) – {j['url']}")
    if errors: lines += ["", "Errors: " + "; ".join(errors)]
    open(os.path.join(HERE, "LATEST.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

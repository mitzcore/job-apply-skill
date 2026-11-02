#!/usr/bin/env python3
"""Screen DreamWork listings: JD blockers + H-1B LCA history + already-applied dedupe.

Usage: python3 screen.py [data/dreamwork.json] [--no-h1b]
  --no-h1b  skip the H-1B LCA check (for candidates who do not need sponsorship)
Writes data/candidates.json (ranked, eligible) and prints a table incl. rejects with reasons.
H-1B lookups are cached in data/h1b_cache.json (keyed by search name).
"""
import json, re, sys, csv, pathlib, subprocess, urllib.parse, concurrent.futures as cf

ROOT = pathlib.Path(__file__).parent
DATA = ROOT / "data"
CACHE = DATA / "h1b_cache.json"

# Hard blockers in the job description (sponsorship refused, citizenship/clearance required)
BLOCK = re.compile(
    r"not (pursue|provide|offer|be able to|able to)[^.]{0,30}sponsor|unable to sponsor|will not sponsor|cannot sponsor|"
    r"does not (offer |provide )?sponsor|no (visa )?sponsorship|without[^.]{0,40}sponsorship|"
    r"citizen(ship)? (is )?required|must be a u\.?s\.? citizen|u\.?s\.? citizens? only|"
    r"security clearance|ts/sci|secret clearance|\bITAR\b|green card|permanent resident", re.I)

# Without the H-1B gate, still reject roles that need clearance/citizenship (edit if you have one)
CLEARANCE = re.compile(r"security clearance|ts/sci|secret clearance|\bITAR\b", re.I)

# Company-name aliases for LCA search where DreamWork's display name != legal employer name
ALIASES = {
    "chubb": ["ACE American Insurance"], "coinbase": ["Coinbase Inc"], "jpmorgan chase": ["JPMorgan Chase"],
    "american express": ["American Express Company"], "orioninnovation": ["Orion Systems Integrators"],
    "formationbio": ["Formation Bio"], "eliseai": ["Elise AI"], "harnessinc": ["Harness Inc"],
    "legion": ["Legion Technologies"], "gemini": ["Gemini Trust"], "kong": ["Kong Inc"], "writer": ["Writer Inc"],
    "altanaai": ["Altana"], "nomic.ai": ["Nomic"], "waabi": ["Waabi"], "descript": ["Descript"],
}

# Companies whose LCA match was verified by hand (DreamWork name, lowercase). Add after verifying a CHECK row.
VERIFIED = {"jpmorgan chase", "gemini", "nbcuniversal", "waabi", "chubb", "coinbase", "pinterest", "sentinelone",
            "demandbase", "mirantis", "deepgram", "harnessinc", "legion", "descript", "kong", "writer", "eliseai",
            "langchain", "altanaai", "formationbio", "nomic.ai", "orioninnovation", "quantiphi", "reltio"}
# Known false matches (LCA hits belong to a different company). Treated as no record.
FALSE_MATCH = {"basis ai", "camber", "roche", "comet", "axion", "tenex", "scribe", "rain", "circle", "recar", "gitlab", "kraken", "confido"}

def lca_rows(name):
    u = "https://h1bdata.info/index.php?" + urllib.parse.urlencode({"em": name, "job": "", "city": "", "year": "all years"})
    s = subprocess.run(["curl", "-sL", "-m", "40", "-A", "Mozilla/5.0", u], capture_output=True, text=True).stdout
    rows = []
    for r in re.findall(r"<tr>(.*?)</tr>", s, re.S)[1:]:
        c = [x.strip() for x in re.findall(r"<td[^>]*>(.*?)</td>", re.sub(r"</?a[^>]*>", "", r), re.S)]
        if len(c) >= 5: rows.append(c)
    return rows

def search_names(co):
    k = co.lower().strip()
    if k in ALIASES: return ALIASES[k]
    base = re.sub(r"(\.ai|\.io|\.com)$", "", k)
    base = re.sub(r"\b(inc|llc|corp|ai|technologies)\b", "", base).strip(" .,")
    return list(dict.fromkeys([base.title(), co]))

def h1b(co, cache):
    for nm in search_names(co):
        if nm not in cache:
            rows = lca_rows(nm)
            cache[nm] = {"n": len(rows), "employers": sorted({r[0] for r in rows})[:4],
                         "years": sorted({r[4][-4:] for r in rows}), "eng": sum(bool(re.search(r"ENGINEER|DEVOPS|ARCHITECT|RELIAB|INFRA|PLATFORM", r[1])) for r in rows)}
        if cache[nm]["n"]:
            return nm, cache[nm]
    return None, {"n": 0}

def applied_keys():
    keys = set()
    p = ROOT / "applied.csv"
    if p.exists():
        for r in csv.DictReader(open(p)):
            keys.add((r["company"].lower()[:10], r["title"].lower()[:25]))
    return keys

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    need_h1b = "--no-h1b" not in sys.argv
    src = pathlib.Path(args[0] if args else DATA / "dreamwork.json")
    d = json.loads(src.read_text())
    if isinstance(d, str): d = json.loads(d)
    L = d["listings"]
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    done = applied_keys()
    rejects, todo = [], []
    for l in L:
        key = (l["co"].lower()[:10], l["title"].lower()[:25])
        if any(key[0][:6] == a[:6] and key[1][:15] == b[:15] for a, b in done):
            rejects.append((l, "already applied")); continue
        desc = re.sub("<[^>]+>", " ", l.get("description") or "")
        m = BLOCK.search(desc) if need_h1b else CLEARANCE.search(desc)
        if m:
            rejects.append((l, f"JD blocker: '{m.group(0)}'")); continue
        todo.append(l)
    if not need_h1b:
        for l in todo: l.update(h1b="n/a", h1b_n=0, h1b_check=False)
    with cf.ThreadPoolExecutor(6) as ex:
        res = list(ex.map(lambda l: (l, h1b(l["co"], cache)), todo)) if need_h1b else []
    CACHE.write_text(json.dumps(cache, indent=1))
    ok = [] if need_h1b else list(todo)
    for l, (nm, info) in res:
        if not info["n"] or l["co"].lower() in FALSE_MATCH:
            rejects.append((l, "no H-1B LCA record" if info["n"] == 0 else "H-1B hits belong to a different company")); continue
        # Prefix search can hit unrelated companies (Camber -> Camber Collective, Roche -> Roche Bobois).
        # Trust only an exact legal-name match (NAME + optional INC/LLC/CORP...) from a single employer; else CHECK.
        base = re.escape(nm.upper().rstrip("."))
        exact = [e for e in info["employers"] if re.fullmatch(base + r"(,? (INC|LLC|CORP|CORPORATION|CO|COMPANY|LP|TECHNOLOGIES INC|TECHNOLOGIES CORP)\.?)?", e.strip())]
        l["h1b_check"] = l["co"].lower() not in VERIFIED and not (exact and len(info["employers"]) <= 2)
        l["h1b"] = f"{info['n']} LCAs ({', '.join(info['employers'][:2])}; {info['years'][0]}-{info['years'][-1]})"
        l["h1b_n"] = info["n"]
        ok.append(l)
    # rank: NYC first, then pay ceiling, then H-1B depth
    nyc = lambda l: bool(re.search(r"new york|nyc|brooklyn|manhattan|jersey|, ny|, nj", (l["loc"] or ""), re.I)) and l["remote"] != "remote"
    ok.sort(key=lambda l: (not nyc(l), -(l["max"] or 0), -l["h1b_n"]))
    (DATA / "candidates.json").write_text(json.dumps(ok, indent=1))
    print(f"ELIGIBLE {len(ok)} (of {len(L)} prefiltered, {d.get('totalMatches')} total matches)")
    for i, l in enumerate(ok):
        print(f"{i:3} {'NYC' if nyc(l) else 'REM'} ${(l['min'] or 0)//1000}-{(l['max'] or 0)//1000}k | {l['plat']:<10} | {l['co'][:20]:<20} | {l['title'][:55]:<55} | {'CHECK ' if l['h1b_check'] else ''}{l['h1b'][:45]}")
    print(f"\nREJECTED {len(rejects)}")
    for l, why in rejects:
        print(f"    {l['co'][:20]:<20} | {l['title'][:45]:<45} | {why}")

if __name__ == "__main__":
    main()

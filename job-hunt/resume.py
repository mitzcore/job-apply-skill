#!/usr/bin/env python3
"""Resume generator: profile.py + per-job overrides -> HTML -> PDF (headless Chrome).

Usage:
  python3 resume.py                 # build master
  python3 resume.py variants.json   # build every variant in file
"""
import html, json, os, subprocess, sys, pathlib

OUT = pathlib.Path(__file__).parent / "out"
CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

from profile import NAME, FILE_PREFIX, CONTACT, PILLARS, NUMBERS, EXPERIENCE, EARLIER, EDUCATION, MASTER

CSS = """
@page { size: Letter; margin: 0.4in 0.5in; }
* { box-sizing: border-box; }
body { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; color: #1a1a1a; font-size: 9.4pt; line-height: 1.33; margin: 0; }
h1 { font-size: 21pt; letter-spacing: 0.5px; margin: 0; font-weight: 700; }
.headline { font-size: 11.5pt; color: #0b5cad; font-weight: 600; margin-top: 2px; }
.tagline { font-size: 9pt; color: #555; margin-top: 1px; }
.contact { font-size: 8.8pt; color: #333; margin-top: 4px; }
.top { border-bottom: 2px solid #0b5cad; padding-bottom: 7px; margin-bottom: 8px; }
h2 { font-size: 9.2pt; text-transform: uppercase; letter-spacing: 1.4px; color: #0b5cad; margin: 9px 0 4px; font-weight: 700; }
.summary { margin: 0; }
.nums { display: flex; gap: 0; margin: 9px 0 2px; border: 1px solid #d6e2ef; border-radius: 4px; }
.num { flex: 1; text-align: center; padding: 5px 2px; border-right: 1px solid #d6e2ef; }
.num:last-child { border-right: 0; }
.num b { display: block; font-size: 13pt; color: #0b5cad; }
.num span { font-size: 7.8pt; color: #555; }
.grid { display: grid; grid-template-columns: 1fr 1fr; column-gap: 18px; row-gap: 6px; }
.pillar b { display: block; font-size: 9.6pt; }
.pillar p { margin: 1px 0 0; color: #333; font-size: 9pt; }
.job { margin-bottom: 7px; }
.jh { display: flex; justify-content: space-between; }
.jh b { font-size: 10pt; }
.jh span { color: #555; font-size: 9pt; white-space: nowrap; }
.jc { color: #333; font-size: 9.2pt; }
.lead { margin: 2px 0 1px; font-style: italic; color: #333; }
ul { margin: 2px 0 0 15px; padding: 0; }
li { margin: 1px 0; }
.small { font-size: 9pt; color: #333; margin: 0; }
"""

def e(s): return html.escape(s)

def render(v):
    p = v["pillars"]
    ptext = v.get("pillar_text", {})  # per-job rewording of proof lines, keyed by pillar id
    pillars = "".join(f'<div class="pillar"><b>{e(PILLARS[k][0])}</b><p>{e(ptext.get(k, PILLARS[k][1]))}</p></div>' for k in p)
    nums = "".join(f'<div class="num"><b>{e(a)}</b><span>{e(b)}</span></div>' for a, b in NUMBERS)
    jobs = ""
    for i, j in enumerate(EXPERIENCE):
        if i == 0:  # current role can be re-angled per job
            j = {**j, "lead": v.get("current_lead", j["lead"]), "bullets": v.get("current_bullets", j["bullets"])}
        lead = f'<p class="lead">{e(j["lead"])}</p>' if j["lead"] else ""
        bl = "".join(f"<li>{e(b)}</li>" for b in j["bullets"])
        jobs += (f'<div class="job"><div class="jh"><b>{e(j["title"])}</b><span>{e(j["dates"])}</span></div>'
                 f'<div class="jc">{e(j["co"])} · {e(j["loc"])}</div>{lead}<ul>{bl}</ul></div>')
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{e(NAME)} - {e(v['headline'])}</title>
<style>{CSS}</style></head><body>
<div class="top"><h1>{e(NAME.upper())}</h1><div class="headline">{e(v['headline'])}</div>
<div class="tagline">{e(v['tagline'])}</div><div class="contact">{e(CONTACT)}</div></div>
<p class="summary">{e(v['summary'])}</p>
<div class="nums">{nums}</div>
<h2>Areas of Expertise</h2><div class="grid">{pillars}</div>
<h2>Experience</h2>{jobs}
<p class="small"><b>Earlier:</b> {e(EARLIER)}</p>
<h2>Toolkit &amp; Education</h2><p class="small">{e(v['skills'])}</p>
<p class="small" style="margin-top:3px"><b>Education:</b> {e(EDUCATION)}</p>
</body></html>"""

def build(v):
    OUT.mkdir(exist_ok=True)
    base = {**MASTER, **v}
    d = OUT / base["dir"] if base.get("dir") else OUT
    d.mkdir(parents=True, exist_ok=True)
    name = f"{FILE_PREFIX}_Resume" if base.get("dir") else f"{FILE_PREFIX}_{base['slug']}"
    h = d / f"{name}.html"; pdf = d / f"{name}.pdf"
    h.write_text(render(base))
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", h.as_uri()], check=True, capture_output=True)
    pages = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    n = next((l.split()[-1] for l in pages.splitlines() if l.startswith("Pages")), "?")
    print(f"{pdf}  pages={n}")
    return pdf

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for v in json.load(open(sys.argv[1])): build(v)
    else:
        build({})
